<script lang="ts">
  import { products, parseProductDescription } from '$lib/data/productStore';
  import type { Product } from '$lib/data/productStore';
  
  // State for sorting
  let sortField: keyof Product | 'category' | 'price' = 'name';
  let sortDirection: 'asc' | 'desc' = 'asc';
  
  // State for filtering
  let nameFilter = '';
  let categoryFilter = '';
  
  // Derived products with sorting and filtering
  $: filteredProducts = $products
    .filter(product => {
      // Filter by name
      const nameMatch = nameFilter === '' || 
        product.name.toLowerCase().includes(nameFilter.toLowerCase());
      
      // Filter by category
      const categoryMatch = categoryFilter === '' || 
        (product.other && product.other.includes(`CATEGORY\n${categoryFilter}`));
      
      return nameMatch && categoryMatch;
    })
    .sort((a, b) => {
      let valueA: any;
      let valueB: any;
      
      // Handle special sort fields
      if (sortField === 'category') {
        const categoryA = a.other ? (a.other.match(/CATEGORY\n([^\n]+)/) || [])[1] || '' : '';
        const categoryB = b.other ? (b.other.match(/CATEGORY\n([^\n]+)/) || [])[1] || '' : '';
        valueA = categoryA;
        valueB = categoryB;
      } else if (sortField === 'price') {
        valueA = a.options && a.options.length > 0 ? a.options[0].price.replace('$', '') : '0';
        valueB = b.options && b.options.length > 0 ? b.options[0].price.replace('$', '') : '0';
        // Convert to numbers for price comparison
        valueA = parseFloat(valueA);
        valueB = parseFloat(valueB);
      } else {
        valueA = a[sortField];
        valueB = b[sortField];
      }
      
      // Compare values based on sort direction
      if (sortDirection === 'asc') {
        return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
      } else {
        return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
      }
    });
  
  // Function to handle sorting
  function handleSort(field: typeof sortField) {
    if (sortField === field) {
      // Toggle direction if clicking the same field
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Set new field and reset direction to ascending
      sortField = field;
      sortDirection = 'asc';
    }
  }
  
  // Function to get category from product
  function getCategory(product: Product): string {
    if (product.other) {
      const match = product.other.match(/CATEGORY\n([^\n]+)/);
      return match && match[1] ? match[1] : '';
    }
    return '';
  }
  
  // Function to get price from product
  function getPrice(product: Product): string {
    return product.options && product.options.length > 0 ? product.options[0].price : '';
  }
  
  // Function to get ingredient count
  function getIngredientCount(product: Product): number {
    return product.ingredients ? product.ingredients.length : 0;
  }
</script>

<div class="table-container">
  <div class="filters">
    <div class="filter">
      <label for="name-filter">Filter by Name:</label>
      <input 
        id="name-filter" 
        type="text" 
        bind:value={nameFilter} 
        placeholder="Enter product name..."
      />
    </div>
    
    <div class="filter">
      <label for="category-filter">Filter by Category:</label>
      <input 
        id="category-filter" 
        type="text" 
        bind:value={categoryFilter} 
        placeholder="Enter category..."
      />
    </div>
  </div>
  
  <div class="table-stats">
    <p>Showing {filteredProducts.length} of {$products.length} products</p>
  </div>
  
  <table>
    <thead>
      <tr>
        <th on:click={() => handleSort('name')} class:active={sortField === 'name'}>
          Name {sortField === 'name' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
        </th>
        <th on:click={() => handleSort('category')} class:active={sortField === 'category'}>
          Category {sortField === 'category' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
        </th>
        <th on:click={() => handleSort('price')} class:active={sortField === 'price'}>
          Price {sortField === 'price' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
        </th>
        <th>Ingredients</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      {#each filteredProducts as product}
        <tr>
          <td>{product.name}</td>
          <td>{getCategory(product)}</td>
          <td>{getPrice(product)}</td>
          <td>{getIngredientCount(product)}</td>
          <td>
            <a href={`/product/${encodeURIComponent(product.name)}`} class="view-button">View</a>
          </td>
        </tr>
      {/each}
      
      {#if filteredProducts.length === 0}
        <tr>
          <td colspan="5" class="no-results">No products found matching your filters</td>
        </tr>
      {/if}
    </tbody>
  </table>
</div>

<style>
  .table-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    overflow-x: auto;
  }
  
  .filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }
  
  .filter {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 200px;
  }
  
  .filter label {
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: #555;
  }
  
  .filter input {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .table-stats {
    margin-bottom: 1rem;
    color: #666;
    font-size: 0.9rem;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
  }
  
  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  
  th {
    background-color: #f5f5f5;
    font-weight: bold;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.2s;
  }
  
  th:hover {
    background-color: #e9e9e9;
  }
  
  th.active {
    background-color: #e0e0e0;
    color: #333;
  }
  
  tr:hover {
    background-color: #f9f9f9;
  }
  
  .view-button {
    display: inline-block;
    padding: 0.3rem 0.6rem;
    background-color: #333;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-size: 0.8rem;
    transition: background-color 0.2s;
  }
  
  .view-button:hover {
    background-color: #e91e63;
  }
  
  .no-results {
    text-align: center;
    color: #888;
    padding: 2rem 0;
  }
  
  @media (max-width: 768px) {
    .filters {
      flex-direction: column;
    }
    
    th, td {
      padding: 0.5rem;
    }
  }
</style>
