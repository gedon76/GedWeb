const searchForm = document.getElementById('search-form');
      const searchInput = document.getElementById('search-input');
      searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const query = searchInput.value;
        const searchUrl = 'https://duckduckgo.com?q=' + query;
        window.location.href = searchUrl;
      });