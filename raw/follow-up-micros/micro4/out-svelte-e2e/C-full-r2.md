# Svelte Todo List - Implementation Plan

## Global Constraints

- Framework: Svelte (with TypeScript)
- Build tool: Vite (Svelte + TS template)
- Language: TypeScript for all `.ts` files and `<script lang="ts">` blocks
- Persistence: browser `localStorage` under key `svelte-todos`
- Unit/component tests: Vitest + `@testing-library/svelte`
- E2E tests: Playwright; `npx playwright test` must pass
- Data model (verbatim):
  ```typescript
  interface Todo {
    id: string;        // UUID
    text: string;      // Todo text
    completed: boolean;
  }
  type Filter = 'all' | 'active' | 'completed';
  ```
- File structure must match the spec exactly (`src/App.svelte`, `src/lib/*`)
- IDs generated with `crypto.randomUUID()`

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Vite + Svelte + Vitest config |
| `tsconfig.json` | TypeScript config |
| `playwright.config.ts` | Playwright config |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | `loadTodos()` / `saveTodos()` localStorage helpers |
| `src/lib/store.ts` | Svelte store + actions (add/toggle/delete/clearCompleted) |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo row (checkbox, text, delete) |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear completed |
| `src/App.svelte` | Wires components, holds filter state |
| `src/main.ts` | App mount |
| `tests/storage.test.ts` | Unit tests for storage |
| `tests/store.test.ts` | Unit tests for store |
| `tests/TodoInput.test.ts` | Component tests |
| `tests/TodoItem.test.ts` | Component tests |
| `tests/FilterBar.test.ts` | Component tests |
| `e2e/todos.spec.ts` | Playwright e2e tests |

---

### Task 1: Project Scaffold

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `src/main.ts`, `src/App.svelte`, `index.html`, `src/vite-env.d.ts`

**Interfaces:**
- Produces: a runnable Vite + Svelte + TS project; `npm run dev`, `npm run build`, `npm test` scripts; `src/App.svelte` placeholder component exporting nothing.

Steps:

- [ ] Create project directory and scaffold with Vite Svelte-TS template:
  ```bash
  npm create vite@latest svelte-todos -- --template svelte-ts
  cd svelte-todos
  ```
- [ ] Install base dependencies:
  ```bash
  npm install
  ```
- [ ] Install test dependencies:
  ```bash
  npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @playwright/test
  ```
- [ ] Replace `vite.config.ts` with config including Vitest:
  ```typescript
  /// <reference types="vitest" />
  import { defineConfig } from 'vite';
  import { svelte } from '@sveltejs/vite-plugin-svelte';

  export default defineConfig({
    plugins: [svelte({ hot: !process.env.VITEST })],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./tests/setup.ts'],
      include: ['tests/**/*.test.ts'],
    },
  });
  ```
- [ ] Create `tests/setup.ts`:
  ```typescript
  import '@testing-library/jest-dom';
  ```
- [ ] Set `package.json` scripts (merge into existing `"scripts"`):
  ```json
  {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "e2e": "playwright test"
  }
  ```
- [ ] Replace `src/App.svelte` with a minimal placeholder:
  ```svelte
  <script lang="ts">
  </script>

  <main>
    <h1>Svelte Todos</h1>
  </main>
  ```
- [ ] Remove default template clutter (`src/lib/Counter.svelte`, `src/assets`, default styles in `src/app.css` if present); keep `src/main.ts` mounting `App`.
- [ ] Verify dev build compiles:
  ```bash
  npm run build
  ```
  Expected: build completes with `✓ built in ...` and no errors.
- [ ] Verify test runner starts (no tests yet is OK):
  ```bash
  npm test
  ```
  Expected: `No test files found` or exit 0.
- [ ] Commit:
  ```bash
  git init && git add -A && git commit -m "Scaffold Svelte TS project with Vitest and Playwright"
  ```

---

### Task 2: Types

**Files:** `src/lib/types.ts`

**Interfaces:**
- Produces:
  ```typescript
  export interface Todo { id: string; text: string; completed: boolean; }
  export type Filter = 'all' | 'active' | 'completed';
  ```

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
- [ ] Type-check:
  ```bash
  npx tsc --noEmit
  ```
  Expected: no output, exit 0.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Todo and Filter types"
  ```

---

### Task 3: Storage

**Files:** `src/lib/storage.ts`, `tests/storage.test.ts`

**Interfaces:**
- Consumes: `Todo` from `src/lib/types.ts`.
- Produces:
  ```typescript
  export const STORAGE_KEY = 'svelte-todos';
  export function loadTodos(): Todo[];
  export function saveTodos(todos: Todo[]): void;
  ```
  `loadTodos` returns `[]` when nothing stored or on parse error.

Steps:

- [ ] Write failing test `tests/storage.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { loadTodos, saveTodos, STORAGE_KEY } from '../src/lib/storage';
  import type { Todo } from '../src/lib/types';

  const sample: Todo[] = [{ id: '1', text: 'a', completed: false }];

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
      expect(localStorage.getItem(STORAGE_KEY)).toEqual(JSON.stringify(sample));
    });

    it('returns empty array on corrupt data', () => {
      localStorage.setItem(STORAGE_KEY, 'not json');
      expect(loadTodos()).toEqual([]);
    });
  });
  ```
- [ ] Run to see it fail:
  ```bash
  npm test
  ```
  Expected: failure — `Cannot find module '../src/lib/storage'`.
- [ ] Implement `src/lib/storage.ts`:
  ```typescript
  import type { Todo } from './types';

  export const STORAGE_KEY = 'svelte-todos';

  export function loadTodos(): Todo[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
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
- [ ] Run to see it pass:
  ```bash
  npm test
  ```
  Expected: 4 passing tests.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add localStorage persistence helpers"
  ```

---

### Task 4: Store

**Files:** `src/lib/store.ts`, `tests/store.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `loadTodos`, `saveTodos` from `storage.ts`.
- Produces:
  ```typescript
  export const todos: Writable<Todo[]>;          // svelte writable, initialized from loadTodos()
  export function addTodo(text: string): void;   // ignores empty/whitespace-only text
  export function toggleTodo(id: string): void;
  export function deleteTodo(id: string): void;
  export function clearCompleted(): void;
  ```
  Every mutation persists via `saveTodos`. IDs from `crypto.randomUUID()`.

Steps:

- [ ] Write failing test `tests/store.test.ts`:
  ```typescript
  import { describe, it, expect, beforeEach } from 'vitest';
  import { get } from 'svelte/store';

  async function freshStore() {
    localStorage.clear();
    vi.resetModules();
    return await import('../src/lib/store');
  }

  import { vi } from 'vitest';

  describe('store', () => {
    beforeEach(() => localStorage.clear());

    it('adds a todo', async () => {
      const { todos, addTodo } = await freshStore();
      addTodo('Buy milk');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0]).toMatchObject({ text: 'Buy milk', completed: false });
      expect(typeof list[0].id).toBe('string');
    });

    it('ignores empty text', async () => {
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
      deleteTodo(get(todos)[0].id);
      expect(get(todos)).toHaveLength(0);
    });

    it('clears completed', async () => {
      const { todos, addTodo, toggleTodo, clearCompleted } = await freshStore();
      addTodo('a');
      addTodo('b');
      toggleTodo(get(todos)[0].id);
      clearCompleted();
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('b');
    });

    it('persists to localStorage', async () => {
      const { addTodo } = await freshStore();
      addTodo('persist me');
      expect(localStorage.getItem('svelte-todos')).toContain('persist me');
    });
  });
  ```
- [ ] Run to see it fail:
  ```bash
  npm test
  ```
  Expected: failure — cannot find `../src/lib/store`.
- [ ] Implement `src/lib/store.ts`:
  ```typescript
  import { writable } from 'svelte/store';
  import type { Todo } from './types';
  import { loadTodos, saveTodos } from './storage';

  export const todos = writable<Todo[]>(loadTodos());

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
- [ ] Run to see it pass:
  ```bash
  npm test
  ```
  Expected: store tests + storage tests all passing.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add todos store with add/toggle/delete/clearCompleted"
  ```

---

### Task 5: TodoInput Component

**Files:** `src/lib/TodoInput.svelte`, `tests/TodoInput.test.ts`

**Interfaces:**
- Produces: `TodoInput.svelte` dispatching a CustomEvent `add` with `detail: string` (trimmed text) when Enter pressed or Add clicked; clears the input afterward; does not dispatch for empty input.

Steps:

- [ ] Write failing test `tests/TodoInput.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoInput from '../src/lib/TodoInput.svelte';

  describe('TodoInput', () => {
    it('dispatches add on button click', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', (e) => handler(e.detail));
      const input = getByRole('textbox');
      await fireEvent.input(input, { target: { value: 'New task' } });
      await fireEvent.click(getByRole('button', { name: /add/i }));
      expect(handler).toHaveBeenCalledWith('New task');
    });

    it('dispatches add on Enter', async () => {
      const { getByRole, component } = render(TodoInput);
      const handler = vi.fn();
      component.$on('add', (e) => handler(e.detail));
      const input = getByRole('textbox');
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

    it('clears input after add', async () => {
      const { getByRole } = render(TodoInput);
      const input = getByRole('textbox') as HTMLInputElement;
      await fireEvent.input(input, { target: { value: 'Clear me' } });
      await fireEvent.click(getByRole('button', { name: /add/i }));
      expect(input.value).toBe('');
    });
  });
  ```
- [ ] Run to see it fail:
  ```bash
  npm test -- tests/TodoInput.test.ts
  ```
  Expected: failure — cannot find component module.
- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher<{ add: string }>();
    let value = '';

    function submit() {
      const trimmed = value.trim();
      if (!trimmed) return;
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
  npm test -- tests/TodoInput.test.ts
  ```
  Expected: 4 passing tests.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoInput component"
  ```

---

### Task 6: TodoItem Component

**Files:** `src/lib/TodoItem.svelte`, `tests/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`.
- Produces: `TodoItem.svelte` with prop `todo: Todo`; dispatches `toggle` (detail `string` id) when checkbox clicked and `delete` (detail `string` id) when delete button clicked. Renders text; applies `completed` class when `todo.completed`.

Steps:

- [ ] Write failing test `tests/TodoItem.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import TodoItem from '../src/lib/TodoItem.svelte';
  import type { Todo } from '../src/lib/types';

  const todo: Todo = { id: 'abc', text: 'Walk dog', completed: false };

  describe('TodoItem', () => {
    it('renders text', () => {
      const { getByText } = render(TodoItem, { props: { todo } });
      expect(getByText('Walk dog')).toBeInTheDocument();
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

    it('checkbox reflects completed state', () => {
      const { getByRole } = render(TodoItem, {
        props: { todo: { ...todo, completed: true } },
      });
      expect(getByRole('checkbox')).toBeChecked();
    });
  });
  ```
- [ ] Run to see it fail:
  ```bash
  npm test -- tests/TodoItem.test.ts
  ```
  Expected: failure — cannot find component module.
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
      x
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
  npm test -- tests/TodoItem.test.ts
  ```
  Expected: 4 passing tests.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoItem component"
  ```

---

### Task 7: TodoList Component

**Files:** `src/lib/TodoList.svelte`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `TodoItem.svelte`.
- Produces: `TodoList.svelte` with prop `todos: Todo[]`; forwards `toggle` and `delete` events from each `TodoItem`. Shows empty-state message `No todos yet. Add one above!` when `todos.length === 0`.

Steps:

- [ ] Implement `src/lib/TodoList.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';
    import TodoItem from './TodoItem.svelte';

    export let todos: Todo[];
  </script>

  {#if todos.length === 0}
    <p class="empty">No todos yet. Add one above!</p>
  {:else}
    <ul class="todo-list">
      {#each todos as todo (todo.id)}
        <TodoItem {todo} on:toggle on:delete />
      {/each}
    </ul>
  {/if}
  ```
- [ ] Type-check:
  ```bash
  npx tsc --noEmit
  ```
  Expected: no errors. (Run `npm run build` if `tsc` does not parse `.svelte`.)
- [ ] Build to confirm Svelte compiles the component:
  ```bash
  npm run build
  ```
  Expected: build succeeds.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoList component with empty state"
  ```

---

### Task 8: FilterBar Component

**Files:** `src/lib/FilterBar.svelte`, `tests/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` from `types.ts`.
- Produces: `FilterBar.svelte` with props `filter: Filter` and `remaining: number`. Dispatches `filterChange` (detail `Filter`) when a filter button clicked and `clearCompleted` (no detail) when Clear clicked. Renders `{remaining} items left`, three filter buttons (`All`, `Active`, `Completed`), and a `Clear completed` button. Active filter button has class `active`.

Steps:

- [ ] Write failing test `tests/FilterBar.test.ts`:
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  import { render, fireEvent } from '@testing-library/svelte';
  import FilterBar from '../src/lib/FilterBar.svelte';

  describe('FilterBar', () => {
    it('shows remaining count', () => {
      const { getByText } = render(FilterBar, {
        props: { filter: 'all', remaining: 2 },
      });
      expect(getByText('2 items left')).toBeInTheDocument();
    });

    it('dispatches filterChange', async () => {
      const { getByRole, component } = render(FilterBar, {
        props: { filter: 'all', remaining: 0 },
      });
      const handler = vi.fn();
      component.$on('filterChange', (e) => handler(e.detail));
      await fireEvent.click(getByRole('button', { name: 'Active' }));
      expect(handler).toHaveBeenCalledWith('active');
    });

    it('marks current filter active', () => {
      const { getByRole } = render(FilterBar, {
        props: { filter: 'completed', remaining: 0 },
      });
      expect(getByRole('button', { name: 'Completed' })).toHaveClass('active');
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
- [ ] Run to see it fail:
  ```bash
  npm test -- tests/FilterBar.test.ts
  ```
  Expected: failure — cannot find component module.
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
    <button class="clear" on:click={() => dispatch('clearCompleted')}>
      Clear completed
    </button>
  </div>
  ```
- [ ] Run to see it pass:
  ```bash
  npm test -- tests/FilterBar.test.ts
  ```
  Expected: 4 passing tests.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add FilterBar component"
  ```

---

### Task 9: App Wiring

**Files:** `src/App.svelte`

**Interfaces:**
- Consumes: `todos` store and `addTodo`/`toggleTodo`/`deleteTodo`/`clearCompleted` from `store.ts`; `Filter` from `types.ts`; `TodoInput`, `TodoList`, `FilterBar` components.
- Produces: full app. Holds local `filter: Filter` (default `'all'`). Computes `filtered` todos and `remaining` count reactively. Wires component events to store actions.

Steps:

- [ ] Implement `src/App.svelte`:
  ```svelte
  <script lang="ts">
    import { todos, addTodo, toggleTodo, deleteTodo, clearCompleted } from './lib/store';
    import type { Filter } from './lib/types';
    import TodoInput from './lib/TodoInput.svelte';
    import TodoList from './lib/TodoList.svelte';
    import FilterBar from './lib/FilterBar.svelte';

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
      font-family: sans-serif;
    }
  </style>
  ```
- [ ] Build and run dev server, manually verify in browser:
  ```bash
  npm run build && npm run dev
  ```
  Expected: build succeeds; at the dev URL you can add, toggle, delete, filter todos, and they survive a refresh.
- [ ] Run full unit suite:
  ```bash
  npm test
  ```
  Expected: all component/unit tests pass.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Wire App with store, filtering, and components"
  ```

---

### Task 10: Playwright E2E

**Files:** `playwright.config.ts`, `e2e/todos.spec.ts`

**Interfaces:**
- Consumes: running app via Vite preview server.
- Produces: e2e tests covering add, complete, delete, filter, persistence-across-reload. `npx playwright test` passes.

Steps:

- [ ] Install browsers:
  ```bash
  npx playwright install --with-deps chromium
  ```
- [ ] Create `playwright.config.ts`:
  ```typescript
  import { defineConfig } from '@playwright/test';

  export default defineConfig({
    testDir: './e2e',
    use: { baseURL: 'http://localhost:4173' },
    webServer: {
      command: 'npm run build && npm run preview -- --port 4173',
      url: 'http://localhost:4173',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  });
  ```
- [ ] Create `e2e/todos.spec.ts`:
  ```typescript
  import { test, expect } from '@playwright/test';

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('add a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Buy groceries');
    await page.getByRole('button', { name: 'Add' }).click();
    await expect(page.getByText('Buy groceries')).toBeVisible();
    await expect(page.getByText('1 items left')).toBeVisible();
  });

  test('complete a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Walk the dog');
    await page.getByRole('button', { name: 'Add' }).click();
    await page.getByRole('checkbox').click();
    await expect(page.getByRole('checkbox')).toBeChecked();
    await expect(page.getByText('0 items left')).toBeVisible();
  });

  test('delete a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Temp');
    await page.getByRole('button', { name: 'Add' }).click();
    await page.getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByText('No todos yet. Add one above!')).toBeVisible();
  });

  test('filter todos', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Active task');
    await page.getByRole('button', { name: 'Add' }).click();
    await input.fill('Done task');
    await page.getByRole('button', { name: 'Add' }).click();
    await page.getByRole('checkbox').last().click();

    await page.getByRole('button', { name: 'Active' }).click();
    await expect(page.getByText('Active task')).toBeVisible();
    await expect(page.getByText('Done task')).toHaveCount(0);

    await page.getByRole('button', { name: 'Completed' }).click();
    await expect(page.getByText('Done task')).toBeVisible();
    await expect(page.getByText('Active task')).toHaveCount(0);
  });

  test('clear completed', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Keep me');
    await page.getByRole('button', { name: 'Add' }).click();
    await input.fill('Remove me');
    await page.getByRole('button', { name: 'Add' }).click();
    await page.getByRole('checkbox').last().click();
    await page.getByRole('button', { name: /clear completed/i }).click();
    await expect(page.getByText('Remove me')).toHaveCount(0);
    await expect(page.getByText('Keep me')).toBeVisible();
  });

  test('persists across reload', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Persistent');
    await page.getByRole('button', { name: 'Add' }).click();
    await page.reload();
    await expect(page.getByText('Persistent')).toBeVisible();
  });
  ```
- [ ] Run e2e:
  ```bash
  npx playwright test
  ```
  Expected: `6 passed`.
- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Playwright e2e tests"
  ```

---

### Task 11: Final Verification

**Files:** none (verification only)

Steps:

- [ ] Run the complete unit suite:
  ```bash
  npm test
  ```
  Expected: all tests pass, exit 0.
- [ ] Run e2e suite:
  ```bash
  npx playwright test
  ```
  Expected: `6 passed`.
- [ ] Production build:
  ```bash
  npm run build
  ```
  Expected: build succeeds with no errors.
- [ ] Commit any final cleanup:
  ```bash
  git add -A && git commit -m "Final verification" --allow-empty
  ```

---

## Self-Review

- **Spec coverage:**
  1. Add via Enter/Add → Task 5 + e2e Task 10 ✓
  2. Toggle via checkbox → Task 6 + e2e ✓
  3. Delete via X → Task 6 + e2e ✓
  4. Filter subsets → Task 8/9 + e2e ✓
  5. "X items left" → Task 8/9 (`remaining`) + e2e ✓
  6. Clear completed → Task 4/8/9 + e2e ✓
  7. Persistence → Task 3/4 