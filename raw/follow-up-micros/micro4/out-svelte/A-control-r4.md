# Svelte Todo List - Implementation Plan

## Overview

We're building a Svelte todo list app with localStorage persistence. This plan assumes you have zero context for the codebase. We'll use Vite + Svelte + TypeScript, with Vitest for testing.

The build order is bottom-up: pure logic first (storage, store), then leaf UI components, then container components, then the App. Each piece is tested before the next is built. TDD throughout: write a failing test, see it fail, implement, see it pass, commit.

## File Structure

| File | Responsibility |
|------|---------------|
| `src/lib/types.ts` | `Todo` interface and `Filter` type (single source of truth) |
| `src/lib/storage.ts` | Read/write todos array to localStorage |
| `src/lib/store.ts` | Svelte writable store of todos + filter; CRUD actions; localStorage sync |
| `src/lib/TodoInput.svelte` | Text input + Add button; emits `add` event |
| `src/lib/TodoItem.svelte` | One todo row: checkbox, text, delete button; emits `toggle`/`delete` |
| `src/lib/TodoList.svelte` | Renders list of `TodoItem`s or empty-state message |
| `src/lib/FilterBar.svelte` | Items-left count, filter buttons, clear-completed button |
| `src/App.svelte` | Wires store to components |
| `src/main.ts` | Mounts `App` |
| `vitest-setup.ts` | jsdom + jest-dom matchers + localStorage reset |

---

## Task 1: Project Scaffold

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `svelte.config.js`, `vitest-setup.ts`, `index.html`, `src/main.ts`, `src/App.svelte`

- [ ] Create the project directory and scaffold with Vite:

```bash
npm create vite@latest svelte-todos -- --template svelte-ts
cd svelte-todos
```

Expected output ends with instructions to run `npm install`.

- [ ] Install runtime and test dependencies:

```bash
npm install
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```

Expected: `added N packages` with no errors.

- [ ] Create `vitest-setup.ts` in the project root:

```typescript
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/svelte';

afterEach(() => {
  cleanup();
  localStorage.clear();
});
```

- [ ] Replace `vite.config.ts` with config that adds the Vitest block:

```typescript
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

- [ ] Add a `test` script to `package.json` in the `"scripts"` block:

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "check": "svelte-check --tsconfig ./tsconfig.json",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] Verify the scaffold builds and the test runner starts (no tests yet):

```bash
npm run test
```

Expected: `No test files found, exiting with code 0` (or similar). This confirms Vitest is wired up.

- [ ] Initialize git and commit:

```bash
git init
git add -A
git commit -m "Scaffold Svelte + TS + Vitest project"
```

---

## Task 2: Types

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

- [ ] Type-check passes:

```bash
npm run check
```

Expected: `svelte-check found 0 errors and 0 warnings`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add Todo and Filter types"
```

---

## Task 3: Storage Module (TDD)

**Files:** `src/lib/storage.test.ts`, `src/lib/storage.ts`

The storage module reads and writes the todos array to localStorage under one key, gracefully handling missing or corrupt data.

- [ ] Write the failing test in `src/lib/storage.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { loadTodos, saveTodos } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('storage', () => {
  it('returns empty array when nothing is stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns empty array when stored value is corrupt', () => {
    localStorage.setItem('svelte-todos', 'not json{');
    expect(loadTodos()).toEqual([]);
  });

  it('returns empty array when stored value is not an array', () => {
    localStorage.setItem('svelte-todos', '{"foo":1}');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- storage
```

Expected: failure with `Failed to resolve import "./storage"` or `loadTodos is not a function`.

- [ ] Implement `src/lib/storage.ts`:

```typescript
import type { Todo } from './types';

const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
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

- [ ] Run the test, see it pass:

```bash
npm run test -- storage
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add localStorage storage module with tests"
```

---

## Task 4: Store Module (TDD)

**Files:** `src/lib/store.test.ts`, `src/lib/store.ts`

The store holds the todos array and the active filter, exposes CRUD actions, persists to localStorage on every change, and exposes a derived count of remaining (incomplete) items.

- [ ] Write the failing test in `src/lib/store.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  filter,
  remainingCount,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
  setFilter,
  resetStore,
} from './store';

beforeEach(() => {
  localStorage.clear();
  resetStore();
});

describe('store', () => {
  it('starts empty with filter "all"', () => {
    expect(get(todos)).toEqual([]);
    expect(get(filter)).toBe('all');
  });

  it('adds a todo with generated id, given text, not completed', () => {
    addTodo('Buy groceries');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy groceries');
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

  it('toggles completion', () => {
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
    const [first, second] = get(todos);
    toggleTodo(first.id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].id).toBe(second.id);
  });

  it('counts remaining (incomplete) todos', () => {
    addTodo('a');
    addTodo('b');
    expect(get(remainingCount)).toBe(2);
    toggleTodo(get(todos)[0].id);
    expect(get(remainingCount)).toBe(1);
  });

  it('persists todos to localStorage on add', () => {
    addTodo('persist me');
    const raw = localStorage.getItem('svelte-todos');
    expect(raw).toContain('persist me');
  });

  it('setFilter updates the filter store', () => {
    setFilter('active');
    expect(get(filter)).toBe('active');
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- store
```

Expected: failure resolving `./store`.

- [ ] Implement `src/lib/store.ts`:

```typescript
import { writable, derived, get } from 'svelte/store';
import type { Todo, Filter } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());
export const filter = writable<Filter>('all');

todos.subscribe((value) => saveTodos(value));

export const remainingCount = derived(todos, ($todos) =>
  $todos.filter((t) => !t.completed).length
);

function createId(): string {
  return crypto.randomUUID();
}

export function addTodo(text: string): void {
  const trimmed = text.trim();
  if (!trimmed) return;
  todos.update((list) => [
    ...list,
    { id: createId(), text: trimmed, completed: false },
  ]);
}

export function toggleTodo(id: string): void {
  todos.update((list) =>
    list.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
  );
}

export function deleteTodo(id: string): void {
  todos.update((list) => list.filter((t) => t.id !== id));
}

export function clearCompleted(): void {
  todos.update((list) => list.filter((t) => !t.completed));
}

export function setFilter(value: Filter): void {
  filter.set(value);
}

// Test helper: reset stores to a clean initial state.
export function resetStore(): void {
  todos.set([]);
  filter.set('all');
}
```

> Note: `crypto.randomUUID()` is available in jsdom and modern browsers. If your jsdom version lacks it, the test for id generation will reveal it.

- [ ] Run the test, see it pass:

```bash
npm run test -- store
```

Expected: `10 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add todos store with CRUD, persistence, and derived count"
```

---

## Task 5: TodoInput Component (TDD)

**Files:** `src/lib/TodoInput.test.ts`, `src/lib/TodoInput.svelte`

A controlled text input plus an Add button. Dispatches an `add` event with the text, and clears itself. Add on Enter key or button click.

- [ ] Write the failing test in `src/lib/TodoInput.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add with typed text on button click', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoInput);
    component.$on('add', (e) => handler(e.detail));

    await user.type(screen.getByRole('textbox'), 'New task');
    await user.click(screen.getByRole('button', { name: /add/i }));

    expect(handler).toHaveBeenCalledWith('New task');
  });

  it('dispatches add on Enter key', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoInput);
    component.$on('add', (e) => handler(e.detail));

    await user.type(screen.getByRole('textbox'), 'Enter task{Enter}');

    expect(handler).toHaveBeenCalledWith('Enter task');
  });

  it('clears the input after adding', async () => {
    const user = userEvent.setup();
    render(TodoInput);
    const input = screen.getByRole('textbox') as HTMLInputElement;

    await user.type(input, 'Clear me{Enter}');

    expect(input.value).toBe('');
  });

  it('does not dispatch when input is empty', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoInput);
    component.$on('add', (e) => handler(e.detail));

    await user.click(screen.getByRole('button', { name: /add/i }));

    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- TodoInput
```

Expected: failure resolving `./TodoInput.svelte`.

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

  function onKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') submit();
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
  }
</style>
```

- [ ] Run the test, see it pass:

```bash
npm run test -- TodoInput
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoInput component with tests"
```

---

## Task 6: TodoItem Component (TDD)

**Files:** `src/lib/TodoItem.test.ts`, `src/lib/TodoItem.svelte`

A single row: a checkbox reflecting `completed`, the todo text, and a delete button. Dispatches `toggle` and `delete` with the todo id.

- [ ] Write the failing test in `src/lib/TodoItem.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders the todo text', () => {
    render(TodoItem, { todo });
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
  });

  it('checkbox reflects completed state', () => {
    render(TodoItem, { todo: { ...todo, completed: true } });
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('dispatches toggle with id when checkbox clicked', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoItem, { todo });
    component.$on('toggle', (e) => handler(e.detail));

    await user.click(screen.getByRole('checkbox'));

    expect(handler).toHaveBeenCalledWith('abc');
  });

  it('dispatches delete with id when delete button clicked', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoItem, { todo });
    component.$on('delete', (e) => handler(e.detail));

    await user.click(screen.getByRole('button', { name: /delete/i }));

    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- TodoItem
```

Expected: failure resolving `./TodoItem.svelte`.

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
    on:click={() => dispatch('delete', todo.id)}>x</button
  >
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
  .delete {
    border: none;
    background: none;
    cursor: pointer;
  }
</style>
```

- [ ] Run the test, see it pass:

```bash
npm run test -- TodoItem
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoItem component with tests"
```

---

## Task 7: TodoList Component (TDD)

**Files:** `src/lib/TodoList.test.ts`, `src/lib/TodoList.svelte`

Renders a `TodoItem` per todo, or an empty-state message when the list is empty. Forwards `toggle` and `delete` events upward.

- [ ] Write the failing test in `src/lib/TodoList.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'Buy groceries', completed: false },
  { id: '2', text: 'Walk the dog', completed: true },
];

describe('TodoList', () => {
  it('renders one item per todo', () => {
    render(TodoList, { todos });
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
  });

  it('shows empty-state message when no todos', () => {
    render(TodoList, { todos: [] });
    expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
  });

  it('forwards toggle event from a child item', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoList, { todos });
    component.$on('toggle', (e) => handler(e.detail));

    await user.click(screen.getAllByRole('checkbox')[0]);

    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete event from a child item', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(TodoList, { todos });
    component.$on('delete', (e) => handler(e.detail));

    await user.click(screen.getAllByRole('button', { name: /delete/i })[0]);

    expect(handler).toHaveBeenCalledWith('1');
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- TodoList
```

Expected: failure resolving `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:

```svelte
<script lang="ts">
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './types';

  export let todos: Todo[];
</script>

{#if todos.length === 0}
  <p class="empty">Nothing here yet — add your first todo above!</p>
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
    color: #888;
    padding: 1rem 0;
  }
</style>
```

> Note: `on:toggle` and `on:delete` with no handler forward the child's events to the parent.

- [ ] Run the test, see it pass:

```bash
npm run test -- TodoList
```

Expected: `4 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add TodoList component with empty state and tests"
```

---

## Task 8: FilterBar Component (TDD)

**Files:** `src/lib/FilterBar.test.ts`, `src/lib/FilterBar.svelte`

Shows "X items left", the three filter buttons (highlighting the active one), and a "Clear completed" button. Dispatches `filter` (with the chosen `Filter`) and `clear` events.

- [ ] Write the failing test in `src/lib/FilterBar.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows the remaining count', () => {
    render(FilterBar, { remaining: 2, current: 'all' });
    expect(screen.getByText(/2 items left/i)).toBeInTheDocument();
  });

  it('uses singular "item" for a count of 1', () => {
    render(FilterBar, { remaining: 1, current: 'all' });
    expect(screen.getByText(/1 item left/i)).toBeInTheDocument();
  });

  it('marks the current filter button as active', () => {
    render(FilterBar, { remaining: 0, current: 'active' });
    expect(screen.getByRole('button', { name: 'Active' })).toHaveClass('active');
  });

  it('dispatches filter when a filter button is clicked', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(FilterBar, { remaining: 0, current: 'all' });
    component.$on('filter', (e) => handler(e.detail));

    await user.click(screen.getByRole('button', { name: 'Completed' }));

    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clear when clear button is clicked', async () => {
    const user = userEvent.setup();
    const handler = vi.fn();
    const { component } = render(FilterBar, { remaining: 0, current: 'all' });
    component.$on('clear', handler);

    await user.click(screen.getByRole('button', { name: /clear completed/i }));

    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- FilterBar
```

Expected: failure resolving `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let remaining: number;
  export let current: Filter;

  const dispatch = createEventDispatcher<{ filter: Filter; clear: void }>();

  const filters: Filter[] = ['all', 'active', 'completed'];

  function label(f: Filter): string {
    return f.charAt(0).toUpperCase() + f.slice(1);
  }
</script>

<div class="filter-bar">
  <span class="count">{remaining} {remaining === 1 ? 'item' : 'items'} left</span>

  <div class="filters">
    {#each filters as f}
      <button
        class:active={current === f}
        on:click={() => dispatch('filter', f)}>{label(f)}</button
      >
    {/each}
  </div>

  <button class="clear" on:click={() => dispatch('clear')}>Clear completed</button>
</div>

<style>
  .filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: wrap;
    padding-top: 0.5rem;
  }
  .filters button.active {
    font-weight: bold;
    text-decoration: underline;
  }
</style>
```

- [ ] Run the test, see it pass:

```bash
npm run test -- FilterBar
```

Expected: `5 passed`.

- [ ] Commit:

```bash
git add -A
git commit -m "Add FilterBar component with tests"
```

---

## Task 9: App Integration (TDD)

**Files:** `src/App.test.ts`, `src/App.svelte`

`App` wires the store to the components: derives the visible todos from `todos` + `filter`, and dispatches store actions in response to component events. This is an integration test covering the acceptance criteria end-to-end.

- [ ] Write the failing test in `src/App.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import App from './App.svelte';
import { resetStore } from './lib/store';

beforeEach(() => {
  localStorage.clear();
  resetStore();
});

async function addTodo(user: ReturnType<typeof userEvent.setup>, text: string) {
  await user.type(screen.getByRole('textbox'), `${text}{Enter}`);
}

describe('App integration', () => {
  it('adds a todo and shows it', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'Buy groceries');
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
  });

  it('shows correct remaining count', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'a');
    await addTodo(user, 'b');
    expect(screen.getByText(/2 items left/i)).toBeInTheDocument();
  });

  it('toggles a todo and updates the count', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'a');
    await user.click(screen.getByRole('checkbox'));
    expect(screen.getByText(/0 items left/i)).toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'delete me');
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(screen.queryByText('delete me')).not.toBeInTheDocument();
  });

  it('filters to active todos only', async () => {
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

  it('filters to completed todos only', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'active one');
    await addTodo(user, 'done one');
    await user.click(screen.getAllByRole('checkbox')[1]);
    await user.click(screen.getByRole('button', { name: 'Completed' }));
    expect(screen.getByText('done one')).toBeInTheDocument();
    expect(screen.queryByText('active one')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'keep me');
    await addTodo(user, 'remove me');
    await user.click(screen.getAllByRole('checkbox')[1]);
    await user.click(screen.getByRole('button', { name: /clear completed/i }));
    expect(screen.getByText('keep me')).toBeInTheDocument();
    expect(screen.queryByText('remove me')).not.toBeInTheDocument();
  });

  it('persists todos to localStorage', async () => {
    const user = userEvent.setup();
    render(App);
    await addTodo(user, 'persist me');
    expect(localStorage.getItem('svelte-todos')).toContain('persist me');
  });
});
```

- [ ] Run the test, see it fail:

```bash
npm run test -- App
```

Expected: failures because `App.svelte` is still the Vite default template.

- [ ] Replace `src/App.svelte`:

```svelte
<script lang="ts">
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
  import FilterBar from './lib/FilterBar.svelte';
  import {
    todos,
    filter,
    remainingCount,
    addTodo,
    toggleTodo,
    deleteTodo,
    clearCompleted,
    setFilter,
  } from './lib/store';
  import type { Todo, Filter } from './lib/types';

  let visible: Todo[] = [];
  $: visible = $todos.filter((t) => {
    if ($filter === 'active') return !t.completed;
    if ($filter === 'completed') return t.completed;
    return true;
  });
</script>

<main>
  <h1>Svelte Todos</h1>

  <TodoInput on:add={(e) => addTodo(e.detail)} />

  <TodoList
    todos={visible}
    on:toggle={(e) => toggleTodo(e.detail)}
    on:delete={(e) => deleteTodo(e.detail)}
  />

  <FilterBar
    remaining={$remainingCount}
    current={$filter}
    on:filter={(e) => setFilter(e.detail as Filter)}
    on:clear={clearCompleted}
  />
</main>

<style>
  main {
    max-width: 480px;
    margin: 2rem auto;
    font-family: system-ui, sans-serif;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
  }
  h1 {
    font-size: 1.5rem;
    margin-top: 0;
  }
</style>
```

- [ ] Run the test, see it pass:

```bash
npm run test -- App
```

Expected: `8 passed`.

- [ ] Run the full suite and type-check:

```bash
npm run test && npm run check
```

Expected: all test files pass (storage 4, store 10, TodoInput 4, TodoItem 4, TodoList 4, FilterBar 5, App 8), and `svelte-check found 0 errors`.

- [ ] Commit:

```bash
git add -A
git commit -m "Wire App to store; integration tests cover acceptance criteria"
```

---

## Task 10: Manual Smoke Test & Cleanup

**Files:** `src/main.ts` (verify only), delete leftover scaffold assets

- [ ] Confirm `src/main.ts` mounts `App` (Vite's default does this; verify it reads):

```typescript
import './app.css';
import App from './App.svelte';

const app = new App({ target: document.getElementById('app')! });

export default app;
```

If `app.css` does not exist, create an empty one or remove the import.

- [ ] Remove unused scaffold assets if present (the default counter component and svelte logo):

```bash
rm -f src/lib/Counter.svelte src/assets/svelte.svg
```

(No error if they don't exist — that's fine.)

- [ ] Run the dev server and manually verify each acceptance criterion in the browser:

```bash
npm run dev
```

Open the printed `localhost` URL and confirm:
1. Type "Buy groceries" + Enter → appears in list.
2. Click its checkbox → text gets strikethrough, count drops.
3. Click X → row disappears.
4. Add a few, complete one, click All/Active/Completed → correct subsets show.
5. Count text reads "N items left" (singular at 1).
6. Click "Clear