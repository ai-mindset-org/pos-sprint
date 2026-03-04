"""
Telegram Saved Messages Extractor

Reads messages from Telegram "Saved Messages" (Favorites) for the last N days
and outputs structured JSON to /tmp/tg_saved_output.json.

First run requires interactive OTP authorization.
Session is stored next to the script (gitignored).

Usage:
    python3 tg_saved_extract.py [--days 30]
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import re
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaWebPage,
    PeerUser,
    PeerChannel,
    PeerChat,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger('tg_saved_extract')

# Credentials — set via environment variables or replace with your own
# Get your API_ID and API_HASH at https://my.telegram.org
API_ID = int(os.environ.get('TELEGRAM_API_ID', '0'))
API_HASH = os.environ.get('TELEGRAM_API_HASH', 'your-api-hash-here')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(SCRIPT_DIR, 'tg_saved_session')
OUTPUT_PATH = '/tmp/tg_saved_output.json'
STATE_PATH = os.path.join(SCRIPT_DIR, 'processed_ids.json')


def load_processed_ids() -> set[int]:
    """Load set of already-processed message IDs from state file."""
    if not os.path.exists(STATE_PATH):
        return set()
    try:
        with open(STATE_PATH, 'r') as f:
            data = json.load(f)
        return set(data.get('ids', []))
    except Exception as e:
        logger.warning(f'Failed to load state: {e}')
        return set()


def save_processed_ids(ids: set[int]) -> None:
    """Save processed message IDs to state file."""
    with open(STATE_PATH, 'w') as f:
        json.dump({'ids': sorted(ids), 'updated_at': datetime.now(timezone.utc).isoformat()}, f)
    logger.info(f'State saved: {len(ids)} processed IDs')


def mark_output_as_processed() -> None:
    """Read output JSON and mark those message IDs as processed."""
    if not os.path.exists(OUTPUT_PATH):
        logger.error(f'Output file not found: {OUTPUT_PATH}')
        return
    with open(OUTPUT_PATH, 'r') as f:
        data = json.load(f)
    new_ids = {msg['id'] for msg in data.get('messages', [])}
    existing = load_processed_ids()
    combined = existing | new_ids
    save_processed_ids(combined)
    logger.info(f'Marked {len(new_ids)} new IDs as processed (total: {len(combined)})')


FETCH_TIMEOUT = 10
MAX_CONTENT_LENGTH = 5000
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'


def fetch_url_content(url: str) -> dict | None:
    """Fetch URL and return title + text content (up to MAX_CONTENT_LENGTH chars)."""
    try:
        resp = requests.get(
            url,
            timeout=FETCH_TIMEOUT,
            headers={'User-Agent': USER_AGENT},
            allow_redirects=True,
        )
        resp.raise_for_status()

        content_type = resp.headers.get('content-type', '')
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return {'url': url, 'title': None, 'content': f'[Non-HTML: {content_type}]'}

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove script, style, nav, footer
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else None

        # Try article/main first, fallback to body
        main = soup.find('article') or soup.find('main') or soup.find('body')
        text = main.get_text(separator='\n', strip=True) if main else ''

        # Collapse whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text[:MAX_CONTENT_LENGTH]

        return {'url': url, 'title': title, 'content': text}

    except Exception as e:
        logger.warning(f'Failed to fetch {url}: {e}')
        return {'url': url, 'title': None, 'content': f'[Fetch error: {e}]'}


def fetch_urls_batch(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs in parallel using threads."""
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(fetch_url_content, urls))
    return [r for r in results if r]


def detect_media_type(message) -> str | None:
    """Detect media type from message."""
    if not message.media:
        return None
    if isinstance(message.media, MessageMediaPhoto):
        return 'photo'
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        if doc:
            for attr in doc.attributes:
                attr_name = type(attr).__name__
                if 'Video' in attr_name:
                    return 'video'
                if 'Audio' in attr_name or 'Voice' in attr_name:
                    return 'audio'
                if 'Sticker' in attr_name:
                    return 'sticker'
            return 'document'
    if isinstance(message.media, MessageMediaWebPage):
        return 'webpage'
    return 'other'


def extract_urls(text: str) -> list[str]:
    """Extract URLs from message text."""
    if not text:
        return []
    url_pattern = r'https?://[^\s<>\"\')\]]+'
    return re.findall(url_pattern, text)


async def get_forward_name(message, client) -> str | None:
    """Get the name of the forwarded source."""
    fwd = message.forward
    if not fwd:
        return None

    # Try chat title first (channels, groups)
    if fwd.chat:
        return fwd.chat.title or str(fwd.chat.id)

    # Try sender (users)
    if fwd.sender:
        sender = fwd.sender
        name_parts = []
        if hasattr(sender, 'first_name') and sender.first_name:
            name_parts.append(sender.first_name)
        if hasattr(sender, 'last_name') and sender.last_name:
            name_parts.append(sender.last_name)
        if name_parts:
            return ' '.join(name_parts)
        if hasattr(sender, 'title') and sender.title:
            return sender.title

    # Try from_name (for hidden forwards)
    if fwd.from_name:
        return fwd.from_name

    return None


async def extract_messages(client: TelegramClient, days: int, skip_processed: bool = True) -> list[dict]:
    """Extract messages from Saved Messages for the last N days.

    If skip_processed=True, filters out messages already in processed_ids.json.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    processed_ids = load_processed_ids() if skip_processed else set()

    messages = []
    count = 0
    skipped = 0

    logger.info(f'Reading Saved Messages for the last {days} days (since {cutoff.date()})...')
    if processed_ids:
        logger.info(f'Skipping {len(processed_ids)} already-processed messages')

    async for msg in client.iter_messages('me', limit=None):
        # Stop if message is older than cutoff
        if msg.date < cutoff:
            break

        count += 1

        # Skip already-processed messages
        if msg.id in processed_ids:
            skipped += 1
            continue
        text = msg.text or msg.message or ''
        media_type = detect_media_type(msg)
        forward_from = await get_forward_name(msg, client)
        urls = extract_urls(text)

        # Extract webpage URL if present
        if isinstance(msg.media, MessageMediaWebPage) and msg.media.webpage:
            wp = msg.media.webpage
            if hasattr(wp, 'url') and wp.url:
                urls.append(wp.url)
            urls = list(dict.fromkeys(urls))  # deduplicate

        entry = {
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': text,
            'media_type': media_type,
            'forward_from': forward_from,
            'urls': urls,
        }

        # Add webpage metadata if available
        if isinstance(msg.media, MessageMediaWebPage) and msg.media.webpage:
            wp = msg.media.webpage
            if hasattr(wp, 'title') and wp.title:
                entry['webpage_title'] = wp.title
            if hasattr(wp, 'description') and wp.description:
                entry['webpage_description'] = wp.description

        messages.append(entry)

    # Fetch URL contents in parallel for all messages
    all_urls = []
    url_to_msg_indices = {}  # url -> list of message indices
    for i, msg in enumerate(messages):
        for url in msg.get('urls', []):
            if url not in url_to_msg_indices:
                all_urls.append(url)
                url_to_msg_indices[url] = []
            url_to_msg_indices[url].append(i)

    if all_urls:
        logger.info(f'Fetching {len(all_urls)} unique URLs...')
        fetched = fetch_urls_batch(all_urls)
        url_content_map = {r['url']: r for r in fetched}

        for i, msg in enumerate(messages):
            msg_url_contents = []
            for url in msg.get('urls', []):
                if url in url_content_map:
                    msg_url_contents.append(url_content_map[url])
            if msg_url_contents:
                msg['url_contents'] = msg_url_contents

    logger.info(f'Extracted {len(messages)} new messages (scanned {count}, skipped {skipped} processed), fetched {len(all_urls)} URLs')
    return messages


async def main():
    parser = argparse.ArgumentParser(description='Extract Telegram Saved Messages')
    parser.add_argument('--days', type=int, default=30, help='Number of days to look back (default: 30)')
    parser.add_argument('--all', action='store_true', help='Process ALL messages (ignore processed_ids state)')
    parser.add_argument('--mark-processed', action='store_true',
                        help='Mark messages from output JSON as processed (call after notes are created)')
    parser.add_argument('--phone', type=str, default=None, help='Phone number (e.g. +1234567890)')
    parser.add_argument('--sms', action='store_true', help='Force SMS code delivery')
    args = parser.parse_args()

    # --mark-processed: just update state file, no Telegram connection needed
    if args.mark_processed:
        mark_output_as_processed()
        return

    client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            phone = args.phone or input('Enter phone number: ')
            sent = await client.send_code_request(phone, force_sms=args.sms)
            logger.info(f'Code sent via: {sent.type.__class__.__name__}')
            print(f'Code type: {sent.type.__class__.__name__}')

            code = input('Enter the code: ')
            try:
                await client.sign_in(phone, code)
            except Exception as e:
                if 'Two-steps verification' in str(e) or 'password' in str(e).lower():
                    password = input('Enter 2FA password: ')
                    await client.sign_in(password=password)
                else:
                    raise

        logger.info('Connected to Telegram')

        me = await client.get_me()
        logger.info(f'Logged in as: {me.first_name} (id={me.id})')

        messages = await extract_messages(client, args.days, skip_processed=not args.all)

        output = {
            'extracted_at': datetime.now(timezone.utc).isoformat(),
            'days': args.days,
            'total_messages': len(messages),
            'messages': messages,
        }

        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f'Output saved to {OUTPUT_PATH}')
        print(f'\nDone! {len(messages)} new messages saved to {OUTPUT_PATH}')

    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
