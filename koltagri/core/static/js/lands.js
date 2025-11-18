

let areas = [
    {
        id: 1,
        name: "Estufa Principal",
        coordinates: "-23.5505, -46.6333",
        description: "Estufa com sistema de irrigação automatizado para cultivo de hortaliças."
    },
    {
        id: 2,
        name: "Área de Compostagem",
        coordinates: "-23.5507, -46.6335",
        description: "Local para processamento de resíduos orgânicos e produção de composto."
    },
    {
        id: 3,
        name: "Viveiro de Mudas",
        coordinates: "",
        description: "Setor dedicado ao cultivo e desenvolvimento de mudas antes do transplante."
    },
    {
        id: 4,
        name: "Campo Aberto - Norte",
        coordinates: "-23.5503, -46.6331",
        description: ""
    }
];

// Elementos DOM
const areasContainer = document.getElementById('areas-container');
const emptyState = document.getElementById('empty-state');
const filterSection = document.getElementById('filter-section');
const searchInput = document.getElementById('search-input');
const filterToggle = document.getElementById('filter-toggle');
const clearFiltersBtn = document.getElementById('clear-filters');
const applyFiltersBtn = document.getElementById('apply-filters');
const addAreaBtn = document.getElementById('add-area-btn');
const addFirstAreaBtn = document.getElementById('add-first-area');

// Modais
const areaModal = document.getElementById('area-modal');
const deleteModal = document.getElementById('delete-modal');
const closeAreaModal = document.getElementById('close-area-modal');
const closeDeleteModal = document.getElementById('close-delete-modal');
const cancelArea = document.getElementById('cancel-area');
const cancelDelete = document.getElementById('cancel-delete');
const confirmDelete = document.getElementById('confirm-delete');


const areaForm = document.getElementById('area-form');
const areaModalTitle = document.getElementById('area-modal-title');
const areaIdInput = document.getElementById('area-id');
const areaNameInput = document.getElementById('area-name');
const areaCoordinatesInput = document.getElementById('area-coordinates');
const areaDescriptionInput = document.getElementById('area-description');
const deleteAreaName = document.getElementById('delete-area-name');


let currentFilter = '';
let areaToDelete = null;


document.addEventListener('DOMContentLoaded', function() {
    renderAreas();
    setupEventListeners();
});


function setupEventListeners() {
    
    filterToggle.addEventListener('click', toggleFilterSection);
    clearFiltersBtn.addEventListener('click', clearFilters);
    applyFiltersBtn.addEventListener('click', applyFilters);
    
    
    addAreaBtn.addEventListener('click', openAddAreaModal);
    addFirstAreaBtn.addEventListener('click', openAddAreaModal);
    
    
    closeAreaModal.addEventListener('click', closeAreaModalFunc);
    closeDeleteModal.addEventListener('click', closeDeleteModalFunc);
    cancelArea.addEventListener('click', closeAreaModalFunc);
    cancelDelete.addEventListener('click', closeDeleteModalFunc);
    confirmDelete.addEventListener('click', deleteArea);
    
    
    areaForm.addEventListener('submit', saveArea);
    
    
    areaModal.addEventListener('click', function(e) {
        if (e.target === areaModal) closeAreaModalFunc();
    });
    
    deleteModal.addEventListener('click', function(e) {
        if (e.target === deleteModal) closeDeleteModalFunc();
    });
}

function renderAreas() {
    const filteredAreas = areas.filter(area => 
        area.name.toLowerCase().includes(currentFilter.toLowerCase()) ||
        (area.description && area.description.toLowerCase().includes(currentFilter.toLowerCase()))
    );
    
    if (filteredAreas.length === 0) {
        areasContainer.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    areasContainer.style.display = 'grid';
    emptyState.style.display = 'none';
    
    areasContainer.innerHTML = '';
    
    filteredAreas.forEach(area => {
        const areaCard = document.createElement('div');
        areaCard.className = 'area-card';
        areaCard.innerHTML = `
            <div class="area-header">
                <h3 class="area-name">${area.name}</h3>
                <div class="area-actions">
                    <button class="btn small icon-only edit-area" data-id="${area.id}">
                        <span class="material-icons">edit</span>
                    </button>
                    <button class="btn small icon-only delete-area" data-id="${area.id}">
                        <span class="material-icons">delete</span>
                    </button>
                </div>
            </div>
            ${area.coordinates ? `<div class="area-coordinates">${area.coordinates}</div>` : ''}
            ${area.description ? `<p class="area-description">${area.description}</p>` : ''}
        `;
        
        areasContainer.appendChild(areaCard);
    });
    
    document.querySelectorAll('.edit-area').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.getAttribute('data-id'));
            openEditAreaModal(id);
        });
    });
    
    document.querySelectorAll('.delete-area').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = parseInt(this.getAttribute('data-id'));
            openDeleteModal(id);
        });
    });
}

function toggleFilterSection() {
    filterSection.style.display = filterSection.style.display === 'none' ? 'block' : 'none';
}

function clearFilters() {
    searchInput.value = '';
    currentFilter = '';
    renderAreas();
}

function applyFilters() {
    currentFilter = searchInput.value;
    renderAreas();
}

// Funções do modal de área
function openAddAreaModal() {
    areaModalTitle.textContent = 'Nova Área';
    areaIdInput.value = '';
    areaNameInput.value = '';
    areaCoordinatesInput.value = '';
    areaDescriptionInput.value = '';
    areaModal.style.display = 'flex';
}

function openEditAreaModal(id) {
    const area = areas.find(a => a.id === id);
    if (!area) return;
    
    areaModalTitle.textContent = 'Editar Área';
    areaIdInput.value = area.id;
    areaNameInput.value = area.name;
    areaCoordinatesInput.value = area.coordinates || '';
    areaDescriptionInput.value = area.description || '';
    areaModal.style.display = 'flex';
}

function closeAreaModalFunc() {
    areaModal.style.display = 'none';
}

function saveArea(e) {
    e.preventDefault();
    
    const id = areaIdInput.value ? parseInt(areaIdInput.value) : null;
    const name = areaNameInput.value.trim();
    const coordinates = areaCoordinatesInput.value.trim();
    const description = areaDescriptionInput.value.trim();
    
    if (!name) {
        alert('O nome da área é obrigatório');
        return;
    }
    
    if (id) {
        // Editar área existente
        const index = areas.findIndex(a => a.id === id);
        if (index !== -1) {
            areas[index] = {
                id: id,
                name: name,
                coordinates: coordinates,
                description: description
            };
        }
    } else {
        // Adicionar nova área
        const newId = areas.length > 0 ? Math.max(...areas.map(a => a.id)) + 1 : 1;
        areas.push({
            id: newId,
            name: name,
            coordinates: coordinates,
            description: description
        });
    }
    
    renderAreas();
    closeAreaModalFunc();
}

function openDeleteModal(id) {
    const area = areas.find(a => a.id === id);
    if (!area) return;
    
    areaToDelete = id;
    deleteAreaName.textContent = `"${area.name}"`;
    deleteModal.style.display = 'flex';
}

function closeDeleteModalFunc() {
    deleteModal.style.display = 'none';
    areaToDelete = null;
}

function deleteArea() {
    if (!areaToDelete) return;
    
    areas = areas.filter(a => a.id !== areaToDelete);
    renderAreas();
    closeDeleteModalFunc();
}
