# Svelte Todo List - Implementation Plan

## Overview

We are building a Svelte todo application with localStorage persistence. The architecture uses a Svelte store (`store.ts`) as the single source of truth, a thin persistence layer (`storage.ts`), and presentational components driven by the store.

This plan assumes **zero context**. Every file path, command, and expected output is spelled out. We use TDD: write a failing test, watch it fail, implement, watch it pass, commit.

## Tech Stack

- **Svelte 4** + **Vite** (project scaffolding)
- **TypeScript**
- **Vitest** + **@testing-library/svelte** for tests
- **jsdom** for DOM/localStorage in tests

## File Structure

```
src/
  App.svelte           # Main app: wires store to components
  main.ts              # Vite entry point (scaffolded)
  app.css              # Global styles (scaffolded, edited)
  lib/
    types.ts           # Todo interface + Filter type
    storage.ts         # loadTodos() / saveTodos() against localStorage
    store.ts           # writable todos store + filter store + actions
    TodoInput.svelte   # Text input + Add button, emits "add"
    TodoList.svelte    # Renders filtered todos or empty state
    TodoItem.svelte    # Single todo: checkbox, text, delete button
    FilterBar.svelte   # Count, filter buttons, clear completed
  lib/__tests__/
    storage.test.ts
    store.test.ts
    TodoInput.test.ts
    TodoItem.test.ts
    TodoList.test.ts
    FilterBar.test.ts
  App.test.ts          # Integration test (acceptance criteria)
```

**Single responsibility per file:**

- `types.ts` — data shapes only, no logic.
- `storage.ts` — only talks to `localStorage`. Knows nothing about Svelte.
- `store.ts` — holds state, exposes actions, calls `storage.ts` on change. Knows nothing about the DOM.
- Components — render and emit events. They read the store and call store actions.

---

### Task 1: Project Scaffolding

**Files:** `package.json`, `vite.config.ts`, `vitest-setup.ts`, `tsconfig.json`

- [ ] Scaffold the Vite + Svelte + TS project in a fresh directory:

```bash
npm create vite@latest svelte-todos -- --template svelte-ts
cd svelte-todos
npm install
```

Expected: a `svelte-todos/` directory with `src/App.svelte`, `src/main.ts`, `package.json`.

- [ ] Install test dependencies:

```bash
npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @vitest/ui
```

Expected: `npm install` completes, devDependencies updated in `package.json`.

- [ ] Create `vitest-setup.ts` at the project root:

```typescript
import '@testing-library/jest-dom';
```

- [ ] Replace `vite.config.ts` at the project root with:

```typescript
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

- [ ] Add a `test` script to `package.json`. Open `package.json`, find the `"scripts"` block, and ensure it contains:

```json
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "test": "vitest run",
    "test:watch": "vitest"
  },
```

- [ ] Verify the test runner starts (no tests yet is fine):

```bash
npm test
```

Expected output includes: `No test files found, exiting with code 1` — this confirms Vitest is wired up. We will add tests next.

- [ ] Commit:

```bash
git init && git add -A && git commit -m "Scaffold Svelte+TS+Vitest project"
```

---

### Task 2: Data Types

**Files:** `src/lib/types.ts`

- [ ] Create `src/lib/types.ts`:

```typescript
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

- [ ] Verify it type-checks:

```bash
npm run check
```

Expected: `svelte-check found 0 errors`.

- [ ] Commit:

```bash
git add -A && git commit -m "Add Todo and Filter types"
```

---

### Task 3: Storage Layer (TDD)

**Files:** `src/lib/storage.ts`, `src/lib/__tests__/storage.test.ts`

- [ ] Create the test file `src/lib/__tests__/storage.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos } from '../storage';
import type { Todo } from '../types';

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

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns an empty array when stored data is corrupt', () => {
    localStorage.setItem('svelte-todos', 'not json{');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run the test and watch it fail (module does not exist yet):

```bash
npm test
```

Expected: failure `Failed to resolve import "../storage"`.

- [ ] Implement `src/lib/storage.ts`:

```typescript
import type { Todo } from './types';

const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Todo[]) : [];
  } catch {
    return [];
  }
}

export function saveTodos(todos: Todo[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}
```

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `storage.test.ts` — 3 passed.

- [ ] Commit:

```bash
git add -A && git commit -m "Add localStorage persistence layer"
```

---

### Task 4: Store + Actions (TDD)

**Files:** `src/lib/store.ts`, `src/lib/__tests__/store.test.ts`

The store holds the todos array, exposes a `filter` store, and exposes action functions: `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted`. It auto-persists via `saveTodos` on every change, and a `remaining` derived store counts incomplete todos.

- [ ] Create the test file `src/lib/__tests__/store.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  filter,
  remaining,
  filteredTodos,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
  resetStore,
} from '../store';
import { loadTodos } from '../storage';

describe('store', () => {
  beforeEach(() => {
    localStorage.clear();
    resetStore();
  });

  it('starts empty', () => {
    expect(get(todos)).toEqual([]);
  });

  it('adds a todo with a unique id and incomplete status', () => {
    addTodo('Write code');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Write code');
    expect(list[0].completed).toBe(false);
    expect(typeof list[0].id).toBe('string');
    expect(list[0].id.length).toBeGreaterThan(0);
  });

  it('ignores empty or whitespace-only text', () => {
    addTodo('   ');
    addTodo('');
    expect(get(todos)).toHaveLength(0);
  });

  it('trims whitespace from added text', () => {
    addTodo('  hello  ');
    expect(get(todos)[0].text).toBe('hello');
  });

  it('toggles a todo completion', () => {
    addTodo('task');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deletes a todo', () => {
    addTodo('task');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  it('clears completed todos only', () => {
    addTodo('a');
    addTodo('b');
    const [first] = get(todos);
    toggleTodo(first.id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('counts remaining (incomplete) todos', () => {
    addTodo('a');
    addTodo('b');
    toggleTodo(get(todos)[0].id);
    expect(get(remaining)).toBe(1);
  });

  it('filters todos by active and completed', () => {
    addTodo('a');
    addTodo('b');
    toggleTodo(get(todos)[0].id);

    filter.set('active');
    expect(get(filteredTodos).map((t) => t.text)).toEqual(['b']);

    filter.set('completed');
    expect(get(filteredTodos).map((t) => t.text)).toEqual(['a']);

    filter.set('all');
    expect(get(filteredTodos)).toHaveLength(2);
  });

  it('persists changes to localStorage', () => {
    addTodo('persisted');
    expect(loadTodos()).toHaveLength(1);
    expect(loadTodos()[0].text).toBe('persisted');
  });

  it('initializes from localStorage on load via resetStore', () => {
    addTodo('survivor');
    // resetStore re-reads from storage
    resetStore();
    expect(get(todos)[0].text).toBe('survivor');
  });
});
```

- [ ] Run the test and watch it fail:

```bash
npm test
```

Expected: failure `Failed to resolve import "../store"`.

- [ ] Implement `src/lib/store.ts`:

```typescript
import { writable, derived, get } from 'svelte/store';
import type { Todo, Filter } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());
export const filter = writable<Filter>('all');

// Persist on every change.
todos.subscribe((value) => {
  saveTodos(value);
});

export const remaining = derived(todos, ($todos) =>
  $todos.filter((t) => !t.completed).length
);

export const filteredTodos = derived(
  [todos, filter],
  ([$todos, $filter]) => {
    switch ($filter) {
      case 'active':
        return $todos.filter((t) => !t.completed);
      case 'completed':
        return $todos.filter((t) => t.completed);
      default:
        return $todos;
    }
  }
);

export function addTodo(text: string): void {
  const trimmed = text.trim();
  if (!trimmed) return;
  const todo: Todo = {
    id: crypto.randomUUID(),
    text: trimmed,
    completed: false,
  };
  todos.update(($todos) => [...$todos, todo]);
}

export function toggleTodo(id: string): void {
  todos.update(($todos) =>
    $todos.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
  );
}

export function deleteTodo(id: string): void {
  todos.update(($todos) => $todos.filter((t) => t.id !== id));
}

export function clearCompleted(): void {
  todos.update(($todos) => $todos.filter((t) => !t.completed));
}

/** Test helper: re-read state from localStorage. */
export function resetStore(): void {
  todos.set(loadTodos());
  filter.set('all');
}
```

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `store.test.ts` — all passed. (`crypto.randomUUID` is available in jsdom under modern Node; if running Node < 19 in CI, ensure Node ≥ 19.)

- [ ] Commit:

```bash
git add -A && git commit -m "Add todos store with actions and derived state"
```

---

### Task 5: TodoInput Component (TDD)

**Files:** `src/lib/TodoInput.svelte`, `src/lib/__tests__/TodoInput.test.ts`

This component owns local input text and emits an `add` event with the text on Enter or Add click. It does not call the store directly — `App.svelte` wires it.

- [ ] Create the test file `src/lib/__tests__/TodoInput.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from '../TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add with text when Add clicked', async () => {
    const { getByPlaceholderText, getByText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Buy milk' } });
    await fireEvent.click(getByText('Add'));

    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler.mock.calls[0][0].detail).toBe('Buy milk');
  });

  it('dispatches add on Enter key', async () => {
    const { getByPlaceholderText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Walk dog' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler.mock.calls[0][0].detail).toBe('Walk dog');
  });

  it('clears the input after dispatching', async () => {
    const { getByPlaceholderText, getByText } = render(TodoInput);
    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'task' } });
    await fireEvent.click(getByText('Add'));
    expect(input.value).toBe('');
  });

  it('does not dispatch for empty input', async () => {
    const { getByText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);
    await fireEvent.click(getByText('Add'));
    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run the test and watch it fail:

```bash
npm test
```

Expected: failure resolving `../TodoInput.svelte`.

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

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') submit();
  }
</script>

<div class="todo-input">
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value={text}
    on:keydown={onKeydown}
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

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `TodoInput.test.ts` — 4 passed.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 6: TodoItem Component (TDD)

**Files:** `src/lib/TodoItem.svelte`, `src/lib/__tests__/TodoItem.test.ts`

Renders a single todo. Emits `toggle` and `delete` events carrying the todo id.

- [ ] Create the test file `src/lib/__tests__/TodoItem.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from '../TodoItem.svelte';
import type { Todo } from '../types';

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
    component.$on('toggle', handler);
    await fireEvent.click(getByRole('checkbox'));
    expect(handler.mock.calls[0][0].detail).toBe('abc');
  });

  it('dispatches delete with id when delete clicked', async () => {
    const { getByLabelText, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', handler);
    await fireEvent.click(getByLabelText('Delete'));
    expect(handler.mock.calls[0][0].detail).toBe('abc');
  });
});
```

- [ ] Run the test and watch it fail:

```bash
npm test
```

Expected: failure resolving `../TodoItem.svelte`.

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
  <button class="delete" aria-label="Delete" on:click={() => dispatch('delete', todo.id)}>
    ✕
  </button>
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
    cursor: pointer;
    font-size: 1rem;
  }
</style>
```

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `TodoItem.test.ts` — 4 passed.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 7: TodoList Component (TDD)

**Files:** `src/lib/TodoList.svelte`, `src/lib/__tests__/TodoList.test.ts`

Renders a list of `TodoItem`s, or an empty-state message. Forwards `toggle`/`delete` events upward.

- [ ] Create the test file `src/lib/__tests__/TodoList.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from '../TodoList.svelte';
import type { Todo } from '../types';

const todos: Todo[] = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

describe('TodoList', () => {
  it('renders all provided todos', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('a')).toBeInTheDocument();
    expect(getByText('b')).toBeInTheDocument();
  });

  it('shows empty state when no todos', () => {
    const { getByText } = render(TodoList, { props: { todos: [] } });
    expect(getByText('Nothing here yet. Add your first todo!')).toBeInTheDocument();
  });

  it('forwards toggle events from items', async () => {
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('toggle', handler);
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(handler.mock.calls[0][0].detail).toBe('1');
  });

  it('forwards delete events from items', async () => {
    const { getAllByLabelText, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('delete', handler);
    await fireEvent.click(getAllByLabelText('Delete')[1]);
    expect(handler.mock.calls[0][0].detail).toBe('2');
  });
});
```

- [ ] Run the test and watch it fail:

```bash
npm test
```

Expected: failure resolving `../TodoList.svelte`.

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
    margin: 0;
    padding: 0;
  }
  .empty {
    color: #999;
    text-align: center;
    padding: 1rem 0;
  }
</style>
```

Note: `on:toggle on:delete` without a handler **forwards** the child's events to the parent.

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `TodoList.test.ts` — 4 passed.

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 8: FilterBar Component (TDD)

**Files:** `src/lib/FilterBar.svelte`, `src/lib/__tests__/FilterBar.test.ts`

Shows the remaining count, three filter buttons, and a "Clear completed" button. Takes `remaining` and `filter` as props; emits `setFilter` and `clearCompleted`.

- [ ] Create the test file `src/lib/__tests__/FilterBar.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from '../FilterBar.svelte';

describe('FilterBar', () => {
  it('shows singular item count', () => {
    const { getByText } = render(FilterBar, {
      props: { remaining: 1, filter: 'all' },
    });
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('shows plural item count', () => {
    const { getByText } = render(FilterBar, {
      props: { remaining: 2, filter: 'all' },
    });
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    const { getByText } = render(FilterBar, {
      props: { remaining: 0, filter: 'active' },
    });
    expect(getByText('Active')).toHaveClass('selected');
    expect(getByText('All')).not.toHaveClass('selected');
  });

  it('dispatches setFilter when a filter button clicked', async () => {
    const { getByText, component } = render(FilterBar, {
      props: { remaining: 0, filter: 'all' },
    });
    const handler = vi.fn();
    component.$on('setFilter', handler);
    await fireEvent.click(getByText('Completed'));
    expect(handler.mock.calls[0][0].detail).toBe('completed');
  });

  it('dispatches clearCompleted when Clear clicked', async () => {
    const { getByText, component } = render(FilterBar, {
      props: { remaining: 0, filter: 'all' },
    });
    const handler = vi.fn();
    component.$on('clearCompleted', handler);
    await fireEvent.click(getByText('Clear completed'));
    expect(handler).toHaveBeenCalledTimes(1);
  });
});
```

- [ ] Run the test and watch it fail:

```bash
npm test
```

Expected: failure resolving `../FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let remaining: number;
  export let filter: Filter;

  const dispatch = createEventDispatcher<{
    setFilter: Filter;
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
  <span class="count">{remaining} {remaining === 1 ? 'item' : 'items'} left</span>

  <div class="filters">
    {#each filters as f}
      <button
        class:selected={filter === f}
        on:click={() => dispatch('setFilter', f)}
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
    padding-top: 0.5rem;
    flex-wrap: wrap;
  }
  .filters button {
    border: 1px solid transparent;
    background: none;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
  }
  .filters button.selected {
    border-color: #888;
    border-radius: 4px;
  }
  .clear {
    border: none;
    background: none;
    cursor: pointer;
    color: #c00;
  }
</style>
```

- [ ] Run the test and watch it pass:

```bash
npm test
```

Expected: `FilterBar.test.ts` — 5 passed.

- [ ] Commit:

```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 9: App Wiring + Integration Tests (TDD)

**Files:** `src/App.svelte`, `src/App.test.ts`, `src/app.css`

`App.svelte` connects the store to the components: subscribes to `filteredTodos`, `filter`, and `remaining`; calls store actions on events. The integration test exercises the acceptance criteria end-to-end.

- [ ] Create the integration test `src/App.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent, within } from '@testing-library/svelte';
import App from './App.svelte';
import { resetStore } from './lib/store';

async function addTodo(getByPlaceholderText: any, getByText: any, text: string) {
  const input = getByPlaceholderText('What needs to be done?');
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.click(getByText('Add'));
}

describe('App (integration)', () => {
  beforeEach(() => {
    localStorage.clear();
    resetStore();
  });

  it('adds a todo and shows it', async () => {
    const { getByPlaceholderText, getByText } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'Buy groceries');
    expect(getByText('Buy groceries')).toBeInTheDocument();
  });

  it('toggles completion and updates remaining count', async () => {
    const { getByPlaceholderText, getByText, getByRole } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'task');
    expect(getByText('1 item left')).toBeInTheDocument();
    await fireEvent.click(getByRole('checkbox'));
    expect(getByText('0 items left')).toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const { getByPlaceholderText, getByText, getByLabelText, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'delete me');
    await fireEvent.click(getByLabelText('Delete'));
    expect(queryByText('delete me')).not.toBeInTheDocument();
  });

  it('filters by active and completed', async () => {
    const { getByPlaceholderText, getByText, getAllByRole, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'a');
    await addTodo(getByPlaceholderText, getByText, 'b');
    await fireEvent.click(getAllByRole('checkbox')[0]); // complete 'a'

    await fireEvent.click(getByText('Active'));
    expect(queryByText('a')).not.toBeInTheDocument();
    expect(getByText('b')).toBeInTheDocument();

    await fireEvent.click(getByText('Completed'));
    expect(getByText('a')).toBeInTheDocument();
    expect(queryByText('b')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const { getByPlaceholderText, getByText, getAllByRole, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'a');
    await addTodo(getByPlaceholderText, getByText, 'b');
    await fireEvent.click(getAllByRole('checkbox')[0]); // complete 'a'
    await fireEvent.click(getByText('Clear completed'));
    expect(queryByText('a')).not.toBeInTheDocument();
    expect(getByText('b')).toBeInTheDocument();
  });

  it('persists todos to localStorage', async () => {
    const { getByPlaceholderText, getByText } = render(App);
    await addTodo(getByPlaceholderText, getByText, 'persisted');
    const stored = JSON.parse(localStorage.getItem('svelte-todos') || '[]');
    expect(stored).toHaveLength(1);
    expect(stored[0].text).toBe('persisted');
  });

  it('shows empty state initially', () => {
    const { getByText } = render(App);
    expect(getByText('Nothing here yet. Add your first todo!')).toBeInTheDocument();
  });
});
```

- [ ] Run the test and watch it fail (App still has scaffold content):

```bash
npm test
```

Expected: failures in `App.test.ts` (placeholder text not found, etc.).

- [ ] Replace `src/App.svelte` entirely with:

```svelte
<script lang="ts">
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
  import FilterBar from './lib/FilterBar.svelte';
  import {
    filteredTodos,
    filter,
    remaining,
    addTodo,
    toggleTodo,
    deleteTodo,
    clearCompleted,
  } from './lib/store';
  import type { Filter } from './lib/types';
</script>

<main>
  <h1>Svelte Todos</h1>

  <TodoInput on:add={(e) => addTodo(e.detail)} />

  <TodoList
    todos={$filteredTodos}
    on:toggle={(e) => toggleTodo(e.detail)}
    on:delete={(e) => deleteTodo(e.detail)}
  />

  <FilterBar
    remaining={$remaining}
    filter={$filter}
    on:setFilter={(e: CustomEvent<Filter>) => filter.set(e.detail)}
    on:clearCompleted={clearCompleted}
  />
</main>

<style>
  main {
    max-