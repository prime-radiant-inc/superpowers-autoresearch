# Svelte Todo List — Implementation Plan

## Global Constraints

- Framework: Svelte (use Vite scaffold `npm create vite@latest` with the `svelte-ts` template).
- Language: TypeScript for all `.ts` files and `<script lang="ts">` in components.
- Data model `Todo`: `{ id: string; text: string; completed: boolean }` — `id` is a UUID.
- Filter type: `type Filter = 'all' | 'active' | 'completed'`.
- localStorage key: `'svelte-todos'` (verbatim).
- Component/file layout exactly as specified: `src/App.svelte`, `src/lib/TodoInput.svelte`, `src/lib/TodoList.svelte`, `src/lib/TodoItem.svelte`, `src/lib/FilterBar.svelte`, `src/lib/store.ts`, `src/lib/storage.ts`.
- Tests: Vitest + `@testing-library/svelte` + `jsdom`.
- UI header text: `Svelte Todos`. Remaining-count copy: `N items left` (use `1 item left` for singular). Clear button label: `Clear completed`. Filter labels: `All`, `Active`, `Completed`.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/storage.ts` | Pure load/save of `Todo[]` to localStorage under key `svelte-todos`. |
| `src/lib/store.ts` | Svelte writable store of `Todo[]` + actions (add/toggle/delete/clearCompleted), filter store, derived stores. Wires persistence via `storage.ts`. |
| `src/lib/TodoItem.svelte` | One todo row: checkbox, text, delete button. Emits events. |
| `src/lib/TodoList.svelte` | Renders list of `TodoItem`s or empty-state message. |
| `src/lib/TodoInput.svelte` | Text input + Add button; Enter or click adds. |
| `src/lib/FilterBar.svelte` | Items-left count, filter buttons, clear-completed button. |
| `src/App.svelte` | Composes all components, subscribes to stores. |
| `src/main.ts` | Vite entry (from scaffold). |
| `vite.config.ts` | Vite + Vitest config. |

---

## Task 0: Project Scaffold & Test Harness

**Files:** `package.json`, `vite.config.ts`, `src/main.ts`, `src/App.svelte`, `tsconfig.json`

**Interfaces:** Produces a runnable Vite+Svelte+TS project with Vitest configured; `npm test` runs and `npm run dev` serves. Produces no app logic yet.

- [ ] Scaffold the project in a temp dir and move contents up (run from the intended project root):
  ```bash
  npm create vite@latest . -- --template svelte-ts
  ```
  Accept overwrite if prompted. Expected: `src/App.svelte`, `src/main.ts`, `vite.config.ts` exist.

- [ ] Install base deps:
  ```bash
  npm install
  ```
  Expected: `node_modules/` created, no errors.

- [ ] Install test deps:
  ```bash
  npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @testing-library/user-event
  ```
  Expected: packages added to `devDependencies`.

- [ ] Replace `vite.config.ts` with:
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
  ```

- [ ] Add test script to `package.json` `scripts`:
  ```json
  "test": "vitest run",
  "test:watch": "vitest"
  ```

- [ ] Create a smoke test `src/smoke.test.ts`:
  ```ts
  import { describe, it, expect } from 'vitest';

  describe('harness', () => {
    it('runs', () => {
      expect(1 + 1).toBe(2);
    });
  });
  ```

- [ ] Run tests:
  ```bash
  npm test
  ```
  Expected: `1 passed`.

- [ ] Delete `src/smoke.test.ts`, then commit:
  ```bash
  rm src/smoke.test.ts
  git init && git add -A && git commit -m "Scaffold Svelte+TS project with Vitest harness"
  ```

---

## Task 1: Storage Module

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `src/lib/types.ts`: `export interface Todo { id: string; text: string; completed: boolean }` and `export type Filter = 'all' | 'active' | 'completed'`.
  - `src/lib/storage.ts`:
    - `export const STORAGE_KEY = 'svelte-todos'`
    - `export function loadTodos(): Todo[]` — returns `[]` if nothing stored or on parse error.
    - `export function saveTodos(todos: Todo[]): void`

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

  const sample: Todo[] = [{ id: 'a', text: 'Buy milk', completed: false }];

  describe('storage', () => {
    beforeEach(() => localStorage.clear());

    it('returns empty array when nothing stored', () => {
      expect(loadTodos()).toEqual([]);
    });

    it('returns empty array on corrupt data', () => {
      localStorage.setItem(STORAGE_KEY, 'not json');
      expect(loadTodos()).toEqual([]);
    });

    it('saves and loads todos', () => {
      saveTodos(sample);
      expect(loadTodos()).toEqual(sample);
    });

    it('uses the svelte-todos key', () => {
      saveTodos(sample);
      expect(localStorage.getItem(STORAGE_KEY)).not.toBeNull();
      expect(STORAGE_KEY).toBe('svelte-todos');
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (`Cannot find module './storage'`).

- [ ] Implement `src/lib/storage.ts`:
  ```ts
  import type { Todo } from './types';

  export const STORAGE_KEY = 'svelte-todos';

  export function loadTodos(): Todo[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
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

- [ ] Run tests, expect pass:
  ```bash
  npm test
  ```
  Expected: `4 passed` (plus harness if any).

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add types and localStorage persistence module"
  ```

---

## Task 2: Todo Store

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo`, `Filter` from `./types`; `loadTodos`, `saveTodos` from `./storage`.
- Produces `src/lib/store.ts`:
  - `export const todos` — `Writable<Todo[]>`, initialized from `loadTodos()`, auto-persists on change via subscribe.
  - `export const filter` — `Writable<Filter>`, default `'all'`.
  - `export const filteredTodos` — `Readable<Todo[]>` derived from `todos` + `filter`.
  - `export const remainingCount` — `Readable<number>` (count of `!completed`).
  - `export function addTodo(text: string): void` — trims; ignores empty; prepends/appends new `{ id: crypto.randomUUID(), text, completed: false }`.
  - `export function toggleTodo(id: string): void`
  - `export function deleteTodo(id: string): void`
  - `export function clearCompleted(): void`

- [ ] Write failing test `src/lib/store.test.ts`:
  ```ts
  import { describe, it, expect, beforeEach } from 'vitest';
  import { get } from 'svelte/store';
  import {
    todos, filter, filteredTodos, remainingCount,
    addTodo, toggleTodo, deleteTodo, clearCompleted,
  } from './store';

  describe('store', () => {
    beforeEach(() => {
      localStorage.clear();
      todos.set([]);
      filter.set('all');
    });

    it('adds a todo with generated id', () => {
      addTodo('Buy milk');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('Buy milk');
      expect(list[0].completed).toBe(false);
      expect(typeof list[0].id).toBe('string');
      expect(list[0].id.length).toBeGreaterThan(0);
    });

    it('ignores empty/whitespace todos', () => {
      addTodo('   ');
      expect(get(todos)).toHaveLength(0);
    });

    it('trims todo text', () => {
      addTodo('  hi  ');
      expect(get(todos)[0].text).toBe('hi');
    });

    it('toggles completion', () => {
      addTodo('x');
      const id = get(todos)[0].id;
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(true);
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(false);
    });

    it('deletes a todo', () => {
      addTodo('x');
      const id = get(todos)[0].id;
      deleteTodo(id);
      expect(get(todos)).toHaveLength(0);
    });

    it('clears completed', () => {
      addTodo('a'); addTodo('b');
      const id = get(todos)[0].id;
      toggleTodo(id);
      clearCompleted();
      expect(get(todos)).toHaveLength(1);
      expect(get(todos).every(t => !t.completed)).toBe(true);
    });

    it('remainingCount counts incomplete', () => {
      addTodo('a'); addTodo('b');
      toggleTodo(get(todos)[0].id);
      expect(get(remainingCount)).toBe(1);
    });

    it('filteredTodos respects filter', () => {
      addTodo('a'); addTodo('b');
      toggleTodo(get(todos)[0].id);
      filter.set('active');
      expect(get(filteredTodos).every(t => !t.completed)).toBe(true);
      filter.set('completed');
      expect(get(filteredTodos).every(t => t.completed)).toBe(true);
      filter.set('all');
      expect(get(filteredTodos)).toHaveLength(2);
    });

    it('persists to localStorage on change', () => {
      addTodo('persist me');
      expect(localStorage.getItem('svelte-todos')).toContain('persist me');
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (`Cannot find module './store'`).

- [ ] Implement `src/lib/store.ts`:
  ```ts
  import { writable, derived, get } from 'svelte/store';
  import type { Todo, Filter } from './types';
  import { loadTodos, saveTodos } from './storage';

  export const todos = writable<Todo[]>(loadTodos());
  export const filter = writable<Filter>('all');

  todos.subscribe((list) => saveTodos(list));

  export const filteredTodos = derived([todos, filter], ([$todos, $filter]) => {
    switch ($filter) {
      case 'active':
        return $todos.filter((t) => !t.completed);
      case 'completed':
        return $todos.filter((t) => t.completed);
      default:
        return $todos;
    }
  });

  export const remainingCount = derived(todos, ($todos) =>
    $todos.filter((t) => !t.completed).length
  );

  export function addTodo(text: string): void {
    const trimmed = text.trim();
    if (!trimmed) return;
    const todo: Todo = { id: crypto.randomUUID(), text: trimmed, completed: false };
    todos.update((list) => [...list, todo]);
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
  > Note: `get` import retained only if used elsewhere; remove if unused to satisfy lint. (Remove it now — it is unused.)

- [ ] Remove the unused `get` import from the implementation, then run tests:
  ```bash
  npm test
  ```
  Expected: all store tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add todos store with actions, derived stores, persistence"
  ```

---

## Task 3: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` type.
- Produces `TodoItem.svelte` with prop `export let todo: Todo;` and dispatched events:
  - `toggle` with `detail: { id: string }`
  - `delete` with `detail: { id: string }`
- DOM contract: a checkbox `role="checkbox"` reflecting `todo.completed`; text rendered in an element; a delete button with accessible name `Delete`.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './types';

  const todo: Todo = { id: '1', text: 'Walk dog', completed: false };

  describe('TodoItem', () => {
    it('renders text', () => {
      render(TodoItem, { props: { todo } });
      expect(screen.getByText('Walk dog')).toBeInTheDocument();
    });

    it('checkbox reflects completed', () => {
      render(TodoItem, { props: { todo: { ...todo, completed: true } } });
      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('dispatches toggle with id', async () => {
      const { component } = render(TodoItem, { props: { todo } });
      const handler = vi.fn();
      component.$on('toggle', handler);
      await fireEvent.click(screen.getByRole('checkbox'));
      expect(handler).toHaveBeenCalled();
      expect(handler.mock.calls[0][0].detail).toEqual({ id: '1' });
    });

    it('dispatches delete with id', async () => {
      const { component } = render(TodoItem, { props: { todo } });
      const handler = vi.fn();
      component.$on('delete', handler);
      await fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
      expect(handler).toHaveBeenCalled();
      expect(handler.mock.calls[0][0].detail).toEqual({ id: '1' });
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (cannot resolve `TodoItem.svelte`).

- [ ] Implement `src/lib/TodoItem.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Todo } from './types';

    export let todo: Todo;

    const dispatch = createEventDispatcher<{
      toggle: { id: string };
      delete: { id: string };
    }>();
  </script>

  <li class="todo-item" class:completed={todo.completed}>
    <input
      type="checkbox"
      checked={todo.completed}
      on:change={() => dispatch('toggle', { id: todo.id })}
    />
    <span class="text">{todo.text}</span>
    <button class="delete" aria-label="Delete" on:click={() => dispatch('delete', { id: todo.id })}>
      x
    </button>
  </li>

  <style>
    .todo-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0; }
    .text { flex: 1; }
    .completed .text { text-decoration: line-through; opacity: 0.6; }
    .delete { border: none; background: none; cursor: pointer; }
  </style>
  ```

- [ ] Run tests, expect pass:
  ```bash
  npm test
  ```
  Expected: TodoItem tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoItem component with toggle/delete events"
  ```

---

## Task 4: TodoList Component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` type, `TodoItem.svelte`.
- Produces `TodoList.svelte`:
  - Prop `export let items: Todo[];`
  - Renders one `TodoItem` per item, forwarding its `toggle` and `delete` events upward (re-dispatched with same `detail`).
  - When `items.length === 0`, renders empty-state text `No todos yet` inside an element with `data-testid="empty"`.

- [ ] Write failing test `src/lib/TodoList.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import TodoList from './TodoList.svelte';
  import type { Todo } from './types';

  const items: Todo[] = [
    { id: '1', text: 'a', completed: false },
    { id: '2', text: 'b', completed: true },
  ];

  describe('TodoList', () => {
    it('renders an item per todo', () => {
      render(TodoList, { props: { items } });
      expect(screen.getByText('a')).toBeInTheDocument();
      expect(screen.getByText('b')).toBeInTheDocument();
    });

    it('shows empty state when no items', () => {
      render(TodoList, { props: { items: [] } });
      expect(screen.getByTestId('empty')).toHaveTextContent('No todos yet');
    });

    it('forwards toggle events', async () => {
      const { component } = render(TodoList, { props: { items } });
      const handler = vi.fn();
      component.$on('toggle', handler);
      await fireEvent.click(screen.getAllByRole('checkbox')[0]);
      expect(handler.mock.calls[0][0].detail).toEqual({ id: '1' });
    });

    it('forwards delete events', async () => {
      const { component } = render(TodoList, { props: { items } });
      const handler = vi.fn();
      component.$on('delete', handler);
      await fireEvent.click(screen.getAllByRole('button', { name: 'Delete' })[1]);
      expect(handler.mock.calls[0][0].detail).toEqual({ id: '2' });
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (cannot resolve `TodoList.svelte`).

- [ ] Implement `src/lib/TodoList.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';
    import TodoItem from './TodoItem.svelte';

    export let items: Todo[];
  </script>

  {#if items.length === 0}
    <p class="empty" data-testid="empty">No todos yet</p>
  {:else}
    <ul class="todo-list">
      {#each items as todo (todo.id)}
        <TodoItem {todo} on:toggle on:delete />
      {/each}
    </ul>
  {/if}

  <style>
    .todo-list { list-style: none; padding: 0; margin: 0; }
    .empty { text-align: center; color: #888; padding: 1rem 0; }
  </style>
  ```
  > Note: `on:toggle on:delete` without handlers forwards the events with their original `detail`.

- [ ] Run tests, expect pass:
  ```bash
  npm test
  ```
  Expected: TodoList tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoList component with empty state and event forwarding"
  ```

---

## Task 5: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Consumes: nothing (self-contained input).
- Produces `TodoInput.svelte`:
  - Dispatches `add` with `detail: { text: string }` on Enter key in the input or click of the Add button.
  - Clears the input after a successful dispatch.
  - Does not dispatch when input is empty/whitespace.
  - Input has accessible name/placeholder `What needs to be done?`; button text `Add`.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import TodoInput from './TodoInput.svelte';

  describe('TodoInput', () => {
    it('dispatches add on button click', async () => {
      const { component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', handler);
      const input = screen.getByPlaceholderText('What needs to be done?');
      await fireEvent.input(input, { target: { value: 'New task' } });
      await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
      expect(handler.mock.calls[0][0].detail).toEqual({ text: 'New task' });
    });

    it('dispatches add on Enter', async () => {
      const { component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', handler);
      const input = screen.getByPlaceholderText('What needs to be done?');
      await fireEvent.input(input, { target: { value: 'Via enter' } });
      await fireEvent.keyDown(input, { key: 'Enter' });
      expect(handler.mock.calls[0][0].detail).toEqual({ text: 'Via enter' });
    });

    it('clears input after add', async () => {
      render(TodoInput);
      const input = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
      await fireEvent.input(input, { target: { value: 'x' } });
      await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
      expect(input.value).toBe('');
    });

    it('does not dispatch on empty', async () => {
      const { component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', handler);
      await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
      expect(handler).not.toHaveBeenCalled();
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (cannot resolve `TodoInput.svelte`).

- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ add: { text: string } }>();
    let value = '';

    function submit() {
      const text = value.trim();
      if (!text) return;
      dispatch('add', { text });
      value = '';
    }

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Enter') submit();
    }
  </script>

  <div class="todo-input">
    <input
      type="text"
      placeholder="What needs to be done?"
      bind:value
      on:keydown={onKeyDown}
    />
    <button on:click={submit}>Add</button>
  </div>

  <style>
    .todo-input { display: flex; gap: 0.5rem; }
    .todo-input input { flex: 1; padding: 0.4rem; }
  </style>
  ```

- [ ] Run tests, expect pass:
  ```bash
  npm test
  ```
  Expected: TodoInput tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoInput component"
  ```

---

## Task 6: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` type.
- Produces `FilterBar.svelte`:
  - Props: `export let current: Filter;` and `export let remaining: number;`
  - Renders `N items left` (singular `1 item left`).
  - Renders three buttons `All`, `Active`, `Completed`; the one matching `current` has class `active`.
  - Renders `Clear completed` button.
  - Dispatches `filter` with `detail: { filter: Filter }` on filter button click.
  - Dispatches `clear` (no detail payload required) on clear-completed click.

- [ ] Write failing test `src/lib/FilterBar.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import FilterBar from './FilterBar.svelte';

  describe('FilterBar', () => {
    it('shows plural count', () => {
      render(FilterBar, { props: { current: 'all', remaining: 2 } });
      expect(screen.getByText('2 items left')).toBeInTheDocument();
    });

    it('shows singular count', () => {
      render(FilterBar, { props: { current: 'all', remaining: 1 } });
      expect(screen.getByText('1 item left')).toBeInTheDocument();
    });

    it('marks current filter active', () => {
      render(FilterBar, { props: { current: 'active', remaining: 0 } });
      expect(screen.getByRole('button', { name: 'Active' })).toHaveClass('active');
    });

    it('dispatches filter change', async () => {
      const { component } = render(FilterBar, { props: { current: 'all', remaining: 0 } });
      const handler = vi.fn();
      component.$on('filter', handler);
      await fireEvent.click(screen.getByRole('button', { name: 'Completed' }));
      expect(handler.mock.calls[0][0].detail).toEqual({ filter: 'completed' });
    });

    it('dispatches clear', async () => {
      const { component } = render(FilterBar, { props: { current: 'all', remaining: 0 } });
      const handler = vi.fn();
      component.$on('clear', handler);
      await fireEvent.click(screen.getByRole('button', { name: 'Clear completed' }));
      expect(handler).toHaveBeenCalled();
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (cannot resolve `FilterBar.svelte`).

- [ ] Implement `src/lib/FilterBar.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Filter } from './types';

    export let current: Filter;
    export let remaining: number;

    const dispatch = createEventDispatcher<{
      filter: { filter: Filter };
      clear: void;
    }>();

    const filters: Filter[] = ['all', 'active', 'completed'];
    const labels: Record<Filter, string> = {
      all: 'All',
      active: 'Active',
      completed: 'Completed',
    };

    $: countLabel = `${remaining} ${remaining === 1 ? 'item' : 'items'} left`;
  </script>

  <div class="filter-bar">
    <span class="count">{countLabel}</span>
    <div class="filters">
      {#each filters as f}
        <button
          class:active={current === f}
          on:click={() => dispatch('filter', { filter: f })}
        >
          {labels[f]}
        </button>
      {/each}
    </div>
    <button class="clear" on:click={() => dispatch('clear')}>Clear completed</button>
  </div>

  <style>
    .filter-bar { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; }
    .filters button.active { font-weight: bold; text-decoration: underline; }
  </style>
  ```

- [ ] Run tests, expect pass:
  ```bash
  npm test
  ```
  Expected: FilterBar tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add FilterBar component"
  ```

---

## Task 7: App Composition & Integration

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: stores/actions from `./lib/store`, all four lib components.
- Produces the wired application:
  - Header `Svelte Todos`.
  - `TodoInput` `add` → `addTodo(detail.text)`.
  - `TodoList` fed by `$filteredTodos`; `toggle` → `toggleTodo(detail.id)`; `delete` → `deleteTodo(detail.id)`.
  - `FilterBar` fed by `$filter` and `$remainingCount`; `filter` → `filter.set(detail.filter)`; `clear` → `clearCompleted()`.

- [ ] Write failing integration test `src/App.test.ts`:
  ```ts
  import { describe, it, expect, beforeEach } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import App from './App.svelte';
  import { todos, filter } from './lib/store';

  async function addTodo(text: string) {
    const input = screen.getByPlaceholderText('What needs to be done?');
    await fireEvent.input(input, { target: { value: text } });
    await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
  }

  describe('App integration', () => {
    beforeEach(() => {
      localStorage.clear();
      todos.set([]);
      filter.set('all');
    });

    it('renders header and empty state', () => {
      render(App);
      expect(screen.getByText('Svelte Todos')).toBeInTheDocument();
      expect(screen.getByTestId('empty')).toBeInTheDocument();
    });

    it('adds todos and updates count', async () => {
      render(App);
      await addTodo('Buy groceries');
      expect(screen.getByText('Buy groceries')).toBeInTheDocument();
      expect(screen.getByText('1 item left')).toBeInTheDocument();
    });

    it('toggles completion and updates count', async () => {
      render(App);
      await addTodo('Walk dog');
      await fireEvent.click(screen.getByRole('checkbox'));
      expect(screen.getByText('0 items left')).toBeInTheDocument();
    });

    it('filters to active', async () => {
      render(App);
      await addTodo('a');
      await addTodo('b');
      await fireEvent.click(screen.getAllByRole('checkbox')[0]);
      await fireEvent.click(screen.getByRole('button', { name: 'Active' }));
      expect(screen.queryByText('a')).not.toBeInTheDocument();
      expect(screen.getByText('b')).toBeInTheDocument();
    });

    it('deletes a todo', async () => {
      render(App);
      await addTodo('delete me');
      await fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
      expect(screen.queryByText('delete me')).not.toBeInTheDocument();
    });

    it('clears completed', async () => {
      render(App);
      await addTodo('a');
      await addTodo('b');
      await fireEvent.click(screen.getAllByRole('checkbox')[0]);
      await fireEvent.click(screen.getByRole('button', { name: 'Clear completed' }));
      expect(screen.queryByText('a')).not.toBeInTheDocument();
      expect(screen.getByText('b')).toBeInTheDocument();
    });

    it('persists across remount', async () => {
      const { unmount } = render(App);
      await addTodo('persist');
      unmount();
      todos.set(JSON.parse(localStorage.getItem('svelte-todos') || '[]'));
      render(App);
      expect(screen.getByText('persist')).toBeInTheDocument();
    });
  });
  ```

- [ ] Run it, expect failure:
  ```bash
  npm test
  ```
  Expected: failure (App still has scaffold content).

- [ ] Replace `src/App.svelte`:
  ```svelte
  <script lang="ts">
    import Tod