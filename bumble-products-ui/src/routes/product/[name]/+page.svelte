<script lang="ts">
  import { page } from '$app/stores';
  import { getProductByName, parseProductDescription } from '$lib/data/productStore';
  import type { Product } from '$lib/data/productStore';
  import { onMount } from 'svelte';
  
  let product: Product | undefined;
  let parsedDescription: { category: string, description: string, details: string } = {
    category: '',
    description: '',
    details: ''
  };
  
  onMount(() => {
    const productName = decodeURIComponent($page.params.name);
    product = getProductByName(productName);
    
    if (product && product.other) {
      parsedDescription = parseProductDescription(product.other);
    }
  });
</script>

<div class="product-detail">
  {#if !product}
    <div class="not-found">
      <h1>Product Not Found</h1>
      <p>The product you're looking for doesn't exist or has been removed.</p>
      <a href="/" class="back-button">Back to Products</a>
    </div>
  {:else}
    <div class="product-header">
      <a href="/" class="back-button">← Back to Products</a>
      <h1>{product.name}</h1>
      <div class="category">{parsedDescription.category}</div>
    </div>
    
    <div class="product-content">
      <div class="product-info">
        {#if product.options && product.options.length > 0}
          <div class="options">
            <h2>Options</h2>
            <div class="options-grid">
              {#each product.options as option}
                <div class="option-card">
                  <div class="option-size">{option.size}</div>
                  <div class="option-price">{option.price}</div>
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if parsedDescription.description}
          <div class="description">
            <h2>Description</h2>
            <div class="description-content">
              {#each parsedDescription.description.split('\n\n') as paragraph}
                <p>{paragraph}</p>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if parsedDescription.details}
          <div class="details">
            <h2>Details</h2>
            <div class="details-content">
              {#each parsedDescription.details.split('\n\n') as paragraph}
                <p>{paragraph}</p>
              {/each}
            </div>
          </div>
        {/if}
      </div>
      
      {#if product.ingredients && product.ingredients.length > 0}
        <div class="ingredients">
          <h2>Ingredients ({product.ingredients.length})</h2>
          <ul class="ingredients-list">
            {#each product.ingredients as ingredient}
              <li>{ingredient}</li>
            {/each}
          </ul>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .product-detail {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }
  
  .product-header {
    margin-bottom: 2rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
  }
  
  h1 {
    margin: 0.5rem 0;
    font-size: 2rem;
    color: #333;
  }
  
  h2 {
    color: #444;
    margin: 1.5rem 0 1rem;
    font-size: 1.3rem;
  }
  
  .back-button {
    display: inline-block;
    margin-bottom: 1rem;
    color: #666;
    text-decoration: none;
    transition: color 0.2s;
  }
  
  .back-button:hover {
    color: #e91e63;
  }
  
  .category {
    background-color: #f0f0f0;
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    font-size: 0.9rem;
    display: inline-block;
  }
  
  .product-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
  
  .options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .option-card {
    background-color: #f9f9f9;
    padding: 1rem;
    border-radius: 6px;
    text-align: center;
  }
  
  .option-size {
    font-weight: bold;
    margin-bottom: 0.5rem;
  }
  
  .option-price {
    color: #e91e63;
    font-weight: bold;
  }
  
  .description-content, .details-content {
    color: #555;
    line-height: 1.6;
  }
  
  .ingredients {
    background-color: #f9f9f9;
    padding: 1.5rem;
    border-radius: 8px;
  }
  
  .ingredients-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.5rem;
  }
  
  .ingredients-list li {
    background-color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.9rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .not-found {
    text-align: center;
    padding: 3rem;
  }
  
  @media (max-width: 768px) {
    .product-content {
      grid-template-columns: 1fr;
    }
    
    .ingredients-list {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
  }
</style>
