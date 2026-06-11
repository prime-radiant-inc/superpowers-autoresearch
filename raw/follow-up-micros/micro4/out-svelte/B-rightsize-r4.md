# Svelte Todo List - Implementation Plan

## Overview

We are building a Svelte todo application with TypeScript, Vite, and Vitest. The app supports adding, toggling, deleting, and filtering todos, with localStorage persistence. We build bottom-up: storage layer → store → leaf components → container components → main app.

This plan assumes **zero prior context**. Every file path, command, and code block is given in full.

## Tech Stack & Conventions

- **Svelte 4** with TypeScript
- **Vite** as build tool / dev server
- **Vitest** + **@testing-library/svelte** for tests
- **jsdom** test environment (gives us `localStorage` and DOM)
- Package manager: `npm`

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Dependencies and scripts |
| `tsconfig.json` | TypeScript config |
| `vite.config.ts` | Vite + Vitest config |
| `vitest-setup.ts` | Test setup (jest-dom matchers) |
| `index.html` | HTML entry point |
| `src/main.ts` | Mounts `App.svelte` |
| `src/app.css` | Global styles |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte store with todo CRUD operations |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo (checkbox, text, delete) |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear completed |
| `src/App.svelte` | Main app wiring components + store |

Test files live next to their sources with a `.test.ts` / `.test.svelte.ts` suffix as noted per task.

---

### Task 1: Project Scaffolding

Sets up the buildable, testable project skeleton. Deliverable: `npm test` runs (with zero tests) and `npm run build` succeeds.

**Files:** `package.json`, `tsconfig.json`, `tsconfig.node.json`, `vite.config.ts`, `vitest-setup.ts`, `index.html`, `src/main.ts`, `src/app.css`, `src/App.svelte`, `.gitignore`

- [ ] Create `.gitignore`:

```
node_modules
dist
*.local
.DS_Store
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
    "test:watch": "vitest"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3.1.2",
    "@testing-library/jest-dom": "^6.4.8",
    "@testing-library/svelte": "^5.2.1",
    "@tsconfig/svelte": "^5.0.4",
    "jsdom": "^25.0.0",
    "svelte": "^4.2.19",
    "svelte-check": "^4.0.2",
    "tslib": "^2.7.0",
    "typescript": "^5.5.4",
    "vite": "^5.4.3",
    "vitest": "^2.0.5"
  }
}
```

- [ ] Run install:

```bash
npm install
```

Expected: completes without errors, creates `node_modules/` and `package-lock.json`.

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
  "include": ["src/**/*.ts", "src/**/*.svelte", "vitest-setup.ts"],
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

```typescript
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

```typescript
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
  color: #213547;
  background-color: #f6f6f6;
}

body {
  margin: 0;
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
}
```

- [ ] Create `src/App.svelte`:

```svelte
<script lang="ts">
</script>

<main>
  <h1>Svelte Todos</h1>
</main>

<style>
  main {
    width: 100%;
    max-width: 480px;
  }
</style>
```

- [ ] Create `src/main.ts`:

```typescript
import './app.css';
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')!,
});

export default app;
```

- [ ] Verify the build works:

```bash
npm run build
```

Expected: ends with `✓ built in ...ms` and creates a `dist/` folder, no errors.

- [ ] Verify the test runner works (no tests yet):

```bash
npm test
```

Expected: Vitest reports `No test files found` and exits with code 0 (because `vitest run` treats no-files as success). If it exits non-zero on your version, that's fine — the next task adds a real test.

- [ ] Commit:

```bash
git init && git add -A && git commit -m "Scaffold Svelte + Vite + Vitest project"
```

---

### Task 2: Types and Storage Layer

Deliverable: `storage.ts` with `loadTodos` / `saveTodos` backed by localStorage, fully tested.

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

- [ ] Create `src/lib/types.ts`:

```typescript
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

- [ ] Write failing test `src/lib/storage.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos, STORAGE_KEY } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns an empty array when nothing is stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves todos to localStorage under STORAGE_KEY', () => {
    saveTodos(sample);
    expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
  });

  it('loads previously saved todos', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns an empty array when stored data is invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not json{');
    expect(loadTodos()).toEqual([]);
  });

  it('returns an empty array when stored data is not an array', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ foo: 'bar' }));
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: fails with `Failed to resolve import "./storage"` or similar (file doesn't exist yet).

- [ ] Implement `src/lib/storage.ts`:

```typescript
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

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `5 passed`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add types and localStorage persistence layer"
```

---

### Task 3: Todo Store

Deliverable: a Svelte writable store wrapper exposing `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted`, auto-persisting on every change. Fully tested.

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

- [ ] Write failing test `src/lib/store.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { createTodoStore } from './store';
import { loadTodos, STORAGE_KEY } from './storage';

describe('todo store', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('initializes empty when nothing is stored', () => {
    const store = createTodoStore();
    expect(get(store)).toEqual([]);
  });

  it('initializes from localStorage', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify([{ id: 'x', text: 'preloaded', completed: false }]),
    );
    const store = createTodoStore();
    expect(get(store)).toHaveLength(1);
    expect(get(store)[0].text).toBe('preloaded');
  });

  it('adds a todo with a unique id, trimmed text, incomplete', () => {
    const store = createTodoStore();
    store.addTodo('  Buy milk  ');
    const todos = get(store);
    expect(todos).toHaveLength(1);
    expect(todos[0].text).toBe('Buy milk');
    expect(todos[0].completed).toBe(false);
    expect(todos[0].id).toBeTruthy();
  });

  it('ignores empty or whitespace-only text', () => {
    const store = createTodoStore();
    store.addTodo('   ');
    store.addTodo('');
    expect(get(store)).toHaveLength(0);
  });

  it('gives each todo a distinct id', () => {
    const store = createTodoStore();
    store.addTodo('a');
    store.addTodo('b');
    const [first, second] = get(store);
    expect(first.id).not.toBe(second.id);
  });

  it('toggles completion', () => {
    const store = createTodoStore();
    store.addTodo('task');
    const id = get(store)[0].id;
    store.toggleTodo(id);
    expect(get(store)[0].completed).toBe(true);
    store.toggleTodo(id);
    expect(get(store)[0].completed).toBe(false);
  });

  it('deletes a todo', () => {
    const store = createTodoStore();
    store.addTodo('task');
    const id = get(store)[0].id;
    store.deleteTodo(id);
    expect(get(store)).toHaveLength(0);
  });

  it('clears completed todos only', () => {
    const store = createTodoStore();
    store.addTodo('keep');
    store.addTodo('remove');
    const removeId = get(store)[1].id;
    store.toggleTodo(removeId);
    store.clearCompleted();
    const todos = get(store);
    expect(todos).toHaveLength(1);
    expect(todos[0].text).toBe('keep');
  });

  it('persists every change to localStorage', () => {
    const store = createTodoStore();
    store.addTodo('persisted');
    expect(loadTodos()).toHaveLength(1);
    const id = get(store)[0].id;
    store.toggleTodo(id);
    expect(loadTodos()[0].completed).toBe(true);
    store.deleteTodo(id);
    expect(loadTodos()).toHaveLength(0);
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: fails resolving `./store`.

- [ ] Implement `src/lib/store.ts`:

```typescript
import { writable } from 'svelte/store';
import type { Todo } from './types';
import { loadTodos, saveTodos } from './storage';

export function createTodoStore() {
  const { subscribe, update } = writable<Todo[]>(loadTodos());

  function persist(todos: Todo[]): Todo[] {
    saveTodos(todos);
    return todos;
  }

  return {
    subscribe,

    addTodo(text: string) {
      const trimmed = text.trim();
      if (trimmed === '') return;
      update((todos) =>
        persist([
          ...todos,
          { id: crypto.randomUUID(), text: trimmed, completed: false },
        ]),
      );
    },

    toggleTodo(id: string) {
      update((todos) =>
        persist(
          todos.map((t) =>
            t.id === id ? { ...t, completed: !t.completed } : t,
          ),
        ),
      );
    },

    deleteTodo(id: string) {
      update((todos) => persist(todos.filter((t) => t.id !== id)));
    },

    clearCompleted() {
      update((todos) => persist(todos.filter((t) => !t.completed)));
    },
  };
}

export const todos = createTodoStore();
```

> Note: `crypto.randomUUID()` is available in jsdom (Node 19+) and all modern browsers.

- [ ] Run to see it pass:

```bash
npm test
```

Expected: all store tests plus storage tests pass (`14 passed`).

- [ ] Commit:

```bash
git add -A && git commit -m "Add todo store with CRUD and persistence"
```

---

### Task 4: TodoInput Component

Deliverable: input + Add button that dispatches an `add` event on Enter or click, clearing the field. Tested via Testing Library.

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

- [ ] Write failing test `src/lib/TodoInput.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add with text when Add button is clicked', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'New task' } });
    await fireEvent.click(getByRole('button', { name: /add/i }));

    expect(handler).toHaveBeenCalledWith('New task');
  });

  it('dispatches add when Enter is pressed', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Via enter' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Via enter');
  });

  it('clears the input after adding', async () => {
    const { getByRole } = render(TodoInput);
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Clear me' } });
    await fireEvent.click(getByRole('button', { name: /add/i }));
    expect(input.value).toBe('');
  });

  it('does not dispatch add for whitespace-only input', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);

    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: '   ' } });
    await fireEvent.click(getByRole('button', { name: /add/i }));

    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: fails resolving `./TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ add: string }>();
  let value = '';

  function submit() {
    if (value.trim() === '') return;
    dispatch('add', value);
    value = '';
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') submit();
  }
</script>

<div class="todo-input">
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value
    on:keydown={handleKeydown}
  />
  <button on:click={submit}>Add</button>
</div>

<style>
  .todo-input {
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
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: 4 new tests pass.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 5: TodoItem Component

Deliverable: renders one todo with a checkbox, text, and delete button; dispatches `toggle` and `delete` events with the todo id.

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

- [ ] Write failing test `src/lib/TodoItem.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders the todo text', () => {
    const { getByText } = render(TodoItem, { props: { todo } });
    expect(getByText('Walk the dog')).toBeInTheDocument();
  });

  it('reflects completed state in the checkbox', () => {
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

  it('dispatches delete with id when delete clicked', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: /delete/i }));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: fails resolving `./TodoItem.svelte`.

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
    aria-label="Delete"
    on:click={() => dispatch('delete', todo.id)}>×</button
  >
</li>

<style>
  .todo-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
  }
  .text {
    flex: 1;
  }
  .completed .text {
    text-decoration: line-through;
    color: #999;
  }
  .delete {
    border: none;
    background: none;
    color: #c00;
    font-size: 1.2rem;
    cursor: pointer;
    line-height: 1;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: 4 new tests pass.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 6: TodoList Component

Deliverable: renders a list of `TodoItem`s, forwards their `toggle`/`delete` events, and shows an empty-state message when there are no todos.

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

- [ ] Write failing test `src/lib/TodoList.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'First', completed: false },
  { id: '2', text: 'Second', completed: true },
];

describe('TodoList', () => {
  it('renders all todos', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('First')).toBeInTheDocument();
    expect(getByText('Second')).toBeInTheDocument();
  });

  it('shows empty state when there are no todos', () => {
    const { getByText } = render(TodoList, { props: { todos: [] } });
    expect(getByText(/nothing here/i)).toBeInTheDocument();
  });

  it('forwards toggle events from items', async () => {
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete events from items', async () => {
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getAllByRole('button', { name: /delete/i })[1]);
    expect(handler).toHaveBeenCalledWith('2');
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: fails resolving `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:

```svelte
<script lang="ts">
  import type { Todo } from './types';
  import TodoItem from './TodoItem.svelte';

  export let todos: Todo[];
</script>

{#if todos.length === 0}
  <p class="empty">Nothing here yet — add your first todo!</p>
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
    color: #999;
    padding: 1rem 0;
  }
</style>
```

> Note: `on:toggle on:delete` with no handler forwards the child's events upward.

- [ ] Run to see it pass:

```bash
npm test
```

Expected: 4 new tests pass.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 7: FilterBar Component

Deliverable: shows remaining-item count, three filter buttons (highlighting the active filter), and a "Clear completed" button. Dispatches `filter` and `clearCompleted` events.

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

- [ ] Write failing test `src/lib/FilterBar.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows singular item count', () => {
    const { getByText } = render(FilterBar, {
      props: { activeCount: 1, filter: 'all' },
    });
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('shows plural item count', () => {
    const { getByText } = render(FilterBar, {
      props: { activeCount: 2, filter: 'all' },
    });
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    const { getByRole } = render(FilterBar, {
      props: { activeCount: 0, filter: 'active' },
    });
    expect(getByRole('button', { name: 'Active' })).toHaveClass('selected');
    expect(getByRole('button', { name: 'All' })).not.toHaveClass('selected');
  });

  it('dispatches filter when a filter button is clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { activeCount: 0, filter: 'all' },
    });
    const handler = vi.fn();
    component.$on('filter', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clearCompleted when clear button clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { activeCount: 0, filter: 'all' },
    });
    const handler = vi.fn();
    component.$on('clearCompleted', handler);
    await fireEvent.click(getByRole('button', { name: /clear completed/i }));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: fails resolving `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let activeCount: number;
  export let filter: Filter;

  const dispatch = createEventDispatcher<{
    filter: Filter;
    clearCompleted: void;
  }>();

  const filters: { value: Filter; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
  ];

  $: itemWord = activeCount === 1 ? 'item' : 'items';
</script>

<div class="filter-bar">
  <span class="count">{activeCount} {itemWord} left</span>

  <div class="filters">
    {#each filters as f}
      <button
        class:selected={filter === f.value}
        on:click={() => dispatch('filter', f.value)}>{f.label}</button
      >
    {/each}
  </div>

  <button class="clear" on:click={() => dispatch('clearCompleted')}
    >Clear completed</button
  >
</div>

<style>
  .filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-top: 0.75rem;
    font-size: 0.9rem;
  }
  .filters {
    display: flex;
    gap: 0.25rem;
  }
  button {
    border: 1px solid transparent;
    background: none;
    padding: 0.25rem 0.5rem;
    cursor: pointer;
    border-radius: 4px;
  }
  .filters button.selected {
    border-color: #c00;
  }
  .clear {
    color: #c00;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: 5 new tests pass.

- [ ] Commit:

```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 8: App Wiring & Integration

Deliverable: `App.svelte` connects the store and all components — adding, toggling, deleting, filtering, clearing, and persistence all work end-to-end. Covers acceptance criteria 1–8.

**Files:** `src/App.svelte`, `src/App.test.ts`

- [ ] Write failing test `src/App.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent, within } from '@testing-library/svelte';
import App from './App.svelte';
import { STORAGE_KEY } from './lib/storage';

async function addTodo(getByRole: any, text: string) {
  const input = getByRole('textbox') as HTMLInputElement;
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.click(getByRole('button', { name: /^add$/i }));
}

describe('App integration', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('adds todos and shows them in the list', async () => {
    const { getByRole, getByText } = render(App);
    await addTodo(getByRole, 'Buy groceries');
    expect(getByText('Buy groceries')).toBeInTheDocument();
  });

  it('updates the remaining count as todos are added and toggled', async () => {
    const { getByRole, getByText, getAllByRole } = render(App);
    await addTodo(getByRole, 'A');
    await addTodo(getByRole, 'B');
    expect(getByText('2 items left')).toBeInTheDocument();
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodo(getByRole, 'Delete me');
    await fireEvent.click(getAllByRole('button', { name: /delete/i })[0]);
    expect(queryByText('Delete me')).not.toBeInTheDocument();
  });

  it('filters to active and completed', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodo(getByRole, 'Active task');
    await addTodo(getByRole, 'Done task');
    // complete the second todo
    await fireEvent.click(getAllByRole('checkbox')[1]);

    await fireEvent.click(getByRole('button', { name: 'Active' }));
    expect(queryByText('Active task')).toBeInTheDocument();
    expect(queryByText('Done task')).not.toBeInTheDocument();

    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(queryByText('Active task')).not.toBeInTheDocument();
    expect(queryByText('Done task')).toBeInTheDocument();

    await fireEvent.click(getByRole('button', { name: 'All' }));
    expect(queryByText('Active task')).toBeInTheDocument();
    expect(queryByText('Done task')).toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodo(getByRole, 'Keep');
    await addTodo(getByRole, 'Remove');
    await fireEv