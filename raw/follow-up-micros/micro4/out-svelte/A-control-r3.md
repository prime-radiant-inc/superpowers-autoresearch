# Svelte Todo List - Implementation Plan

## Overview

This plan builds a Svelte todo list app with localStorage persistence using TDD. We use Vite + Svelte + TypeScript, and Vitest for testing. Each task is self-contained with exact commands and expected output.

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Project config, dependencies, scripts |
| `vite.config.ts` | Vite + Vitest config |
| `tsconfig.json` | TypeScript config |
| `src/main.ts` | App entry point, mounts `App.svelte` |
| `src/app.css` | Global styles |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte store: todos state + actions |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear completed |
| `src/App.svelte` | Wires components together, applies filter |
| `index.html` | HTML host page |

Test files live next to their source:
- `src/lib/storage.test.ts`
- `src/lib/store.test.ts`
- `src/lib/TodoInput.test.ts`
- `src/lib/TodoItem.test.ts`
- `src/lib/TodoList.test.ts`
- `src/lib/FilterBar.test.ts`
- `src/App.test.ts`

---

### Task 1: Project Scaffolding

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `index.html`, `src/main.ts`, `src/App.svelte`, `src/app.css`, `svelte.config.js`

- [ ] Create the project directory and initialize git:

```bash
mkdir svelte-todos && cd svelte-todos
git init
```

Expected output:
```
Initialized empty Git repository in .../svelte-todos/.git/
```

- [ ] Create `package.json`:

```json
{
  "name": "svelte-todos",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "check": "svelte-check --tsconfig ./tsconfig.json"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3.1.2",
    "@testing-library/jest-dom": "^6.4.8",
    "@testing-library/svelte": "^5.2.1",
    "@tsconfig/svelte": "^5.0.4",
    "jsdom": "^24.1.1",
    "svelte": "^4.2.19",
    "svelte-check": "^3.8.5",
    "tslib": "^2.6.3",
    "typescript": "^5.5.4",
    "vite": "^5.4.2",
    "vitest": "^2.0.5"
  }
}
```

- [ ] Install dependencies:

```bash
npm install
```

Expected output (last line approximately):
```
added N packages, and audited N packages in Xs
```

- [ ] Create `svelte.config.js`:

```js
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
};
```

- [ ] Create `tsconfig.json`:

```json
{
  "extends": "@tsconfig/svelte/tsconfig.json",
  "compilerOptions": {
    "target": "ESNext",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "resolveJsonModule": true,
    "allowJs": true,
    "checkJs": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src/**/*.ts", "src/**/*.svelte"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] Create `tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler"
  },
  "include": ["vite.config.ts"]
}
```

- [ ] Create `vite.config.ts`:

```ts
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest-setup.ts'],
  },
});
```

- [ ] Create `vitest-setup.ts`:

```ts
import '@testing-library/jest-dom/vitest';
```

- [ ] Create `index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Svelte Todos</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] Create `src/app.css`:

```css
:root {
  font-family: system-ui, sans-serif;
  background: #f4f4f5;
  color: #18181b;
}

body {
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
  margin: 0;
}
```

- [ ] Create `src/main.ts`:

```ts
import './app.css';
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')!,
});

export default app;
```

- [ ] Create a minimal `src/App.svelte` (filled out fully in Task 8):

```svelte
<main>
  <h1>Svelte Todos</h1>
</main>
```

- [ ] Create `.gitignore`:

```
node_modules
dist
.DS_Store
```

- [ ] Verify the dev build starts, then stop it with Ctrl+C:

```bash
npm run dev
```

Expected output (approximately):
```
  VITE v5.x.x  ready in Xms
  ➜  Local:   http://localhost:5173/
```

- [ ] Verify Vitest runs (no tests yet is fine):

```bash
npm test
```

Expected output:
```
No test files found, exiting with code 1
```

(That non-zero exit is expected because no tests exist yet; the next task adds one.)

- [ ] Commit:

```bash
git add -A && git commit -m "Scaffold Svelte + Vite + Vitest project"
```

---

### Task 2: Types

**Files:** `src/lib/types.ts`

- [ ] Create `src/lib/types.ts`:

```ts
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

- [ ] Type-check:

```bash
npm run check
```

Expected output (approximately):
```
svelte-check found 0 errors and 0 warnings
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add Todo and Filter types"
```

---

### Task 3: localStorage Persistence

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

- [ ] Write the failing test in `src/lib/storage.test.ts`:

```ts
import { beforeEach, describe, expect, it } from 'vitest';
import { loadTodos, saveTodos } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns empty array when nothing is stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns empty array when stored data is invalid JSON', () => {
    localStorage.setItem('svelte-todos', 'not json');
    expect(loadTodos()).toEqual([]);
  });

  it('returns empty array when stored data is not an array', () => {
    localStorage.setItem('svelte-todos', '{"foo":"bar"}');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- storage
```

Expected output (approximately):
```
Error: Failed to load url ./storage (resolved id: ./storage) ... Does the file exist?
```

- [ ] Implement `src/lib/storage.ts`:

```ts
import type { Todo } from './types';

const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw === null) return [];
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as Todo[];
  } catch {
    return [];
  }
}

export function saveTodos(todos: Todo[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}
```

- [ ] Run the test to see it pass:

```bash
npm test -- storage
```

Expected output (approximately):
```
 ✓ src/lib/storage.test.ts (4 tests)
 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add localStorage persistence with tests"
```

---

### Task 4: Todos Store

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

The store wraps a Svelte writable, exposes actions (`addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted`), and persists on every change.

- [ ] Write the failing test in `src/lib/store.test.ts`:

```ts
import { beforeEach, describe, expect, it } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
} from './store';
import { loadTodos } from './storage';

describe('store', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
  });

  it('addTodo appends a non-completed todo with text', () => {
    addTodo('Buy groceries');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy groceries');
    expect(list[0].completed).toBe(false);
    expect(list[0].id).toBeTruthy();
  });

  it('addTodo trims whitespace and ignores empty input', () => {
    addTodo('   ');
    expect(get(todos)).toHaveLength(0);
    addTodo('  hello  ');
    expect(get(todos)[0].text).toBe('hello');
  });

  it('addTodo gives each todo a unique id', () => {
    addTodo('a');
    addTodo('b');
    const [first, second] = get(todos);
    expect(first.id).not.toBe(second.id);
  });

  it('toggleTodo flips completed state', () => {
    addTodo('task');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deleteTodo removes the matching todo', () => {
    addTodo('a');
    addTodo('b');
    const id = get(todos)[0].id;
    deleteTodo(id);
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('clearCompleted removes only completed todos', () => {
    addTodo('a');
    addTodo('b');
    const id = get(todos)[0].id;
    toggleTodo(id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('persists changes to localStorage', () => {
    addTodo('persist me');
    expect(loadTodos()).toHaveLength(1);
    expect(loadTodos()[0].text).toBe('persist me');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- store
```

Expected output (approximately):
```
Error: Failed to load url ./store ... Does the file exist?
```

- [ ] Implement `src/lib/store.ts`:

```ts
import { writable } from 'svelte/store';
import type { Todo } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());

todos.subscribe((value) => {
  saveTodos(value);
});

export function addTodo(text: string): void {
  const trimmed = text.trim();
  if (trimmed === '') return;
  const todo: Todo = {
    id: crypto.randomUUID(),
    text: trimmed,
    completed: false,
  };
  todos.update((list) => [...list, todo]);
}

export function toggleTodo(id: string): void {
  todos.update((list) =>
    list.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t)),
  );
}

export function deleteTodo(id: string): void {
  todos.update((list) => list.filter((t) => t.id !== id));
}

export function clearCompleted(): void {
  todos.update((list) => list.filter((t) => !t.completed));
}
```

- [ ] Run the test to see it pass:

```bash
npm test -- store
```

Expected output (approximately):
```
 ✓ src/lib/store.test.ts (7 tests)
 Test Files  1 passed (1)
      Tests  7 passed (7)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add todos store with actions and persistence"
```

---

### Task 5: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

The input dispatches an `add` event with the text. The parent decides what to do; this keeps the component focused (single responsibility).

- [ ] Write the failing test in `src/lib/TodoInput.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add event with text when Add is clicked', async () => {
    const { getByRole, getByLabelText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByLabelText('New todo') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Buy milk' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));

    expect(handler).toHaveBeenCalledWith('Buy milk');
  });

  it('dispatches add event when Enter is pressed', async () => {
    const { getByLabelText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByLabelText('New todo') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Walk dog' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Walk dog');
  });

  it('clears the input after dispatching', async () => {
    const { getByLabelText, getByRole } = render(TodoInput);
    const input = getByLabelText('New todo') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Something' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(input.value).toBe('');
  });

  it('does not dispatch when input is empty or whitespace', async () => {
    const { getByLabelText, getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);

    const input = getByLabelText('New todo') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: '   ' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));

    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- TodoInput
```

Expected output (approximately):
```
Error: Failed to load url ./TodoInput.svelte ... Does the file exist?
```

- [ ] Implement `src/lib/TodoInput.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ add: string }>();
  let text = '';

  function submit() {
    if (text.trim() === '') return;
    dispatch('add', text);
    text = '';
  }

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      submit();
    }
  }
</script>

<div class="input-row">
  <label class="sr-only" for="new-todo">New todo</label>
  <input
    id="new-todo"
    aria-label="New todo"
    type="text"
    placeholder="What needs to be done?"
    bind:value={text}
    on:keydown={onKeyDown}
  />
  <button type="button" on:click={submit}>Add</button>
</div>

<style>
  .input-row {
    display: flex;
    gap: 0.5rem;
  }
  input {
    flex: 1;
    padding: 0.5rem;
    font-size: 1rem;
  }
  button {
    padding: 0.5rem 1rem;
    cursor: pointer;
  }
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test -- TodoInput
```

Expected output (approximately):
```
 ✓ src/lib/TodoInput.test.ts (4 tests)
 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoInput component with tests"
```

---

### Task 6: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

Renders a single todo and dispatches `toggle` and `delete` events with the todo id.

- [ ] Write the failing test in `src/lib/TodoItem.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Buy groceries', completed: false };

describe('TodoItem', () => {
  it('renders the todo text', () => {
    const { getByText } = render(TodoItem, { props: { todo } });
    expect(getByText('Buy groceries')).toBeInTheDocument();
  });

  it('checkbox reflects completed state', () => {
    const { getByRole } = render(TodoItem, {
      props: { todo: { ...todo, completed: true } },
    });
    expect(getByRole('checkbox')).toBeChecked();
  });

  it('dispatches toggle with id when checkbox clicked', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(getByRole('checkbox'));
    expect(handler).toHaveBeenCalledWith('abc');
  });

  it('dispatches delete with id when delete button clicked', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Delete Buy groceries' }));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- TodoItem
```

Expected output (approximately):
```
Error: Failed to load url ./TodoItem.svelte ... Does the file exist?
```

- [ ] Implement `src/lib/TodoItem.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Todo } from './types';

  export let todo: Todo;

  const dispatch = createEventDispatcher<{ toggle: string; delete: string }>();
</script>

<li class="todo-item" class:completed={todo.completed}>
  <input
    type="checkbox"
    checked={todo.completed}
    on:change={() => dispatch('toggle', todo.id)}
  />
  <span class="text">{todo.text}</span>
  <button
    type="button"
    class="delete"
    aria-label={`Delete ${todo.text}`}
    on:click={() => dispatch('delete', todo.id)}
  >
    ✕
  </button>
</li>

<style>
  .todo-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e4e4e7;
  }
  .text {
    flex: 1;
  }
  .completed .text {
    text-decoration: line-through;
    color: #a1a1aa;
  }
  .delete {
    background: none;
    border: none;
    cursor: pointer;
    color: #ef4444;
    font-size: 1rem;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test -- TodoItem
```

Expected output (approximately):
```
 ✓ src/lib/TodoItem.test.ts (4 tests)
 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoItem component with tests"
```

---

### Task 7: TodoList Component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

Renders a list of `TodoItem`s and forwards their events. Shows an empty-state message when there are no todos.

- [ ] Write the failing test in `src/lib/TodoList.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('TodoList', () => {
  it('renders one item per todo', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('Buy groceries')).toBeInTheDocument();
    expect(getByText('Walk the dog')).toBeInTheDocument();
  });

  it('shows empty state when there are no todos', () => {
    const { getByText } = render(TodoList, { props: { todos: [] } });
    expect(getByText('Nothing here yet. Add your first todo!')).toBeInTheDocument();
  });

  it('forwards toggle events from items', async () => {
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete events from items', async () => {
    const { getByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Delete Walk the dog' }));
    expect(handler).toHaveBeenCalledWith('2');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- TodoList
```

Expected output (approximately):
```
Error: Failed to load url ./TodoList.svelte ... Does the file exist?
```

- [ ] Implement `src/lib/TodoList.svelte`:

```svelte
<script lang="ts">
  import type { Todo } from './types';
  import TodoItem from './TodoItem.svelte';

  export let todos: Todo[];
</script>

{#if todos.length === 0}
  <p class="empty">Nothing here yet. Add your first todo!</p>
{:else}
  <ul class="todo-list">
    {#each todos as todo (todo.id)}
      <TodoItem {todo} on:toggle on:delete />
    {/each}
  </ul>
{/if}

<style>
  .todo-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .empty {
    text-align: center;
    color: #71717a;
    padding: 1rem 0;
  }
</style>
```

Note: `on:toggle on:delete` without a handler forwards the child events to this component's consumers.

- [ ] Run the test to see it pass:

```bash
npm test -- TodoList
```

Expected output (approximately):
```
 ✓ src/lib/TodoList.test.ts (4 tests)
 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoList component with empty state and tests"
```

---

### Task 8: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

Shows remaining count, three filter buttons, and a clear-completed button. Receives `filter` and `remaining` props, dispatches `filter` and `clearCompleted`.

- [ ] Write the failing test in `src/lib/FilterBar.test.ts`:

```ts
import { describe, expect, it, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows singular item count', () => {
    const { getByText } = render(FilterBar, {
      props: { filter: 'all', remaining: 1 },
    });
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('shows plural item count', () => {
    const { getByText } = render(FilterBar, {
      props: { filter: 'all', remaining: 2 },
    });
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    const { getByRole } = render(FilterBar, {
      props: { filter: 'active', remaining: 0 },
    });
    expect(getByRole('button', { name: 'Active' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(getByRole('button', { name: 'All' })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  it('dispatches filter event with chosen filter', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { filter: 'all', remaining: 0 },
    });
    const handler = vi.fn();
    component.$on('filter', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clearCompleted when Clear completed clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { filter: 'all', remaining: 0 },
    });
    const handler = vi.fn();
    component.$on('clearCompleted', handler);
    await fireEvent.click(getByRole('button', { name: 'Clear completed' }));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test -- FilterBar
```

Expected output (approximately):
```
Error: Failed to load url ./FilterBar.svelte ... Does the file exist?
```

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let filter: Filter;
  export let remaining: number;

  const dispatch = createEventDispatcher<{
    filter: Filter;
    clearCompleted: void;
  }>();

  const filters: Filter[] = ['all', 'active', 'completed'];
  const labels: Record<Filter, string> = {
    all: 'All',
    active: 'Active',
    completed: 'Completed',
  };
</script>

<div class="filter-bar">
  <span class="count">
    {remaining} {remaining === 1 ? 'item' : 'items'} left
  </span>

  <div class="filters">
    {#each filters as f}
      <button
        type="button"
        aria-pressed={filter === f}
        class:active={filter === f}
        on:click={() => dispatch('filter', f)}
      >
        {labels[f]}
      </button>
    {/each}
  </div>

  <button type="button" class="clear" on:click={() => dispatch('clearCompleted')}>
    Clear completed
  </button>
</div>

<style>
  .filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: wrap;
    padding-top: 0.75rem;
    font-size: 0.875rem;
  }
  .filters {
    display: flex;
    gap: 0.25rem;
  }
  button {
    cursor: pointer;
    border: 1px solid transparent;
    background: none;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }
  .filters button.active {
    border-color: #6366f1;
    color: #6366f1;
  }
  .clear {
    color: #71717a;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test -- FilterBar
```

Expected output (approximately):
```
 ✓ src/lib/FilterBar.test.ts (5 tests)
 Test Files  1 passed (1)
      Tests  5 passed (5)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add FilterBar component with tests"
```

---

### Task 9: App Integration

**Files:** `src/App.svelte`, `src/App.test.ts`

`App.svelte` wires the store and components together: holds the current `filter`, computes the visible todos and remaining count, and connects events to store actions.

- [ ] Write the failing test in `src/App.test.ts`:

```ts
import { beforeEach, describe, expect, it } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import App from './App.svelte';
import { todos } from './lib/store';

async function addTodo(input: HTMLInputElement, addBtn: HTMLElement, text: string) {
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.click(addBtn);
}

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
  });

  it('adds a todo and displays it', async () => {
    const { getByLabelText, getByRole, getByText } = render(App);
    await addTodo(
      getByLabelText('New todo') as HTMLInputElement,
      getByRole('button', { name: 'Add' }),
      'Buy groceries',
    );
    expect(getByText('Buy groceries')).toBeInTheDocument();
  });

  it('shows count of remaining items', async () => {
    const { getByLabelText, getByRole, getByText } = render(App);
    const input = getByLabelText('New todo') as HTMLInputElement;
    const addBtn = getByRole('button', { name: 'Add' });
    await addTodo(input, addBtn, 'a');
    await addTodo(input, addBtn, 'b');
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('toggling a todo updates the remaining count', async () => {
    const { getByLabelText, getByRole, getByText, getAllByRole } = render(App);
    await addTodo(
      getByLabelText('New todo') as HTMLInputElement,
      getByRole('button', { name: 'Add' }),
      'a',
    );
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(getByText('0 items left')).toBeInTheDocument();
  });

  it('filters to active todos only', async () => {
    const { getByLabelText, getByRole, getAllByRole, queryByText