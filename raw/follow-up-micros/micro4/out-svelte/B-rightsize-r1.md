# Svelte Todo List - Implementation Plan

## Overview

This plan builds a Svelte todo list application with localStorage persistence, following TDD. The codebase is created from scratch using Vite's Svelte + TypeScript template. Tests use Vitest and `@testing-library/svelte`.

Assume the engineer has zero context. Every command, file path, and code block is provided in full.

## File Structure

| File | Responsibility |
|------|---------------|
| `package.json` | Dependencies and scripts (generated, then modified) |
| `vite.config.ts` | Vite + Vitest config |
| `vitest-setup.ts` | Test environment setup (jsdom, jest-dom matchers) |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | Load/save todos to localStorage |
| `src/lib/store.ts` | Svelte writable store + derived stores + actions |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | List container, empty state |
| `src/lib/FilterBar.svelte` | Filter buttons, item count, clear completed |
| `src/App.svelte` | Wires components together |
| `src/main.ts` | App entry point (generated) |

Test files live next to their source: `src/lib/storage.test.ts`, `src/lib/store.test.ts`, `src/lib/TodoInput.test.ts`, etc.

---

### Task 1: Project Scaffolding & Test Harness

Set up the Vite Svelte+TS project, install test tooling, and verify a trivial test runs. This task's deliverable is a green test run.

**Files:** `package.json`, `vite.config.ts`, `vitest-setup.ts`, `src/lib/smoke.test.ts` (temporary)

- [ ] Scaffold the project into the current directory. Run:

```bash
npm create vite@latest . -- --template svelte-ts
```

If prompted about a non-empty directory, choose **"Ignore files and continue"**. Expected: files like `src/App.svelte`, `src/main.ts`, `package.json` are created.

- [ ] Install base dependencies:

```bash
npm install
```

Expected: `node_modules/` populated, exit code 0.

- [ ] Install test tooling:

```bash
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```

Expected: packages added to `devDependencies`.

- [ ] Replace `vite.config.ts` with this content (adds Vitest config):

```typescript
import { defineConfig } from 'vite';
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

- [ ] Add a `test` script to `package.json`. Open `package.json` and ensure the `"scripts"` block includes:

```json
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-check --tsconfig ./tsconfig.json",
    "test": "vitest run",
    "test:watch": "vitest"
  },
```

- [ ] Create a temporary smoke test `src/lib/smoke.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';

describe('smoke', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] Run the tests:

```bash
npm test
```

Expected output includes:

```
 ✓ src/lib/smoke.test.ts (1 test)
 Test Files  1 passed (1)
      Tests  1 passed (1)
```

- [ ] Delete the smoke test and any boilerplate counter:

```bash
rm src/lib/smoke.test.ts
rm -f src/lib/Counter.svelte src/assets/svelte.svg
```

- [ ] Commit:

```bash
git init -q 2>/dev/null; git add -A && git commit -q -m "Scaffold Svelte+TS project with Vitest test harness"
```

---

### Task 2: Types

Define the shared data model. Tiny but isolated so later tasks import from one place.

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

- [ ] Verify it type-checks:

```bash
npx tsc --noEmit src/lib/types.ts
```

Expected: no output, exit code 0.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add Todo and Filter types"
```

---

### Task 3: Storage Module

localStorage load/save with graceful handling of missing/corrupt data. TDD.

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

- [ ] Write the failing test `src/lib/storage.test.ts`:

```typescript
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

Expected: failure with `Cannot find module './storage'` or similar.

- [ ] Implement `src/lib/storage.ts`:

```typescript
import type { Todo } from './types';

const KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(KEY);
  if (raw === null) return [];
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as Todo[];
  } catch {
    return [];
  }
}

export function saveTodos(todos: Todo[]): void {
  localStorage.setItem(KEY, JSON.stringify(todos));
}
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `3 passed`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add localStorage persistence module"
```

---

### Task 4: Store

Writable store seeded from localStorage, persisting on every change, with derived stores and action functions. TDD.

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

- [ ] Write the failing test `src/lib/store.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  filter,
  filteredTodos,
  remainingCount,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
} from './store';
import { loadTodos } from './storage';

describe('store', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
    filter.set('all');
  });

  it('addTodo appends a todo with text and incomplete status', () => {
    addTodo('Buy milk');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy milk');
    expect(list[0].completed).toBe(false);
    expect(list[0].id).toBeTruthy();
  });

  it('addTodo ignores empty or whitespace-only text', () => {
    addTodo('   ');
    expect(get(todos)).toHaveLength(0);
  });

  it('addTodo trims text', () => {
    addTodo('  hello  ');
    expect(get(todos)[0].text).toBe('hello');
  });

  it('addTodo persists to localStorage', () => {
    addTodo('Persist me');
    expect(loadTodos()).toHaveLength(1);
  });

  it('toggleTodo flips completed', () => {
    addTodo('task');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deleteTodo removes by id', () => {
    addTodo('task');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  it('clearCompleted removes completed todos only', () => {
    addTodo('a');
    addTodo('b');
    const [first] = get(todos);
    toggleTodo(first.id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('remainingCount counts incomplete todos', () => {
    addTodo('a');
    addTodo('b');
    toggleTodo(get(todos)[0].id);
    expect(get(remainingCount)).toBe(1);
  });

  it('filteredTodos respects active filter', () => {
    addTodo('a');
    addTodo('b');
    toggleTodo(get(todos)[0].id);
    filter.set('active');
    expect(get(filteredTodos).map((t) => t.text)).toEqual(['b']);
    filter.set('completed');
    expect(get(filteredTodos).map((t) => t.text)).toEqual(['a']);
    filter.set('all');
    expect(get(filteredTodos)).toHaveLength(2);
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure resolving `./store`.

- [ ] Implement `src/lib/store.ts`:

```typescript
import { writable, derived, get } from 'svelte/store';
import type { Todo, Filter } from './types';
import { loadTodos, saveTodos } from './storage';

export const todos = writable<Todo[]>(loadTodos());
export const filter = writable<Filter>('all');

todos.subscribe((value) => {
  saveTodos(value);
});

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
  if (trimmed === '') return;
  const todo: Todo = {
    id: crypto.randomUUID(),
    text: trimmed,
    completed: false,
  };
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

Note: `get` is imported for completeness of the store API but `crypto.randomUUID` is available in jsdom (Node 19+). If your Node is older, the test `addTodo appends...` will fail on `id` — in that case upgrade Node to >=19.

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `10 passed` (storage 3 + store 10... reported per-file; all green).

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add todo store with derived filters and actions"
```

---

### Task 5: TodoInput Component

Text input + Add button. Adds on click and on Enter. Clears input after add. TDD with `@testing-library/svelte`.

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

- [ ] Write the failing test `src/lib/TodoInput.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { get } from 'svelte/store';
import TodoInput from './TodoInput.svelte';
import { todos } from './store';

describe('TodoInput', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
  });

  it('adds a todo when Add button clicked', async () => {
    const user = userEvent.setup();
    render(TodoInput);
    await user.type(screen.getByRole('textbox'), 'Buy milk');
    await user.click(screen.getByRole('button', { name: /add/i }));
    expect(get(todos)).toHaveLength(1);
    expect(get(todos)[0].text).toBe('Buy milk');
  });

  it('adds a todo when Enter pressed', async () => {
    const user = userEvent.setup();
    render(TodoInput);
    await user.type(screen.getByRole('textbox'), 'Walk dog{Enter}');
    expect(get(todos)).toHaveLength(1);
  });

  it('clears the input after adding', async () => {
    const user = userEvent.setup();
    render(TodoInput);
    const input = screen.getByRole('textbox') as HTMLInputElement;
    await user.type(input, 'Write code{Enter}');
    expect(input.value).toBe('');
  });

  it('does not add an empty todo', async () => {
    const user = userEvent.setup();
    render(TodoInput);
    await user.click(screen.getByRole('button', { name: /add/i }));
    expect(get(todos)).toHaveLength(0);
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure resolving `./TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:

```svelte
<script lang="ts">
  import { addTodo } from './store';

  let text = '';

  function submit() {
    addTodo(text);
    text = '';
  }

  function onKeydown(event: KeyboardEvent) {
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
  button {
    padding: 0.5rem 1rem;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `TodoInput.test.ts (4 tests) passed`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add TodoInput component"
```

---

### Task 6: TodoItem Component

Checkbox, text, delete button for a single todo. Takes a `todo` prop. TDD.

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

- [ ] Write the failing test `src/lib/TodoItem.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { get } from 'svelte/store';
import TodoItem from './TodoItem.svelte';
import { todos } from './store';
import type { Todo } from './types';

const todo: Todo = { id: 'x1', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([{ ...todo }]);
  });

  it('renders the todo text', () => {
    render(TodoItem, { props: { todo } });
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
  });

  it('toggles completion when checkbox clicked', async () => {
    const user = userEvent.setup();
    render(TodoItem, { props: { todo } });
    await user.click(screen.getByRole('checkbox'));
    expect(get(todos)[0].completed).toBe(true);
  });

  it('reflects completed state in checkbox', () => {
    render(TodoItem, { props: { todo: { ...todo, completed: true } } });
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('deletes the todo when delete button clicked', async () => {
    const user = userEvent.setup();
    render(TodoItem, { props: { todo } });
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(get(todos)).toHaveLength(0);
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure resolving `./TodoItem.svelte`.

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
  <button
    class="delete"
    aria-label="Delete {todo.text}"
    on:click={() => deleteTodo(todo.id)}>×</button
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
    color: #999;
  }
  .delete {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.2rem;
    color: #c00;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `TodoItem.test.ts (4 tests) passed`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add TodoItem component"
```

---

### Task 7: TodoList Component

Renders filtered todos, shows empty-state message when none. TDD.

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

- [ ] Write the failing test `src/lib/TodoList.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import { todos, filter } from './store';

describe('TodoList', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
    filter.set('all');
  });

  it('shows empty state message when no todos', () => {
    render(TodoList);
    expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
  });

  it('renders todos from the store', () => {
    todos.set([
      { id: '1', text: 'Alpha', completed: false },
      { id: '2', text: 'Beta', completed: false },
    ]);
    render(TodoList);
    expect(screen.getByText('Alpha')).toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });

  it('respects the active filter', () => {
    todos.set([
      { id: '1', text: 'Alpha', completed: false },
      { id: '2', text: 'Beta', completed: true },
    ]);
    filter.set('completed');
    render(TodoList);
    expect(screen.queryByText('Alpha')).not.toBeInTheDocument();
    expect(screen.getByText('Beta')).toBeInTheDocument();
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure resolving `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:

```svelte
<script lang="ts">
  import { filteredTodos } from './store';
  import TodoItem from './TodoItem.svelte';
</script>

{#if $filteredTodos.length === 0}
  <p class="empty">Nothing here yet — add your first todo!</p>
{:else}
  <ul class="todo-list">
    {#each $filteredTodos as todo (todo.id)}
      <TodoItem {todo} />
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
    color: #999;
    text-align: center;
    padding: 1rem 0;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `TodoList.test.ts (3 tests) passed`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add TodoList component with empty state"
```

---

### Task 8: FilterBar Component

Item count, three filter buttons, clear-completed button. TDD.

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

- [ ] Write the failing test `src/lib/FilterBar.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { get } from 'svelte/store';
import FilterBar from './FilterBar.svelte';
import { todos, filter } from './store';

describe('FilterBar', () => {
  beforeEach(() => {
    localStorage.clear();
    filter.set('all');
    todos.set([
      { id: '1', text: 'Alpha', completed: false },
      { id: '2', text: 'Beta', completed: true },
    ]);
  });

  it('shows count of remaining (incomplete) items', () => {
    render(FilterBar);
    expect(screen.getByText(/1 item left/i)).toBeInTheDocument();
  });

  it('pluralizes when not exactly one item left', () => {
    todos.set([
      { id: '1', text: 'Alpha', completed: false },
      { id: '2', text: 'Beta', completed: false },
    ]);
    render(FilterBar);
    expect(screen.getByText(/2 items left/i)).toBeInTheDocument();
  });

  it('changes the filter when a filter button is clicked', async () => {
    const user = userEvent.setup();
    render(FilterBar);
    await user.click(screen.getByRole('button', { name: /^active$/i }));
    expect(get(filter)).toBe('active');
  });

  it('clears completed todos', async () => {
    const user = userEvent.setup();
    render(FilterBar);
    await user.click(screen.getByRole('button', { name: /clear completed/i }));
    const remaining = get(todos);
    expect(remaining).toHaveLength(1);
    expect(remaining[0].text).toBe('Alpha');
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure resolving `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:

```svelte
<script lang="ts">
  import { filter, remainingCount, clearCompleted } from './store';
  import type { Filter } from './types';

  const filters: Filter[] = ['all', 'active', 'completed'];

  function setFilter(value: Filter) {
    filter.set(value);
  }
</script>

<div class="filter-bar">
  <span class="count">
    {$remainingCount} {$remainingCount === 1 ? 'item' : 'items'} left
  </span>

  <div class="filters">
    {#each filters as f}
      <button class:active={$filter === f} on:click={() => setFilter(f)}>
        {f.charAt(0).toUpperCase() + f.slice(1)}
      </button>
    {/each}
  </div>

  <button class="clear" on:click={clearCompleted}>Clear completed</button>
</div>

<style>
  .filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    padding-top: 0.5rem;
  }
  .filters {
    display: flex;
    gap: 0.25rem;
  }
  button {
    padding: 0.25rem 0.5rem;
    cursor: pointer;
  }
  button.active {
    font-weight: bold;
    border-color: #333;
  }
</style>
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: `FilterBar.test.ts (4 tests) passed`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Add FilterBar component with count and clear-completed"
```

---

### Task 9: App Integration

Wire all components together. Integration test covers the full add → filter → complete flow. TDD.

**Files:** `src/App.svelte`, `src/App.test.ts`, `src/app.css` (optional styling), `src/main.ts` (verify)

- [ ] Write the failing integration test `src/App.test.ts`:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import App from './App.svelte';
import { todos, filter } from './lib/store';

describe('App integration', () => {
  beforeEach(() => {
    localStorage.clear();
    todos.set([]);
    filter.set('all');
  });

  it('renders the title', () => {
    render(App);
    expect(screen.getByText(/svelte todos/i)).toBeInTheDocument();
  });

  it('supports the full add, complete, filter flow', async () => {
    const user = userEvent.setup();
    render(App);

    const input = screen.getByRole('textbox');
    await user.type(input, 'Buy groceries{Enter}');
    await user.type(input, 'Walk the dog{Enter}');

    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
    expect(screen.getByText(/2 items left/i)).toBeInTheDocument();

    // Complete the first todo
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[0]);
    expect(screen.getByText(/1 item left/i)).toBeInTheDocument();

    // Filter to active
    await user.click(screen.getByRole('button', { name: /^active$/i }));
    expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument();
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();

    // Filter to completed
    await user.click(screen.getByRole('button', { name: /^completed$/i }));
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.queryByText('Walk the dog')).not.toBeInTheDocument();

    // Clear completed (back on completed filter, but clear works regardless)
    await user.click(screen.getByRole('button', { name: /^all$/i }));
    await user.click(screen.getByRole('button', { name: /clear completed/i }));
    expect(screen.queryByText('Buy groceries')).not.toBeInTheDocument();
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
  });
});
```

- [ ] Run to see it fail:

```bash
npm test
```

Expected: failure because the generated `App.svelte` does not contain "Svelte Todos".

- [ ] Replace `src/App.svelte` with:

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
  main {
    max-width: 480px;
    margin: 2rem auto;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: system-ui, sans-serif;
  }
  h1 {
    font-size: 1.5rem;
    margin: 0 0 1rem;
  }
</style>
```

- [ ] Verify `src/main.ts` mounts `App` (generated by template). It should read approximately:

```typescript
import './app.css';
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')!,
});

export default app;
```

If `./app.css` does not exist, create an empty `src/app.css`:

```bash
touch src/app.css
```

- [ ] Run to see it pass:

```bash
npm test
```

Expected: all test files green, including `App.test.ts (2 tests)`.

- [ ] Run the full suite once more to confirm every test passes together:

```bash
npm test
```

Expected output ends with all test files passing, e.g.:

```
 Test Files  6 passed (6)
      Tests  28 passed (28)
```

- [ ] Type-check the whole project:

```bash
npm run check
```

Expected: `svelte-check found 0 errors`.

- [ ] Commit:

```bash
git add -A && git commit -q -m "Integrate components into App with passing integration tests"
```

---

### Task 10: Manual Verification & Build

Confirm the app runs in a browser and persistence works, then verify the production build.

**Files:** none (verification only)

- [ ] Start the dev server:

```bash
npm run dev
```

Expected: Vite prints a `Local: http://localhost:5173/` URL.

- [ ] In a browser, manually verify each acceptance criterion:
  - Add a todo via Enter and via the Add button.
  - Toggle a checkbox; confirm strike-through styling.
  - Delete a todo via the × button.
  - Click All / Active / Completed and confirm the visible subset changes.
  - Confirm "X items left" updates and pluralizes correctly.
  - Click "Clear completed" and confirm completed todos disappear.
  - Refresh the page; confirm todos persist (localStorage).
  - Delete all todos; confirm the empty-state message appears.

- [ ] Stop the dev server (Ctrl+C) and run a production build:

```bash
npm run build
```

Expected: `dist/` produced, exit code 0, no errors.

- [ ] Commit any incidental changes (e.g., lockfile):

```bash
git add -A && git commit -q -m "Verify build and manual acceptance" --allow-empty
```

---

## Self-Review

**Spec coverage check:**

| Acceptance criterion | Covered by |
|----------------------|-----------|
| 1. Add via Enter or Add button | Task 5 (TodoInput tests + impl) |
| 2. Toggle completion via checkbox | Task 6 (TodoItem) |
| 3. Delete via X button | Task 6 (TodoItem, `aria-label="Delete ..."`, renders `×`) |
| 4. Filter buttons show correct subset | Task 4 (filteredTodos), Task 7 (TodoList), Task 8 (FilterBar), Task 9 (integration) |
| 5. "X items left" count | Task 4 (remainingCount), Task 8 (FilterBar, with pluralization) |
| 6. Clear completed | Task 4 (clearCompleted), Task 8 (FilterBar) |
| 7. Persist across refresh | Task 3 (storage), Task 4 (subscribe-to-save), Task 10 (manual) |
| 8. Empty state message | Task 7 (TodoList) |
| 9. All tests pass | Tasks 3–9, confirmed in Task 9 |

All six components and both store/storage modules from the spec's file tree are created. Spec lists `store.ts` and `storage.ts`; the additional `types.ts` (Task 2) holds the spec's data model interfaces — a DRY extraction so each component imports types from one place.

**Placeholder scan:** No `TODO`, `FIXME`, or stub bodies remain; every code block is complete and runnable.

**Type consistency:** `Todo` and `Filter` are defined once in `types.ts` and imported everywhere (`storage.ts`, `store.ts`, `TodoItem.svelte`, `FilterBar.svelte`, tests). `Filter` values `'all' | 'active' | 'completed'` match the FilterBar `filters` array and the store's switch cases.

**Known environment caveat fixed inline:** `crypto.randomUUID` requires Node ≥19 (noted in Task 4). The `get