const priorityPicker = document.getElementById("priority-picker");
const taskPrioritySelection = document.getElementById("taskPriority");
const priorityBtns = document.querySelectorAll(".priority-btn");

priorityPicker.addEventListener("click", (event) => {
  let target = event.target.closest(".priority-btn");
  
  if (target) {
    // Remover classe active de todos os botões
    priorityBtns.forEach(btn => {
      btn.classList.remove("active");
    });
    
    // Adicionar classe active ao botão clicado
    target.classList.add("active");
    
    // Atualizar o valor no select
    let selectedValue = target.getAttribute("data-value");
    taskPrioritySelection.value = String(selectedValue);
    
    // Efeito visual adicional
    target.style.transform = "scale(0.95)";
    setTimeout(() => {
      target.style.transform = "";
    }, 150);
  }
});

// Inicializar com a prioridade padrão (baixa)
document.addEventListener("DOMContentLoaded", () => {
  const defaultBtn = document.querySelector('.priority-btn[data-value="3"]');
  if (defaultBtn) {
    defaultBtn.classList.add("active");
  }
});