# Svelte Todo List — Implementation Plan

## Global Constraints

- Framework: Svelte (use Vite + Svelte + TypeScript template)
- Language: TypeScript for all logic files (`store.ts`, `storage.ts`)
- Data model: `Todo { id: string; text: string; completed: boolean }`
- Filter type: `type Filter = 'all' | 'active' | 'completed'`
- `id` must be a UUID (use `crypto.randomUUID()`)
- localStorage key: `svelte-todos`
- App title text: `Svelte Todos`
- Remaining count copy: `N items left` (literal word `items`, even for 1)
- Unit tests: Vitest
- E2E tests: Playwright — `npx playwright test` must pass
- Component file layout exactly as in spec under `src/` and `src/lib/`

---

## File Structure

| File | Responsibility |
|------|----------------|
| `package.json` | Scripts and dependencies |
| `vite.config.ts` | Vite + Svelte + Vitest config |
| `playwright.config.ts` | Playwright config (dev server, test dir) |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Writable store of todos + derived helpers + mutations |
| `src/lib/TodoInput.svelte` | Text input + Add button; emits add events |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | Renders list of TodoItem or empty state |
| `src/lib/FilterBar.svelte` | Count, filter buttons, clear-completed button |
| `src/App.svelte` | Composes components, holds current filter |
| `src/main.ts` | Mounts App |
| `tests/*.test.ts` | Vitest unit tests |
| `e2e/todo.spec.ts` | Playwright end-to-end tests |

---

### Task 1: Project scaffold

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `src/main.ts`, `src/App.svelte`, `index.html`

**Interfaces:**
- Produces: a runnable Vite + Svelte + TS project; `npm run dev`, `npm run build`, `npm test` scripts; Vitest configured with jsdom.

Steps:

- [ ] Scaffold the project:
```bash
npm create vite@latest svelte-todos -- --template svelte-ts
cd svelte-todos
npm install
```

- [ ] Install test dependencies:
```bash
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @playwright/test
npx playwright install
```

- [ ] Replace `vite.config.ts` with:
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

- [ ] In `package.json`, ensure `scripts` contains:
```json
"scripts": {
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

- [ ] Verify build and dev start:
```bash
npm run build
```
Expected: build completes with `✓ built in ...`, no errors.

- [ ] Commit:
```bash
git init && git add -A && git commit -m "Scaffold Svelte TS project with Vitest and Playwright"
```

---

### Task 2: storage.ts (localStorage persistence)

**Files:** `src/lib/storage.ts`, `tests/storage.test.ts`

**Interfaces:**
- Consumes: `Todo` type (defined here and re-exported).
- Produces:
  - `interface Todo { id: string; text: string; completed: boolean }`
  - `type Filter = 'all' | 'active' | 'completed'`
  - `const STORAGE_KEY = 'svelte-todos'`
  - `loadTodos(): Todo[]` — returns `[]` if missing or invalid JSON
  - `saveTodos(todos: Todo[]): void`

Steps:

- [ ] Write failing test `tests/storage.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos, STORAGE_KEY, type Todo } from '../src/lib/storage';

const sample: Todo[] = [{ id: '1', text: 'a', completed: false }];

describe('storage', () => {
  beforeEach(() => localStorage.clear());

  it('returns empty array when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('returns empty array on invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not-json');
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });
});
```

- [ ] Run it (fails — module missing):
```bash
npm test
```
Expected: failure `Cannot find module '../src/lib/storage'`.

- [ ] Implement `src/lib/storage.ts`:
```ts
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

export type Filter = 'all' | 'active' | 'completed';

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

- [ ] Run tests (pass):
```bash
npm test
```
Expected: `3 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add storage.ts with localStorage persistence"
```

---

### Task 3: store.ts (todo store + mutations)

**Files:** `src/lib/store.ts`, `tests/store.test.ts`

**Interfaces:**
- Consumes: `Todo`, `loadTodos`, `saveTodos` from `storage.ts`.
- Produces:
  - `todos` — a Svelte writable store of `Todo[]`, initialized from `loadTodos()`, auto-persisting via `saveTodos` on every change.
  - `addTodo(text: string): void` — trims text; no-op if empty; prepends new todo with `crypto.randomUUID()` id, `completed: false`.
  - `toggleTodo(id: string): void`
  - `deleteTodo(id: string): void`
  - `clearCompleted(): void`
  - `filterTodos(list: Todo[], filter: Filter): Todo[]`
  - `remainingCount(list: Todo[]): number` — count of `!completed`.

Steps:

- [ ] Write failing test `tests/store.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos, addTodo, toggleTodo, deleteTodo, clearCompleted,
  filterTodos, remainingCount,
} from '../src/lib/store';
import type { Todo } from '../src/lib/storage';

describe('store', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
  });

  it('addTodo prepends a todo', () => {
    addTodo('hello');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('hello');
    expect(list[0].completed).toBe(false);
    expect(list[0].id).toBeTruthy();
  });

  it('addTodo trims and ignores empty', () => {
    addTodo('   ');
    expect(get(todos)).toHaveLength(0);
    addTodo('  spaced  ');
    expect(get(todos)[0].text).toBe('spaced');
  });

  it('toggleTodo flips completed', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deleteTodo removes by id', () => {
    addTodo('a');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  it('clearCompleted removes completed', () => {
    addTodo('a');
    addTodo('b');
    toggleTodo(get(todos)[0].id);
    clearCompleted();
    expect(get(todos)).toHaveLength(1);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('persists to localStorage', () => {
    addTodo('persist');
    expect(localStorage.getItem('svelte-todos')).toContain('persist');
  });

  it('filterTodos filters correctly', () => {
    const list: Todo[] = [
      { id: '1', text: 'x', completed: false },
      { id: '2', text: 'y', completed: true },
    ];
    expect(filterTodos(list, 'all')).toHaveLength(2);
    expect(filterTodos(list, 'active')).toEqual([list[0]]);
    expect(filterTodos(list, 'completed')).toEqual([list[1]]);
  });

  it('remainingCount counts incomplete', () => {
    const list: Todo[] = [
      { id: '1', text: 'x', completed: false },
      { id: '2', text: 'y', completed: true },
    ];
    expect(remainingCount(list)).toBe(1);
  });
});
```

- [ ] Run it (fails — module missing):
```bash
npm test
```
Expected: failure resolving `../src/lib/store`.

- [ ] Implement `src/lib/store.ts`:
```ts
import { writable } from 'svelte/store';
import { loadTodos, saveTodos, type Todo, type Filter } from './storage';

export const todos = writable<Todo[]>(loadTodos());

todos.subscribe((list) => saveTodos(list));

export function addTodo(text: string): void {
  const trimmed = text.trim();
  if (!trimmed) return;
  const todo: Todo = {
    id: crypto.randomUUID(),
    text: trimmed,
    completed: false,
  };
  todos.update((list) => [todo, ...list]);
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

export function filterTodos(list: Todo[], filter: Filter): Todo[] {
  if (filter === 'active') return list.filter((t) => !t.completed);
  if (filter === 'completed') return list.filter((t) => t.completed);
  return list;
}

export function remainingCount(list: Todo[]): number {
  return list.filter((t) => !t.completed).length;
}
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: all `store` + `storage` tests pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add todo store with mutations, filtering, persistence"
```

---

### Task 4: TodoInput.svelte

**Files:** `src/lib/TodoInput.svelte`, `tests/TodoInput.test.ts`

**Interfaces:**
- Consumes: nothing from store directly.
- Produces: a `<TodoInput>` component dispatching `on:add` with `event.detail: string` (trimmed-or-raw text) when Add is clicked or Enter pressed; clears the input afterward. No dispatch for empty/whitespace-only input.

Steps:

- [ ] Write failing test `tests/TodoInput.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoInput from '../src/lib/TodoInput.svelte';

describe('TodoInput', () => {
  it('dispatches add on button click', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e: CustomEvent) => handler(e.detail));
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'task one' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(handler).toHaveBeenCalledWith('task one');
    expect(input.value).toBe('');
  });

  it('dispatches add on Enter key', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e: CustomEvent) => handler(e.detail));
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'task two' } });
    await fireEvent.keyDown(input, { key: 'Enter' });
    expect(handler).toHaveBeenCalledWith('task two');
  });

  it('does not dispatch for empty input', async () => {
    const { getByRole, component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run it (fails — module missing):
```bash
npm test
```
Expected: failure resolving `TodoInput.svelte`.

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
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: `TodoInput` tests pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 5: TodoItem.svelte

**Files:** `src/lib/TodoItem.svelte`, `tests/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` type.
- Produces: `<TodoItem>` with prop `todo: Todo`; dispatches `on:toggle` with `detail: string` (id) and `on:delete` with `detail: string` (id). Renders a checkbox reflecting `todo.completed`, the text, and a delete button labeled `x`.

Steps:

- [ ] Write failing test `tests/TodoItem.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoItem from '../src/lib/TodoItem.svelte';
import type { Todo } from '../src/lib/storage';

const todo: Todo = { id: 'abc', text: 'Buy milk', completed: false };

describe('TodoItem', () => {
  it('renders text and checkbox state', () => {
    const { getByText, getByRole } = render(TodoItem, { todo });
    expect(getByText('Buy milk')).toBeInTheDocument();
    expect((getByRole('checkbox') as HTMLInputElement).checked).toBe(false);
  });

  it('dispatches toggle with id', async () => {
    const { getByRole, component } = render(TodoItem, { todo });
    const handler = vi.fn();
    component.$on('toggle', (e: CustomEvent) => handler(e.detail));
    await fireEvent.click(getByRole('checkbox'));
    expect(handler).toHaveBeenCalledWith('abc');
  });

  it('dispatches delete with id', async () => {
    const { getByRole, component } = render(TodoItem, { todo });
    const handler = vi.fn();
    component.$on('delete', (e: CustomEvent) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'x' }));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run it (fails):
```bash
npm test
```
Expected: failure resolving `TodoItem.svelte`.

- [ ] Implement `src/lib/TodoItem.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Todo } from './storage';

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
  <button class="delete" aria-label="x" on:click={() => dispatch('delete', todo.id)}>x</button>
</li>

<style>
  .completed .text {
    text-decoration: line-through;
    opacity: 0.6;
  }
</style>
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: `TodoItem` tests pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 6: TodoList.svelte

**Files:** `src/lib/TodoList.svelte`, `tests/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` type, `TodoItem`.
- Produces: `<TodoList>` with prop `todos: Todo[]`; renders one `TodoItem` per todo; forwards `on:toggle` and `on:delete` (re-dispatched with same `detail: string` id). When `todos` is empty, renders text `Nothing here yet — add your first todo!`.

Steps:

- [ ] Write failing test `tests/TodoList.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TodoList from '../src/lib/TodoList.svelte';
import type { Todo } from '../src/lib/storage';

const list: Todo[] = [
  { id: '1', text: 'one', completed: false },
  { id: '2', text: 'two', completed: true },
];

describe('TodoList', () => {
  it('shows empty state when no todos', () => {
    const { getByText } = render(TodoList, { todos: [] });
    expect(getByText('Nothing here yet — add your first todo!')).toBeInTheDocument();
  });

  it('renders a TodoItem per todo', () => {
    const { getByText } = render(TodoList, { todos: list });
    expect(getByText('one')).toBeInTheDocument();
    expect(getByText('two')).toBeInTheDocument();
  });

  it('forwards toggle events', async () => {
    const { getAllByRole, component } = render(TodoList, { todos: list });
    const handler = vi.fn();
    component.$on('toggle', (e: CustomEvent) => handler(e.detail));
    await fireEvent.click(getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });
});
```

- [ ] Run it (fails):
```bash
npm test
```
Expected: failure resolving `TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:
```svelte
<script lang="ts">
  import type { Todo } from './storage';
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
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: `TodoList` tests pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 7: FilterBar.svelte

**Files:** `src/lib/FilterBar.svelte`, `tests/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` type.
- Produces: `<FilterBar>` with props `filter: Filter` and `remaining: number`; renders `{remaining} items left`, three buttons `All`/`Active`/`Completed` (active one has class `active`), and a `Clear ✓` button. Dispatches `on:filter` with `detail: Filter` and `on:clear` (no detail).

Steps:

- [ ] Write failing test `tests/FilterBar.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import FilterBar from '../src/lib/FilterBar.svelte';

describe('FilterBar', () => {
  it('shows remaining count', () => {
    const { getByText } = render(FilterBar, { filter: 'all', remaining: 2 });
    expect(getByText('2 items left')).toBeInTheDocument();
  });

  it('marks active filter button', () => {
    const { getByRole } = render(FilterBar, { filter: 'active', remaining: 1 });
    expect(getByRole('button', { name: 'Active' })).toHaveClass('active');
  });

  it('dispatches filter on click', async () => {
    const { getByRole, component } = render(FilterBar, { filter: 'all', remaining: 0 });
    const handler = vi.fn();
    component.$on('filter', (e: CustomEvent) => handler(e.detail));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clear', async () => {
    const { getByRole, component } = render(FilterBar, { filter: 'all', remaining: 0 });
    const handler = vi.fn();
    component.$on('clear', handler);
    await fireEvent.click(getByRole('button', { name: 'Clear ✓' }));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run it (fails):
```bash
npm test
```
Expected: failure resolving `FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './storage';

  export let filter: Filter;
  export let remaining: number;

  const dispatch = createEventDispatcher<{ filter: Filter; clear: void }>();
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
      <button class:active={filter === f} on:click={() => dispatch('filter', f)}>
        {label[f]}
      </button>
    {/each}
  </div>
  <button class="clear" on:click={() => dispatch('clear')}>Clear ✓</button>
</div>
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: `FilterBar` tests pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 8: App.svelte (composition)

**Files:** `src/App.svelte`, `tests/App.test.ts`

**Interfaces:**
- Consumes: `todos` store, `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted`, `filterTodos`, `remainingCount` from `store.ts`; `Filter` type; all four lib components.
- Produces: full app. Holds local `filter: Filter = 'all'`. Wires component events to store mutations. Adds `data-testid="todo-list"` wrapper for E2E.

Steps:

- [ ] Write failing test `tests/App.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import App from '../src/App.svelte';
import { todos } from '../src/lib/store';

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
  });

  it('renders title', () => {
    const { getByText } = render(App);
    expect(getByText('Svelte Todos')).toBeInTheDocument();
  });

  it('adds a todo end-to-end through the store', async () => {
    const { getByRole, getByText } = render(App);
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'integration todo' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    expect(getByText('integration todo')).toBeInTheDocument();
    expect(getByText('1 items left')).toBeInTheDocument();
  });

  it('filters to completed', async () => {
    const { getByRole, getByText, queryByText } = render(App);
    const input = getByRole('textbox') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'a' } });
    await fireEvent.click(getByRole('button', { name: 'Add' }));
    await fireEvent.click(getByRole('checkbox'));
    await fireEvent.click(getByRole('button', { name: 'Completed' }));
    expect(getByText('a')).toBeInTheDocument();
    await fireEvent.click(getByRole('button', { name: 'Active' }));
    expect(queryByText('a')).toBeNull();
  });
});
```

- [ ] Run it (fails — App is placeholder):
```bash
npm test
```
Expected: `App` add/filter tests fail.

- [ ] Implement `src/App.svelte`:
```svelte
<script lang="ts">
  import { todos, addTodo, toggleTodo, deleteTodo, clearCompleted, filterTodos, remainingCount } from './lib/store';
  import type { Filter } from './lib/storage';
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
  import FilterBar from './lib/FilterBar.svelte';

  let filter: Filter = 'all';

  $: visible = filterTodos($todos, filter);
  $: remaining = remainingCount($todos);
</script>

<main>
  <h1>Svelte Todos</h1>

  <TodoInput on:add={(e) => addTodo(e.detail)} />

  <div data-testid="todo-list">
    <TodoList
      todos={visible}
      on:toggle={(e) => toggleTodo(e.detail)}
      on:delete={(e) => deleteTodo(e.detail)}
    />
  </div>

  <FilterBar
    {filter}
    {remaining}
    on:filter={(e) => (filter = e.detail)}
    on:clear={clearCompleted}
  />
</main>

<style>
  main {
    max-width: 480px;
    margin: 2rem auto;
    font-family: system-ui, sans-serif;
  }
</style>
```

- [ ] Run tests (pass):
```bash
npm test
```
Expected: all unit tests pass.

- [ ] Verify build:
```bash
npm run build
```
Expected: `✓ built in ...`.

- [ ] Commit:
```bash
git add -A && git commit -m "Compose App with all components and store wiring"
```

---

### Task 9: Playwright E2E tests

**Files:** `playwright.config.ts`, `e2e/todo.spec.ts`

**Interfaces:**
- Consumes: the running app via `npm run dev` (Vite default port 5173).
- Produces: E2E coverage for add, complete, delete, filter, persistence-across-reload.

Steps:

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

async function add(page, text: string) {
  await page.getByRole('textbox').fill(text);
  await page.getByRole('button', { name: 'Add' }).click();
}

test('add a todo', async ({ page }) => {
  await add(page, 'Buy groceries');
  await expect(page.getByText('Buy groceries')).toBeVisible();
  await expect(page.getByText('1 items left')).toBeVisible();
});

test('complete a todo', async ({ page }) => {
  await add(page, 'Walk the dog');
  await page.getByRole('checkbox').click();
  await expect(page.getByText('0 items left')).toBeVisible();
});

test('delete a todo', async ({ page }) => {
  await add(page, 'Write code');
  await page.getByRole('button', { name: 'x' }).click();
  await expect(page.getByText('Write code')).toHaveCount(0);
});

test('filter todos', async ({ page }) => {
  await add(page, 'active task');
  await add(page, 'done task');
  // checkboxes appear newest-first; second-added is at top
  await page.getByRole('checkbox').first().click();
  await page.getByRole('button', { name: 'Completed' }).click();
  await expect(page.getByText('done task')).toBeVisible();
  await page.getByRole('button', { name: 'Active' }).click();
  await expect(page.getByText('active task')).toBeVisible();
  await expect(page.getByText('done task')).toHaveCount(0);
});

test('persists across reload', async ({ page }) => {
  await add(page, 'persistent todo');
  await page.reload();
  await expect(page.getByText('persistent todo')).toBeVisible();
});
```

- [ ] Run E2E tests:
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

Steps:

- [ ] Run full unit suite:
```bash
npm test
```
Expected: all suites pass (storage, store, TodoInput, TodoItem, TodoList, FilterBar, App).

- [ ] Run E2E suite:
```bash
npx playwright test
```
Expected: `5 passed`.

- [ ] Run production build:
```bash
npm run build
```
Expected: `✓ built in ...`, no type errors.

- [ ] Commit any final adjustments:
```bash
git add -A && git commit -m "Final verification: all unit and e2e tests passing" --allow-empty
```

---

## Self-Review

**Spec coverage:**
1. Add via Enter or Add — Task 4 tests both; ✓
2. Toggle via checkbox — Task 5 + App test; ✓
3. Delete via X — Task 5 (`x` button) + App; ✓
4. Filter subsets — Task 3 `filterTodos`, Task 8 App test, Task 9 E2E; ✓
5. "X items left" — `remainingCount` + FilterBar `{remaining} items left`; ✓
6. Clear completed — `clearCompleted` + FilterBar `Clear ✓`; ✓
7. localStorage persistence — Task 2/3 + Task 9 reload test; ✓
8. Empty state — TodoList `Nothing here yet — add your first todo!`; ✓
9. All tests pass — Task 10; ✓
10. Playwright covers add/complete/delete/filter/persistence — Task 9; ✓

**Type consistency:** `Todo` and `Filter` defined once in `storage.ts`, imported everywhere. Event dispatch detail types (`string