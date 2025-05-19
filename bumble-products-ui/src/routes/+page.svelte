<script lang="ts">
  import { filteredProducts, parseProductDescription } from '$lib/data/productStore';
  import type { Product } from '$lib/data/productStore';
</script>

<div class="product-grid">
  {#if $filteredProducts.length === 0}
    <div class="no-results">
      <h2>No products found</h2>
      <p>Try adjusting your search or filter criteria.</p>
    </div>
  {:else}
    {#each $filteredProducts as product}
      <a href={`/product/${encodeURIComponent(product.name)}`} class="product-card">
        <h2>{product.name}</h2>
        
        {#if product.options && product.options.length > 0}
          <div class="price">{product.options[0].price}</div>
        {/if}
        
        {#if product.other}
          {@const parsedDescription = parseProductDescription(product.other)}
          <div class="category">{parsedDescription.category}</div>
          
          {#if parsedDescription.description}
            <div class="description">
              {#if parsedDescription.description.includes('What It Is')}
                <p>{parsedDescription.description.split('What It Is')[1].split('FORMULATED FOR')[0].trim()}</p>
              {:else}
                <p>{parsedDescription.description.substring(0, 150)}...</p>
              {/if}
            </div>
          {/if}
        {/if}
        
        <div class="ingredients-preview">
          {#if product.ingredients && product.ingredients.length > 0}
            <p>Contains {product.ingredients.length} ingredients</p>
          {/if}
        </div>
      </a>
    {/each}
  {/if}
</div>

<style>
  .product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1rem 0;
  }
  
  .product-card {
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    text-decoration: none;
    color: inherit;
    height: 100%;
  }
  
  .product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  h2 {
    margin-top: 0;
    font-size: 1.2rem;
    color: #333;
    margin-bottom: 0.5rem;
  }
  
  .price {
    font-weight: bold;
    color: #e91e63;
    margin-bottom: 0.5rem;
  }
  
  .category {
    background-color: #f0f0f0;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    display: inline-block;
    margin-bottom: 0.5rem;
  }
  
  .description {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 1rem;
    flex-grow: 1;
  }
  
  .ingredients-preview {
    font-size: 0.8rem;
    color: #888;
    margin-top: auto;
  }
  
  .no-results {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
</style>
