---
name: ai-bear-newsletter
description: Use when creating AI-Bear newsletter articles for LinkedIn/Substack - triggered by requests to write, draft, or execute an article from Notion drafts, or when the user references the framework and workflow.
---

# AI-Bear Newsletter

## Overview

Transforms raw Notion drafts into publication-ready LinkedIn/Substack articles following the AI-Bear Single-Article Newsletter Framework. One issue = one article. No invention, no expansion beyond the source.

## Workflow

### 1. Fetch Draft from Notion

Fetch the draft page by publishing date from the Drafts database.

- Drafts database ID: `fdf75999-5031-487b-877c-196d21e7061b`
- URL: https://www.notion.so/98fcc07dffeb40adb0d563f7fabb9c52

### 2. Research and Verify

Search the web for each topic. Gather:
- Accurate numbers, dates, names
- 2-4 primary source URLs (official announcements, research papers, reliable reporting)
- 2-3 official/open-access images with source attribution

### 3. Write Article

Write immediately — no review step in chat. Follow the framework below exactly.

### 4. Publish to Scheduled Database

**Step 4a:** Create new page in Scheduled database
- Parent data source ID: `248aa851-3792-43a6-a065-06ebb14ec81a`
- URL: https://www.notion.so/bf352fce2bfd401c83af25830273c75f
- Set: `Meeting name` = article headline, `Platform` = ["LinkedIn/Substack"], `Date for publishing` = same date as draft

**Step 4b:** Add full article content to the new page (body + Midjourney prompts + reference images)

**Step 4c:** Leave original draft untouched in Drafts database

### 5. Report

Reply: "Done! Article ready in Scheduled at [URL]. Ready for your review."

---

## Article Structure

### 1. Headline

- 2-3 emojis maximum — must reflect topic category, no decorative randomness
- Category examples: 🚀 product launch · 🧠 model capability · 💰 funding · 🏛️ regulation · 👔 leadership · ⚠️ risk

### 2. Date + Teaser Block

```
[Date]. Inside this issue:

- 3-4 sharp bullets
- Each previews a core development
- No emojis, no fluff, no vague phrasing
```

### 3. Three Fixed Sections

Section emojis are permanent — never change them.

#### ✍️ Essentials
Factual core. Stay close to the source. Tighten language. No opinions, no invented data, no speculation unless clearly labelled. Every key claim links to its primary source inline. Link text = entity or document name, not "click here". Link to exact primary sources — never homepages. All abbreviations explained on first use. Short, direct sentences.

#### 🐻 Bear's take
Practical interpretation. Answers: what does this mean? Focused on founders, operators, marketers. Analytical, calm, sharp. No philosophy, no grand predictions, no political/religious/sexual framing.

#### 🚨 Bear in mind
Exposure and risk mapping. Must cover: who is exposed, who benefits, what changes operationally, what action to consider. No fear tactics, no drama.

### 4. Visuals

Two Midjourney prompts per article. Never change the baseline style:

- Editorial flat vector illustration
- AI-Bear mascot present
- White background
- Brand palette: Teal `#00e0c6` · Violet `#6c63ff` · Navy `#0a1e3f`
- 16:9, `--v 6`, `--q 2`, no text, no logos

**Variant 1 — Mascot focus:** Close-up AI-Bear + one key symbolic prop
**Variant 2 — Environment focus:** AI-Bear in contextual scene + 2-3 minimal icons

Prompt template:
```
/imagine editorial-style flat vector illustration of the ai bear mascot, [scene context], [2-3 visual props], simple composition, white background, brand colors teal #00e0c6, violet #6c63ff, navy #0a1e3f --no text --ar 16:9 --v 6 --q 2
```

### 5. Reference Images

2-3 images per article. Official or open-access sources only (company blogs, research pages, arXiv, GitHub, product pages). Each image followed by a source attribution line.

```markdown
![Brief descriptive alt text](image URL)
Source: [Source name](source URL)
```

---

## House Style

| Rule | Detail |
|------|--------|
| Punctuation | No em dashes — use ` - ` with spaces. Straight quotes only |
| Capitalisation | Sentence case everywhere. Only proper nouns capitalised |
| Emojis | Required in headline. Fixed in section headers only. Not in body text |
| Tone | Practical over clever. No sarcasm, no political/religious/sexual content |
| Language | British English throughout |
| Length | ~1,200 characters for article body (excluding prompts and images) |

---

## Quality Checklist (run before creating Notion page)

- [ ] ~1,200 characters article body
- [ ] Emojis appropriate to category, present in headline only
- [ ] No em dashes
- [ ] British English
- [ ] Names, dates, numbers fact-checked
- [ ] All three sections present
- [ ] Inline source links on every key claim in ✍️ Essentials
- [ ] Two Midjourney prompts included
- [ ] 2-3 reference images with attribution
- [ ] New page created in Scheduled (never overwrite original draft)

---

## Database Reference

| Database | ID | Purpose |
|----------|----|---------|
| Drafts | `fdf75999-5031-487b-877c-196d21e7061b` | Raw inputs — read only |
| Scheduled | `248aa851-3792-43a6-a065-06ebb14ec81a` | Publication-ready output |
| Posted | `b6c9ff9d-62c9-45f5-b62e-c725dff94fd5` | Archive (user moves manually after posting) |
| Ai-Bear articles | legacy | Do not use |

---

## Non-Negotiables

- One article only per session
- No chat review step — proceed directly to Notion
- Original draft always preserved untouched
- No invented angles, no content beyond the source
- Framework is non-negotiable — follow precisely
