// ── Utilities ──────────────────────────────────────────────
function $(id) { return document.getElementById(id); }

function todayKey() {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD
}

function load(key, fallback = null) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; }
  catch { return fallback; }
}

function save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

// ── Clock ───────────────────────────────────────────────────
function initClock() {
  function tick() {
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const date = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
    $('clock').textContent = time;
    $('date').textContent = date;
  }
  tick();
  setInterval(tick, 1000);
}

// ── Editable text (focus + notes) ──────────────────────────
function initEditableText(elementId, storageKey, placeholder) {
  const el = document.getElementById(elementId);
  const stored = load(storageKey, '');

  function render(text) {
    if (text) {
      el.textContent = text;
      el.classList.remove('placeholder');
    } else {
      el.textContent = placeholder;
      el.classList.add('placeholder');
    }
  }

  render(stored);

  el.addEventListener('click', () => {
    const current = load(storageKey, '');
    const isTextarea = elementId === 'notes';
    const input = document.createElement(isTextarea ? 'textarea' : 'input');
    input.type = 'text';
    input.className = 'editable-input';
    input.value = current;
    if (isTextarea) { input.rows = 6; }
    el.replaceWith(input);
    input.focus();

    function commit() {
      const val = input.value.trim();
      save(storageKey, val);
      input.replaceWith(el);
      render(val);
    }

    input.addEventListener('blur', commit);
    input.addEventListener('keydown', (e) => {
      if (!isTextarea && e.key === 'Enter') { e.preventDefault(); commit(); }
      if (e.key === 'Escape') { input.replaceWith(el); render(load(storageKey, '')); }
    });
  });
}

// ── Tasks ───────────────────────────────────────────────────
function initTasks() {
  const key = `tasks-${todayKey()}`;
  let tasks = load(key, []);

  function saveTasks() { save(key, tasks); }

  function renderTasks() {
    const list = $('tasks-list');
    list.innerHTML = '';
    tasks.forEach(task => {
      const item = document.createElement('div');
      item.className = `task-item${task.completed ? ' completed' : ''}`;
      item.dataset.id = task.id;

      const check = document.createElement('div');
      check.className = 'task-check';
      check.textContent = task.completed ? '✓' : '';
      check.addEventListener('click', () => toggleTask(task.id));

      const text = document.createElement('span');
      text.className = 'task-text';
      text.textContent = task.text;
      text.addEventListener('click', () => editTask(task.id, text));

      const del = document.createElement('button');
      del.className = 'task-delete';
      del.textContent = '✕';
      del.addEventListener('click', () => deleteTask(task.id));

      item.append(check, text, del);
      list.appendChild(item);
    });
  }

  function addTask(text) {
    if (!text.trim()) return;
    tasks.push({ id: Date.now(), text: text.trim(), completed: false, order: tasks.length });
    saveTasks();
    renderTasks();
  }

  function toggleTask(id) {
    const task = tasks.find(t => t.id === id);
    if (task) { task.completed = !task.completed; saveTasks(); renderTasks(); }
  }

  function deleteTask(id) {
    tasks = tasks.filter(t => t.id !== id);
    saveTasks();
    renderTasks();
  }

  function editTask(id, textEl) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'editable-input';
    input.value = task.text;
    textEl.replaceWith(input);
    input.focus();

    function commit() {
      const val = input.value.trim();
      if (val) { task.text = val; saveTasks(); }
      renderTasks();
    }

    input.addEventListener('blur', commit);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); commit(); }
      if (e.key === 'Escape') { renderTasks(); }
    });
  }

  // Input row
  const taskInput = $('task-input');
  const addBtn = $('add-task-btn');

  addBtn.addEventListener('click', () => {
    addTask(taskInput.value);
    taskInput.value = '';
  });

  taskInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      addTask(taskInput.value);
      taskInput.value = '';
    }
  });

  renderTasks();
}

// ── Quick Links ─────────────────────────────────────────────
const LINK_COLORS = ['red','blue','green','purple','pink','yellow','indigo','gray'];
const COLOR_HEX = {
  red:'#ef4444', blue:'#3b82f6', green:'#22c55e', purple:'#a855f7',
  pink:'#ec4899', yellow:'#ca8a04', indigo:'#6366f1', gray:'#6b7280'
};

function initLinks() {
  let links = load('links', []);
  let selectedColor = 'blue';

  function saveLinks() { save('links', links); }

  function normalizeUrl(url) {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return 'https://' + url;
    }
    return url;
  }

  function renderLinks() {
    const list = $('links-list');
    list.innerHTML = '';
    links.forEach(link => {
      const a = document.createElement('a');
      a.className = `link-item color-${link.color}`;
      a.href = link.url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';

      const title = document.createElement('span');
      title.textContent = link.title;

      const actions = document.createElement('div');
      actions.className = 'link-actions';

      const delBtn = document.createElement('button');
      delBtn.textContent = '✕';
      delBtn.title = 'Delete';
      delBtn.addEventListener('click', (e) => {
        e.preventDefault();
        links = links.filter(l => l.id !== link.id);
        saveLinks();
        renderLinks();
      });

      actions.appendChild(delBtn);
      a.append(title, actions);
      list.appendChild(a);
    });
  }

  function renderColorPicker() {
    const picker = $('color-picker');
    picker.innerHTML = '';
    LINK_COLORS.forEach(color => {
      const swatch = document.createElement('div');
      swatch.className = `color-swatch${color === selectedColor ? ' selected' : ''}`;
      swatch.style.background = COLOR_HEX[color];
      swatch.dataset.color = color;
      swatch.addEventListener('click', () => {
        selectedColor = color;
        renderColorPicker();
      });
      picker.appendChild(swatch);
    });
  }

  // Show/hide form
  $('add-link-btn').addEventListener('click', () => {
    $('link-form').classList.remove('hidden');
    $('add-link-btn').style.display = 'none';
    renderColorPicker();
    $('link-title').focus();
  });

  $('cancel-link-btn').addEventListener('click', () => {
    $('link-form').classList.add('hidden');
    $('add-link-btn').style.display = '';
    $('link-title').value = '';
    $('link-url').value = '';
  });

  $('link-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const title = $('link-title').value.trim();
    const url = $('link-url').value.trim();
    if (!title || !url) return;
    links.push({ id: Date.now(), title, url: normalizeUrl(url), color: selectedColor, order: links.length });
    saveLinks();
    renderLinks();
    $('link-form').classList.add('hidden');
    $('add-link-btn').style.display = '';
    $('link-title').value = '';
    $('link-url').value = '';
  });

  // Seed default links if none exist
  if (links.length === 0) {
    links = [
      { id: 1, title: 'Claude', url: 'https://claude.ai', color: 'purple', order: 0 },
      { id: 2, title: 'Notion', url: 'https://notion.so', color: 'gray', order: 1 },
      { id: 3, title: 'LinkedIn', url: 'https://linkedin.com', color: 'blue', order: 2 },
    ];
    saveLinks();
  }

  renderLinks();
}

// ── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initEditableText('focus-week', 'focus-week', 'Click to set your weekly focus...');
  initEditableText('notes', 'notes', 'Click to add notes...');
  initTasks();
  initLinks();
});
