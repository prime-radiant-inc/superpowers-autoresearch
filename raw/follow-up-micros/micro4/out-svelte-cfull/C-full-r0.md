# Svelte Todo List - Implementation Plan

## Global Constraints

- Framework: Svelte (with TypeScript)
- All TypeScript source files use `.ts` extension; components use `.svelte`
- Data model `Todo`: `{ id: string; text: string; completed: boolean }`
- `id` must be a UUID (use `crypto.randomUUID()`)
- `Filter` type: `'all' | 'active' | 'completed'`
- localStorage key: `svelte-todos`
- File layout exactly as in spec (`src/App.svelte`, `src/lib/*`)
- Tests run with Vitest; all tests must pass

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/types.ts` | `Todo` interface and `Filter` type definitions |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte writable store with todo operations (add/toggle/delete/clearCompleted) |
| `src/lib/TodoInput.svelte` | Text input + Add button; emits new todo text |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | Renders filtered list of `TodoItem`s; empty state |
| `src/lib/FilterBar.svelte` | Filter buttons + items-left count + clear completed |
| `src/App.svelte` | Wires components together, holds filter state |

---

## Setup

### Task 0: Project Scaffolding

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `src/main.ts`, `index.html`

**Interfaces:**
- Produces: a working Svelte + TypeScript + Vitest project; `npm test` runs Vitest, `npm run dev` runs the app.

- [ ] Scaffold the project (run in an empty directory):
  ```bash
  npm create vite@latest . -- --template svelte-ts
  ```
  Expected: project files generated including `src/App.svelte`, `src/main.ts`, `vite.config.ts`.

- [ ] Install dependencies:
  ```bash
  npm install
  ```
  Expected: `node_modules/` created, exit code 0.

- [ ] Install test tooling:
  ```bash
  npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @testing-library/user-event
  ```
  Expected: packages added to `devDependencies`.

- [ ] Configure Vitest. Replace `vite.config.ts` with:
  ```typescript
  import { defineConfig } from 'vitest/config';
  import { svelte } from '@sveltejs/vite-plugin-svelte';

  export default defineConfig({
    plugins: [svelte({ hot: false })],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test-setup.ts'],
    },
  });
  ```

- [ ] Create `src/test-setup.ts`:
  ```typescript
  import '@testing-library/jest-dom/vitest';
  ```

- [ ] Add the test script to `package.json` `"scripts"`:
  ```json
  "test": "vitest run",
  "test:watch": "vitest"
  ```

- [ ] Add a smoke test `src/smoke.test.ts`:
  ```typescript
  import { describe, it, expect } from 'vitest';

  describe('smoke', () => {
    it('runs', () => {
      expect(1 + 1).toBe(2);
    });
  });
  ```

- [ ] Run the test:
  ```bash
  npm test
  ```
  Expected: `1 passed`, exit code 0.

- [ ] Remove the smoke test and any scaffold demo files we won't use:
  ```bash
  rm src/smoke.test.ts src/lib/Counter.svelte src/assets/svelte.svg 2>/dev/null; true
  ```

- [ ] Commit:
  ```bash
  git init -q && git add -A && git commit -q -m "Scaffold Svelte + TS + Vitest project"
  ```

---

### Task 1: Types

**Files:** `src/lib/types.ts`

**Interfaces:**
- Produces:
  - `interface Todo { id: string; text: string; completed: boolean }`
  - `type Filter = 'all' | 'active' | 'completed'`

- [ ] Create `src/lib/types.ts`:
  ```typescript
  export interface Todo {
    id: string;
    text: string;
    completed: boolean;
  }

  export type Filter = 'all' | 'active' | 'completed';
  ```

- [ ] Type-check:
  ```bash
  npx tsc --noEmit
  ```
  Expected: no errors, exit code 0.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add Todo and Filter types"
  ```

---

### Task 2: Storage

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`.
- Produces:
  - `const STORAGE_KEY = 'svelte-todos'`
  - `function loadTodos(): Todo[]` — returns parsed todos, or `[]` if absent/invalid.
  - `function saveTodos(todos: Todo[]): void` — writes JSON to localStorage.

- [ ] Write failing test `src/lib/storage.test.ts`:
  ```typescript
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

    it('returns empty array when stored value is invalid JSON', () => {
      localStorage.setItem(STORAGE_KEY, 'not json');
      expect(loadTodos()).toEqual([]);
    });

    it('saves and loads todos round-trip', () => {
      saveTodos(sample);
      expect(loadTodos()).toEqual(sample);
    });

    it('writes under the correct key', () => {
      saveTodos(sample);
      expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- storage
  ```
  Expected: fails — `loadTodos` not found / module missing.

- [ ] Implement `src/lib/storage.ts`:
  ```typescript
  import type { Todo } from './types';

  export const STORAGE_KEY = 'svelte-todos';

  export function loadTodos(): Todo[] {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) return [];
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

- [ ] Run to see it pass:
  ```bash
  npm test -- storage
  ```
  Expected: `4 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add localStorage persistence"
  ```

---

### Task 3: Store

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`; `loadTodos`, `saveTodos` from `./storage`.
- Produces:
  - `const todos: Writable<Todo[]>` — initialized from `loadTodos()`, auto-saves on every change via `subscribe`.
  - `function addTodo(text: string): void` — trims text; ignores empty; pushes `{ id: crypto.randomUUID(), text, completed: false }`.
  - `function toggleTodo(id: string): void`
  - `function deleteTodo(id: string): void`
  - `function clearCompleted(): void`

- [ ] Write failing test `src/lib/store.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { get } from 'svelte/store';

  async function freshStore() {
    localStorage.clear();
    const mod = await import('./store?t=' + Math.random());
    return mod;
  }

  describe('store', () => {
    beforeEach(() => localStorage.clear());

    it('adds a trimmed todo', async () => {
      const { todos, addTodo } = await freshStore();
      addTodo('  Buy milk  ');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('Buy milk');
      expect(list[0].completed).toBe(false);
      expect(typeof list[0].id).toBe('string');
    });

    it('ignores empty/whitespace todos', async () => {
      const { todos, addTodo } = await freshStore();
      addTodo('   ');
      addTodo('');
      expect(get(todos)).toHaveLength(0);
    });

    it('toggles completion', async () => {
      const { todos, addTodo, toggleTodo } = await freshStore();
      addTodo('x');
      const id = get(todos)[0].id;
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(true);
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(false);
    });

    it('deletes a todo', async () => {
      const { todos, addTodo, deleteTodo } = await freshStore();
      addTodo('x');
      const id = get(todos)[0].id;
      deleteTodo(id);
      expect(get(todos)).toHaveLength(0);
    });

    it('clears completed todos', async () => {
      const { todos, addTodo, toggleTodo, clearCompleted } = await freshStore();
      addTodo('a');
      addTodo('b');
      toggleTodo(get(todos)[0].id);
      clearCompleted();
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('b');
    });

    it('persists changes to localStorage', async () => {
      const { addTodo } = await freshStore();
      addTodo('persisted');
      const raw = localStorage.getItem('svelte-todos');
      expect(raw).toContain('persisted');
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- store
  ```
  Expected: fails — module `./store` missing.

- [ ] Implement `src/lib/store.ts`:
  ```typescript
  import { writable } from 'svelte/store';
  import type { Todo } from './types';
  import { loadTodos, saveTodos } from './storage';

  export const todos = writable<Todo[]>(loadTodos());

  todos.subscribe((value) => saveTodos(value));

  export function addTodo(text: string): void {
    const trimmed = text.trim();
    if (trimmed === '') return;
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

- [ ] Run to see it pass:
  ```bash
  npm test -- store
  ```
  Expected: `6 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add todos store with CRUD operations"
  ```

---

### Task 4: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Produces: `TodoInput.svelte` dispatching event `add` with `detail: string` (trimmed text) when Enter pressed or Add clicked; clears the input after dispatch; does not dispatch on empty input.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoInput from './TodoInput.svelte';

  describe('TodoInput', () => {
    it('dispatches add on Add button click and clears input', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', (e) => handler(e.detail));

      const input = getByRole('textbox') as HTMLInputElement;
      await fireEvent.input(input, { target: { value: 'New task' } });
      await fireEvent.click(getByRole('button', { name: /add/i }));

      expect(handler).toHaveBeenCalledWith('New task');
      expect(input.value).toBe('');
    });

    it('dispatches add on Enter key', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', (e) => handler(e.detail));

      const input = getByRole('textbox') as HTMLInputElement;
      await fireEvent.input(input, { target: { value: 'Via enter' } });
      await fireEvent.keyDown(input, { key: 'Enter' });

      expect(handler).toHaveBeenCalledWith('Via enter');
    });

    it('does not dispatch for empty input', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', handler);

      await fireEvent.click(getByRole('button', { name: /add/i }));
      expect(handler).not.toHaveBeenCalled();
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoInput
  ```
  Expected: fails — component missing.

- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ add: string }>();
    let value = '';

    function submit() {
      const trimmed = value.trim();
      if (trimmed === '') return;
      dispatch('add', trimmed);
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
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoInput
  ```
  Expected: `3 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add TodoInput component"
  ```

---

### Task 5: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`.
- Produces: `TodoItem.svelte` with prop `todo: Todo`; dispatches `toggle` with `detail: string` (id) on checkbox change, and `delete` with `detail: string` (id) on X button click; renders todo text; applies a `completed` class when `todo.completed`.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
  ```typescript
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

    it('dispatches toggle with id on checkbox change', async () => {
      const { getByRole, component } = render(TodoItem, { props: { todo } });
      const handler = vi.fn();
      component.$on('toggle', (e) => handler(e.detail));
      await fireEvent.click(getByRole('checkbox'));
      expect(handler).toHaveBeenCalledWith('abc');
    });

    it('dispatches delete with id on X click', async () => {
      const { getByRole, component } = render(TodoItem, { props: { todo } });
      const handler = vi.fn();
      component.$on('delete', (e) => handler(e.detail));
      await fireEvent.click(getByRole('button', { name: /delete/i }));
      expect(handler).toHaveBeenCalledWith('abc');
    });

    it('reflects completed state on the checkbox', () => {
      const { getByRole } = render(TodoItem, {
        props: { todo: { ...todo, completed: true } },
      });
      expect((getByRole('checkbox') as HTMLInputElement).checked).toBe(true);
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoItem
  ```
  Expected: fails — component missing.

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
    .completed .text {
      text-decoration: line-through;
      opacity: 0.6;
    }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoItem
  ```
  Expected: `4 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add TodoItem component"
  ```

---

### Task 6: TodoList Component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./types`; `TodoItem.svelte`.
- Produces: `TodoList.svelte` with prop `todos: Todo[]`; renders one `TodoItem` per todo; forwards `toggle` and `delete` events (with id detail) up; shows empty-state message `No todos yet` when `todos` is empty.

- [ ] Write failing test `src/lib/TodoList.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoList from './TodoList.svelte';
  import type { Todo } from './types';

  const todos: Todo[] = [
    { id: '1', text: 'a', completed: false },
    { id: '2', text: 'b', completed: true },
  ];

  describe('TodoList', () => {
    it('renders empty state when no todos', () => {
      const { getByText } = render(TodoList, { props: { todos: [] } });
      expect(getByText(/no todos yet/i)).toBeInTheDocument();
    });

    it('renders one item per todo', () => {
      const { getAllByRole } = render(TodoList, { props: { todos } });
      expect(getAllByRole('checkbox')).toHaveLength(2);
    });

    it('forwards toggle events with id', async () => {
      const { getAllByRole, component } = render(TodoList, { props: { todos } });
      const handler = vi.fn();
      component.$on('toggle', (e) => handler(e.detail));
      await fireEvent.click(getAllByRole('checkbox')[0]);
      expect(handler).toHaveBeenCalledWith('1');
    });

    it('forwards delete events with id', async () => {
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
  npm test -- TodoList
  ```
  Expected: fails — component missing.

- [ ] Implement `src/lib/TodoList.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';
    import TodoItem from './TodoItem.svelte';

    export let todos: Todo[];
  </script>

  {#if todos.length === 0}
    <p class="empty">No todos yet — add one above!</p>
  {:else}
    <ul class="todo-list">
      {#each todos as todo (todo.id)}
        <TodoItem {todo} on:toggle on:delete />
      {/each}
    </ul>
  {/if}
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoList
  ```
  Expected: `4 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add TodoList component with empty state"
  ```

---

### Task 7: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` from `./types`.
- Produces: `FilterBar.svelte` with props `filter: Filter` and `remaining: number`; renders `"{remaining} item(s) left"`; renders All/Active/Completed buttons; dispatches `setFilter` with `detail: Filter` on a filter button click; dispatches `clearCompleted` (no detail) on Clear button click; marks the active filter button with an `active` class.

- [ ] Write failing test `src/lib/FilterBar.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import FilterBar from './FilterBar.svelte';

  describe('FilterBar', () => {
    it('shows remaining count', () => {
      const { getByText } = render(FilterBar, {
        props: { filter: 'all', remaining: 2 },
      });
      expect(getByText(/2 items left/i)).toBeInTheDocument();
    });

    it('shows singular for one item', () => {
      const { getByText } = render(FilterBar, {
        props: { filter: 'all', remaining: 1 },
      });
      expect(getByText(/1 item left/i)).toBeInTheDocument();
    });

    it('dispatches setFilter with the chosen filter', async () => {
      const { getByRole, component } = render(FilterBar, {
        props: { filter: 'all', remaining: 0 },
      });
      const handler = vi.fn();
      component.$on('setFilter', (e) => handler(e.detail));
      await fireEvent.click(getByRole('button', { name: /^active$/i }));
      expect(handler).toHaveBeenCalledWith('active');
    });

    it('dispatches clearCompleted', async () => {
      const { getByRole, component } = render(FilterBar, {
        props: { filter: 'all', remaining: 0 },
      });
      const handler = vi.fn();
      component.$on('clearCompleted', handler);
      await fireEvent.click(getByRole('button', { name: /clear/i }));
      expect(handler).toHaveBeenCalled();
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- FilterBar
  ```
  Expected: fails — component missing.

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
    <span class="count">{remaining} {remaining === 1 ? 'item' : 'items'} left</span>
    <div class="filters">
      {#each filters as f}
        <button
          class:active={filter === f}
          on:click={() => dispatch('setFilter', f)}
        >
          {label[f]}
        </button>
      {/each}
    </div>
    <button class="clear" on:click={() => dispatch('clearCompleted')}>
      Clear ✓
    </button>
  </div>

  <style>
    .active {
      font-weight: bold;
    }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- FilterBar
  ```
  Expected: `4 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Add FilterBar component"
  ```

---

### Task 8: App Integration

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: `todos`, `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted` from `./lib/store`; `Filter` from `./lib/types`; all four components.
- Produces: `App.svelte` — holds `filter: Filter` state (default `'all'`), computes `visibleTodos` per filter and `remaining` (count of incomplete), wires all child events to store operations.

- [ ] Write failing test `src/App.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import App from './App.svelte';

  async function addTodo(getByRole: any, text: string) {
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: text } });
    await fireEvent.click(getByRole('button', { name: /^add$/i }));
  }

  describe('App', () => {
    beforeEach(() => localStorage.clear());

    it('adds and displays a todo', async () => {
      const { getByRole, getByText } = render(App);
      await addTodo(getByRole, 'Buy milk');
      expect(getByText('Buy milk')).toBeInTheDocument();
    });

    it('updates remaining count', async () => {
      const { getByRole, getByText } = render(App);
      await addTodo(getByRole, 'one');
      await addTodo(getByRole, 'two');
      expect(getByText(/2 items left/i)).toBeInTheDocument();
    });

    it('filters to active and completed', async () => {
      const { getByRole, getAllByRole, queryByText, getByText } = render(App);
      await addTodo(getByRole, 'keep active');
      await addTodo(getByRole, 'will complete');

      // complete the second todo
      const checkboxes = getAllByRole('checkbox');
      await fireEvent.click(checkboxes[1]);

      // Completed filter -> only completed shown
      await fireEvent.click(getByRole('button', { name: /^completed$/i }));
      expect(getByText('will complete')).toBeInTheDocument();
      expect(queryByText('keep active')).not.toBeInTheDocument();

      // Active filter -> only active shown
      await fireEvent.click(getByRole('button', { name: /^active$/i }));
      expect(getByText('keep active')).toBeInTheDocument();
      expect(queryByText('will complete')).not.toBeInTheDocument();
    });

    it('clears completed todos', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'done');
      await fireEvent.click(getAllByRole('checkbox')[0]);
      await fireEvent.click(getByRole('button', { name: /clear/i }));
      expect(queryByText('done')).not.toBeInTheDocument();
    });

    it('deletes a todo', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'remove me');
      await fireEvent.click(getAllByRole('button', { name: /delete/i })[0]);
      expect(queryByText('remove me')).not.toBeInTheDocument();
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- App
  ```
  Expected: fails — `App.svelte` still has scaffold content / no input.

- [ ] Implement `src/App.svelte` (overwrite scaffold):
  ```svelte
  <script lang="ts">
    import type { Filter } from './lib/types';
    import {
      todos,
      addTodo,
      toggleTodo,
      deleteTodo,
      clearCompleted,
    } from './lib/store';
    import TodoInput from './lib/TodoInput.svelte';
    import TodoList from './lib/TodoList.svelte';
    import FilterBar from './lib/FilterBar.svelte';

    let filter: Filter = 'all';

    $: visibleTodos = $todos.filter((t) => {
      if (filter === 'active') return !t.completed;
      if (filter === 'completed') return t.completed;
      return true;
    });

    $: remaining = $todos.filter((t) => !t.completed).length;
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
      {filter}
      {remaining}
      on:setFilter={(e) => (filter = e.detail)}
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

- [ ] Run to see it pass:
  ```bash
  npm test -- App
  ```
  Expected: `5 passed`.

- [ ] Run the full suite:
  ```bash
  npm test
  ```
  Expected: all suites pass (storage 4, store 6, TodoInput 3, TodoItem 4, TodoList 4, FilterBar 4, App 5).

- [ ] Type-check the whole project:
  ```bash
  npx tsc --noEmit
  ```
  Expected: no errors.

- [ ] Manually verify persistence in the browser:
  ```bash
  npm run dev
  ```
  Add a todo, refresh the page, confirm it persists. Stop the server.

- [ ] Commit:
  ```bash
  git add -A && git commit -q -m "Wire App integration with filtering and persistence"
  ```

---

## Self-Review

**Spec coverage check:**

| Acceptance Criterion | Covered by |
|---|---|
| 1. Add via Enter or Add button | Task 4 tests; Task 8 add test |
| 2. Toggle completion via checkbox | Task 5 toggle test; Task 8 filter test toggles |
| 3. Delete via X button | Task 5 delete test; Task 8 delete test |
| 4. Filters show correct subset | Task 8 filter test |
| 5. "X items left" count | Task 7 count tests; Task 8 remaining test |
| 6. Clear completed | Task 3 clearCompleted test; Task 8 clear test |
| 7. Persist across refresh (localStorage) | Task 2 round-trip; Task 3 persistence test; Task 8 manual verify |
| 8. Empty state message | Task 6 empty-state test |
| 9. All tests pass | Task 8 full-suite run |

**Placeholder scan:** No `TODO`, `FIXME`, or stub bodies remain; every component and module has a full implementation.

**Type consistency check:** `Todo` and `Filter` defined once in `types.ts` and imported everywhere. Event detail types are consistent: `add: string`, `toggle: string`, `delete: string`, `setFilter: Filter`, `clearCompleted: void`. Store functions all take `string` ids matching `Todo.id`. `crypto.randomUUID()` satisfies the UUID requirement and is available in jsdom and modern browsers.

**File layout check:** All files match the spec's prescribed paths (`src/App.svelte`, `src/lib/{TodoInput,TodoList,TodoItem,FilterBar}.svelte`, `src/lib/store.ts`, `src/lib/storage.ts`), plus `src/lib/types.ts` (extracted shared types) which the spec's data model section implies.