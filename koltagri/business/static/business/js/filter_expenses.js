const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");

function makeSearch() {
    const value = searchInput.value.trim();
    
    if (value) {
        // Pega a URL atual do navegador
        const url = new URL(window.location.href);
        
        // Adiciona ou atualiza o parâmetro 'name'
        url.searchParams.set('description', value);
        
        // Redireciona para a nova URL (isso dispara o GET)
        window.location.href = url.toString();
    }
}

searchButton.addEventListener("click", makeSearch);