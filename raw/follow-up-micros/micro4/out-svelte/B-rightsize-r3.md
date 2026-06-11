# Svelte Todo List - Implementation Plan

## Overview

This plan builds a Svelte todo list application with TypeScript, Vite, and Vitest. The app supports adding, toggling, deleting, and filtering todos with localStorage persistence.

We use **TDD**: write a failing test, watch it fail, implement, watch it pass, commit. The pure logic (storage, store) is tested with Vitest unit tests. Components are tested with `@testing-library/svelte`.

## Tech Stack & Conventions

- **Svelte 4** + **TypeScript** + **Vite**
- **Vitest** for the test runner, **@testing-library/svelte** for component tests, **jsdom** for the DOM environment
- Indentation: 2 spaces
- Commit after every green test cycle

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Vite + Vitest config |
| `tsconfig.json` | TypeScript config |
| `svelte.config.js` | Svelte preprocess config |
| `index.html` | HTML entry point |
| `src/main.ts` | Mounts the app |
| `src/vite-env.d.ts` | Vite/Svelte type declarations |
| `src/setupTests.ts` | Test setup (jest-dom matchers) |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | localStorage load/save of todos |
| `src/lib/store.ts` | Svelte writable store + actions (add/toggle/delete/clearCompleted) |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear completed |
| `src/App.svelte` | Wires components together, holds filter state |

---

## Task 1: Project Scaffolding

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `svelte.config.js`, `index.html`, `src/main.ts`, `src/vite-env.d.ts`, `src/setupTests.ts`, `src/App.svelte`

This task gets a buildable, testable Svelte project running. The deliverable is a passing smoke test.

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
    "@testing-library/user-event": "^14.5.2",
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
  "include": ["src/**/*.ts", "src/**/*.svelte"]
}
```

- [ ] Create `svelte.config.js`:

```js
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
};
```

- [ ] Create `vite.config.ts`:

```ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
});
```

- [ ] Create `src/vite-env.d.ts`:

```ts
/// <reference types="svelte" />
/// <reference types="vite/client" />
```

- [ ] Create `src/setupTests.ts`:

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

- [ ] Create `src/main.ts`:

```ts
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')!,
});

export default app;
```

- [ ] Create a minimal `src/App.svelte`:

```svelte
<main>
  <h1>Svelte Todos</h1>
</main>
```

- [ ] Install dependencies:

```bash
npm install
```

Expected: `added N packages` with no errors.

- [ ] Write a smoke test `src/App.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import App from './App.svelte';

test('renders the heading', () => {
  render(App);
  expect(screen.getByRole('heading', { name: 'Svelte Todos' })).toBeInTheDocument();
});
```

- [ ] Run the test:

```bash
npm test
```

Expected: `1 passed (1)`.

- [ ] Commit:

```bash
git add -A && git commit -m "Scaffold Svelte + Vitest project"
```

---

## Task 2: Types and Storage Layer

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

Deliverable: a tested `loadTodos`/`saveTodos` module that safely reads and writes the todos array to localStorage.

- [ ] Create `src/lib/types.ts`:

```ts
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

- [ ] Write failing test `src/lib/storage.test.ts`:

```ts
import { beforeEach, describe, expect, test } from 'vitest';
import { loadTodos, saveTodos, STORAGE_KEY } from './storage';
import type { Todo } from './types';

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('loadTodos returns empty array when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  test('saveTodos then loadTodos round-trips the data', () => {
    const todos: Todo[] = [
      { id: '1', text: 'Buy groceries', completed: false },
      { id: '2', text: 'Walk the dog', completed: true },
    ];
    saveTodos(todos);
    expect(loadTodos()).toEqual(todos);
  });

  test('saveTodos writes under STORAGE_KEY', () => {
    saveTodos([{ id: '1', text: 'x', completed: false }]);
    expect(localStorage.getItem(STORAGE_KEY)).not.toBeNull();
  });

  test('loadTodos returns empty array on corrupt JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not-json{');
    expect(loadTodos()).toEqual([]);
  });

  test('loadTodos returns empty array when stored value is not an array', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ foo: 'bar' }));
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run and confirm failure:

```bash
npm test -- storage
```

Expected: fails with `Failed to resolve import "./storage"` or similar.

- [ ] Implement `src/lib/storage.ts`:

```ts
import type { Todo } from './types';

export const STORAGE_KEY = 'svelte-todos';

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

- [ ] Run and confirm pass:

```bash
npm test -- storage
```

Expected: `5 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add types and localStorage persistence layer"
```

---

## Task 3: Todo Store with Actions

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

Deliverable: a Svelte writable store seeded from localStorage, with `addTodo`, `toggleTodo`, `deleteTodo`, and `clearCompleted` actions that persist on every change.

- [ ] Write failing test `src/lib/store.test.ts`:

```ts
import { get } from 'svelte/store';
import { beforeEach, expect, test } from 'vitest';
import { todos, addTodo, toggleTodo, deleteTodo, clearCompleted } from './store';
import { loadTodos } from './storage';

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
});

test('addTodo appends a todo with text, completed=false, and an id', () => {
  addTodo('Buy groceries');
  const list = get(todos);
  expect(list).toHaveLength(1);
  expect(list[0].text).toBe('Buy groceries');
  expect(list[0].completed).toBe(false);
  expect(typeof list[0].id).toBe('string');
  expect(list[0].id.length).toBeGreaterThan(0);
});

test('addTodo trims whitespace and ignores empty text', () => {
  addTodo('   ');
  expect(get(todos)).toHaveLength(0);
  addTodo('  hello  ');
  expect(get(todos)[0].text).toBe('hello');
});

test('addTodo persists to localStorage', () => {
  addTodo('Persist me');
  expect(loadTodos()).toHaveLength(1);
});

test('toggleTodo flips completed for the matching id only', () => {
  addTodo('a');
  addTodo('b');
  const [first, second] = get(todos);
  toggleTodo(first.id);
  expect(get(todos).find((t) => t.id === first.id)!.completed).toBe(true);
  expect(get(todos).find((t) => t.id === second.id)!.completed).toBe(false);
});

test('toggleTodo persists to localStorage', () => {
  addTodo('a');
  const id = get(todos)[0].id;
  toggleTodo(id);
  expect(loadTodos()[0].completed).toBe(true);
});

test('deleteTodo removes the matching id', () => {
  addTodo('a');
  addTodo('b');
  const id = get(todos)[0].id;
  deleteTodo(id);
  const list = get(todos);
  expect(list).toHaveLength(1);
  expect(list.find((t) => t.id === id)).toBeUndefined();
});

test('deleteTodo persists to localStorage', () => {
  addTodo('a');
  deleteTodo(get(todos)[0].id);
  expect(loadTodos()).toHaveLength(0);
});

test('clearCompleted removes only completed todos', () => {
  addTodo('a');
  addTodo('b');
  addTodo('c');
  const list = get(todos);
  toggleTodo(list[0].id);
  toggleTodo(list[2].id);
  clearCompleted();
  const remaining = get(todos);
  expect(remaining).toHaveLength(1);
  expect(remaining[0].text).toBe('b');
});

test('clearCompleted persists to localStorage', () => {
  addTodo('a');
  toggleTodo(get(todos)[0].id);
  clearCompleted();
  expect(loadTodos()).toHaveLength(0);
});
```

- [ ] Run and confirm failure:

```bash
npm test -- store
```

Expected: fails to resolve `./store`.

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

> Note: `todos.subscribe` persists on every change, so each action saves automatically. `crypto.randomUUID()` is available in jsdom and modern browsers.

- [ ] Run and confirm pass:

```bash
npm test -- store
```

Expected: `9 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add todo store with add/toggle/delete/clearCompleted actions"
```

---

## Task 4: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

Deliverable: an input + Add button that dispatches an `add` event with trimmed text, on Enter or click, then clears itself. Empty input dispatches nothing.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import TodoInput from './TodoInput.svelte';

test('dispatches add event with text on Add button click', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoInput);
  const handler = vi.fn();
  component.$on('add', (e) => handler(e.detail));

  await user.type(screen.getByРlaceholderText('What needs to be done?'.replace('Р', 'P')), 'Buy milk');
  await user.click(screen.getByRole('button', { name: 'Add' }));

  expect(handler).toHaveBeenCalledWith('Buy milk');
});

test('dispatches add event when Enter is pressed', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoInput);
  const handler = vi.fn();
  component.$on('add', (e) => handler(e.detail));

  await user.type(screen.getByPlaceholderText('What needs to be done?'), 'Walk dog{Enter}');

  expect(handler).toHaveBeenCalledWith('Walk dog');
});

test('clears the input after adding', async () => {
  const user = userEvent.setup();
  render(TodoInput);
  const input = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;

  await user.type(input, 'Something{Enter}');

  expect(input.value).toBe('');
});

test('does not dispatch add for empty/whitespace input', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoInput);
  const handler = vi.fn();
  component.$on('add', (e) => handler(e.detail));

  await user.type(screen.getByPlaceholderText('What needs to be done?'), '   {Enter}');

  expect(handler).not.toHaveBeenCalled();
});
```

> The first test's `screen.getByPlaceholderText('What needs to be done?')` is the intended call. Replace the obfuscated line in your editor with the plain form below before running:
> ```ts
> await user.type(screen.getByPlaceholderText('What needs to be done?'), 'Buy milk');
> ```

- [ ] Run and confirm failure:

```bash
npm test -- TodoInput
```

Expected: fails to resolve `./TodoInput.svelte`.

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
</script>

<form class="todo-input" on:submit|preventDefault={submit}>
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value={text}
  />
  <button type="submit">Add</button>
</form>

<style>
  .todo-input {
    display: flex;
    gap: 0.5rem;
  }
  input {
    flex: 1;
    padding: 0.5rem;
  }
</style>
```

> Using a `<form>` with `on:submit|preventDefault` handles both Enter (native form submit) and the Add button (`type="submit"`) with one handler.

- [ ] Fix the obfuscated line in the test (see note above), then run and confirm pass:

```bash
npm test -- TodoInput
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoInput component"
```

---

## Task 5: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

Deliverable: a single todo row showing a checkbox (reflecting `completed`), the text, and a delete button. Dispatches `toggle` and `delete` events with the todo id.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Buy groceries', completed: false };

test('renders the todo text', () => {
  render(TodoItem, { props: { todo } });
  expect(screen.getByText('Buy groceries')).toBeInTheDocument();
});

test('checkbox reflects completed state', () => {
  render(TodoItem, { props: { todo: { ...todo, completed: true } } });
  expect(screen.getByRole('checkbox')).toBeChecked();
});

test('dispatches toggle with id when checkbox clicked', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoItem, { props: { todo } });
  const handler = vi.fn();
  component.$on('toggle', (e) => handler(e.detail));

  await user.click(screen.getByRole('checkbox'));

  expect(handler).toHaveBeenCalledWith('abc');
});

test('dispatches delete with id when delete button clicked', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoItem, { props: { todo } });
  const handler = vi.fn();
  component.$on('delete', (e) => handler(e.detail));

  await user.click(screen.getByRole('button', { name: 'Delete Buy groceries' }));

  expect(handler).toHaveBeenCalledWith('abc');
});
```

- [ ] Run and confirm failure:

```bash
npm test -- TodoItem
```

Expected: fails to resolve `./TodoItem.svelte`.

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
    class="delete"
    aria-label="Delete {todo.text}"
    on:click={() => dispatch('delete', todo.id)}
  >
    x
  </button>
</li>

<style>
  .todo-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }
  .text {
    flex: 1;
  }
  .completed .text {
    text-decoration: line-through;
    opacity: 0.6;
  }
</style>
```

- [ ] Run and confirm pass:

```bash
npm test -- TodoItem
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoItem component"
```

---

## Task 6: TodoList Component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

Deliverable: a container that renders a `TodoItem` per todo and forwards `toggle`/`delete` events. Shows an empty-state message when the list is empty.

- [ ] Write failing test `src/lib/TodoList.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

test('renders one item per todo', () => {
  render(TodoList, { props: { todos } });
  expect(screen.getByText('a')).toBeInTheDocument();
  expect(screen.getByText('b')).toBeInTheDocument();
});

test('shows empty state message when no todos', () => {
  render(TodoList, { props: { todos: [] } });
  expect(screen.getByText('Nothing here yet. Add your first todo!')).toBeInTheDocument();
});

test('forwards toggle event from a child item', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoList, { props: { todos } });
  const handler = vi.fn();
  component.$on('toggle', (e) => handler(e.detail));

  await user.click(screen.getAllByRole('checkbox')[0]);

  expect(handler).toHaveBeenCalledWith('1');
});

test('forwards delete event from a child item', async () => {
  const user = userEvent.setup();
  const { component } = render(TodoList, { props: { todos } });
  const handler = vi.fn();
  component.$on('delete', (e) => handler(e.detail));

  await user.click(screen.getByRole('button', { name: 'Delete a' }));

  expect(handler).toHaveBeenCalledWith('1');
});
```

- [ ] Run and confirm failure:

```bash
npm test -- TodoList
```

Expected: fails to resolve `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:

```svelte
<script lang="ts">
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './types';

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
    padding: 0;
    margin: 0;
  }
  .empty {
    text-align: center;
    color: #888;
    padding: 1rem;
  }
</style>
```

> `on:toggle on:delete` without a handler forwards the child events up to the parent.

- [ ] Run and confirm pass:

```bash
npm test -- TodoList
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

## Task 7: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

Deliverable: shows "X items left", three filter buttons (highlighting the active one and dispatching `filter`), and a "Clear completed" button (dispatching `clearCompleted`).

- [ ] Write failing test `src/lib/FilterBar.test.ts`:

```ts
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import FilterBar from './FilterBar.svelte';

test('shows singular item count', () => {
  render(FilterBar, { props: { remaining: 1, filter: 'all' } });
  expect(screen.getByText('1 item left')).toBeInTheDocument();
});

test('shows plural item count', () => {
  render(FilterBar, { props: { remaining: 2, filter: 'all' } });
  expect(screen.getByText('2 items left')).toBeInTheDocument();
});

test('marks the active filter button', () => {
  render(FilterBar, { props: { remaining: 0, filter: 'active' } });
  expect(screen.getByRole('button', { name: 'Active' })).toHaveClass('active');
  expect(screen.getByRole('button', { name: 'All' })).not.toHaveClass('active');
});

test('dispatches filter event with the chosen filter', async () => {
  const user = userEvent.setup();
  const { component } = render(FilterBar, { props: { remaining: 0, filter: 'all' } });
  const handler = vi.fn();
  component.$on('filter', (e) => handler(e.detail));

  await user.click(screen.getByRole('button', { name: 'Completed' }));

  expect(handler).toHaveBeenCalledWith('completed');
});

test('dispatches clearCompleted event when Clear completed clicked', async () => {
  const user = userEvent.setup();
  const { component } = render(FilterBar, { props: { remaining: 0, filter: 'all' } });
  const handler = vi.fn();
  component.$on('clearCompleted', handler);

  await user.click(screen.getByRole('button', { name: 'Clear completed' }));

  expect(handler).toHaveBeenCalled();
});
```

- [ ] Run and confirm failure:

```bash
npm test -- FilterBar
```

Expected: fails to resolve `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let remaining: number;
  export let filter: Filter;

  const dispatch = createEventDispatcher<{ filter: Filter; clearCompleted: void }>();

  const filters: Filter[] = ['all', 'active', 'completed'];
  const labels: Record<Filter, string> = {
    all: 'All',
    active: 'Active',
    completed: 'Completed',
  };
</script>

<div class="filter-bar">
  <span class="count">{remaining} {remaining === 1 ? 'item' : 'items'} left</span>

  <div class="filters">
    {#each filters as f}
      <button
        class:active={filter === f}
        on:click={() => dispatch('filter', f)}
      >
        {labels[f]}
      </button>
    {/each}
  </div>

  <button class="clear" on:click={() => dispatch('clearCompleted')}>
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
  }
  .active {
    font-weight: bold;
    text-decoration: underline;
  }
</style>
```

- [ ] Run and confirm pass:

```bash
npm test -- FilterBar
```

Expected: `5 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add FilterBar component"
```

---

## Task 8: App Integration

**Files:** `src/App.svelte`, `src/App.test.ts`

Deliverable: the full app wired together — adding, toggling, deleting, filtering, clearing completed, and showing the remaining count, all backed by the store and localStorage.

- [ ] Replace `src/App.test.ts` with integration tests:

```ts
import { render, screen, within } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, test } from 'vitest';
import App from './App.svelte';
import { todos } from './lib/store';

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
});

async function addTodo(user: ReturnType<typeof userEvent.setup>, text: string) {
  await user.type(screen.getByPlaceholderText('What needs to be done?'), `${text}{Enter}`);
}

test('renders the heading', () => {
  render(App);
  expect(screen.getByRole('heading', { name: 'Svelte Todos' })).toBeInTheDocument();
});

test('can add todos and they appear in the list', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'Buy groceries');
  await addTodo(user, 'Walk the dog');

  expect(screen.getByText('Buy groceries')).toBeInTheDocument();
  expect(screen.getByText('Walk the dog')).toBeInTheDocument();
});

test('shows remaining count and updates on toggle', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'a');
  await addTodo(user, 'b');
  expect(screen.getByText('2 items left')).toBeInTheDocument();

  await user.click(screen.getAllByRole('checkbox')[0]);
  expect(screen.getByText('1 item left')).toBeInTheDocument();
});

test('can delete a todo', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'Delete me');
  await user.click(screen.getByRole('button', { name: 'Delete Delete me' }));

  expect(screen.queryByText('Delete me')).not.toBeInTheDocument();
});

test('Active filter shows only incomplete todos', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'active one');
  await addTodo(user, 'done one');
  // complete the second todo
  await user.click(screen.getAllByRole('checkbox')[1]);

  await user.click(screen.getByRole('button', { name: 'Active' }));

  expect(screen.getByText('active one')).toBeInTheDocument();
  expect(screen.queryByText('done one')).not.toBeInTheDocument();
});

test('Completed filter shows only completed todos', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'active one');
  await addTodo(user, 'done one');
  await user.click(screen.getAllByRole('checkbox')[1]);

  await user.click(screen.getByRole('button', { name: 'Completed' }));

  expect(screen.queryByText('active one')).not.toBeInTheDocument();
  expect(screen.getByText('done one')).toBeInTheDocument();
});

test('Clear completed removes completed todos only', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'keep');
  await addTodo(user, 'remove');
  await user.click(screen.getAllByRole('checkbox')[1]);

  await user.click(screen.getByRole('button', { name: 'Clear completed' }));

  expect(screen.getByText('keep')).toBeInTheDocument();
  expect(screen.queryByText('remove')).not.toBeInTheDocument();
});

test('todos persist to localStorage', async () => {
  const user = userEvent.setup();
  render(App);

  await addTodo(user, 'Persisted');

  const stored = JSON.parse(localStorage.getItem('svelte-todos')!);
  expect(stored).toHaveLength(1);
  expect(stored[0].text).toBe('Persisted');
});
```

- [ ] Run and confirm failure:

```bash
npm test -- App
```

Expected: tests fail (current `App.svelte` only renders the heading).

- [ ] Implement `src/App.svelte`:

```svelte
<script lang="ts">
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
