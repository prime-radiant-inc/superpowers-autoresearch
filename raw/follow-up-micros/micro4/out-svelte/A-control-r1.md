# Svelte Todo List - Implementation Plan

## Overview

We are building a Svelte todo list app with TypeScript, Vite, and Vitest. The app supports adding, completing, deleting, and filtering todos with localStorage persistence.

This plan assumes **zero context**. Every file path, command, and code block is provided in full. Follow steps in order. Each step is a single small action. Commit frequently.

## Tech Stack

- **Svelte 4** + **TypeScript** + **Vite**
- **Vitest** + **@testing-library/svelte** for tests
- **jsdom** test environment for localStorage and DOM

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Vite + Vitest config (jsdom environment) |
| `tsconfig.json` | TypeScript config |
| `svelte.config.js` | Svelte preprocess config |
| `vitest-setup.ts` | Test setup (jest-dom matchers, localStorage reset) |
| `index.html` | HTML entry point |
| `src/main.ts` | App bootstrap |
| `src/app.css` | Global styles |
| `src/lib/types.ts` | `Todo` interface, `Filter` type |
| `src/lib/storage.ts` | localStorage load/save functions |
| `src/lib/store.ts` | Svelte store with todo CRUD operations |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Filter buttons, count, clear completed |
| `src/App.svelte` | Main app, wires everything together |

Test files live next to their source: `storage.test.ts`, `store.test.ts`, `TodoInput.test.ts`, etc.

---

## Task 1: Project Scaffolding

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `svelte.config.js`, `vitest-setup.ts`, `index.html`, `src/main.ts`, `src/app.css`, `src/App.svelte`, `.gitignore`

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
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3.1.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/svelte": "^5.1.0",
    "@tsconfig/svelte": "^5.0.4",
    "jsdom": "^24.0.0",
    "svelte": "^4.2.18",
    "svelte-check": "^3.8.0",
    "tslib": "^2.6.3",
    "typescript": "^5.4.5",
    "vite": "^5.3.0",
    "vitest": "^1.6.0"
  }
}
```

- [ ] Install dependencies:

```bash
npm install
```

Expected output ends with something like:
```
added 250 packages, and audited 251 packages in 8s
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
    "types": ["svelte", "vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src/**/*.ts", "src/**/*.svelte", "vitest-setup.ts"]
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
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest-setup.ts'],
  },
});
```

- [ ] Create `vitest-setup.ts`:

```ts
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';

afterEach(() => {
  localStorage.clear();
});
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
  font-family: system-ui, -apple-system, sans-serif;
  color: #213547;
  background-color: #f5f5f5;
}

body {
  margin: 0;
  display: flex;
  justify-content: center;
  padding: 2rem;
}

* {
  box-sizing: border-box;
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

- [ ] Create `src/App.svelte` (placeholder, fleshed out in Task 8):

```svelte
<main>
  <h1>Svelte Todos</h1>
</main>

<style>
  main {
    width: 480px;
    max-width: 100%;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  h1 {
    font-size: 1.5rem;
    margin: 0;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #eee;
  }
</style>
```

- [ ] Create `.gitignore`:

```
node_modules
dist
.DS_Store
```

- [ ] Verify the dev server boots:

```bash
npm run dev
```

Expected output includes:
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

Press `Ctrl+C` to stop.

- [ ] Verify the test runner works (no tests yet is fine):

```bash
npm test
```

Expected output includes:
```
No test files found, exiting with code 0
```

- [ ] Commit:

```bash
git add -A
git commit -m "Scaffold Svelte + TypeScript + Vitest project"
```

---

## Task 2: Types

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

- [ ] Verify TypeScript is happy:

```bash
npm run check
```

Expected output includes:
```
svelte-check found 0 errors and 0 warnings
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add Todo and Filter types"
```

---

## Task 3: Storage (localStorage persistence)

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

The storage module reads and writes the todo array to localStorage under a fixed key. Invalid/missing data returns an empty array.

- [ ] Write the failing test. Create `src/lib/storage.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { loadTodos, saveTodos } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('storage', () => {
  it('returns an empty array when nothing is stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns an empty array when stored data is invalid JSON', () => {
    localStorage.setItem('svelte-todos', 'not json{');
    expect(loadTodos()).toEqual([]);
  });

  it('returns an empty array when stored data is not an array', () => {
    localStorage.setItem('svelte-todos', '{"foo":"bar"}');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test storage
```

Expected output includes:
```
Error: Failed to resolve import "./storage"
```

- [ ] Implement `src/lib/storage.ts`:

```ts
import type { Todo } from './types';

const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed;
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
npm test storage
```

Expected output includes:
```
 ✓ src/lib/storage.test.ts (4)

 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add localStorage persistence module"
```

---

## Task 4: Store (todo CRUD + persistence)

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

The store is a custom Svelte writable that exposes `addTodo`, `toggleTodo`, `deleteTodo`, and `clearCompleted`. Every mutation persists to localStorage. It initializes from localStorage on creation.

- [ ] Write the failing test. Create `src/lib/store.test.ts`:

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { createTodoStore } from './store';
import { loadTodos } from './storage';

describe('todo store', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('starts empty when localStorage is empty', () => {
    const store = createTodoStore();
    expect(get(store)).toEqual([]);
  });

  it('initializes from localStorage', () => {
    localStorage.setItem(
      'svelte-todos',
      JSON.stringify([{ id: 'a', text: 'Existing', completed: false }])
    );
    const store = createTodoStore();
    expect(get(store)).toHaveLength(1);
    expect(get(store)[0].text).toBe('Existing');
  });

  it('adds a todo with a unique id and completed=false', () => {
    const store = createTodoStore();
    store.addTodo('Buy milk');
    const todos = get(store);
    expect(todos).toHaveLength(1);
    expect(todos[0].text).toBe('Buy milk');
    expect(todos[0].completed).toBe(false);
    expect(typeof todos[0].id).toBe('string');
    expect(todos[0].id.length).toBeGreaterThan(0);
  });

  it('does not add a todo with empty/whitespace text', () => {
    const store = createTodoStore();
    store.addTodo('   ');
    store.addTodo('');
    expect(get(store)).toHaveLength(0);
  });

  it('trims whitespace from todo text', () => {
    const store = createTodoStore();
    store.addTodo('  padded  ');
    expect(get(store)[0].text).toBe('padded');
  });

  it('toggles a todo completion', () => {
    const store = createTodoStore();
    store.addTodo('Task');
    const id = get(store)[0].id;
    store.toggleTodo(id);
    expect(get(store)[0].completed).toBe(true);
    store.toggleTodo(id);
    expect(get(store)[0].completed).toBe(false);
  });

  it('deletes a todo by id', () => {
    const store = createTodoStore();
    store.addTodo('Keep');
    store.addTodo('Remove');
    const removeId = get(store)[1].id;
    store.deleteTodo(removeId);
    const todos = get(store);
    expect(todos).toHaveLength(1);
    expect(todos[0].text).toBe('Keep');
  });

  it('clears all completed todos', () => {
    const store = createTodoStore();
    store.addTodo('A');
    store.addTodo('B');
    store.addTodo('C');
    const todos = get(store);
    store.toggleTodo(todos[0].id);
    store.toggleTodo(todos[2].id);
    store.clearCompleted();
    const remaining = get(store);
    expect(remaining).toHaveLength(1);
    expect(remaining[0].text).toBe('B');
  });

  it('persists changes to localStorage', () => {
    const store = createTodoStore();
    store.addTodo('Persist me');
    expect(loadTodos()).toHaveLength(1);
    expect(loadTodos()[0].text).toBe('Persist me');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test store
```

Expected output includes:
```
Error: Failed to resolve import "./store"
```

- [ ] Implement `src/lib/store.ts`:

```ts
import { writable } from 'svelte/store';
import type { Todo } from './types';
import { loadTodos, saveTodos } from './storage';

export function createTodoStore() {
  const { subscribe, update, set } = writable<Todo[]>(loadTodos());

  function persist(todos: Todo[]): Todo[] {
    saveTodos(todos);
    return todos;
  }

  return {
    subscribe,
    set,
    addTodo(text: string) {
      const trimmed = text.trim();
      if (!trimmed) return;
      update((todos) =>
        persist([
          ...todos,
          { id: crypto.randomUUID(), text: trimmed, completed: false },
        ])
      );
    },
    toggleTodo(id: string) {
      update((todos) =>
        persist(
          todos.map((t) =>
            t.id === id ? { ...t, completed: !t.completed } : t
          )
        )
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

- [ ] Run the test to see it pass:

```bash
npm test store
```

Expected output includes:
```
 ✓ src/lib/store.test.ts (9)

 Test Files  1 passed (1)
      Tests  9 passed (9)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add todo store with CRUD operations and persistence"
```

---

## Task 5: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

The input dispatches an `add` event with the text string when the user presses Enter or clicks Add. It clears itself after a successful add and ignores empty submissions.

- [ ] Write the failing test. Create `src/lib/TodoInput.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add event with text on Add button click', async () => {
    const { getByRole, getByPlaceholderText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'New task' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));

    expect(handler).toHaveBeenCalledWith('New task');
  });

  it('dispatches add event on Enter key', async () => {
    const { getByPlaceholderText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Enter task' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Enter task');
  });

  it('clears the input after adding', async () => {
    const { getByRole, getByPlaceholderText } = render(TodoInput);
    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Task' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(input.value).toBe('');
  });

  it('does not dispatch when input is empty', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test TodoInput
```

Expected output includes:
```
Error: Failed to resolve import "./TodoInput.svelte"
```

- [ ] Implement `src/lib/TodoInput.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ add: string }>();
  let text = '';

  function submit() {
    const trimmed = text.trim();
    if (!trimmed) return;
    dispatch('add', trimmed);
    text = '';
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') submit();
  }
</script>

<div class="input-row">
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value={text}
    on:keydown={handleKeydown}
  />
  <button on:click={submit}>Add</button>
</div>

<style>
  .input-row {
    display: flex;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #eee;
  }

  input {
    flex: 1;
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    background: #ff3e00;
    color: white;
    cursor: pointer;
  }

  button:hover {
    background: #e63600;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test TodoInput
```

Expected output includes:
```
 ✓ src/lib/TodoInput.test.ts (4)

 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoInput component"
```

---

## Task 6: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

Displays one todo. Dispatches `toggle` and `delete` events carrying the todo id. Shows completed state visually.

- [ ] Write the failing test. Create `src/lib/TodoItem.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'x1', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders the todo text', () => {
    const { getByText } = render(TodoItem, { props: { todo } });
    expect(getByText('Walk the dog')).toBeInTheDocument();
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
    expect(handler).toHaveBeenCalledWith('x1');
  });

  it('dispatches delete with id when delete button clicked', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Delete' }));
    expect(handler).toHaveBeenCalledWith('x1');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test TodoItem
```

Expected output includes:
```
Error: Failed to resolve import "./TodoItem.svelte"
```

- [ ] Implement `src/lib/TodoItem.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Todo } from './types';

  export let todo: Todo;

  const dispatch = createEventDispatcher<{ toggle: string; delete: string }>();
</script>

<li class="item" class:completed={todo.completed}>
  <input
    type="checkbox"
    checked={todo.completed}
    on:change={() => dispatch('toggle', todo.id)}
  />
  <span class="text">{todo.text}</span>
  <button
    class="delete"
    aria-label="Delete"
    on:click={() => dispatch('delete', todo.id)}
  >
    ✕
  </button>
</li>

<style>
  .item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid #f0f0f0;
  }

  .text {
    flex: 1;
  }

  .completed .text {
    text-decoration: line-through;
    color: #aaa;
  }

  input[type='checkbox'] {
    width: 1.1rem;
    height: 1.1rem;
    cursor: pointer;
  }

  .delete {
    border: none;
    background: none;
    color: #cc0000;
    cursor: pointer;
    font-size: 1rem;
    line-height: 1;
    padding: 0.25rem;
  }

  .delete:hover {
    color: #ff0000;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test TodoItem
```

Expected output includes:
```
 ✓ src/lib/TodoItem.test.ts (4)

 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoItem component"
```

---

## Task 7: TodoList Component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

Renders a list of TodoItems and forwards their `toggle`/`delete` events. Shows an empty-state message when there are no todos to show.

- [ ] Write the failing test. Create `src/lib/TodoList.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'First', completed: false },
  { id: '2', text: 'Second', completed: true },
];

describe('TodoList', () => {
  it('renders all todos passed in', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('First')).toBeInTheDocument();
    expect(getByText('Second')).toBeInTheDocument();
  });

  it('shows empty-state message when list is empty', () => {
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
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getAllByRole('button', { name: 'Delete' })[1]);
    expect(handler).toHaveBeenCalledWith('2');
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test TodoList
```

Expected output includes:
```
Error: Failed to resolve import "./TodoList.svelte"
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
  <ul>
    {#each todos as todo (todo.id)}
      <TodoItem {todo} on:toggle on:delete />
    {/each}
  </ul>
{/if}

<style>
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .empty {
    text-align: center;
    color: #999;
    padding: 2rem 1.25rem;
    margin: 0;
  }
</style>
```

Note: `on:toggle on:delete` without handlers forwards the events from `TodoItem` up to `TodoList`'s parent, preserving `event.detail`.

- [ ] Run the test to see it pass:

```bash
npm test TodoList
```

Expected output includes:
```
 ✓ src/lib/TodoList.test.ts (4)

 Test Files  1 passed (1)
      Tests  4 passed (4)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoList component with empty state"
```

---

## Task 8: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

Shows the count of remaining (incomplete) items, three filter buttons (highlighting the active one), and a "Clear completed" button. Dispatches `filter` (with the chosen `Filter` value) and `clear` events.

- [ ] Write the failing test. Create `src/lib/FilterBar.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows singular item count', () => {
    const { getByText } = render(FilterBar, {
      props: { activeFilter: 'all', remaining: 1 },
    });
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('shows plural item count', () => {
    const { getByText } = render(FilterBar, {
      props: { activeFilter: 'all', remaining: 3 },
    });
    expect(getByText('3 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    const { getByRole } = render(FilterBar, {
      props: { activeFilter: 'active', remaining: 0 },
    });
    expect(getByRole('button', { name: 'Active' })).toHaveClass('active');
    expect(getByRole('button', { name: 'All' })).not.toHaveClass('active');
  });

  it('dispatches filter event with the chosen filter', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { activeFilter: 'all', remaining: 0 },
    });
    const handler = vi.fn();
    component.$on('filter', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clear event when Clear completed clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { activeFilter: 'all', remaining: 0 },
    });
    const handler = vi.fn();
    component.$on('clear', handler);
    await fireEvent.click(getByRole('button', { name: 'Clear completed' }));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run the test to see it fail:

```bash
npm test FilterBar
```

Expected output includes:
```
Error: Failed to resolve import "./FilterBar.svelte"
```

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let activeFilter: Filter;
  export let remaining: number;

  const dispatch = createEventDispatcher<{ filter: Filter; clear: void }>();
  const filters: Filter[] = ['all', 'active', 'completed'];

  function label(f: Filter): string {
    return f.charAt(0).toUpperCase() + f.slice(1);
  }
</script>

<div class="bar">
  <span class="count">
    {remaining} {remaining === 1 ? 'item' : 'items'} left
  </span>

  <div class="filters">
    {#each filters as f}
      <button
        class:active={activeFilter === f}
        on:click={() => dispatch('filter', f)}
      >
        {label(f)}
      </button>
    {/each}
  </div>

  <button class="clear" on:click={() => dispatch('clear')}>
    Clear completed
  </button>
</div>

<style>
  .bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    border-top: 1px solid #eee;
    font-size: 0.9rem;
  }

  .count {
    color: #666;
  }

  .filters {
    display: flex;
    gap: 0.25rem;
    margin-left: auto;
  }

  button {
    border: 1px solid transparent;
    background: none;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    color: #333;
  }

  button:hover {
    border-color: #ddd;
  }

  .filters button.active {
    border-color: #ff3e00;
    color: #ff3e00;
  }

  .clear {
    color: #cc0000;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test FilterBar
```

Expected output includes:
```
 ✓ src/lib/FilterBar.test.ts (5)

 Test Files  1 passed (1)
      Tests  5 passed (5)
```

- [ ] Commit:

```bash
git add -A
git commit -m "Add FilterBar component"
```

---

## Task 9: App Integration

**Files:** `src/App.svelte`, `src/App.test.ts`

Wire all components to the store. App holds the active filter, computes the filtered view and remaining count, and connects component events to store methods.

- [ ] Write the failing integration test. Create `src/App.test.ts`:

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import App from './App.svelte';

async function addTodo(input: HTMLInputElement, text: string) {
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.keyDown(input, { key: 'Enter' });
}

describe('App integration', () => {
  beforeEach(() => {
    localStorage.clear();
