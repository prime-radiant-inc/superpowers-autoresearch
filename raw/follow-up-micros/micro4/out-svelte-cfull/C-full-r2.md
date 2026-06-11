# Svelte Todo List - Implementation Plan

## Global Constraints

- Framework: Svelte (via Vite + `npm create vite@latest`, `svelte-ts` template)
- Language: TypeScript for all `.ts` and `<script lang="ts">` blocks
- Test runner: Vitest + `@testing-library/svelte` + `jsdom`
- Data model: `interface Todo { id: string; text: string; completed: boolean; }`
- Filter type: `type Filter = 'all' | 'active' | 'completed';`
- localStorage key: `'svelte-todos'` (exact string)
- IDs generated with `crypto.randomUUID()`
- Empty-state message copy: `No todos yet. Add one above!`
- Items-left copy: `<N> items left` (e.g. `2 items left`); for exactly one use `1 item left`
- Component file paths exactly as in spec under `src/` and `src/lib/`

## File Structure

| File | Responsibility |
|------|----------------|
| `src/lib/storage.ts` | Read/write `Todo[]` to localStorage under key `svelte-todos` |
| `src/lib/store.ts` | Svelte writable store of `Todo[]`, CRUD actions, persistence wiring; `Filter` type |
| `src/lib/TodoInput.svelte` | Text input + Add button; emits new todo text |
| `src/lib/TodoItem.svelte` | Single todo row: checkbox, text, delete button |
| `src/lib/TodoList.svelte` | Renders list of `TodoItem`, empty state |
| `src/lib/FilterBar.svelte` | Items-left count, filter buttons, clear-completed |
| `src/App.svelte` | Composes components, holds active filter, derives filtered list |
| `src/main.ts` | Vite entry (generated) |
| `vitest.config.ts` | Vitest config with jsdom + svelte plugin |
| `src/setupTests.ts` | Testing-library jest-dom matchers setup |

---

### Task 1: Project scaffold and test infrastructure

**Files:** `package.json`, `vitest.config.ts`, `src/setupTests.ts`, `tsconfig.json` (generated), `src/App.svelte` (replace), `src/lib/sanity.test.ts`

**Interfaces:**
- Produces: a working `npm test` command running Vitest with jsdom and `@testing-library/svelte`.

- [ ] Scaffold the Vite Svelte-TS project into the current directory:
```bash
npm create vite@latest . -- --template svelte-ts
npm install
```
Expected: `src/App.svelte`, `src/main.ts`, `vite.config.ts`, `tsconfig.json` exist.

- [ ] Install test dependencies:
```bash
npm install -D vitest jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
```
Expected: packages added to `devDependencies`.

- [ ] Create `vitest.config.ts`:
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

- [ ] Add the test script to `package.json` `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] Create `src/lib/sanity.test.ts`:
```ts
import { describe, it, expect } from 'vitest';

describe('sanity', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

- [ ] Run the test to confirm infrastructure works:
```bash
npm test
```
Expected: `1 passed` for `src/lib/sanity.test.ts`.

- [ ] Delete `src/lib/sanity.test.ts` and commit:
```bash
rm src/lib/sanity.test.ts
git add -A && git commit -m "Scaffold Svelte-TS project with Vitest"
```

---

### Task 2: localStorage persistence module

**Files:** `src/lib/storage.ts`, `src/lib/storage.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `interface Todo { id: string; text: string; completed: boolean; }`
  - `function loadTodos(): Todo[]` — returns parsed array from localStorage key `'svelte-todos'`, or `[]` if missing/invalid.
  - `function saveTodos(todos: Todo[]): void` — serializes to localStorage key `'svelte-todos'`.

- [ ] Write failing test `src/lib/storage.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { loadTodos, saveTodos, type Todo } from './storage';

const sample: Todo[] = [
  { id: 'a', text: 'one', completed: false },
  { id: 'b', text: 'two', completed: true },
];

describe('storage', () => {
  beforeEach(() => localStorage.clear());

  it('returns [] when nothing stored', () => {
    expect(loadTodos()).toEqual([]);
  });

  it('returns [] when stored value is invalid JSON', () => {
    localStorage.setItem('svelte-todos', 'not json');
    expect(loadTodos()).toEqual([]);
  });

  it('saves and loads todos round-trip', () => {
    saveTodos(sample);
    expect(loadTodos()).toEqual(sample);
  });

  it('uses the key svelte-todos', () => {
    saveTodos(sample);
    expect(localStorage.getItem('svelte-todos')).toBe(JSON.stringify(sample));
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./storage`.

- [ ] Implement `src/lib/storage.ts`:
```ts
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

const KEY = 'svelte-todos';

export function loadTodos(): Todo[] {
  const raw = localStorage.getItem(KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Todo[]) : [];
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
Expected: `4 passed`.

- [ ] Commit:
```bash
git add -A && git commit -m "Add localStorage persistence module"
```

---

### Task 3: Todo store with CRUD actions

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Todo`, `loadTodos`, `saveTodos` from `./storage`.
- Produces:
  - `type Filter = 'all' | 'active' | 'completed';`
  - re-export `type Todo` from storage.
  - `const todos: Writable<Todo[]>` (Svelte writable, initialized from `loadTodos()`, subscribes to persist via `saveTodos`).
  - `function addTodo(text: string): void` — trims text; ignores empty; prepends nothing—appends new `{ id: crypto.randomUUID(), text, completed: false }`.
  - `function toggleTodo(id: string): void`
  - `function deleteTodo(id: string): void`
  - `function clearCompleted(): void`
  - `function filterTodos(list: Todo[], filter: Filter): Todo[]` — pure helper.
  - `function remainingCount(list: Todo[]): number` — count of `!completed`.

- [ ] Write failing test `src/lib/store.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
  todos,
  addTodo,
  toggleTodo,
  deleteTodo,
  clearCompleted,
  filterTodos,
  remainingCount,
  type Todo,
} from './store';

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
});

describe('store actions', () => {
  it('addTodo appends a todo with generated id', () => {
    addTodo('Buy milk');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('Buy milk');
    expect(list[0].completed).toBe(false);
    expect(typeof list[0].id).toBe('string');
    expect(list[0].id.length).toBeGreaterThan(0);
  });

  it('addTodo trims whitespace and ignores empty input', () => {
    addTodo('  hi  ');
    addTodo('   ');
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('hi');
  });

  it('toggleTodo flips completed', () => {
    addTodo('x');
    const id = get(todos)[0].id;
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(true);
    toggleTodo(id);
    expect(get(todos)[0].completed).toBe(false);
  });

  it('deleteTodo removes by id', () => {
    addTodo('x');
    const id = get(todos)[0].id;
    deleteTodo(id);
    expect(get(todos)).toHaveLength(0);
  });

  it('clearCompleted removes completed todos only', () => {
    addTodo('a');
    addTodo('b');
    const [a] = get(todos);
    toggleTodo(a.id);
    clearCompleted();
    const list = get(todos);
    expect(list).toHaveLength(1);
    expect(list[0].text).toBe('b');
  });

  it('persists to localStorage on change', () => {
    addTodo('persist me');
    expect(localStorage.getItem('svelte-todos')).toContain('persist me');
  });
});

describe('pure helpers', () => {
  const list: Todo[] = [
    { id: '1', text: 'a', completed: false },
    { id: '2', text: 'b', completed: true },
  ];

  it('filterTodos all returns everything', () => {
    expect(filterTodos(list, 'all')).toHaveLength(2);
  });
  it('filterTodos active returns incomplete', () => {
    expect(filterTodos(list, 'active')).toEqual([list[0]]);
  });
  it('filterTodos completed returns complete', () => {
    expect(filterTodos(list, 'completed')).toEqual([list[1]]);
  });
  it('remainingCount counts incomplete', () => {
    expect(remainingCount(list)).toBe(1);
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./store`.

- [ ] Implement `src/lib/store.ts`:
```ts
import { writable } from 'svelte/store';
import { loadTodos, saveTodos, type Todo } from './storage';

export type { Todo };
export type Filter = 'all' | 'active' | 'completed';

export const todos = writable<Todo[]>(loadTodos());

todos.subscribe((list) => saveTodos(list));

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

- [ ] Run to see it pass:
```bash
npm test
```
Expected: all `store.test.ts` cases pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add todo store with CRUD actions and helpers"
```

---

### Task 4: TodoInput component

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

**Interfaces:**
- Consumes: nothing (decoupled; emits text upward).
- Produces: `TodoInput.svelte` default export. Dispatches a Svelte `add` event with `detail: string` (trimmed not required here—parent calls `addTodo`). Clears the input after dispatch. Renders an `<input>` with placeholder `What needs to be done?` and a button labeled `Add`. Enter key in input triggers `add`.

- [ ] Write failing test `src/lib/TodoInput.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TodoInput from './TodoInput.svelte';

describe('TodoInput', () => {
  it('renders input and Add button', () => {
    render(TodoInput);
    expect(screen.getByPlaceholderText('What needs to be done?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument();
  });

  it('dispatches add event with text on button click and clears input', async () => {
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
    await fireEvent.input(input, { target: { value: 'Buy milk' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    expect(handler).toHaveBeenCalledWith('Buy milk');
    expect(input.value).toBe('');
  });

  it('dispatches add event on Enter key', async () => {
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', (e) => handler(e.detail));

    const input = screen.getByPlaceholderText('What needs to be done?');
    await fireEvent.input(input, { target: { value: 'Walk dog' } });
    await fireEvent.keyDown(input, { key: 'Enter' });

    expect(handler).toHaveBeenCalledWith('Walk dog');
  });

  it('does not dispatch when input is empty', async () => {
    const { component } = render(TodoInput);
    const handler = vi.fn();
    component.$on('add', handler);
    await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
    expect(handler).not.toHaveBeenCalled();
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./TodoInput.svelte`.

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

- [ ] Run to see it pass:
```bash
npm test
```
Expected: all `TodoInput.test.ts` cases pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoInput component"
```

---

### Task 5: TodoItem component

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`

**Interfaces:**
- Consumes: `Todo` type from `./store`.
- Produces: `TodoItem.svelte` with prop `export let todo: Todo;`. Dispatches `toggle` event (`detail: string` = id) when checkbox clicked, and `delete` event (`detail: string` = id) when delete button clicked. Delete button has accessible name `Delete`. Checkbox is a `role="checkbox"`/`<input type="checkbox">` reflecting `todo.completed`.

- [ ] Write failing test `src/lib/TodoItem.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TodoItem from './TodoItem.svelte';
import type { Todo } from './store';

const todo: Todo = { id: 'x1', text: 'Walk the dog', completed: false };

describe('TodoItem', () => {
  it('renders text and checkbox state', () => {
    render(TodoItem, { props: { todo: { ...todo, completed: true } } });
    expect(screen.getByText('Walk the dog')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeChecked();
  });

  it('dispatches toggle with id on checkbox click', async () => {
    const { component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(screen.getByRole('checkbox'));
    expect(handler).toHaveBeenCalledWith('x1');
  });

  it('dispatches delete with id on delete click', async () => {
    const { component } = render(TodoItem, { props: { todo } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(handler).toHaveBeenCalledWith('x1');
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./TodoItem.svelte`.

- [ ] Implement `src/lib/TodoItem.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Todo } from './store';

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
npm test
```
Expected: all `TodoItem.test.ts` cases pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoItem component"
```

---

### Task 6: TodoList component

**Files:** `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

**Interfaces:**
- Consumes: `Todo` from `./store`; `TodoItem.svelte`.
- Produces: `TodoList.svelte` with prop `export let items: Todo[];`. Renders one `TodoItem` per item. Forwards `toggle` and `delete` events upward (re-dispatch with same `detail`). When `items` is empty, renders the empty-state text `No todos yet. Add one above!`.

- [ ] Write failing test `src/lib/TodoList.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import TodoList from './TodoList.svelte';
import type { Todo } from './store';

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
    expect(screen.getByText('No todos yet. Add one above!')).toBeInTheDocument();
  });

  it('forwards toggle event from a child', async () => {
    const { component } = render(TodoList, { props: { items } });
    const handler = vi.fn();
    component.$on('toggle', (e) => handler(e.detail));
    await fireEvent.click(screen.getAllByRole('checkbox')[0]);
    expect(handler).toHaveBeenCalledWith('1');
  });

  it('forwards delete event from a child', async () => {
    const { component } = render(TodoList, { props: { items } });
    const handler = vi.fn();
    component.$on('delete', (e) => handler(e.detail));
    await fireEvent.click(screen.getAllByRole('button', { name: 'Delete' })[1]);
    expect(handler).toHaveBeenCalledWith('2');
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:
```svelte
<script lang="ts">
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './store';

  export let items: Todo[];
</script>

{#if items.length === 0}
  <p class="empty">No todos yet. Add one above!</p>
{:else}
  <ul class="todo-list">
    {#each items as todo (todo.id)}
      <TodoItem {todo} on:toggle on:delete />
    {/each}
  </ul>
{/if}
```

> Note: `on:toggle on:delete` without a handler forwards the child events upward with their original `detail`.

- [ ] Run to see it pass:
```bash
npm test
```
Expected: all `TodoList.test.ts` cases pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add TodoList component with empty state"
```

---

### Task 7: FilterBar component

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

**Interfaces:**
- Consumes: `Filter` from `./store`.
- Produces: `FilterBar.svelte` with props `export let remaining: number;` and `export let filter: Filter;`. Renders `<N> items left` (singular `1 item left`). Renders three buttons: `All`, `Active`, `Completed`; clicking dispatches `filterChange` event (`detail: Filter`). Active filter button gets class `active`. Renders a `Clear completed` button that dispatches `clearCompleted` event.

- [ ] Write failing test `src/lib/FilterBar.test.ts`:
```ts
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import FilterBar from './FilterBar.svelte';

describe('FilterBar', () => {
  it('shows plural items left', () => {
    render(FilterBar, { props: { remaining: 2, filter: 'all' } });
    expect(screen.getByText('2 items left')).toBeInTheDocument();
  });

  it('shows singular item left', () => {
    render(FilterBar, { props: { remaining: 1, filter: 'all' } });
    expect(screen.getByText('1 item left')).toBeInTheDocument();
  });

  it('marks the active filter button', () => {
    render(FilterBar, { props: { remaining: 0, filter: 'active' } });
    expect(screen.getByRole('button', { name: 'Active' })).toHaveClass('active');
    expect(screen.getByRole('button', { name: 'All' })).not.toHaveClass('active');
  });

  it('dispatches filterChange on button click', async () => {
    const { component } = render(FilterBar, { props: { remaining: 0, filter: 'all' } });
    const handler = vi.fn();
    component.$on('filterChange', (e) => handler(e.detail));
    await fireEvent.click(screen.getByRole('button', { name: 'Completed' }));
    expect(handler).toHaveBeenCalledWith('completed');
  });

  it('dispatches clearCompleted', async () => {
    const { component } = render(FilterBar, { props: { remaining: 0, filter: 'all' } });
    const handler = vi.fn();
    component.$on('clearCompleted', handler);
    await fireEvent.click(screen.getByRole('button', { name: 'Clear completed' }));
    expect(handler).toHaveBeenCalled();
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failure — cannot resolve `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Filter } from './store';

  export let remaining: number;
  export let filter: Filter;

  const dispatch = createEventDispatcher<{ filterChange: Filter; clearCompleted: void }>();
  const filters: Filter[] = ['all', 'active', 'completed'];
  const labels: Record<Filter, string> = {
    all: 'All',
    active: 'Active',
    completed: 'Completed',
  };

  $: itemsLeft = `${remaining} ${remaining === 1 ? 'item' : 'items'} left`;
</script>

<div class="filter-bar">
  <span class="count">{itemsLeft}</span>
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

<style>
  .filter-bar button.active {
    font-weight: bold;
  }
</style>
```

- [ ] Run to see it pass:
```bash
npm test
```
Expected: all `FilterBar.test.ts` cases pass.

- [ ] Commit:
```bash
git add -A && git commit -m "Add FilterBar component"
```

---

### Task 8: App composition and integration

**Files:** `src/App.svelte`, `src/App.test.ts`

**Interfaces:**
- Consumes: `todos`, `addTodo`, `toggleTodo`, `deleteTodo`, `clearCompleted`, `filterTodos`, `remainingCount`, `Filter` from `./lib/store`; `TodoInput`, `TodoList`, `FilterBar` components.
- Produces: `App.svelte` default export — the full wired application with local `filter` state defaulting to `'all'`.

- [ ] Write failing test `src/App.test.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import App from './App.svelte';
import { todos } from './lib/store';

async function addViaUI(text: string) {
  const input = screen.getByPlaceholderText('What needs to be done?');
  await fireEvent.input(input, { target: { value: text } });
  await fireEvent.click(screen.getByRole('button', { name: 'Add' }));
}

beforeEach(() => {
  localStorage.clear();
  todos.set([]);
});

describe('App integration', () => {
  it('shows title', () => {
    render(App);
    expect(screen.getByText('Svelte Todos')).toBeInTheDocument();
  });

  it('adds a todo via the UI', async () => {
    render(App);
    await addViaUI('Buy groceries');
    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('1 item left')).toBeInTheDocument();
  });

  it('toggles a todo and updates remaining count', async () => {
    render(App);
    await addViaUI('Walk dog');
    await fireEvent.click(screen.getByRole('checkbox'));
    expect(screen.getByText('0 items left')).toBeInTheDocument();
  });

  it('deletes a todo', async () => {
    render(App);
    await addViaUI('Temp');
    await fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(screen.queryByText('Temp')).not.toBeInTheDocument();
    expect(screen.getByText('No todos yet. Add one above!')).toBeInTheDocument();
  });

  it('filters to Active and Completed', async () => {
    render(App);
    await addViaUI('a');
    await addViaUI('b');
    const checkboxes = screen.getAllByRole('checkbox');
    await fireEvent.click(checkboxes[0]); // complete 'a'

    await fireEvent.click(screen.getByRole('button', { name: 'Active' }));
    expect(screen.queryByText('a')).not.toBeInTheDocument();
    expect(screen.getByText('b')).toBeInTheDocument();

    await fireEvent.click(screen.getByRole('button', { name: 'Completed' }));
    expect(screen.getByText('a')).toBeInTheDocument();
    expect(screen.queryByText('b')).not.toBeInTheDocument();
  });

  it('clears completed todos', async () => {
    render(App);
    await addViaUI('keep');
    await addViaUI('remove');
    const checkboxes = screen.getAllByRole('checkbox');
    await fireEvent.click(checkboxes[1]); // complete 'remove'
    await fireEvent.click(screen.getByRole('button', { name: 'Clear completed' }));
    expect(screen.getByText('keep')).toBeInTheDocument();
    expect(screen.queryByText('remove')).not.toBeInTheDocument();
  });

  it('persists todos to localStorage', async () => {
    render(App);
    await addViaUI('persisted');
    expect(localStorage.getItem('svelte-todos')).toContain('persisted');
  });
});
```

- [ ] Run to see it fail:
```bash
npm test
```
Expected: failures in `App.test.ts` (App not yet wired / title differs).

- [ ] Implement `src/App.svelte`:
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
    filterTodos,
    remainingCount,
    type Filter,
  } from './lib/store';

  let filter: Filter = 'all';

  $: visible = filterTodos($todos, filter);
  $: remaining = remainingCount($todos);
</script>

<main class="app">
  <h1>Svelte Todos</h1>
  <TodoInput on:add={(e) => addTodo(e.detail)} />
  <TodoList
    items={visible}
    on:toggle={(e) => toggleTodo(e.detail)}
    on:delete={(e) => deleteTodo(e.detail)}
  />
  <FilterBar
    {remaining}
    {filter}
    on:filterChange={(e) => (filter = e.detail)}
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
npm test
```
Expected: all `App.test.ts` cases pass; whole suite green.

- [ ] Verify the dev build compiles:
```bash
npm run build
```
Expected: build completes with no TypeScript/Svelte errors.

- [ ] Commit:
```bash
git add -A && git commit -m "Wire App composition with full integration tests"
```

---

### Task 9: Final verification

**Files:** none (verification only).

**Interfaces:** Consumes everything; produces a verified green suite mapping to all acceptance criteria.

- [ ] Run the full suite:
```bash
npm test
```
Expected: all test files pass (`storage`, `store`, `TodoInput`, `TodoItem`, `TodoList`, `FilterBar`, `App`).

- [ ] Confirm acceptance-criteria coverage (no code change; checklist):
  - AC1 add via Enter/Add → `TodoInput.test.ts`, `App.test.ts`
  - AC2 toggle → `TodoItem.test.ts`, `App.test.ts`
  - AC3 delete → `TodoItem.test.ts`, `App.test.ts`
  - AC4 filters → `FilterBar.test.ts`, `App.test.ts`
  - AC5 items-left count