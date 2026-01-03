// ===============================
// Seleção de elementos do DOM
// ===============================
const plantInput = document.getElementById("taskPlants");
const plantResults = document.querySelector(".plant-results");
const selectedPlantsContainer = document.querySelector(".selected-plants");
const checkboxContainer = document.getElementById("checkbox-plants");


// ===============================
// 1. Evento de busca (Input)
// ===============================
plantInput.addEventListener("input", () => {
    const query = plantInput.value.trim().toLowerCase();

    if (query.length > 0) {
        carregarPlantas(query);
    } else {
        plantResults.innerHTML = "";
    }
});


// ===============================
// 2. Busca de plantas no servidor
// ===============================
async function carregarPlantas(query) {
    try {
        const response = await fetch(
            `http://localhost:8001/tarefas/plantas-especies/?q=${query}`
        );

        if (!response.ok) {
            throw new Error("Erro ao buscar dados");
        }

        const especies = await response.json();
        plantResults.innerHTML = "";

        especies.forEach(planta => {
            const div = document.createElement("div");
            div.classList.add("plant-selected");
            div.dataset.id = planta.id;
            div.dataset.nome = planta.name;
            div.textContent = planta.name;
            plantResults.appendChild(div);
        });

    } catch (erro) {
        console.error("Erro na busca:", erro);
        plantResults.innerHTML =
            '<div class="error">Erro ao carregar plantas.</div>';
    }
}


// ===============================
// 3. Clique nos resultados da busca
// ===============================
plantResults.addEventListener("click", (event) => {
    const itemClicado = event.target.closest(".plant-selected");

    if (!itemClicado) return;

    const id = itemClicado.dataset.id;
    const nome = itemClicado.dataset.nome;

    // Evita duplicatas
    if (!document.getElementById(`checkbox-plant-${id}`)) {
        adicionarPlanta(id, nome);
    }

    plantResults.innerHTML = "";
    plantInput.value = "";
});


// ===============================
// 4. Adicionar planta (visual + checkbox)
// ===============================
function adicionarPlanta(id, nome) {
    // ---- Marcador visual
    const plantaDiv = document.createElement("div");
    plantaDiv.classList.add("plant-marker");
    plantaDiv.id = `marker-plant-${id}`;
    plantaDiv.innerHTML = `
        <span class="plant-name">${nome}</span>
        <span class="material-icons remove-plant-icon" style="cursor:pointer">
            close
        </span>
    `;

    selectedPlantsContainer.appendChild(plantaDiv);

    // ---- Checkbox oculto (Django)
    const inputCheckbox = document.createElement("input");
    inputCheckbox.type = "checkbox";
    inputCheckbox.name = "plants";
    inputCheckbox.value = id;
    inputCheckbox.id = `checkbox-plant-${id}`;
    inputCheckbox.checked = true;
    inputCheckbox.style.display = "none";

    checkboxContainer.appendChild(inputCheckbox);
}


// ===============================
// 5. REMOÇÃO — EVENT DELEGATION
// ===============================
selectedPlantsContainer.addEventListener("click", (event) => {
    const btnRemover = event.target.closest(".remove-plant-icon");
    if (!btnRemover) return;

    const marcador = btnRemover.closest(".plant-marker");
    if (!marcador) return;

    const id = marcador.id.replace("marker-plant-", "");
    removerPlanta(id);
});


// ===============================
// 6. Função para remover planta
// ===============================
function removerPlanta(id) {
    const marcador = document.getElementById(`marker-plant-${id}`);
    const checkbox = document.getElementById(`checkbox-plant-${id}`);

    if (marcador) marcador.remove();
    if (checkbox) checkbox.remove();
}
