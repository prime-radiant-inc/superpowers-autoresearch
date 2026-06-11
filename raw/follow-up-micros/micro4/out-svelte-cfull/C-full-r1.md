# Svelte Todo List - Implementation Plan

## Global Constraints

- Framework: Svelte with TypeScript
- Build tool: Vite (via `npm create vite@latest`, template `svelte-ts`)
- Test runner: Vitest with `@testing-library/svelte` and `jsdom`
- Data model: `Todo { id: string; text: string; completed: boolean }`, `Filter = 'all' | 'active' | 'completed'`
- IDs generated via `crypto.randomUUID()`
- localStorage key: `svelte-todos`
- All tests must pass before plan is complete

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte writable store + actions (add/toggle/delete/clearCompleted) |
| `src/lib/TodoInput.svelte` | Text input + Add button, emits `add` event |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button; emits `toggle`/`delete` |
| `src/lib/TodoList.svelte` | Renders list of `TodoItem` or empty state |
| `src/lib/FilterBar.svelte` | Items-left count, filter buttons, clear-completed button |
| `src/App.svelte` | Wires store + components together |
| `vitest.config.ts` | Vitest config with jsdom |
| `src/setupTests.ts` | Testing-library cleanup |

---

### Task 1: Project scaffold and test infrastructure

**Files:** `package.json`, `vitest.config.ts`, `src/setupTests.ts`, `src/lib/smoke.test.ts`

**Interfaces:**
- Produces: a runnable `npm test` command using Vitest + jsdom + `@testing-library/svelte`.

- [ ] Scaffold the project (run in an empty parent directory):
```bash
npm create vite@latest svelte-todos -- --template svelte-ts
cd svelte-todos
npm install
```
Expected: `svelte-todos/` created with `src/App.svelte`, `package.json`.

- [ ] Install test dependencies:
```bash
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```
Expected: dependencies added to `package.json` devDependencies.

- [ ] Create `vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: false })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
});
```

- [ ] Create `src/setupTests.ts`:
```ts
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';

afterEach(() => cleanup());
```

- [ ] Add the test script to `package.json` `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] Write a smoke test at `src/lib/smoke.test.ts`:
```ts
import { describe, it, expect } from 'vitest';

describe('smoke', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] Run the test to confirm infrastructure works:
```bash
npm test
```
Expected: `1 passed` for `src/lib/smoke.test.ts`.

- [ ] Delete the smoke test:
```bash
rm src/lib/smoke.test.ts
```

- [ ] Commit:
```bash
git add -A && git commit -m "Scaffold Svelte project with Vitest test infrastructure"
```

---

### Task 2: Types and storage module

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Produces:
  - `src/lib/types.ts`: `interface Todo { id: string; text: string; completed: boolean }`, `type Filter = 'all' | 'active' | 'completed'`
  - `src/lib/storage.ts`: `loadTodos(): Todo[]`, `saveTodos(todos: Todo[]): void`, constant `STORAGE_KEY = 'svelte-todos'`

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
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos, STORAGE_KEY } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

describe('storage', () => {
  beforeEach(() => localStorage.clear());

  it('returns empty array when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('uses the correct storage key', () => {
    saveTodos(sample);
    expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
  });

  it('returns empty array on corrupt data', () => {
    localStorage.setItem(STORAGE_KEY, 'not json');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run the test to see it fail:
```bash
npm test src/lib/storage.test.ts
```
Expected: failure — `loadTodos`/`saveTodos` not found.

- [ ] Implement `src/lib/storage.ts`:
```ts
import type { Todo } from './types';

export const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
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
npm test src/lib/storage.test.ts
```
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add types and localStorage persistence module"
```

---

### Task 3: Todo store with actions

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo`, `Filter` from `./types`; `loadTodos`, `saveTodos` from `./storage`.
- Produces `src/lib/store.ts`:
  - `todos`: a Svelte writable store of `Todo[]`, initialized from `loadTodos()`, auto-persists via subscription.
  - `filter`: a Svelte writable store of `Filter`, initial value `'all'`.
  - `addTodo(text: string): void` — ignores empty/whitespace-only text; trims; new todo `completed: false`, id from `crypto.randomUUID()`.
  - `toggleTodo(id: string): void`
  - `deleteTodo(id: string): void`
  - `clearCompleted(): void`

- [ ] Write failing test `src/lib/store.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  filter,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
} from './store';

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
  filter.set('all');
});

describe('store', () => {
  it('adds a trimmed todo', () => {
    addTodo('  hello  ');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('hello');
    expect(list[0].completed).toBe(false);
    expect(typeof list[0].id).toBe('string');
  });

  it('ignores empty/whitespace text', () => {
    addTodo('   ');
    addTodo('');
    expect(get(todos)).toHaveLength(0);
  });

  it('toggles completion', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deletes a todo', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  it('clears completed todos', () => {
    addTodo('a');
    addTodo('b');
    const [first] = get(todos);
    toggleTodo(first.id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('persists to localStorage on change', () => {
    addTodo('persist me');
    expect(localStorage.getItem('svelte-todos')).toContain('persist me');
  });
});
```

- [ ] Run the test to see it fail:
```bash
npm test src/lib/store.test.ts
```
Expected: failure — `./store` exports not found.

- [ ] Implement `src/lib/store.ts`:
```ts
import { writable } from 'svelte/store';
import type { Todo, Filter } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());
export const filter = writable<Filter>('all');

todos.subscribe((value) => saveTodos(value));

export function addTodo(text: string): void {
  const trimmed = text.trim();
  if (!trimmed) return;
  todos.update((list) => [
    ...list,
    { id: crypto.randomUUID(), text: trimmed, completed: false },
  ]);
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
npm test src/lib/store.test.ts
```
Expected: `6 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add todo store with add/toggle/delete/clearCompleted actions"
```

---

### Task 4: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Produces `src/lib/TodoInput.svelte`: dispatches a custom event `add` with `event.detail` set to the entered string. Clears the input after dispatch. Adds on Add-button click and on Enter keydown. Does not dispatch when the input is empty/whitespace.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add on button click and clears input', async () => {
    const { getByRole, getByPlaceholderText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'New task' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));

    expect(handler).toHaveBeenCalledWith('New task');
    expect(input.value).toBe('');
  });

  it('dispatches add on Enter key', async () => {
    const { getByPlaceholderText, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Via enter' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Via enter');
  });

  it('does not dispatch when empty', async () => {
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
npm test src/lib/TodoInput.test.ts
```
Expected: failure — cannot find `TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ add: string }>();
  let value = '';

  function submit() {
    if (!value.trim()) return;
    dispatch('add', value);
    value = '';
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') submit();
  }
</script>

<div class="todo-input">
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value
    on:keydown={onKeydown}
  />
  <button on:click={submit}>Add</button>
</div>
```

- [ ] Run the test to see it pass:
```bash
npm test src/lib/TodoInput.test.ts
```
Expected: `3 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 5: TodoItem component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`.
- Produces `src/lib/TodoItem.svelte`: prop `todo: Todo`. Renders a checkbox reflecting `todo.completed`, the text, and a delete button labeled `×` (accessible name `Delete`). Dispatches `toggle` with `event.detail = todo.id` on checkbox change, and `delete` with `event.detail = todo.id` on delete-button click.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';

const todo = { id: 'abc', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders text and unchecked checkbox', () => {
    const { getByText, getByRole } = render(TodoItem, { props: { todo } });
    expect(getByText('Walk the dog')).toBeInTheDocument();
    expect((getByRole('checkbox') as HTMLInputElement).checked).toBe(false);
  });

  it('reflects completed state', () => {
    const { getByRole } = render(TodoItem, {
      props: { todo: { ...todo, completed: true } },
    });
    expect((getByRole('checkbox') as HTMLInputElement).checked).toBe(true);
  });

  it('dispatches toggle with id', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(getByRole('checkbox'));
    expect(handler).toHaveBeenCalledWith('abc');
  });

  it('dispatches delete with id', async () => {
    const { getByRole, component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Delete' }));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run the test to see it fail:
```bash
npm test src/lib/TodoItem.test.ts
```
Expected: failure — cannot find `TodoItem.svelte`.

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
    ×
  </button>
</li>
```

- [ ] Run the test to see it pass:
```bash
npm test src/lib/TodoItem.test.ts
```
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 6: TodoList component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`; `TodoItem.svelte`.
- Produces `src/lib/TodoList.svelte`: prop `todos: Todo[]`. Renders a `TodoItem` per todo. When `todos` is empty, renders an empty-state message `No todos yet. Add one above!`. Forwards child `toggle` and `delete` events upward (re-dispatches with same detail).

- [ ] Write failing test `src/lib/TodoList.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';

const todos = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

describe('TodoList', () => {
  it('renders an item per todo', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('a')).toBeInTheDocument();
    expect(getByText('b')).toBeInTheDocument();
  });

  it('shows empty state when no todos', () => {
    const { getByText } = render(TodoList, { props: { todos: [] } });
    expect(getByText('No todos yet. Add one above!')).toBeInTheDocument();
  });

  it('forwards toggle events', async () => {
    const { getAllByRole, component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete events', async () => {
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
npm test src/lib/TodoList.test.ts
```
Expected: failure — cannot find `TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:
```svelte
<script lang="ts">
  import type { Todo } from './types';
  import TodoItem from './TodoItem.svelte';

  export let todos: Todo[];
</script>

{#if todos.length === 0}
  <p class="empty-state">No todos yet. Add one above!</p>
{:else}
  <ul class="todo-list">
    {#each todos as todo (todo.id)}
      <TodoItem {todo} on:toggle on:delete />
    {/each}
  </ul>
{/if}
```

- [ ] Run the test to see it pass:
```bash
npm test src/lib/TodoList.test.ts
```
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 7: FilterBar component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` from `./types`.
- Produces `src/lib/FilterBar.svelte`: props `filter: Filter`, `remaining: number`. Renders `{remaining} items left`, three filter buttons labeled `All`/`Active`/`Completed` (active one gets class `active`), and a `Clear completed` button. Dispatches `setFilter` with `event.detail` = the chosen `Filter`, and `clearCompleted` (no detail) on the clear button.

- [ ] Write failing test `src/lib/FilterBar.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows remaining count', () => {
    const { getByText } = render(FilterBar, {
      props: { filter: 'all', remaining: 2 },
    });
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    const { getByRole } = render(FilterBar, {
      props: { filter: 'active', remaining: 0 },
    });
    expect(getByRole('button', { name: 'Active' })).toHaveClass('active');
  });

  it('dispatches setFilter with chosen filter', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { filter: 'all', remaining: 0 },
    });
    const handler = vi.fn();
    component.$on('setFilter', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clearCompleted', async () => {
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
npm test src/lib/FilterBar.test.ts
```
Expected: failure — cannot find `FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let filter: Filter;
  export let remaining: number;

  const dispatch = createEventDispatcher<{
    setFilter: Filter;
    clearCompleted: void;
  }>();

  const filters: Filter[] = ['all', 'active', 'completed'];
  const label: Record<Filter, string> = {
    all: 'All',
    active: 'Active',
    completed: 'Completed',
  };
</script>

<div class="filter-bar">
  <span class="count">{remaining} items left</span>
  <div class="filters">
    {#each filters as f}
      <button class:active={filter === f} on:click={() => dispatch('setFilter', f)}>
        {label[f]}
      </button>
    {/each}
  </div>
  <button class="clear" on:click={() => dispatch('clearCompleted')}>
    Clear completed
  </button>
</div>
```

- [ ] Run the test to see it pass:
```bash
npm test src/lib/FilterBar.test.ts
```
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 8: App integration

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: `todos`, `filter`, `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted` from `./lib/store`; `TodoInput`, `TodoList`, `FilterBar` components; `Todo`, `Filter` from `./lib/types`.
- Produces: the wired application. Computes `visibleTodos` from `filter`, and `remaining` = count of incomplete todos. Heading text `Svelte Todos`.

- [ ] Write failing integration test `src/App.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import App from './App.svelte';
import { todos, filter } from './lib/store';

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
  filter.set('all');
});

async function addTodo(getByPlaceholderText: any, getByRole: any, text: string) {
  const input = getByPlaceholderText('What needs to be done?');
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.click(getByRole('button', { name: 'Add' }));
}

describe('App', () => {
  it('renders heading', () => {
    const { getByText } = render(App);
    expect(getByText('Svelte Todos')).toBeInTheDocument();
  });

  it('adds a todo and updates count', async () => {
    const { getByPlaceholderText, getByRole, getByText } = render(App);
    await addTodo(getByPlaceholderText, getByRole, 'Buy milk');
    expect(getByText('Buy milk')).toBeInTheDocument();
    expect(getByText('1 items left')).toBeInTheDocument();
  });

  it('toggles a todo and updates count', async () => {
    const { getByPlaceholderText, getByRole, getByText } = render(App);
    await addTodo(getByPlaceholderText, getByRole, 'Task');
    await fireEvent.click(getByRole('checkbox'));
    expect(getByText('0 items left')).toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const { getByPlaceholderText, getByRole, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByRole, 'Delete me');
    await fireEvent.click(getByRole('button', { name: 'Delete' }));
    expect(queryByText('Delete me')).not.toBeInTheDocument();
  });

  it('filters to active and completed', async () => {
    const { getByPlaceholderText, getByRole, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByRole, 'Active task');
    await addTodo(getByPlaceholderText, getByRole, 'Done task');
    const checkboxes = () => document.querySelectorAll('input[type=checkbox]');
    await fireEvent.click(checkboxes()[1]);

    await fireEvent.click(getByRole('button', { name: 'Active' }));
    expect(queryByText('Active task')).toBeInTheDocument();
    expect(queryByText('Done task')).not.toBeInTheDocument();

    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(queryByText('Done task')).toBeInTheDocument();
    expect(queryByText('Active task')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const { getByPlaceholderText, getByRole, queryByText } = render(App);
    await addTodo(getByPlaceholderText, getByRole, 'Keep');
    await addTodo(getByPlaceholderText, getByRole, 'Remove');
    const checkboxes = document.querySelectorAll('input[type=checkbox]');
    await fireEvent.click(checkboxes[1]);
    await fireEvent.click(getByRole('button', { name: 'Clear completed' }));
    expect(queryByText('Keep')).toBeInTheDocument();
    expect(queryByText('Remove')).not.toBeInTheDocument();
  });
});
```

- [ ] Run the test to see it fail:
```bash
npm test src/App.test.ts
```
Expected: failure — App does not render todo UI.

- [ ] Implement `src/App.svelte`:
```svelte
<script lang="ts">
  import {
    todos,
    filter,
    addTodo,
    toggleTodo,
    deleteTodo,
    clearCompleted,
  } from './lib/store';
  import type { Todo } from './lib/types';
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
  import FilterBar from './lib/FilterBar.svelte';

  $: visibleTodos = $todos.filter((t: Todo) => {
    if ($filter === 'active') return !t.completed;
    if ($filter === 'completed') return t.completed;
    return true;
  });

  $: remaining = $todos.filter((t: Todo) => !t.completed).length;
</script>

<main class="app">
  <h1>Svelte Todos</h1>
  <TodoInput on:add={(e) => addTodo(e.detail)} />
  <TodoList
    todos={visibleTodos}
    on:toggle={(e) => toggleTodo(e.detail)}
    on:delete={(e) => deleteTodo(e.detail)}
  />
  <FilterBar
    filter={$filter}
    {remaining}
    on:setFilter={(e) => filter.set(e.detail)}
    on:clearCompleted={clearCompleted}
  />
</main>

<style>
  .app {
    max-width: 480px;
    margin: 2rem auto;
    font-family: sans-serif;
  }
</style>
```

- [ ] Run the test to see it pass:
```bash
npm test src/App.test.ts
```
Expected: `6 passed`.

- [ ] Run the full suite:
```bash
npm test
```
Expected: all test files pass (storage 4, store 6, TodoInput 3, TodoItem 4, TodoList 4, FilterBar 4, App 6).

- [ ] Verify the dev server starts and renders:
```bash
npm run dev
```
Expected: Vite serves the app; opening the URL shows "Svelte Todos" with input, list, and filter bar. Stop with Ctrl-C.

- [ ] Commit:
```bash
git add -A && git commit -m "Wire App integrating store and all components"
```

---

## Self-Review

- **Spec coverage:**
  1. Add via Enter or Add button — Task 4 tests both; App wires `add`. ✓
  2. Toggle completion — Task 5/8. ✓
  3. Delete via X — Task 5 (`×`, aria-label `Delete`) / Task 8. ✓
  4. Filter subsets — Task 8 `filters to active and completed` test. ✓
  5. "X items left" — Task 7/8 (`remaining`). ✓
  6. Clear completed — Task 3/7/8. ✓
  7. localStorage persistence — Task 2/3 (`todos.subscribe` → `saveTodos`). ✓
  8. Empty state message — Task 6. ✓
  9. All tests pass — final suite run in Task 8. ✓
- **Placeholder scan:** No TODOs or stub bodies; all code blocks complete.
- **Type consistency:** `Todo`/`Filter` defined once in `types.ts` and imported everywhere; event detail types match between dispatch (`createEventDispatcher<{...}>`) and consumers (`e.detail`); `STORAGE_KEY = 'svelte-todos'` consistent across storage module and store test assertions.
- **Note:** The "X items left" copy uses `items` unconditionally per the spec mockup (`2 items left`); no pluralization required by the spec.