# Svelte Todo List — Implementation Plan

This plan builds a Svelte + TypeScript todo list with localStorage persistence and Playwright e2e tests. The engineer is assumed to have zero context for this codebase. Follow each step in order: write the failing test, run it, implement, run again, commit.

## Global Constraints

- Framework: Svelte (scaffolded via `npm create vite@latest . -- --template svelte-ts`)
- Language: TypeScript for all `.ts` files and `<script lang="ts">` in `.svelte`
- Unit test runner: Vitest with `@testing-library/svelte` and `jsdom`
- E2E test runner: Playwright (`npx playwright test` must pass)
- Data model: `Todo { id: string; text: string; completed: boolean }`; `Filter = 'all' | 'active' | 'completed'`
- `id` values are UUIDs generated with `crypto.randomUUID()`
- localStorage key: `'svelte-todos'`
- App title text: `Svelte Todos`
- Remaining count copy: `N items left` (exact, including for N=1 — singular not required by spec)
- Empty state copy: `Nothing here yet — add your first todo!`
- Filter button labels: `All`, `Active`, `Completed`
- Clear-completed button label: `Clear ✓`
- Add button label: `Add`

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte writable store + actions (add/toggle/delete/clearCompleted) |
| `src/lib/TodoInput.svelte` | Text input + Add button, emits `add` event |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button; emits `toggle`/`delete` |
| `src/lib/TodoList.svelte` | Renders list of `TodoItem` or empty state |
| `src/lib/FilterBar.svelte` | Filter buttons, items-left count, clear-completed button |
| `src/App.svelte` | Wires store + components, holds active filter |
| `src/main.ts` | App entry (from scaffold) |
| `vitest.config.ts` | Vitest config with jsdom |
| `vitest-setup.ts` | jest-dom matchers + localStorage reset |
| `playwright.config.ts` | Playwright config, runs dev server |
| `e2e/todos.spec.ts` | End-to-end tests |

---

### Task 1: Project scaffold and tooling

**Files:** `package.json`, `vitest.config.ts`, `vitest-setup.ts`, `src/lib/sanity.test.ts` (temporary)

**Interfaces:** Produces a working Vite + Svelte + TS project with `npm test` (Vitest) and `npm run build` available. No exports consumed by other tasks except the toolchain.

- [ ] Scaffold the project in the current directory:
```bash
npm create vite@latest . -- --template svelte-ts
npm install
```
Expected: `package.json`, `src/App.svelte`, `src/main.ts`, `vite.config.ts` created.

- [ ] Install test dependencies:
```bash
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```
Expected: `node_modules` updated, dependencies appear in `package.json` under `devDependencies`.

- [ ] Create `vitest-setup.ts`:
```ts
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';

afterEach(() => {
  localStorage.clear();
});
```

- [ ] Create `vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte({ hot: false })],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest-setup.ts'],
    include: ['src/**/*.{test,spec}.ts'],
  },
});
```

- [ ] Add scripts to `package.json` (merge into existing `"scripts"`):
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] Create a temporary sanity test `src/lib/sanity.test.ts`:
```ts
import { describe, it, expect } from 'vitest';

describe('sanity', () => {
  it('runs vitest', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] Run the test and see it pass:
```bash
npm test
```
Expected: `1 passed`.

- [ ] Delete the sanity test:
```bash
rm src/lib/sanity.test.ts
```

- [ ] Commit:
```bash
git add -A && git commit -m "Scaffold Svelte+TS project with Vitest"
```

---

### Task 2: Types and storage layer

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `src/lib/types.ts`: `export interface Todo { id: string; text: string; completed: boolean }` and `export type Filter = 'all' | 'active' | 'completed';`
  - `src/lib/storage.ts`: `export const STORAGE_KEY = 'svelte-todos';`, `export function loadTodos(): Todo[]`, `export function saveTodos(todos: Todo[]): void`. `loadTodos` returns `[]` when key absent or JSON invalid.

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
import { describe, it, expect } from 'vitest';
import { loadTodos, saveTodos, STORAGE_KEY } from './storage';
import type { Todo } from './types';

const sample: Todo[] = [
  { id: '1', text: 'a', completed: false },
  { id: '2', text: 'b', completed: true },
];

describe('storage', () => {
  it('returns empty array when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('writes to the expected localStorage key', () => {
    saveTodos(sample);
    expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
  });

  it('returns empty array when stored value is invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not json');
    expect(loadTodos()).toEqual([]);
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
```
Expected: failure — `Cannot find module './storage'` / functions undefined.

- [ ] Implement `src/lib/storage.ts`:
```ts
import type { Todo } from './types';

export const STORAGE_KEY = 'svelte-todos';

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

- [ ] Run and see it pass:
```bash
npm test
```
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add types and localStorage storage layer"
```

---

### Task 3: Todos store

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo` from `types.ts`; `loadTodos`/`saveTodos` from `storage.ts`.
- Produces `src/lib/store.ts`:
  - `export const todos: Writable<Todo[]>` (initialised from `loadTodos()`, persists to `saveTodos` on every change via subscription).
  - `export function addTodo(text: string): void` — trims text; no-op if empty; prepends new todo with `crypto.randomUUID()` id and `completed: false`. New todos appear at the top of the list.
  - `export function toggleTodo(id: string): void`
  - `export function deleteTodo(id: string): void`
  - `export function clearCompleted(): void`

- [ ] Write failing test `src/lib/store.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { todos, addTodo, toggleTodo, deleteTodo, clearCompleted } from './store';
import { loadTodos } from './storage';

beforeEach(() => {
  todos.set([]);
});

describe('store', () => {
  it('adds a todo at the top with generated id and completed=false', () => {
    addTodo('first');
    addTodo('second');
    const list = get(todos);
    expect(list).toHaveLength(2);
    expect(list[0].text).toBe('second');
    expect(list[1].text).toBe('first');
    expect(list[0].completed).toBe(false);
    expect(typeof list[0].id).toBe('string');
    expect(list[0].id.length).toBeGreaterThan(0);
  });

  it('trims text and ignores empty input', () => {
    addTodo('  spaced  ');
    addTodo('   ');
    addTodo('');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('spaced');
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

  it('clears completed todos only', () => {
    addTodo('keep');
    addTodo('remove');
    const removeId = get(todos)[0].id;
    toggleTodo(removeId);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('keep');
  });

  it('persists changes to storage', () => {
    addTodo('persisted');
    expect(loadTodos()).toHaveLength(1);
    expect(loadTodos()[0].text).toBe('persisted');
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
```
Expected: failure — `Cannot find module './store'`.

- [ ] Implement `src/lib/store.ts`:
```ts
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
  const todo: Todo = {
    id: crypto.randomUUID(),
    text: trimmed,
    completed: false,
  };
  todos.update((list) => [todo, ...list]);
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

- [ ] Run and see it pass:
```bash
npm test
```
Expected: `6 passed` in this file (plus storage tests passing).

- [ ] Commit:
```bash
git add -A && git commit -m "Add todos store with add/toggle/delete/clearCompleted"
```

---

### Task 4: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces `TodoInput.svelte`: emits an `add` CustomEvent with `detail: string` (trimmed text) when the user presses Enter in the input or clicks the `Add` button. Clears the input after a successful add. Does not emit when text is empty/whitespace. Input has placeholder `What needs to be done?`. Button text `Add`.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('emits add on button click with trimmed text and clears input', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await user.type(input, '  hello  ');
    await user.click(screen.getByText('Add'));

    expect(handler).toHaveBeenCalledWith('hello');
    expect(input.value).toBe('');
  });

  it('emits add on Enter key', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = screen.getByPlaceholderText('What needs to be done?');
    await user.type(input, 'typed{Enter}');

    expect(handler).toHaveBeenCalledWith('typed');
  });

  it('does not emit when input is empty or whitespace', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);

    await user.click(screen.getByText('Add'));
    const input = screen.getByPlaceholderText('What needs to be done?');
    await user.type(input, '   {Enter}');

    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
```
Expected: failure — cannot find `TodoInput.svelte`.

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

- [ ] Run and see it pass:
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
- Produces `TodoItem.svelte`: prop `todo: Todo`. Renders a checkbox reflecting `todo.completed`, the text, and a delete button labelled `×` with `aria-label="Delete"`. Emits `toggle` CustomEvent with `detail: string` (the id) when checkbox clicked, and `delete` CustomEvent with `detail: string` (the id) when delete clicked.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './types';

const todo: Todo = { id: 'abc', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders text and unchecked checkbox', () => {
    render(TodoItem, { props: { todo } });
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).not.toBeChecked();
  });

  it('reflects completed state', () => {
    render(TodoItem, { props: { todo: { ...todo, completed: true } } });
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('emits toggle with id when checkbox clicked', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await user.click(screen.getByRole('checkbox'));
    expect(handler).toHaveBeenCalledWith('abc');
  });

  it('emits delete with id when delete clicked', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await user.click(screen.getByLabelText('Delete'));
    expect(handler).toHaveBeenCalledWith('abc');
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
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
  <button class="delete" aria-label="Delete" on:click={() => dispatch('delete', todo.id)}>×</button>
</li>
```

- [ ] Run and see it pass:
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
- Produces `TodoList.svelte`: prop `todos: Todo[]`. Renders one `TodoItem` per todo inside a `<ul>`. When `todos` is empty, renders the empty-state message `Nothing here yet — add your first todo!` instead. Re-emits `toggle` and `delete` events (each `detail: string` id) bubbled from items.

- [ ] Write failing test `src/lib/TodoList.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import TodoList from './TodoList.svelte';
import type { Todo } from './types';

const todos: Todo[] = [
  { id: '1', text: 'one', completed: false },
  { id: '2', text: 'two', completed: true },
];

describe('TodoList', () => {
  it('renders empty state when no todos', () => {
    render(TodoList, { props: { todos: [] } });
    expect(screen.getByText('Nothing here yet — add your first todo!')).toBeInTheDocument();
  });

  it('renders one item per todo', () => {
    render(TodoList, { props: { todos } });
    expect(screen.getByText('one')).toBeInTheDocument();
    expect(screen.getByText('two')).toBeInTheDocument();
    expect(screen.getAllByRole('checkbox')).toHaveLength(2);
  });

  it('forwards toggle events with id', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await user.click(screen.getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete events with id', async () => {
    const user = userEvent.setup();
    const { component } = render(TodoList, { props: { todos } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await user.click(screen.getAllByLabelText('Delete')[1]);
    expect(handler).toHaveBeenCalledWith('2');
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
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
  <p class="empty">Nothing here yet — add your first todo!</p>
{:else}
  <ul class="todo-list">
    {#each todos as todo (todo.id)}
      <TodoItem {todo} on:toggle on:delete />
    {/each}
  </ul>
{/if}
```

- [ ] Run and see it pass:
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
- Produces `FilterBar.svelte`: props `filter: Filter` and `remaining: number`. Renders `{remaining} items left`, three filter buttons (`All`, `Active`, `Completed`) where the active one has class `active`, and a `Clear ✓` button. Emits `filterChange` CustomEvent with `detail: Filter` when a filter button is clicked, and `clearCompleted` CustomEvent (no detail) when `Clear ✓` clicked.

- [ ] Write failing test `src/lib/FilterBar.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows remaining count', () => {
    render(FilterBar, { props: { filter: 'all', remaining: 2 } });
    expect(screen.getByText('2 items left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    render(FilterBar, { props: { filter: 'active', remaining: 0 } });
    expect(screen.getByText('Active')).toHaveClass('active');
    expect(screen.getByText('All')).not.toHaveClass('active');
  });

  it('emits filterChange with chosen filter', async () => {
    const user = userEvent.setup();
    const { component } = render(FilterBar, { props: { filter: 'all', remaining: 0 } });
    const handler = vi.fn();
    component.$on('filterChange', (e) => handler(e.detail));
    await user.click(screen.getByText('Completed'));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('emits clearCompleted', async () => {
    const user = userEvent.setup();
    const { component } = render(FilterBar, { props: { filter: 'all', remaining: 0 } });
    const handler = vi.fn();
    component.$on('clearCompleted', handler);
    await user.click(screen.getByText('Clear ✓'));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
```
Expected: failure — cannot find `FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './types';

  export let filter: Filter;
  export let remaining: number;

  const dispatch = createEventDispatcher<{ filterChange: Filter; clearCompleted: void }>();

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
      <button class:active={filter === f} on:click={() => dispatch('filterChange', f)}>
        {labels[f]}
      </button>
    {/each}
  </div>
  <button class="clear" on:click={() => dispatch('clearCompleted')}>Clear ✓</button>
</div>
```

- [ ] Run and see it pass:
```bash
npm test
```
Expected: `4 passed` in this file.

- [ ] Commit:
```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 8: App wiring

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: `todos` store + `addTodo`/`toggleTodo`/`deleteTodo`/`clearCompleted` from `store.ts`; `Filter` from `types.ts`; `TodoInput`, `TodoList`, `FilterBar` components.
- Produces: the full app. Holds local `filter: Filter` (default `'all'`). Derives the visible list from `$todos` + `filter`, and `remaining` from `$todos` count where `completed === false`. Renders heading `Svelte Todos`.

- [ ] Write failing test `src/App.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import App from './App.svelte';
import { todos } from './lib/store';

beforeEach(() => {
  todos.set([]);
});

describe('App', () => {
  it('shows the title', () => {
    render(App);
    expect(screen.getByText('Svelte Todos')).toBeInTheDocument();
  });

  it('adds a todo and updates the remaining count', async () => {
    const user = userEvent.setup();
    render(App);
    const input = screen.getByPlaceholderText('What needs to be done?');
    await user.type(input, 'Buy milk{Enter}');
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByText('1 items left')).toBeInTheDocument();
  });

  it('toggles a todo, reducing remaining count', async () => {
    const user = userEvent.setup();
    render(App);
    await user.type(screen.getByPlaceholderText('What needs to be done?'), 'Task{Enter}');
    await user.click(screen.getByRole('checkbox'));
    expect(screen.getByText('0 items left')).toBeInTheDocument();
  });

  it('filters to active only', async () => {
    const user = userEvent.setup();
    render(App);
    const input = screen.getByPlaceholderText('What needs to be done?');
    await user.type(input, 'keep-active{Enter}');
    await user.type(input, 'will-complete{Enter}');
    // complete the top one (will-complete)
    await user.click(screen.getAllByRole('checkbox')[0]);
    await user.click(screen.getByText('Active'));
    expect(screen.getByText('keep-active')).toBeInTheDocument();
    expect(screen.queryByText('will-complete')).not.toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    const user = userEvent.setup();
    render(App);
    await user.type(screen.getByPlaceholderText('What needs to be done?'), 'gone{Enter}');
    await user.click(screen.getByLabelText('Delete'));
    expect(screen.queryByText('gone')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    const user = userEvent.setup();
    render(App);
    const input = screen.getByPlaceholderText('What needs to be done?');
    await user.type(input, 'done{Enter}');
    await user.click(screen.getByRole('checkbox'));
    await user.click(screen.getByText('Clear ✓'));
    expect(screen.queryByText('done')).not.toBeInTheDocument();
  });
});
```

- [ ] Run and see it fail:
```bash
npm test
```
Expected: failure — current scaffold `App.svelte` has no title/input.

- [ ] Replace `src/App.svelte` entirely:
```svelte
<script lang="ts">
  import TodoInput from './lib/TodoInput.svelte';
  import TodoList from './lib/TodoList.svelte';
  import FilterBar from './lib/FilterBar.svelte';
  import { todos, addTodo, toggleTodo, deleteTodo, clearCompleted } from './lib/store';
  import type { Filter } from './lib/types';

  let filter: Filter = 'all';

  $: remaining = $todos.filter((t) => !t.completed).length;
  $: visible = $todos.filter((t) => {
    if (filter === 'active') return !t.completed;
    if (filter === 'completed') return t.completed;
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
    {filter}
    {remaining}
    on:filterChange={(e) => (filter = e.detail)}
    on:clearCompleted={clearCompleted}
  />
</main>
```

- [ ] Run and see it pass:
```bash
npm test
```
Expected: all App tests pass; full suite green.

- [ ] Verify the dev server renders:
```bash
npm run dev
```
Expected: prints a local URL; open it and confirm you can add/toggle/delete/filter. Stop with Ctrl+C.

- [ ] Commit:
```bash
git add -A && git commit -m "Wire App with store and filtering"
```

---

### Task 9: Playwright end-to-end tests

**Files:** `playwright.config.ts`, `e2e/todos.spec.ts`, `package.json`

**Interfaces:**
- Consumes: the running app served by `npm run dev`.
- Produces: e2e coverage of add, complete, delete, filter, and persistence-across-reload. `npx playwright test` passes.

- [ ] Install Playwright and browsers:
```bash
npm install -D @playwright/test
npx playwright install --with-deps chromium
```
Expected: chromium downloaded.

- [ ] Create `playwright.config.ts`:
```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

- [ ] Add an e2e script to `package.json` `"scripts"`:
```json
"test:e2e": "playwright test"
```

- [ ] Ensure Vitest does not pick up e2e files. Confirm `vitest.config.ts` `include` is `['src/**/*.{test,spec}.ts']` (it is from Task 1, so `e2e/` is excluded). No change needed.

- [ ] Create `e2e/todos.spec.ts`:
```ts
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  await page.reload();
});

async function add(page, text: string) {
  const input = page.getByPlaceholder('What needs to be done?');
  await input.fill(text);
  await input.press('Enter');
}

test('adds a todo', async ({ page }) => {
  await add(page, 'Buy groceries');
  await expect(page.getByText('Buy groceries')).toBeVisible();
  await expect(page.getByText('1 items left')).toBeVisible();
});

test('completes a todo',