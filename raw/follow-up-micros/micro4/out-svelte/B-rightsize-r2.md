# Svelte Todo List - Implementation Plan

## Overview

This plan builds a Svelte todo list application with localStorage persistence, filtering, and full test coverage. We use Vite + Svelte + TypeScript, and Vitest for testing. Work proceeds bottom-up: data model and storage first, then the store, then UI components, then wiring them into `App.svelte`.

Each task is TDD: write a failing test, run it to confirm failure, implement, run to confirm pass, commit.

## Prerequisites

- Node.js 18+ installed (`node --version` should print `v18.x` or higher)
- npm installed (`npm --version` should print a version)

## File Structure

Files created or modified across this plan:

| File | Responsibility |
|------|----------------|
| `package.json` | Project dependencies and scripts |
| `vite.config.ts` | Vite + Svelte plugin + Vitest config |
| `tsconfig.json` | TypeScript config |
| `svelte.config.js` | Svelte preprocess config |
| `vitest-setup.ts` | Testing-library cleanup + jest-dom matchers |
| `index.html` | HTML entry point |
| `src/main.ts` | Mounts `App.svelte` |
| `src/app.css` | Global styles |
| `src/lib/types.ts` | `Todo` interface and `Filter` type |
| `src/lib/storage.ts` | localStorage load/save of todos |
| `src/lib/store.ts` | Svelte store with todo CRUD + filter actions |
| `src/lib/TodoInput.svelte` | Text input + Add button |
| `src/lib/TodoItem.svelte` | Single todo: checkbox, text, delete |
| `src/lib/TodoList.svelte` | List container + empty state |
| `src/lib/FilterBar.svelte` | Items-left count, filter buttons, clear completed |
| `src/App.svelte` | Main app wiring all components |

Test files (co-located):

| File | Tests |
|------|-------|
| `src/lib/storage.test.ts` | storage load/save |
| `src/lib/store.test.ts` | store CRUD + filtering |
| `src/lib/TodoInput.test.ts` | input component |
| `src/lib/TodoItem.test.ts` | item component |
| `src/lib/TodoList.test.ts` | list component |
| `src/lib/FilterBar.test.ts` | filter bar component |
| `src/App.test.ts` | end-to-end acceptance |

---

### Task 1: Project Scaffolding

Sets up the Vite + Svelte + TypeScript + Vitest project so all later tasks have a working test runner. The deliverable is a passing smoke test.

**Files:** `package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `svelte.config.js`, `vitest-setup.ts`, `index.html`, `src/main.ts`, `src/app.css`, `src/App.svelte`, `src/smoke.test.ts`, `.gitignore`

- [ ] Initialize git and npm in the project directory:
  ```bash
  git init
  npm init -y
  ```
  Expected: creates `.git/` and a `package.json`.

- [ ] Install dependencies:
  ```bash
  npm install --save-dev svelte @sveltejs/vite-plugin-svelte vite typescript svelte-check tslib \
    vitest @vitest/ui jsdom @testing-library/svelte @testing-library/jest-dom @testing-library/user-event
  ```
  Expected: dependencies appear under `devDependencies` in `package.json`.

- [ ] Overwrite `package.json` scripts and type. Replace the `"scripts"` block and add `"type": "module"`:
  ```json
  {
    "name": "svelte-todos",
    "private": true,
    "version": "0.0.0",
    "type": "module",
    "scripts": {
      "dev": "vite",
      "build": "vite build",
      "preview": "vite preview",
      "check": "svelte-check --tsconfig ./tsconfig.json",
      "test": "vitest run",
      "test:watch": "vitest"
    }
  }
  ```
  Leave the `devDependencies` block as installed.

- [ ] Create `.gitignore`:
  ```
  node_modules
  dist
  .DS_Store
  *.local
  ```

- [ ] Create `tsconfig.json`:
  ```json
  {
    "compilerOptions": {
      "target": "ESNext",
      "useDefineForClassFields": true,
      "module": "ESNext",
      "resolveJsonModule": true,
      "allowJs": true,
      "checkJs": true,
      "isolatedModules": true,
      "moduleResolution": "bundler",
      "lib": ["ESNext", "DOM", "DOM.Iterable"],
      "strict": true,
      "skipLibCheck": true,
      "types": ["vitest/globals", "@testing-library/jest-dom"]
    },
    "include": ["src/**/*.ts", "src/**/*.svelte", "vitest-setup.ts"],
    "references": [{ "path": "./tsconfig.node.json" }]
  }
  ```

- [ ] Create `tsconfig.node.json`:
  ```json
  {
    "compilerOptions": {
      "composite": true,
      "module": "ESNext",
      "moduleResolution": "bundler",
      "allowSyntheticDefaultImports": true,
      "types": ["node"]
    },
    "include": ["vite.config.ts"]
  }
  ```

- [ ] Create `svelte.config.js`:
  ```js
  import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

  export default {
    preprocess: vitePreprocess(),
  };
  ```

- [ ] Create `vite.config.ts`:
  ```ts
  /// <reference types="vitest" />
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
  ```ts
  import '@testing-library/jest-dom/vitest';
  import { afterEach } from 'vitest';
  import { cleanup } from '@testing-library/svelte';

  afterEach(() => {
    cleanup();
  });
  ```

- [ ] Create `index.html`:
  ```html
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Svelte Todos</title>
    </head>
    <body>
      <div id="app"></div>
      <script type="module" src="/src/main.ts"></script>
    </body>
  </html>
  ```

- [ ] Create `src/app.css`:
  ```css
  :root {
    font-family: system-ui, sans-serif;
    color: #213547;
    background-color: #f5f5f5;
  }

  body {
    margin: 0;
    display: flex;
    justify-content: center;
    padding: 2rem 1rem;
  }
  ```

- [ ] Create `src/main.ts`:
  ```ts
  import './app.css';
  import { mount } from 'svelte';
  import App from './App.svelte';

  const app = mount(App, {
    target: document.getElementById('app')!,
  });

  export default app;
  ```

- [ ] Create a minimal `src/App.svelte` (replaced fully in Task 7):
  ```svelte
  <main>
    <h1>Svelte Todos</h1>
  </main>
  ```

- [ ] Create `src/smoke.test.ts` to verify the test harness:
  ```ts
  import { describe, it, expect } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import App from './App.svelte';

  describe('smoke', () => {
    it('renders the heading', () => {
      render(App);
      expect(screen.getByRole('heading', { name: 'Svelte Todos' })).toBeInTheDocument();
    });
  });
  ```

- [ ] Run the test to confirm the harness works:
  ```bash
  npm test
  ```
  Expected: `Test Files  1 passed (1)` and `Tests  1 passed (1)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Scaffold Svelte + Vitest project"
  ```

---

### Task 2: Types and Storage

Defines the `Todo` / `Filter` types and the localStorage persistence layer. Deliverable: tested `load` and `save` functions that round-trip todos and tolerate missing/corrupt data.

**Files:** `src/lib/types.ts`, `src/lib/storage.ts`, `src/lib/storage.test.ts`

- [ ] Create `src/lib/types.ts`:
  ```ts
  export interface Todo {
    id: string;
    text: string;
    completed: boolean;
  }

  export type Filter = 'all' | 'active' | 'completed';
  ```

- [ ] Write the failing test `src/lib/storage.test.ts`:
  ```ts
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

    it('round-trips todos through save and load', () => {
      saveTodos(sample);
      expect(loadTodos()).toEqual(sample);
    });

    it('writes to the expected storage key', () => {
      saveTodos(sample);
      expect(localStorage.getItem(STORAGE_KEY)).toBe(JSON.stringify(sample));
    });

    it('returns empty array when stored value is corrupt', () => {
      localStorage.setItem(STORAGE_KEY, 'not json{');
      expect(loadTodos()).toEqual([]);
    });

    it('returns empty array when stored value is not an array', () => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ foo: 'bar' }));
      expect(loadTodos()).toEqual([]);
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- storage
  ```
  Expected: failure with `Failed to resolve import "./storage"` or similar.

- [ ] Implement `src/lib/storage.ts`:
  ```ts
  import type { Todo } from './types';

  export const STORAGE_KEY = 'svelte-todos';

  export function loadTodos(): Todo[] {
    const raw = localStorage.getItem(STORAGE_KEY);
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
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  }
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- storage
  ```
  Expected: `Tests  5 passed (5)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add types and localStorage persistence"
  ```

---

### Task 3: Todo Store

Builds the Svelte store holding todos plus actions for add/toggle/delete/clear-completed, and a separate filter store. Persists to localStorage on every change. Deliverable: tested store actions.

**Files:** `src/lib/store.ts`, `src/lib/store.test.ts`

- [ ] Write the failing test `src/lib/store.test.ts`:
  ```ts
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

    it('addTodo appends a todo with text, incomplete, and an id', () => {
      addTodo('Buy milk');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('Buy milk');
      expect(list[0].completed).toBe(false);
      expect(typeof list[0].id).toBe('string');
      expect(list[0].id.length).toBeGreaterThan(0);
    });

    it('addTodo trims whitespace and ignores empty input', () => {
      addTodo('  hello  ');
      addTodo('   ');
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('hello');
    });

    it('addTodo gives unique ids', () => {
      addTodo('a');
      addTodo('b');
      const [first, second] = get(todos);
      expect(first.id).not.toBe(second.id);
    });

    it('toggleTodo flips completion', () => {
      addTodo('a');
      const id = get(todos)[0].id;
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(true);
      toggleTodo(id);
      expect(get(todos)[0].completed).toBe(false);
    });

    it('deleteTodo removes the matching todo', () => {
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
      const id = get(todos)[0].id;
      toggleTodo(id);
      clearCompleted();
      const list = get(todos);
      expect(list).toHaveLength(1);
      expect(list[0].text).toBe('b');
    });

    it('persists to localStorage on change', () => {
      addTodo('persisted');
      expect(loadTodos()).toHaveLength(1);
      expect(loadTodos()[0].text).toBe('persisted');
    });

    it('remainingCount counts incomplete todos', () => {
      addTodo('a');
      addTodo('b');
      const id = get(todos)[0].id;
      toggleTodo(id);
      expect(get(remainingCount)).toBe(1);
    });

    it('filteredTodos respects the active filter', () => {
      addTodo('a');
      addTodo('b');
      const id = get(todos)[0].id;
      toggleTodo(id);

      filter.set('all');
      expect(get(filteredTodos)).toHaveLength(2);

      filter.set('active');
      expect(get(filteredTodos).map((t) => t.text)).toEqual(['b']);

      filter.set('completed');
      expect(get(filteredTodos).map((t) => t.text)).toEqual(['a']);
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- store
  ```
  Expected: failure resolving `./store`.

- [ ] Implement `src/lib/store.ts`:
  ```ts
  import { writable, derived } from 'svelte/store';
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
  npm test -- store
  ```
  Expected: `Tests  9 passed (9)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add todo store with CRUD, filter, and persistence"
  ```

---

### Task 4: TodoInput Component

A text input plus Add button that emits an `add` event with trimmed text and clears itself. Deliverable: tested component.

**Files:** `src/lib/TodoInput.svelte`, `src/lib/TodoInput.test.ts`

- [ ] Write the failing test `src/lib/TodoInput.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import userEvent from '@testing-library/user-event';
  import TodoInput from './TodoInput.svelte';

  describe('TodoInput', () => {
    it('dispatches add with typed text on Add button click', async () => {
      const user = userEvent.setup();
      const onAdd = vi.fn();
      render(TodoInput, { props: { onAdd } });

      await user.type(screen.getByRole('textbox'), 'New task');
      await user.click(screen.getByRole('button', { name: 'Add' }));

      expect(onAdd).toHaveBeenCalledWith('New task');
    });

    it('dispatches add on Enter key', async () => {
      const user = userEvent.setup();
      const onAdd = vi.fn();
      render(TodoInput, { props: { onAdd } });

      await user.type(screen.getByRole('textbox'), 'Press enter{Enter}');

      expect(onAdd).toHaveBeenCalledWith('Press enter');
    });

    it('clears the input after adding', async () => {
      const user = userEvent.setup();
      render(TodoInput, { props: { onAdd: () => {} } });

      const input = screen.getByRole('textbox') as HTMLInputElement;
      await user.type(input, 'Clear me{Enter}');

      expect(input.value).toBe('');
    });

    it('does not dispatch when input is empty', async () => {
      const user = userEvent.setup();
      const onAdd = vi.fn();
      render(TodoInput, { props: { onAdd } });

      await user.click(screen.getByRole('button', { name: 'Add' }));

      expect(onAdd).not.toHaveBeenCalled();
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoInput
  ```
  Expected: failure resolving `./TodoInput.svelte`.

- [ ] Implement `src/lib/TodoInput.svelte`:
  ```svelte
  <script lang="ts">
    let { onAdd }: { onAdd: (text: string) => void } = $props();
    let text = $state('');

    function submit() {
      if (text.trim() === '') return;
      onAdd(text.trim());
      text = '';
    }
  </script>

  <form class="todo-input" onsubmit={(e) => { e.preventDefault(); submit(); }}>
    <input
      type="text"
      placeholder="What needs to be done?"
      bind:value={text}
    />
    <button type="submit">Add</button>
  </form>

  <style>
    .todo-input {
      display: flex;
      gap: 0.5rem;
    }
    input {
      flex: 1;
      padding: 0.5rem;
      font-size: 1rem;
    }
    button {
      padding: 0.5rem 1rem;
      font-size: 1rem;
      cursor: pointer;
    }
  </style>
  ```

  Note: the `<form>` `onsubmit` handles both the Add button (type="submit") and Enter key in a single path.

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoInput
  ```
  Expected: `Tests  4 passed (4)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoInput component"
  ```

---

### Task 5: TodoItem and TodoList Components

`TodoItem` renders one todo with a checkbox, text, and delete button, emitting `toggle`/`delete`. `TodoList` renders a list of items or an empty-state message. Deliverable: both components tested.

**Files:** `src/lib/TodoItem.svelte`, `src/lib/TodoItem.test.ts`, `src/lib/TodoList.svelte`, `src/lib/TodoList.test.ts`

- [ ] Write the failing test `src/lib/TodoItem.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import userEvent from '@testing-library/user-event';
  import TodoItem from './TodoItem.svelte';
  import type { Todo } from './types';

  const todo: Todo = { id: '1', text: 'Walk the dog', completed: false };

  describe('TodoItem', () => {
    it('renders the todo text', () => {
      render(TodoItem, { props: { todo, onToggle: () => {}, onDelete: () => {} } });
      expect(screen.getByText('Walk the dog')).toBeInTheDocument();
    });

    it('checkbox reflects completed state', () => {
      render(TodoItem, {
        props: { todo: { ...todo, completed: true }, onToggle: () => {}, onDelete: () => {} },
      });
      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('dispatches toggle with id when checkbox clicked', async () => {
      const user = userEvent.setup();
      const onToggle = vi.fn();
      render(TodoItem, { props: { todo, onToggle, onDelete: () => {} } });

      await user.click(screen.getByRole('checkbox'));

      expect(onToggle).toHaveBeenCalledWith('1');
    });

    it('dispatches delete with id when delete button clicked', async () => {
      const user = userEvent.setup();
      const onDelete = vi.fn();
      render(TodoItem, { props: { todo, onToggle: () => {}, onDelete } });

      await user.click(screen.getByRole('button', { name: /delete/i }));

      expect(onDelete).toHaveBeenCalledWith('1');
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoItem
  ```
  Expected: failure resolving `./TodoItem.svelte`.

- [ ] Implement `src/lib/TodoItem.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';

    let {
      todo,
      onToggle,
      onDelete,
    }: {
      todo: Todo;
      onToggle: (id: string) => void;
      onDelete: (id: string) => void;
    } = $props();
  </script>

  <li class="todo-item" class:completed={todo.completed}>
    <input
      type="checkbox"
      checked={todo.completed}
      onchange={() => onToggle(todo.id)}
    />
    <span class="text">{todo.text}</span>
    <button class="delete" aria-label="Delete" onclick={() => onDelete(todo.id)}>
      ✕
    </button>
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
      border: none;
      background: none;
      cursor: pointer;
      color: #c00;
      font-size: 1rem;
    }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- TodoItem
  ```
  Expected: `Tests  4 passed (4)`.

- [ ] Write the failing test `src/lib/TodoList.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import userEvent from '@testing-library/user-event';
  import TodoList from './TodoList.svelte';
  import type { Todo } from './types';

  const todos: Todo[] = [
    { id: '1', text: 'first', completed: false },
    { id: '2', text: 'second', completed: true },
  ];

  describe('TodoList', () => {
    it('renders one item per todo', () => {
      render(TodoList, { props: { todos, onToggle: () => {}, onDelete: () => {} } });
      expect(screen.getByText('first')).toBeInTheDocument();
      expect(screen.getByText('second')).toBeInTheDocument();
      expect(screen.getAllByRole('listitem')).toHaveLength(2);
    });

    it('shows empty state when there are no todos', () => {
      render(TodoList, { props: { todos: [], onToggle: () => {}, onDelete: () => {} } });
      expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
      expect(screen.queryAllByRole('listitem')).toHaveLength(0);
    });

    it('forwards toggle events from items', async () => {
      const user = userEvent.setup();
      const onToggle = vi.fn();
      render(TodoList, { props: { todos, onToggle, onDelete: () => {} } });

      await user.click(screen.getAllByRole('checkbox')[0]);

      expect(onToggle).toHaveBeenCalledWith('1');
    });

    it('forwards delete events from items', async () => {
      const user = userEvent.setup();
      const onDelete = vi.fn();
      render(TodoList, { props: { todos, onToggle: () => {}, onDelete } });

      await user.click(screen.getAllByRole('button', { name: /delete/i })[1]);

      expect(onDelete).toHaveBeenCalledWith('2');
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- TodoList
  ```
  Expected: failure resolving `./TodoList.svelte`.

- [ ] Implement `src/lib/TodoList.svelte`:
  ```svelte
  <script lang="ts">
    import type { Todo } from './types';
    import TodoItem from './TodoItem.svelte';

    let {
      todos,
      onToggle,
      onDelete,
    }: {
      todos: Todo[];
      onToggle: (id: string) => void;
      onDelete: (id: string) => void;
    } = $props();
  </script>

  {#if todos.length === 0}
    <p class="empty">Nothing here yet — add your first todo above!</p>
  {:else}
    <ul class="todo-list">
      {#each todos as todo (todo.id)}
        <TodoItem {todo} {onToggle} {onDelete} />
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
  npm test -- TodoList
  ```
  Expected: `Tests  4 passed (4)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add TodoItem and TodoList components"
  ```

---

### Task 6: FilterBar Component

Shows the remaining-items count, three filter buttons (highlighting the active one), and a clear-completed button. Deliverable: tested component.

**Files:** `src/lib/FilterBar.svelte`, `src/lib/FilterBar.test.ts`

- [ ] Write the failing test `src/lib/FilterBar.test.ts`:
  ```ts
  import { describe, it, expect, vi } from 'vitest';
  import { render, screen } from '@testing-library/svelte';
  import userEvent from '@testing-library/user-event';
  import FilterBar from './FilterBar.svelte';

  describe('FilterBar', () => {
    const baseProps = {
      remaining: 2,
      filter: 'all' as const,
      onFilterChange: () => {},
      onClearCompleted: () => {},
    };

    it('shows the remaining count with pluralization', () => {
      render(FilterBar, { props: { ...baseProps, remaining: 2 } });
      expect(screen.getByText('2 items left')).toBeInTheDocument();
    });

    it('uses singular for one item', () => {
      render(FilterBar, { props: { ...baseProps, remaining: 1 } });
      expect(screen.getByText('1 item left')).toBeInTheDocument();
    });

    it('marks the active filter button as pressed', () => {
      render(FilterBar, { props: { ...baseProps, filter: 'active' } });
      expect(screen.getByRole('button', { name: 'Active' })).toHaveAttribute(
        'aria-pressed',
        'true'
      );
      expect(screen.getByRole('button', { name: 'All' })).toHaveAttribute(
        'aria-pressed',
        'false'
      );
    });

    it('dispatches filterChange when a filter button is clicked', async () => {
      const user = userEvent.setup();
      const onFilterChange = vi.fn();
      render(FilterBar, { props: { ...baseProps, onFilterChange } });

      await user.click(screen.getByRole('button', { name: 'Completed' }));

      expect(onFilterChange).toHaveBeenCalledWith('completed');
    });

    it('dispatches clearCompleted when clear button is clicked', async () => {
      const user = userEvent.setup();
      const onClearCompleted = vi.fn();
      render(FilterBar, { props: { ...baseProps, onClearCompleted } });

      await user.click(screen.getByRole('button', { name: /clear completed/i }));

      expect(onClearCompleted).toHaveBeenCalled();
    });
  });
  ```

- [ ] Run to see it fail:
  ```bash
  npm test -- FilterBar
  ```
  Expected: failure resolving `./FilterBar.svelte`.

- [ ] Implement `src/lib/FilterBar.svelte`:
  ```svelte
  <script lang="ts">
    import type { Filter } from './types';

    let {
      remaining,
      filter,
      onFilterChange,
      onClearCompleted,
    }: {
      remaining: number;
      filter: Filter;
      onFilterChange: (f: Filter) => void;
      onClearCompleted: () => void;
    } = $props();

    const filters: { value: Filter; label: string }[] = [
      { value: 'all', label: 'All' },
      { value: 'active', label: 'Active' },
      { value: 'completed', label: 'Completed' },
    ];
  </script>

  <div class="filter-bar">
    <span class="count">{remaining} {remaining === 1 ? 'item' : 'items'} left</span>

    <div class="filters">
      {#each filters as f}
        <button
          aria-pressed={filter === f.value}
          class:active={filter === f.value}
          onclick={() => onFilterChange(f.value)}
        >
          {f.label}
        </button>
      {/each}
    </div>

    <button class="clear" onclick={() => onClearCompleted()}>Clear completed</button>
  </div>

  <style>
    .filter-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      flex-wrap: wrap;
      font-size: 0.9rem;
    }
    .filters button {
      border: 1px solid transparent;
      background: none;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
    }
    .filters button.active {
      border-color: #888;
      border-radius: 4px;
    }
    .clear {
      border: none;
      background: none;
      cursor: pointer;
      color: #666;
    }
    .clear:hover {
      text-decoration: underline;
    }
  </style>
  ```

- [ ] Run to see it pass:
  ```bash
  npm test -- FilterBar
  ```
  Expected: `Tests  5 passed (5)`.

- [ ] Commit:
  ```bash
  git add -A && git commit -m "Add FilterBar component"
  ```

---

### Task 7: App Wiring and Acceptance

Wires all components into `App.svelte` using the store, and validates every acceptance criterion end-to-end. Deliverable: complete app with passing acceptance tests.

**Files:** `src/App.svelte`, `src/App.test.ts`, delete `src/smoke.test.ts`

- [ ] Remove the now-redundant smoke test:
  ```bash
  git rm src/smoke.test.ts
  ```

- [ ] Write the failing acceptance test `src/App.test.