# Svelte Todo List - Implementation Plan

## Overview

We are building a todo list app in Svelte + TypeScript with localStorage persistence. The app uses Vite for tooling and Vitest for unit tests. We build bottom-up: storage layer → store → presentational components → app wiring.

This plan assumes **zero prior context**. Every file path, command, and expected output is spelled out.

## Tech Stack Decisions

- **Svelte 4** with **Vite** (`npm create vite@latest`, the `svelte-ts` template).
- **Vitest** + **@testing-library/svelte** + **jsdom** for tests.
- **crypto.randomUUID()** for IDs (built into modern browsers and Node 19+/jsdom).

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/types.ts` | `Todo` interface and `Filter` type. Single source of truth for shared types. |
| `src/lib/storage.ts` | Load/save the todo array to localStorage. Pure persistence, no Svelte. |
| `src/lib/store.ts` | Svelte writable store holding todos + a filter store; action functions (add/toggle/delete/clearCompleted). Wires storage. |
| `src/lib/TodoInput.svelte` | Text input + Add button. Emits an `add` event with the text. |
| `src/lib/TodoItem.svelte` | Single todo row: checkbox, text, delete button. Emits `toggle` and `delete` events. |
| `src/lib/TodoList.svelte` | Renders the list of `TodoItem`s, or an empty-state message. Forwards events. |
| `src/lib/FilterBar.svelte` | "X items left" count, filter buttons, clear-completed button. Emits `setFilter` and `clearCompleted`. |
| `src/App.svelte` | Top-level: subscribes to stores, computes filtered list, wires all components to store actions. |
| `src/main.ts` | Vite entry point (created by template; we mount `App`). |
| Test files | One `*.test.ts` colocated per logic/component file. |

---

### Task 1: Project scaffold and test harness

**Files:** `package.json`, `vite.config.ts`, `vitest-setup.ts`, `tsconfig.json`, `src/lib/sanity.test.ts` (temporary)

- [ ] Scaffold the Vite Svelte-TS project in the current directory:

```bash
npm create vite@latest . -- --template svelte-ts
```

If prompted that the directory is not empty, choose **"Ignore files and continue"**. Expected: a `src/` directory, `package.json`, `vite.config.ts` appear.

- [ ] Install base dependencies:

```bash
npm install
```

Expected: `node_modules/` created, exit code 0.

- [ ] Install test tooling:

```bash
npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @testing-library/user-event
```

Expected: packages added to `devDependencies`, exit code 0.

- [ ] Create `vitest-setup.ts` in the project root:

```ts
import '@testing-library/jest-dom/vitest';
```

- [ ] Replace `vite.config.ts` with test configuration:

```ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest-setup.ts'],
    include: ['src/**/*.test.ts'],
  },
});
```

- [ ] Add a `test` script to `package.json`. Inside the `"scripts"` block add:

```json
"test": "vitest run"
```

- [ ] Create a temporary sanity test `src/lib/sanity.test.ts`:

```ts
import { describe, it, expect } from 'vitest';

describe('sanity', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] Run the test suite:

```bash
npm test
```

Expected output includes:

```
✓ src/lib/sanity.test.ts (1 test)
Test Files  1 passed (1)
```

- [ ] Delete the sanity test and remove the template's demo files we won't use:

```bash
rm src/lib/sanity.test.ts src/lib/Counter.svelte src/assets/svelte.svg
```

(If any file does not exist, that is fine — continue.)

- [ ] Commit:

```bash
git add -A && git commit -m "Scaffold Svelte+TS project with Vitest"
```

---

### Task 2: Shared types

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

- [ ] Type-check (no test needed for type-only file):

```bash
npx tsc --noEmit -p tsconfig.json
```

Expected: exit code 0, no output. (If `tsconfig.json` references project options that error, ignore unrelated template warnings; this file must not introduce errors.)

- [ ] Commit:

```bash
git add -A && git commit -m "Add shared Todo and Filter types"
```

---

### Task 3: Storage layer (localStorage persistence)

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

- [ ] Write the failing test `src/lib/storage.test.ts`:

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('returns empty array when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('returns empty array when stored data is corrupt', () => {
    localStorage.setItem('svelte-todos', 'not json{');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failure because `./storage` cannot be resolved / functions are undefined.

- [ ] Implement `src/lib/storage.ts`:

```ts
import type { Todo } from './types';

const STORAGE_KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
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
npm test
```

Expected:

```
✓ src/lib/storage.test.ts (3 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add localStorage persistence layer"
```

---

### Task 4: Todo store with actions

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

The store holds the canonical todo array and a separate filter value. Actions mutate the store and persist via `storage.ts`. We use `get(store)` from `svelte/store` in tests to read values.

- [ ] Write the failing test `src/lib/store.test.ts`:

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
  remainingCount,
} from './store';

describe('store', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
    filter.set('all');
  });

  it('addTodo appends a todo with text, incomplete, and an id', () => {
    addTodo('Buy milk');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy milk');
    expect(list[0].completed).toBe(false);
    expect(typeof list[0].id).toBe('string');
    expect(list[0].id.length).toBeGreaterThan(0);
  });

  it('addTodo ignores empty/whitespace text', () => {
    addTodo('   ');
    addTodo('');
    expect(get(todos)).toHaveLength(0);
  });

  it('addTodo trims surrounding whitespace', () => {
    addTodo('  hello  ');
    expect(get(todos)[0].text).toBe('hello');
  });

  it('toggleTodo flips completed by id', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deleteTodo removes by id', () => {
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
    const firstId = get(todos)[0].id;
    toggleTodo(firstId);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('remainingCount counts incomplete todos', () => {
    addTodo('a');
    addTodo('b');
    const firstId = get(todos)[0].id;
    toggleTodo(firstId);
    expect(get(remainingCount)).toBe(1);
  });

  it('persists changes to localStorage', () => {
    addTodo('persist me');
    const raw = localStorage.getItem('svelte-todos');
    expect(raw).toContain('persist me');
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failure resolving `./store`.

- [ ] Implement `src/lib/store.ts`:

```ts
import { writable, derived } from 'svelte/store';
import type { Todo, Filter } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());
export const filter = writable<Filter>('all');

// Persist on every change.
todos.subscribe((value) => {
  saveTodos(value);
});

export const remainingCount = derived(todos, ($todos) =>
  $todos.filter((t) => !t.completed).length
);

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
    list.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
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
npm test
```

Expected:

```
✓ src/lib/store.test.ts (8 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add todo store with add/toggle/delete/clear actions"
```

---

### Task 5: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

`TodoInput` is purely presentational: it dispatches an `add` event with the text and clears its own field. It does **not** talk to the store directly.

- [ ] Write the failing test `src/lib/TodoInput.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add event with text when Add clicked', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'New task' } });
    await fireEvent.click(getByRole('button', { name: /add/i }));

    expect(handler).toHaveBeenCalledWith('New task');
  });

  it('dispatches add event when Enter pressed', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = getByRole('textbox');
    await fireEvent.input(input, { target: { value: 'Enter task' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Enter task');
  });

  it('clears the input after dispatching', async () => {
    const { getByRole } = render(TodoInput);
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Clear me' } });
    await fireEvent.click(getByRole('button', { name: /add/i }));
    expect(input.value).toBe('');
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failure resolving `./TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ add: string }>();
  let text = '';

  function submit() {
    dispatch('add', text);
    text = '';
  }

  function onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      submit();
    }
  }
</script>

<div class="todo-input">
  <input
    type="text"
    placeholder="What needs to be done?"
    bind:value={text}
    on:keydown={onKeyDown}
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

- [ ] Run the test to see it pass:

```bash
npm test
```

Expected:

```
✓ src/lib/TodoInput.test.ts (3 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 6: TodoItem component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

`TodoItem` takes a `todo` prop and dispatches `toggle` and `delete` events carrying the todo's id.

- [ ] Write the failing test `src/lib/TodoItem.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Walk dog', completed: false };

describe('TodoItem', () => {
  it('renders the todo text', () => {
    const { getByText } = render(TodoItem, { props: { todo } });
    expect(getByText('Walk dog')).toBeInTheDocument();
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
    await fireEvent.click(getByRole('button', { name: /delete/i }));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
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
    on:click={() => dispatch('delete', todo.id)}>×</button
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
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test
```

Expected:

```
✓ src/lib/TodoItem.test.ts (4 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 7: TodoList component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

`TodoList` takes a `todos` prop (the already-filtered list), renders an empty state if empty, and **forwards** `toggle`/`delete` events from its children.

- [ ] Write the failing test `src/lib/TodoList.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'one', completed: false },
  { id: '2', text: 'two', completed: true },
];

describe('TodoList', () => {
  it('renders all provided todos', () => {
    const { getByText } = render(TodoList, { props: { todos } });
    expect(getByText('one')).toBeInTheDocument();
    expect(getByText('two')).toBeInTheDocument();
  });

  it('shows empty state when no todos', () => {
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

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failure resolving `./TodoList.svelte`.

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
    color: #888;
    padding: 1rem 0;
  }
</style>
```

Note: `on:toggle on:delete` with no handler forwards the child events upward.

- [ ] Run the test to see it pass:

```bash
npm test
```

Expected:

```
✓ src/lib/TodoList.test.ts (4 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 8: FilterBar component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

`FilterBar` takes `count` (remaining) and `current` (active filter) props. It dispatches `setFilter` with a `Filter` value and `clearCompleted` with no detail.

- [ ] Write the failing test `src/lib/FilterBar.test.ts`:

```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows singular item count', () => {
    const { getByText } = render(FilterBar, {
      props: { count: 1, current: 'all' },
    });
    expect(getByText('1 item left')).toBeInTheDocument();
  });

  it('shows plural item count', () => {
    const { getByText } = render(FilterBar, {
      props: { count: 3, current: 'all' },
    });
    expect(getByText('3 items left')).toBeInTheDocument();
  });

  it('dispatches setFilter when a filter button clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { count: 0, current: 'all' },
    });
    const handler = vi.fn();
    component.$on('setFilter', (e) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: /active/i }));
    expect(handler).toHaveBeenCalledWith('active');
  });

  it('dispatches clearCompleted when clear button clicked', async () => {
    const { getByRole, component } = render(FilterBar, {
      props: { count: 0, current: 'all' },
    });
    const handler = vi.fn();
    component.$on('clearCompleted', () => handler());
    await fireEvent.click(getByRole('button', { name: /clear/i }));
    expect(handler).toHaveBeenCalled();
  });

  it('marks the current filter button active', () => {
    const { getByRole } = render(FilterBar, {
      props: { count: 0, current: 'completed' },
    });
    expect(getByRole('button', { name: /completed/i })).toHaveClass('active');
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failure resolving `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let count: number;
  export let current: Filter;

  const dispatch = createEventDispatcher<{
    setFilter: Filter;
    clearCompleted: void;
  }>();

  const filters: Filter[] = ['all', 'active', 'completed'];

  function label(f: Filter): string {
    return f.charAt(0).toUpperCase() + f.slice(1);
  }
</script>

<div class="filter-bar">
  <span class="count">{count} {count === 1 ? 'item' : 'items'} left</span>

  <div class="filters">
    {#each filters as f}
      <button
        class:active={current === f}
        on:click={() => dispatch('setFilter', f)}>{label(f)}</button
      >
    {/each}
  </div>

  <button class="clear" on:click={() => dispatch('clearCompleted')}>
    Clear ✓
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
  .filters {
    display: flex;
    gap: 0.25rem;
  }
  button.active {
    font-weight: bold;
    text-decoration: underline;
  }
</style>
```

- [ ] Run the test to see it pass:

```bash
npm test
```

Expected:

```
✓ src/lib/FilterBar.test.ts (5 tests)
```

- [ ] Commit:

```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 9: App wiring and integration

**Files:** `src/App.svelte`, `src/App.test.ts`, `src/main.ts`, `src/app.css`

This task wires every component to the store and verifies the full acceptance criteria end-to-end.

- [ ] Write the failing integration test `src/App.test.ts`:

```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent, within } from '@testing-library/svelte';
import App from './App.svelte';
import { todos, filter } from './lib/store';

function resetState() {
  localStorage.clear();
  todos.set([]);
  filter.set('all');
}

describe('App integration', () => {
  beforeEach(resetState);

  async function addTodoViaUI(getByRole: any, text: string) {
    const input = getByRole('textbox');
    await fireEvent.input(input, { target: { value: text } });
    await fireEvent.click(getByRole('button', { name: /add/i }));
  }

  it('adds a todo and shows it in the list', async () => {
    const { getByRole, getByText } = render(App);
    await addTodoViaUI(getByRole, 'Buy groceries');
    expect(getByText('Buy groceries')).toBeInTheDocument();
  });

  it('updates remaining count as todos are added', async () => {
    const { getByRole, getByText } = render(App);
    await addTodoViaUI(getByRole, 'a');
    await addTodoViaUI(getByRole, 'b');
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('toggles a todo and updates the count', async () => {
    const { getByRole, getByText } = render(App);
    await addTodoViaUI(getByRole, 'task');
    await fireEvent.click(getByRole('checkbox'));
    expect(getByText('0 items left')).toBeInTheDocument();
  });

  it('filters to active only', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodoViaUI(getByRole, 'keep');
    await addTodoViaUI(getByRole, 'done');
    // complete the second todo
    const checkboxes = getAllByRole('checkbox');
    await fireEvent.click(checkboxes[1]);
    await fireEvent.click(getByRole('button', { name: /active/i }));
    expect(queryByText('keep')).toBeInTheDocument();
    expect(queryByText('done')).not.toBeInTheDocument();
  });

  it('filters to completed only', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodoViaUI(getByRole, 'keep');
    await addTodoViaUI(getByRole, 'done');
    const checkboxes = getAllByRole('checkbox');
    await fireEvent.click(checkboxes[1]);
    await fireEvent.click(getByRole('button', { name: /completed/i }));
    expect(queryByText('done')).toBeInTheDocument();
    expect(queryByText('keep')).not.toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const { getByRole, queryByText } = render(App);
    await addTodoViaUI(getByRole, 'delete me');
    await fireEvent.click(getByRole('button', { name: /delete/i }));
    expect(queryByText('delete me')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const { getByRole, getAllByRole, queryByText } = render(App);
    await addTodoViaUI(getByRole, 'keep');
    await addTodoViaUI(getByRole, 'done');
    const checkboxes = getAllByRole('checkbox');
    await fireEvent.click(checkboxes[1]);
    await fireEvent.click(getByRole('button', { name: /clear/i }));
    expect(queryByText('keep')).toBeInTheDocument();
    expect(queryByText('done')).not.toBeInTheDocument();
  });

  it('persists todos to localStorage', async () => {
    const { getByRole } = render(App);
    await addTodoViaUI(getByRole, 'persisted');
    expect(localStorage.getItem('svelte-todos')).toContain('persisted');
  });
});
```

- [ ] Run it to see it fail:

```bash
npm test
```

Expected: failures in `src/App.test.ts` because the current template `App.svelte` does not contain our UI.

- [ ] Implement `src/App.svelte`:

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
  } from './lib/store';
  import type { Filter, Todo } from './lib/types';

  let visibleTodos: Todo[] = [];

  $: visibleTodos = $todos.filter((t) => {
    if ($filter === 'active') return !t.completed;
    if ($filter === 'completed') return t.completed;
    return true;
  });

  function onAdd(e: CustomEvent<string>) {
    addTodo(e.detail);
  }
  function onToggle(e: CustomEvent<string>) {
    toggleTodo(e.detail);
  }
  function onDelete(e: CustomEvent<string>) {
    deleteTodo(e.detail);
  }
  function onSetFilter(e: CustomEvent<Filter>) {
    filter.set(e.detail);
  }
  function onClearCompleted() {
    clearCompleted();
  }
</script>

<main>
  <h1>Svelte Todos</h1>
  <TodoInput on:add={onAdd} />
  <TodoList todos={visibleTodos} on:toggle={onToggle} on:delete={onDelete} />
  <FilterBar
    count={$remainingCount}
    current={$filter}
    on:setFilter={onSetFilter}
    on:clearCompleted={onClearCompleted}
  />
</main>

<style>
  main {
    max-width: 480px;
    margin: 2rem auto;
    padding: 1.5rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: system-ui, sans-serif;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  h1 {
    margin: 0;
    font-size: 1.5rem;
  }
</style>
```

- [ ] Ensure `src/main.ts` mounts `App` (the template usually already does this). Overwrite `src/main.ts` with:

```ts
import './app.css';
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')!,
});

export default app;
```

- [ ] Ensure `src/app.css` exists with minimal global styles (overwrite the template file):

```css
:root {
  font-family: system-ui, sans-serif;
}
body {
  margin: 0;
  background: #fafafa;
}
```

- [ ] Run the full test suite:

```bash
npm test
```

Expected: all test files pass, e.g.:

```
✓ src/lib/storage.test.ts (3 tests)
✓ src/lib/store.test.ts (8 tests)
✓ src/lib/TodoInput.test.ts (3 tests)
✓ src/lib/TodoItem.test.ts (4 tests)
✓ src/lib/TodoList.test.ts (4 tests)
✓ src/lib/FilterBar.test.ts (5 tests)
✓ src/App.test.