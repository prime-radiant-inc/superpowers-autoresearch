# Svelte Todo List — Implementation Plan

## Global Constraints

- Framework: Svelte (with Vite + TypeScript template, `svelte` + `vite`)
- Language: TypeScript for all `.ts` files and `<script lang="ts">` in components
- Data model: `Todo` = `{ id: string; text: string; completed: boolean }`
- `id` must be a UUID (use `crypto.randomUUID()`)
- Filter type: `Filter` = `'all' | 'active' | 'completed'`
- localStorage key: `svelte-todos`
- Unit/component tests: Vitest + `@testing-library/svelte` + jsdom
- E2E tests: Playwright — `npx playwright test` must pass
- Empty state must show a helpful message when there are no todos to display
- Component file locations exactly as in spec (`src/App.svelte`, `src/lib/*.svelte`, `src/lib/store.ts`, `src/lib/storage.ts`)

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Dependencies, scripts |
| `vite.config.ts` | Vite + Svelte + Vitest config |
| `tsconfig.json` | TypeScript config |
| `playwright.config.ts` | Playwright config |
| `index.html` | App entry HTML |
| `src/main.ts` | Mounts `App.svelte` |
| `src/app.d.ts` / `src/vite-env.d.ts` | Type declarations |
| `src/lib/types.ts` | `Todo` and `Filter` types |
| `src/lib/storage.ts` | localStorage load/save |
| `src/lib/store.ts` | Svelte writable store + actions, derived filtered list & count |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo (checkbox, text, delete) |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Filter buttons + count + clear completed |
| `src/App.svelte` | Composition of all components |
| `tests/*.test.ts` | Vitest unit/component tests (co-located naming) |
| `e2e/todo.spec.ts` | Playwright end-to-end tests |

---

### Task 1: Project scaffolding & tooling

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.ts`, `src/App.svelte`, `src/vite-env.d.ts`

**Interfaces:**
- Produces: a runnable Vite+Svelte+TS project; `npm test` (Vitest) runnable; `App.svelte` default export mountable.

**Steps:**

- [ ] Create the project directory and initialize:
  ```bash
  npm create vite@latest . -- --template svelte-ts
  ```
  When prompted about a non-empty directory, choose to proceed (or run in an empty dir then move files). Expected: scaffolded files appear.

- [ ] Install base deps:
  ```bash
  npm install
  ```
  Expected: `node_modules` created, no errors.

- [ ] Install test tooling:
  ```bash
  npm install -D vitest @testing-library/svelte @testing-library/jest-dom jsdom @playwright/test
  npx playwright install
  ```
  Expected: installs succeed; Playwright browsers downloaded.

- [ ] Replace `vite.config.ts` with Vitest-enabled config:
  ```ts
  import { defineConfig } from 'vite';
  import { svelte } from '@sveltejs/vite-plugin-svelte';

  export default defineConfig({
    plugins: [svelte({ hot: !process.env.VITEST })],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./vitest-setup.ts'],
      include: ['tests/**/*.test.ts'],
    },
  });
  ```

- [ ] Create `vitest-setup.ts`:
  ```ts
  import '@testing-library/jest-dom/vitest';
  ```

- [ ] Add scripts to `package.json` (`"scripts"` block):
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

- [ ] Create `tests/smoke.test.ts`:
  ```ts
  import { render, screen } from '@testing-library/svelte';
  import App from '../src/App.svelte';
  import { test, expect } from 'vitest';

  test('renders title', () => {
    render(App);
    expect(screen.getByText('Svelte Todos')).toBeInTheDocument();
  });
  ```

- [ ] Run the smoke test:
  ```bash
  npm test
  ```
  Expected: `1 passed`.

- [ ] Verify dev server boots:
  ```bash
  npm run dev
  ```
  Expected: Vite prints a local URL; stop with Ctrl-C.

- [ ] Commit:
  ```bash
  git init && git add -A && git commit -m "Scaffold Svelte+TS project with Vitest and Playwright"
  ```

---

### Task 2: Types & storage module

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `tests/storage.test.ts`

**Interfaces:**
- Produces `src/lib/types.ts`:
  ```ts
  export interface Todo { id: string; text: string; completed: boolean; }
  export type Filter = 'all' | 'active' | 'completed';
  ```
- Produces `src/lib/storage.ts`:
  ```ts
  export function loadTodos(): Todo[];        // returns [] if nothing/invalid
  export function saveTodos(todos: Todo[]): void;
  export const STORAGE_KEY = 'svelte-todos';
  ```

**Steps:**

- [ ] Create `src/lib/types.ts`:
  ```ts
  export interface Todo {
    id: string;
    text: string;
    completed: boolean;
  }

  export type Filter = 'all' | 'active' | 'completed';
  ```

- [ ] Write failing test `tests/storage.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { loadTodos, saveTodos, STORAGE_KEY } from '../src/lib/storage';
  import type { Todo } from '../src/lib/types';

  beforeEach(() => localStorage.clear());

  test('loadTodos returns [] when empty', () => {
    expect(loadTodos()).toEqual([]);
  });

  test('loadTodos returns [] on invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not json');
    expect(loadTodos()).toEqual([]);
  });

  test('saveTodos then loadTodos round-trips', () => {
    const todos: Todo[] = [{ id: 'a', text: 'x', completed: false }];
    saveTodos(todos);
    expect(loadTodos()).toEqual(todos);
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- storage
  ```
  Expected: failure — cannot import from `storage`.

- [ ] Implement `src/lib/storage.ts`:
  ```ts
  import type { Todo } from './types';

  export const STORAGE_KEY = 'svelte-todos';

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

- [ ] Run to see it pass:
  ```bash
  npm test -- storage
  ```
  Expected: `3 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Todo types and localStorage persistence"
  ```

---

### Task 3: Todo store with actions, filter, and derived count

**Files:** `src/lib/store.ts`, `tests/store.test.ts`

**Interfaces:**
- Consumes: `Todo`, `Filter` from `types.ts`; `loadTodos`/`saveTodos` from `storage.ts`.
- Produces `src/lib/store.ts`:
  ```ts
  export const todos: Writable<Todo[]>;        // auto-persists on change
  export const filter: Writable<Filter>;        // default 'all'
  export const filteredTodos: Readable<Todo[]>; // todos filtered by filter
  export const remainingCount: Readable<number>;// count of !completed
  export function addTodo(text: string): void;  // ignores empty/whitespace; trims
  export function toggleTodo(id: string): void;
  export function deleteTodo(id: string): void;
  export function clearCompleted(): void;
  export function setFilter(f: Filter): void;
  ```

**Steps:**

- [ ] Write failing test `tests/store.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { get } from 'svelte/store';
  import {
    todos, filter, filteredTodos, remainingCount,
    addTodo, toggleTodo, deleteTodo, clearCompleted, setFilter,
  } from '../src/lib/store';

  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
    setFilter('all');
  });

  test('addTodo adds a trimmed todo with uuid', () => {
    addTodo('  Buy milk  ');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy milk');
    expect(list[0].completed).toBe(false);
    expect(list[0].id).toMatch(/[0-9a-f-]{36}/);
  });

  test('addTodo ignores empty/whitespace', () => {
    addTodo('   ');
    expect(get(todos)).toHaveLength(0);
  });

  test('toggleTodo flips completed', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  test('deleteTodo removes the todo', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  test('remainingCount counts incomplete todos', () => {
    addTodo('a'); addTodo('b');
    toggleTodo(get(todos)[0].id);
    expect(get(remainingCount)).toBe(1);
  });

  test('filteredTodos respects filter', () => {
    addTodo('a'); addTodo('b');
    toggleTodo(get(todos)[0].id);
    setFilter('active');
    expect(get(filteredTodos)).toHaveLength(1);
    setFilter('completed');
    expect(get(filteredTodos)).toHaveLength(1);
    setFilter('all');
    expect(get(filteredTodos)).toHaveLength(2);
  });

  test('clearCompleted removes completed todos', () => {
    addTodo('a'); addTodo('b');
    toggleTodo(get(todos)[0].id);
    clearCompleted();
    expect(get(todos)).toHaveLength(1);
    expect(get(todos)[0].completed).toBe(false);
  });

  test('changes persist to storage', () => {
    addTodo('persist me');
    expect(localStorage.getItem('svelte-todos')).toContain('persist me');
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- store
  ```
  Expected: failure — cannot import from `store`.

- [ ] Implement `src/lib/store.ts`:
  ```ts
  import { writable, derived, get } from 'svelte/store';
  import type { Todo, Filter } from './types';
  import { loadTodos, saveTodos } from './storage';

  export const todos = writable<Todo[]>(loadTodos());
  todos.subscribe((value) => saveTodos(value));

  export const filter = writable<Filter>('all');

  export const filteredTodos = derived([todos, filter], ([$todos, $filter]) => {
    if ($filter === 'active') return $todos.filter((t) => !t.completed);
    if ($filter === 'completed') return $todos.filter((t) => t.completed);
    return $todos;
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

  export function setFilter(f: Filter): void {
    filter.set(f);
  }
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- store
  ```
  Expected: all store tests pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add todo store with actions, filter and derived count"
  ```

---

### Task 4: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `tests/TodoInput.test.ts`

**Interfaces:**
- Consumes: `addTodo` from `store.ts`.
- Produces `TodoInput.svelte`: renders `<input>` (placeholder "What needs to be done?") and an "Add" button. Pressing Enter or clicking Add calls `addTodo(value)` and clears the input.

**Steps:**

- [ ] Write failing test `tests/TodoInput.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import { get } from 'svelte/store';
  import TodoInput from '../src/lib/TodoInput.svelte';
  import { todos } from '../src/lib/store';

  beforeEach(() => { localStorage.clear(); todos.set([]); });

  test('clicking Add adds a todo and clears input', async () => {
    render(TodoInput);
    const input = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'New task' } });
    await fireEvent.click(screen.getByText('Add'));
    expect(get(todos)).toHaveLength(1);
    expect(input.value).toBe('');
  });

  test('pressing Enter adds a todo', async () => {
    render(TodoInput);
    const input = screen.getByPlaceholderText('What needs to be done?');
    await fireEvent.input(input, { target: { value: 'Via enter' } });
    await fireEvent.keyDown(input, { key: 'Enter' });
    expect(get(todos)).toHaveLength(1);
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoInput
  ```
  Expected: failure — component file missing.

- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    import { addTodo } from './store';
    let value = '';

    function submit() {
      addTodo(value);
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
  Expected: `2 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoInput component"
  ```

---

### Task 5: TodoItem component

**Files:** `src/lib/TodoItem.svelte`, `tests/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `toggleTodo`, `deleteTodo` from `store.ts`.
- Produces `TodoItem.svelte` with prop `export let todo: Todo`. Renders a checkbox (checked = `todo.completed`), the text, and a delete button (label "x", `aria-label="Delete"`). Checkbox change → `toggleTodo(todo.id)`; delete click → `deleteTodo(todo.id)`.

**Steps:**

- [ ] Write failing test `tests/TodoItem.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import { get } from 'svelte/store';
  import TodoItem from '../src/lib/TodoItem.svelte';
  import { todos } from '../src/lib/store';
  import type { Todo } from '../src/lib/types';

  const sample: Todo = { id: '1', text: 'Walk dog', completed: false };

  beforeEach(() => { localStorage.clear(); todos.set([{ ...sample }]); });

  test('renders text and unchecked checkbox', () => {
    render(TodoItem, { todo: { ...sample } });
    expect(screen.getByText('Walk dog')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).not.toBeChecked();
  });

  test('checkbox toggles completion', async () => {
    render(TodoItem, { todo: { ...sample } });
    await fireEvent.click(screen.getByRole('checkbox'));
    expect(get(todos)[0].completed).toBe(true);
  });

  test('delete button removes todo', async () => {
    render(TodoItem, { todo: { ...sample } });
    await fireEvent.click(screen.getByLabelText('Delete'));
    expect(get(todos)).toHaveLength(0);
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoItem
  ```
  Expected: failure — component missing.

- [ ] Implement `src/lib/TodoItem.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';
    import { toggleTodo, deleteTodo } from './store';
    export let todo: Todo;
  </script>

  <li class="todo-item" class:completed={todo.completed}>
    <input
      type="checkbox"
      checked={todo.completed}
      on:change={() => toggleTodo(todo.id)}
    />
    <span class="text">{todo.text}</span>
    <button class="delete" aria-label="Delete" on:click={() => deleteTodo(todo.id)}>x</button>
  </li>

  <style>
    .completed .text { text-decoration: line-through; opacity: 0.6; }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoItem
  ```
  Expected: `3 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoItem component"
  ```

---

### Task 6: TodoList component with empty state

**Files:** `src/lib/TodoList.svelte`, `tests/TodoList.test.ts`

**Interfaces:**
- Consumes: `filteredTodos` from `store.ts`; `TodoItem.svelte`.
- Produces `TodoList.svelte`: renders a `<ul>` of `TodoItem` for each filtered todo; when empty renders an empty-state message `No todos yet — add one above!`.

**Steps:**

- [ ] Write failing test `tests/TodoList.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import TodoList from '../src/lib/TodoList.svelte';
  import { todos, setFilter } from '../src/lib/store';

  beforeEach(() => { localStorage.clear(); todos.set([]); setFilter('all'); });

  test('shows empty state when no todos', () => {
    render(TodoList);
    expect(screen.getByText('No todos yet — add one above!')).toBeInTheDocument();
  });

  test('renders one item per filtered todo', () => {
    todos.set([
      { id: '1', text: 'a', completed: false },
      { id: '2', text: 'b', completed: true },
    ]);
    render(TodoList);
    expect(screen.getByText('a')).toBeInTheDocument();
    expect(screen.getByText('b')).toBeInTheDocument();
    expect(screen.queryByText('No todos yet — add one above!')).not.toBeInTheDocument();
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoList
  ```
  Expected: failure — component missing.

- [ ] Implement `src/lib/TodoList.svelte`:
  ```svelte
  <script lang="ts">
    import { filteredTodos } from './store';
    import TodoItem from './TodoItem.svelte';
  </script>

  {#if $filteredTodos.length === 0}
    <p class="empty">No todos yet — add one above!</p>
  {:else}
    <ul class="todo-list">
      {#each $filteredTodos as todo (todo.id)}
        <TodoItem {todo} />
      {/each}
    </ul>
  {/if}
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoList
  ```
  Expected: `2 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoList component with empty state"
  ```

---

### Task 7: FilterBar component

**Files:** `src/lib/FilterBar.svelte`, `tests/FilterBar.test.ts`

**Interfaces:**
- Consumes: `filter`, `remainingCount`, `setFilter`, `clearCompleted` from `store.ts`.
- Produces `FilterBar.svelte`: shows "`N` items left" (using `remainingCount`); three filter buttons "All"/"Active"/"Completed" (active one has class `active`); a "Clear completed" button calling `clearCompleted`.

**Steps:**

- [ ] Write failing test `tests/FilterBar.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import { get } from 'svelte/store';
  import FilterBar from '../src/lib/FilterBar.svelte';
  import { todos, filter, setFilter } from '../src/lib/store';

  beforeEach(() => {
    localStorage.clear();
    todos.set([
      { id: '1', text: 'a', completed: false },
      { id: '2', text: 'b', completed: true },
    ]);
    setFilter('all');
  });

  test('shows remaining count', () => {
    render(FilterBar);
    expect(screen.getByText('1 items left')).toBeInTheDocument();
  });

  test('clicking Active sets filter', async () => {
    render(FilterBar);
    await fireEvent.click(screen.getByText('Active'));
    expect(get(filter)).toBe('active');
  });

  test('Clear completed removes completed todos', async () => {
    render(FilterBar);
    await fireEvent.click(screen.getByText('Clear completed'));
    expect(get(todos)).toHaveLength(1);
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- FilterBar
  ```
  Expected: failure — component missing.

- [ ] Implement `src/lib/FilterBar.svelte`:
  ```svelte
  <script lang="ts">
    import { filter, remainingCount, setFilter, clearCompleted } from './store';
    import type { Filter } from './types';

    const filters: Filter[] = ['all', 'active', 'completed'];
    const labels: Record<Filter, string> = {
      all: 'All', active: 'Active', completed: 'Completed',
    };
  </script>

  <div class="filter-bar">
    <span class="count">{$remainingCount} items left</span>
    <div class="filters">
      {#each filters as f}
        <button class:active={$filter === f} on:click={() => setFilter(f)}>
          {labels[f]}
        </button>
      {/each}
    </div>
    <button class="clear" on:click={clearCompleted}>Clear completed</button>
  </div>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- FilterBar
  ```
  Expected: `3 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add FilterBar component"
  ```

---

### Task 8: App composition

**Files:** `src/App.svelte`, `tests/App.test.ts`

**Interfaces:**
- Consumes: `TodoInput`, `TodoList`, `FilterBar`.
- Produces: final `App.svelte` composing title "Svelte Todos" + the three components.

**Steps:**

- [ ] Replace `tests/smoke.test.ts` content with `tests/App.test.ts` (delete smoke file):
  ```bash
  git rm tests/smoke.test.ts
  ```

- [ ] Write failing test `tests/App.test.ts`:
  ```ts
  import { beforeEach, test, expect } from 'vitest';
  import { render, screen, fireEvent } from '@testing-library/svelte';
  import App from '../src/App.svelte';
  import { todos } from '../src/lib/store';

  beforeEach(() => { localStorage.clear(); todos.set([]); });

  test('full flow: add, see in list, count updates', async () => {
    render(App);
    expect(screen.getByText('Svelte Todos')).toBeInTheDocument();

    const input = screen.getByPlaceholderText('What needs to be done?');
    await fireEvent.input(input, { target: { value: 'Buy groceries' } });
    await fireEvent.click(screen.getByText('Add'));

    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('1 items left')).toBeInTheDocument();
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- App
  ```
  Expected: failure — App lacks the composed components.

- [ ] Implement `src/App.svelte`:
  ```svelte
  <script lang="ts">
    import TodoInput from './lib/TodoInput.svelte';
    import TodoList from './lib/TodoList.svelte';
    import FilterBar from './lib/FilterBar.svelte';
  </script>

  <main>
    <h1>Svelte Todos</h1>
    <TodoInput />
    <TodoList />
    <FilterBar />
  </main>

  <style>
    main { max-width: 480px; margin: 2rem auto; font-family: system-ui, sans-serif; }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- App
  ```
  Expected: `1 passed`.

- [ ] Run the full unit suite:
  ```bash
  npm test
  ```
  Expected: all tests across all files pass.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Compose App from components"
  ```

---

### Task 9: Playwright end-to-end tests

**Files:** `playwright.config.ts`, `e2e/todo.spec.ts`

**Interfaces:**
- Consumes: the running dev server (started by Playwright `webServer`).
- Produces: passing `npx playwright test` covering add, complete, delete, filter, persistence-across-reload.

**Steps:**

- [ ] Create `playwright.config.ts`:
  ```ts
  import { defineConfig } from '@playwright/test';

  export default defineConfig({
    testDir: './e2e',
    use: { baseURL: 'http://localhost:5173' },
    webServer: {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
    },
  });
  ```

- [ ] Create `e2e/todo.spec.ts`:
  ```ts
  import { test, expect } from '@playwright/test';

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('add a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Buy groceries');
    await page.getByText('Add').click();
    await expect(page.getByText('Buy groceries')).toBeVisible();
    await expect(page.getByText('1 items left')).toBeVisible();
  });

  test('complete a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Walk dog');
    await page.getByText('Add').click();
    await page.getByRole('checkbox').check();
    await expect(page.getByText('0 items left')).toBeVisible();
  });

  test('delete a todo', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Temp');
    await page.getByText('Add').click();
    await page.getByLabel('Delete').click();
    await expect(page.getByText('No todos yet — add one above!')).toBeVisible();
  });

  test('filter shows correct subset', async ({ page }) => {
    const input = page.getByPlaceholder('What needs to be done?');
    await input.fill('Task A'); await page.getByText('Add').click();
    await input.fill('Task B'); await page.getByText('Add').click();
    await page.getByRole('checkbox').first().check();

    await page.getByRole('button', { name: 'Active' }).click();
    await expect(page.getByText('Task A')).toBeHidden();
    await expect(page.getByText('Task B')).toBeVisible();

    await page.getByRole('button', { name: 'Completed' }).click();
    await expect(page.getByText('Task A')).toBeVisible();
    await expect(page.getByText('Task B')).toBeHidden();
  });

  test('persists across reload', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('Persist me');
    await page.getByText('Add').click();
    await page.reload();
    await expect(page.getByText('Persist me')).toBeVisible();
  });
  ```

- [ ] Run the e2e suite:
  ```bash
  npx playwright test
  ```
  Expected: `5 passed`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add Playwright end-to-end tests"
  ```

---

### Task 10: Final verification

**Files:** none (verification only)

**Steps:**

- [ ] Run full unit suite:
  ```bash
  npm test
  ```
  Expected: all pass.

- [ ] Run e2e suite:
  ```bash
  npx playwright test
  ```
  Expected: all pass.

- [ ] Build to confirm no type/compile errors:
  ```bash
  npm run build
  ```
  Expected: build completes with no errors.

- [ ] Commit any final fixes:
  ```bash
  git add -A && git commit -m "Final verification" || echo "nothing to commit"
  ```

---

## Self-Review

**Spec coverage check:**
1. Add via Enter or Add — Task 4 tests both; e2e add ✅
2. Toggle completion — Task 5 + e2e complete ✅
3. Delete via X — Task 5 (`aria-label="Delete"`) + e2e delete ✅
4. Filter subsets — Task 3 store + Task 7 + e2e filter ✅
5. "X items left" — `remainingCount` in Task 3, displayed Task 7 ✅
6. Clear completed — Task 3 + Task 7 ✅
7. Persist across refresh — Task 2/3 + e2e reload ✅
8. Empty state — Task 6 (`No todos yet — add one above!`) + e2e delete ✅
9. All tests pass — Task 10 ✅
10. Playwright add/complete/delete/filter/persistence — Task 9 ✅

**Placeholder scan:** No `TODO`/`FIXME`/`...` left in code blocks; every component and module fully implemented.

**Type consistency:** `Todo`/`Filter` defined once in `types.ts` and imported everywhere; store signatures in Task 3 Interfaces match implementation; component props (`export let todo: Todo`) match `TodoItem` usage in `TodoList`. localStorage key `svelte-todos` consistent between `storage.ts`, store test, and Global Constraints.

**Note:** `crypto.randomUUID()` is available in jsdom (Node 18+) and modern browsers; if the local Node version predates 18, upgrade Node before Task 3 — this is the implicit version floor.