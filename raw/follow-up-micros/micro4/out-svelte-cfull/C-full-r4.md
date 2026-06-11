# Implementation Plan: Svelte Todo List

## Global Constraints

- Framework: Svelte with TypeScript
- Build tool: Vite (via `npm create vite@latest`)
- Test runner: Vitest with `@testing-library/svelte` and `jsdom`
- Data model: `Todo` = `{ id: string; text: string; completed: boolean }`
- Filter type: `Filter` = `'all' | 'active' | 'completed'`
- localStorage key: `'svelte-todos'`
- IDs generated via `crypto.randomUUID()`
- Component file structure exactly as specified in spec
- TDD: write failing test, see it fail, implement, see it pass, commit each cycle

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Project deps and scripts (created by scaffold) |
| `vite.config.ts` | Vite + Vitest config (jsdom, globals) |
| `vitest-setup.ts` | Testing-library jest-dom matchers setup |
| `tsconfig.json` | TypeScript config (from scaffold) |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte writable store + actions, syncs to storage |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear completed |
| `src/App.svelte` | Wires components together, holds filter state |
| `src/main.ts` | App mount point (from scaffold) |

---

### Task 1: Project scaffold and test infrastructure

**Files:** `package.json`, `vite.config.ts`, `vitest-setup.ts`, `src/lib/smoke.test.ts` (temporary)

**Interfaces:**
- Produces: working `npm test` command running Vitest with jsdom + jest-dom matchers.

Steps:

- [ ] Scaffold the project in the current directory:
  ```bash
  npm create vite@latest . -- --template svelte-ts
  ```
  If prompted about a non-empty directory, choose "Ignore files and continue".

- [ ] Install base dependencies:
  ```bash
  npm install
  ```

- [ ] Install test dependencies:
  ```bash
  npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
  ```

- [ ] Replace `vite.config.ts` with the following:
  ```typescript
  import { defineConfig } from 'vitest/config';
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

- [ ] Add a `test` script to `package.json` (in the `"scripts"` object):
  ```json
  "test": "vitest run",
  "test:watch": "vitest"
  ```

- [ ] Create a temporary smoke test `src/lib/smoke.test.ts`:
  ```typescript
  import { describe, it, expect } from 'vitest';

  describe('smoke', () => {
    it('runs vitest', () => {
      expect(1 + 1).toBe(2);
    });
  });
  ```

- [ ] Run the test and confirm it passes:
  ```bash
  npm test
  ```
  Expected output includes:
  ```
  ✓ src/lib/smoke.test.ts (1 test)
  Test Files  1 passed (1)
  ```

- [ ] Delete the smoke test:
  ```bash
  rm src/lib/smoke.test.ts
  ```

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Scaffold Svelte+TS project with Vitest"
  ```

---

### Task 2: Types and storage layer

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Produces:
  - `src/lib/types.ts`: `interface Todo { id: string; text: string; completed: boolean }` and `type Filter = 'all' | 'active' | 'completed'`
  - `src/lib/storage.ts`: `loadTodos(): Todo[]` and `saveTodos(todos: Todo[]): void`
  - Storage key constant `STORAGE_KEY = 'svelte-todos'`

Steps:

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

    it('saves and loads todos', () => {
      saveTodos(sample);
      expect(loadTodos()).toEqual(sample);
    });

    it('writes to the expected key', () => {
      saveTodos(sample);
      expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
    });

    it('returns empty array on corrupt data', () => {
      localStorage.setItem(STORAGE_KEY, '{not valid json');
      expect(loadTodos()).toEqual([]);
    });
  });
  ```

- [ ] Run and confirm failure (module not found):
  ```bash
  npm test
  ```
  Expected: failure referencing `./storage`.

- [ ] Implement `src/lib/storage.ts`:
  ```typescript
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

- [ ] Run and confirm pass:
  ```bash
  npm test
  ```
  Expected: `4 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add types and localStorage persistence"
  ```

---

### Task 3: Todo store with actions

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `loadTodos`, `saveTodos` from `storage.ts`.
- Produces `src/lib/store.ts`:
  - `todos`: Svelte `Writable<Todo[]>` initialized from `loadTodos()`, auto-saving on every change.
  - `addTodo(text: string): void` — trims text; ignores empty; appends `{ id: crypto.randomUUID(), text, completed: false }`.
  - `toggleTodo(id: string): void` — flips `completed`.
  - `deleteTodo(id: string): void` — removes by id.
  - `clearCompleted(): void` — removes all completed.

Steps:

- [ ] Write failing test `src/lib/store.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { get } from 'svelte/store';

  async function freshStore() {
    localStorage.clear();
    const mod = await import('./store?t=' + Date.now());
    return mod;
  }

  describe('store', () => {
    beforeEach(() => {
      localStorage.clear();
    });

    it('adds a trimmed todo', async () => {
      const { todos, addTodo } = await freshStore();
      addTodo('  hello  ');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('hello');
      expect(list[0].completed).toBe(false);
      expect(list[0].id).toBeTruthy();
    });

    it('ignores empty/whitespace todos', async () => {
      const { todos, addTodo } = await freshStore();
      addTodo('   ');
      expect(get(todos)).toHaveLength(0);
    });

    it('toggles completion', async () => {
      const { todos, addTodo, toggleTodo } = await freshStore();
      addTodo('a');
      const id = get(todos)[0].id;
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(true);
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(false);
    });

    it('deletes a todo', async () => {
      const { todos, addTodo, deleteTodo } = await freshStore();
      addTodo('a');
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

    it('persists to localStorage on change', async () => {
      const { addTodo } = await freshStore();
      addTodo('persist me');
      const raw = localStorage.getItem('svelte-todos');
      expect(raw).toContain('persist me');
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failure referencing `./store`.

- [ ] Implement `src/lib/store.ts`:
  ```typescript
  import { writable } from 'svelte/store';
  import type { Todo } from './types';
  import { loadTodos, saveTodos } from './storage';

  export const todos = writable<Todo[]>(loadTodos());

  todos.subscribe((value) => {
    saveTodos(value);
  });

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

- [ ] Run and confirm pass:
  ```bash
  npm test
  ```
  Expected: `6 passed` in this file.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add todos store with add/toggle/delete/clear actions"
  ```

---

### Task 4: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Produces `TodoInput.svelte`: dispatches a custom event `add` with `event.detail` being the entered string. Clears the input after dispatch. Triggers on Enter keypress or Add button click. Does not dispatch when input is empty/whitespace.

Steps:

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoInput from './TodoInput.svelte';

  describe('TodoInput', () => {
    it('dispatches add on button click and clears input', async () => {
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

    it('does not dispatch when empty', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', handler);

      await fireEvent.click(getByRole('button', { name: /add/i }));
      expect(handler).not.toHaveBeenCalled();
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failure referencing `./TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ add: string }>();
    let text = '';

    function submit() {
      if (!text.trim()) return;
      dispatch('add', text);
      text = '';
    }

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Enter') submit();
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

- [ ] Run and confirm pass:
  ```bash
  npm test
  ```
  Expected: `3 passed` in this file.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoInput component"
  ```

---

### Task 5: TodoItem component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`.
- Produces `TodoItem.svelte`:
  - Prop: `export let todo: Todo`.
  - Dispatches `toggle` with `detail` = `todo.id` when checkbox clicked.
  - Dispatches `delete` with `detail` = `todo.id` when delete button clicked.
  - Renders todo text; applies a `completed` class to text when `todo.completed`.

Steps:

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './types';

  const todo: Todo = { id: 'abc', text: 'Buy milk', completed: false };

  describe('TodoItem', () => {
    it('renders todo text', () => {
      const { getByText } = render(TodoItem, { props: { todo } });
      expect(getByText('Buy milk')).toBeInTheDocument();
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
      await fireEvent.click(getByRole('button', { name: /delete/i }));
      expect(handler).toHaveBeenCalledWith('abc');
    });

    it('reflects completed state on checkbox', () => {
      const done: Todo = { ...todo, completed: true };
      const { getByRole } = render(TodoItem, { props: { todo: done } });
      expect(getByRole('checkbox')).toBeChecked();
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failure referencing `./TodoItem.svelte`.

- [ ] Implement `src/lib/TodoItem.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Todo } from './types';

    export let todo: Todo;

    const dispatch = createEventDispatcher<{ toggle: string; delete: string }>();
  </script>

  <li class="todo-item">
    <input
      type="checkbox"
      checked={todo.completed}
      on:change={() => dispatch('toggle', todo.id)}
    />
    <span class:completed={todo.completed}>{todo.text}</span>
    <button aria-label="Delete" on:click={() => dispatch('delete', todo.id)}>
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
    span {
      flex: 1;
    }
    .completed {
      text-decoration: line-through;
      opacity: 0.6;
    }
  </style>
  ```

- [ ] Run and confirm pass:
  ```bash
  npm test
  ```
  Expected: `4 passed` in this file.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoItem component"
  ```

---

### Task 6: TodoList component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `TodoItem.svelte`.
- Produces `TodoList.svelte`:
  - Prop: `export let todos: Todo[]`.
  - Renders one `TodoItem` per todo inside a `<ul>`.
  - Re-dispatches `toggle` and `delete` events (with the same `detail` id) upward.
  - When `todos` is empty, renders an empty-state message containing "Nothing here yet".

Steps:

- [ ] Write failing test `src/lib/TodoList.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoList from './TodoList.svelte';
  import type { Todo } from './types';

  const todos: Todo[] = [
    { id: '1', text: 'one', completed: false },
    { id: '2', text: 'two', completed: true },
  ];

  describe('TodoList', () => {
    it('renders an item per todo', () => {
      const { getByText } = render(TodoList, { props: { todos } });
      expect(getByText('one')).toBeInTheDocument();
      expect(getByText('two')).toBeInTheDocument();
    });

    it('shows empty state when no todos', () => {
      const { getByText } = render(TodoList, { props: { todos: [] } });
      expect(getByText(/nothing here yet/i)).toBeInTheDocument();
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
      await fireEvent.click(getAllByRole('button', { name: /delete/i })[1]);
      expect(handler).toHaveBeenCalledWith('2');
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failure referencing `./TodoList.svelte`.

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
    <ul>
      {#each todos as todo (todo.id)}
        <TodoItem {todo} on:toggle on:delete />
      {/each}
    </ul>
  {/if}

  <style>
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .empty {
      text-align: center;
      color: #888;
      padding: 1rem 0;
    }
  </style>
  ```
  Note: `on:toggle on:delete` without a handler forwards the events upward with their original `detail`.

- [ ] Run and confirm pass:
  ```bash
  npm test
  ```
  Expected: `4 passed` in this file.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoList component with empty state"
  ```

---

### Task 7: FilterBar component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` from `types.ts`.
- Produces `FilterBar.svelte`:
  - Props: `export let filter: Filter` and `export let remaining: number`.
  - Renders `"{remaining} items left"` (use exact text including "left").
  - Renders three buttons labeled `All`, `Active`, `Completed`; clicking dispatches `filterChange` with `detail` = the corresponding `Filter` value.
  - Applies an `active` class to the button matching the current `filter`.
  - Renders a "Clear completed" button that dispatches `clearCompleted` (no detail).

Steps:

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
      expect(getByText('2 items left')).toBeInTheDocument();
    });

    it('dispatches filterChange with value', async () => {
      const { getByRole, component } = render(FilterBar, {
        props: { filter: 'all', remaining: 0 },
      });
      const handler = vi.fn();
      component.$on('filterChange', (e) => handler(e.detail));
      await fireEvent.click(getByRole('button', { name: /^active$/i }));
      expect(handler).toHaveBeenCalledWith('active');
    });

    it('marks the current filter active', () => {
      const { getByRole } = render(FilterBar, {
        props: { filter: 'completed', remaining: 0 },
      });
      expect(getByRole('button', { name: /^completed$/i })).toHaveClass('active');
    });

    it('dispatches clearCompleted', async () => {
      const { getByRole, component } = render(FilterBar, {
        props: { filter: 'all', remaining: 0 },
      });
      const handler = vi.fn();
      component.$on('clearCompleted', handler);
      await fireEvent.click(getByRole('button', { name: /clear completed/i }));
      expect(handler).toHaveBeenCalled();
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failure referencing `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import type { Filter } from './types';

    export let filter: Filter;
    export let remaining: number;

    const dispatch = createEventDispatcher<{
      filterChange: Filter;
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
    <span class="count">{remaining} items left</span>
    <div class="filters">
      {#each filters as f}
        <button
          class:active={filter === f}
          on:click={() => dispatch('filterChange', f)}
        >
          {labels[f]}
        </button>
      {/each}
    </div>
    <button on:click={() => dispatch('clearCompleted')}>Clear completed</button>
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
  npm test
  ```
  Expected: `4 passed` in this file.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add FilterBar component"
  ```

---

### Task 8: App integration

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: `todos`, `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted` from `store.ts`; `Filter` from `types.ts`; `TodoInput`, `TodoList`, `FilterBar` components.
- Produces: full wired `App.svelte` with local `filter` state defaulting to `'all'`, derived filtered list, and derived remaining count (incomplete todos).

Steps:

- [ ] Write failing test `src/App.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import App from './App.svelte';

  describe('App', () => {
    beforeEach(() => {
      localStorage.clear();
    });

    async function addTodo(getByRole: any, text: string) {
      const input = getByRole('textbox') as HTMLInputElement;
      await fireEvent.input(input, { target: { value: text } });
      await fireEvent.click(getByRole('button', { name: /^add$/i }));
    }

    it('adds a todo and shows it', async () => {
      const { getByRole, getByText } = render(App);
      await addTodo(getByRole, 'Buy milk');
      expect(getByText('Buy milk')).toBeInTheDocument();
    });

    it('updates remaining count', async () => {
      const { getByRole, getByText } = render(App);
      await addTodo(getByRole, 'a');
      await addTodo(getByRole, 'b');
      expect(getByText('2 items left')).toBeInTheDocument();
    });

    it('toggling updates the count', async () => {
      const { getByRole, getAllByRole, getByText } = render(App);
      await addTodo(getByRole, 'a');
      await fireEvent.click(getAllByRole('checkbox')[0]);
      expect(getByText('0 items left')).toBeInTheDocument();
    });

    it('filters to active only', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'keep');
      await addTodo(getByRole, 'done');
      await fireEvent.click(getAllByRole('checkbox')[1]);
      await fireEvent.click(getByRole('button', { name: /^active$/i }));
      expect(queryByText('keep')).toBeInTheDocument();
      expect(queryByText('done')).not.toBeInTheDocument();
    });

    it('filters to completed only', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'keep');
      await addTodo(getByRole, 'done');
      await fireEvent.click(getAllByRole('checkbox')[1]);
      await fireEvent.click(getByRole('button', { name: /^completed$/i }));
      expect(queryByText('done')).toBeInTheDocument();
      expect(queryByText('keep')).not.toBeInTheDocument();
    });

    it('deletes a todo', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'remove me');
      await fireEvent.click(getAllByRole('button', { name: /delete/i })[0]);
      expect(queryByText('remove me')).not.toBeInTheDocument();
    });

    it('clears completed todos', async () => {
      const { getByRole, getAllByRole, queryByText } = render(App);
      await addTodo(getByRole, 'a');
      await addTodo(getByRole, 'b');
      await fireEvent.click(getAllByRole('checkbox')[0]);
      await fireEvent.click(getByRole('button', { name: /clear completed/i }));
      expect(queryByText('a')).not.toBeInTheDocument();
      expect(queryByText('b')).toBeInTheDocument();
    });
  });
  ```

- [ ] Run and confirm failure:
  ```bash
  npm test
  ```
  Expected: failures in `App.test.ts` (current scaffold App has no todo UI).

- [ ] Replace `src/App.svelte` with:
  ```svelte
  <script lang="ts">
    import TodoInput from './lib/TodoInput.svelte';
    import TodoList from './lib/TodoList.svelte';
    import FilterBar from './lib/FilterBar.svelte';
    import {
      todos,
      addTodo,
      toggleTodo,
      deleteTodo,
      clearCompleted,
    } from './lib/store';
    import type { Filter } from './lib/types';

    let filter: Filter = 'all';

    $: filtered = $todos.filter((t) => {
      if (filter === 'active') return !t.completed;
      if (filter === 'completed') return t.completed;
      return true;
    });

    $: remaining = $todos.filter((t) => !t.completed).length;
  </script>

  <main>
    <h1>Svelte Todos</h1>
    <TodoInput on:add={(e) => addTodo(e.detail)} />
    <TodoList
      todos={filtered}
      on:toggle={(e) => toggleTodo(e.detail)}
      on:delete={(e) => deleteTodo(e.detail)}
    />
    <FilterBar
      {filter}
      {remaining}
      on:filterChange={(e) => (filter = e.detail)}
      on:clearCompleted={clearCompleted}
    />
  </main>

  <style>
    main {
      max-width: 480px;
      margin: 2rem auto;
      padding: 1rem;
      font-family: system-ui, sans-serif;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    h1 {
      text-align: center;
      margin: 0;
    }
  </style>
  ```

- [ ] Run and confirm all tests pass:
  ```bash
  npm test
  ```
  Expected: all test files pass, including `7 passed` in `App.test.ts`.

- [ ] Verify the app builds and runs manually:
  ```bash
  npm run dev
  ```
  Open the printed URL, add a todo, toggle it, refresh the page, and confirm it persists. Stop the dev server with Ctrl+C.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Wire App: integrate input, list, filters, store"
  ```

---

### Task 9: Production build verification

**Files:** none (verification only)

**Interfaces:**
- Consumes: complete app from Task 8.
- Produces: confirmed passing build and full test suite.

Steps:

- [ ] Run the full test suite:
  ```bash
  npm test
  ```
  Expected: all test files passing, `0 failed`.

- [ ] Run a production build: