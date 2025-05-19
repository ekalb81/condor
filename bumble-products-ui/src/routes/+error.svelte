<script>
  import { page } from '$app/stores';
</script>

<div class="error-container">
  <h1>{$page.status}: {$page.error?.message || 'Something went wrong'}</h1>
  <p>We're sorry, but something went wrong. Please try again later.</p>
  <a href="/" class="back-button">Back to Home</a>
</div>

<style>
  .error-container {
    text-align: center;
    padding: 3rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    margin: 2rem auto;
  }
  
  h1 {
    color: #e91e63;
  }
  
  .back-button {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #333;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .back-button:hover {
    background-color: #e91e63;
  }
</style>
