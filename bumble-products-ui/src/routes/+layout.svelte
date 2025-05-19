<script lang="ts">
  import { onMount } from 'svelte';
  import { searchTerm, categoryFilter, getCategories } from '$lib/data/productStore';

  let categories: string[] = [];

  onMount(() => {
    categories = getCategories();
  });

  function handleSearch(event: Event) {
    const input = event.target as HTMLInputElement;
    searchTerm.set(input.value);
  }

  function handleCategoryChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    categoryFilter.set(select.value);
  }
</script>

<div class="app">
  <header>
    <div class="logo">
      <a href="/">Bumble and Bumble Products</a>
    </div>
    <nav class="main-nav">
      <ul>
        <li><a href="/" class="nav-link">Grid View</a></li>
        <li><a href="/table" class="nav-link">Table View</a></li>
      </ul>
    </nav>
    <div class="search-container">
      <input
        type="text"
        placeholder="Search products..."
        on:input={handleSearch}
      />
      <select on:change={handleCategoryChange}>
        <option value="">All Categories</option>
        {#each categories as category}
          <option value={category}>{category}</option>
        {/each}
      </select>
    </div>
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <p>© 2024 Bumble and Bumble Products Viewer</p>
  </footer>
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9f9f9;
    color: #333;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    background-color: #222;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
  }

  .logo a {
    color: white;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: bold;
  }

  .main-nav ul {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 1rem;
  }

  .nav-link {
    color: white;
    text-decoration: none;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .nav-link:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .search-container {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  input, select {
    padding: 0.5rem;
    border: none;
    border-radius: 4px;
  }

  main {
    flex: 1;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  footer {
    background-color: #222;
    color: white;
    text-align: center;
    padding: 1rem;
    margin-top: auto;
  }

  @media (max-width: 768px) {
    header {
      flex-direction: column;
      gap: 1rem;
    }

    .main-nav {
      width: 100%;
      margin: 0.5rem 0;
    }

    .main-nav ul {
      justify-content: center;
    }

    .search-container {
      width: 100%;
    }

    input, select {
      width: 100%;
    }
  }
</style>
