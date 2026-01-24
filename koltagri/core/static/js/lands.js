let areas = [
    { id: 1, name: "Estufa Principal", coordinates: "-23.5505, -46.6333", description: "Estufa com sistema de irrigação..." },
    { id: 2, name: "Área de Compostagem", coordinates: "-23.5507, -46.6335", description: "Local para processamento..." }
];

// Seleção de Elementos do Modal
const areaModal = document.getElementById('area-modal');
const deleteModal = document.getElementById('delete-modal');
const areaForm = document.getElementById('area-form');
const areaModalTitle = document.getElementById('area-modal-title');

// Campos do Formulário
const areaIdInput = document.getElementById('area-id');
const areaNameInput = document.getElementById('area-name');
const areaCoordinatesInput = document.getElementById('area-coordinates');
const areaDescriptionInput = document.getElementById('area-description');
const deleteAreaName = document.getElementById('delete-area-name');

let areaToDelete = null;

document.addEventListener('DOMContentLoaded', function() {
    setupModalListeners();
});

function setupModalListeners() {
    // Fechar modais ao clicar no X ou em Cancelar
    const closeButtons = document.querySelectorAll('#close-area-modal, #close-delete-modal, #cancel-area, #cancel-delete');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            areaModal.style.display = 'none';
            deleteModal.style.display = 'none';
        });
    });

    // Fechar ao clicar fora do modal
    window.onclick = (e) => {
        if (e.target === areaModal) areaModal.style.display = 'none';
        if (e.target === deleteModal) deleteModal.style.display = 'none';
    };

    // Submissão do Formulário
    areaForm.addEventListener('submit', saveArea);

    // Botão de confirmação de exclusão
    document.getElementById('confirm-delete').addEventListener('click', deleteArea);
}

// FUNÇÕES DE ABERTURA (Chame estas funções via onclick no seu HTML estático)

function openAddAreaModal() {
    areaModalTitle.textContent = 'Nova Área';
    areaForm.reset();
    areaIdInput.value = '';
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

function openDeleteModal(id) {
    const area = areas.find(a => a.id === id);
    if (!area) return;
    
    areaToDelete = id;
    deleteAreaName.textContent = `"${area.name}"`;
    deleteModal.style.display = 'flex';
}

// LÓGICA DE DADOS

function saveArea(e) {
    e.preventDefault();
    const id = areaIdInput.value ? parseInt(areaIdInput.value) : null;
    const data = {
        id: id || Date.now(),
        name: areaNameInput.value.trim(),
        coordinates: areaCoordinatesInput.value.trim(),
        description: areaDescriptionInput.value.trim()
    };

    if (id) {
        const index = areas.findIndex(a => a.id === id);
        if (index !== -1) areas[index] = data;
    } else {
        areas.push(data);
    }

    console.log("Dados salvos:", data);
    areaModal.style.display = 'none';
}

function deleteArea() {
    if (!areaToDelete) return;
    areas = areas.filter(a => a.id !== areaToDelete);
    console.log("Área removida. ID:", areaToDelete);
    deleteModal.style.display = 'none';
    areaToDelete = null;
}