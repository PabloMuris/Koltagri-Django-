let slidePosition = 0;
const totalSlides = 2; // 0, 1, 2

const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");
const contentFields = document.querySelectorAll(".content-field");
const stepItems = document.querySelectorAll(".progress-container li");
const progressBar = document.querySelector(".progress");

function updateStepIndicator() {
  // Atualizar progress bar
  const progressPercentage = (slidePosition / totalSlides) * 100;
  progressBar.style.width = `${progressPercentage}%`;
  
  // Atualizar estados dos steps
  stepItems.forEach((item, index) => {
    item.classList.remove("active", "completed");
    
    if (index < slidePosition) {
      item.classList.add("completed");
    } else if (index === slidePosition) {
      item.classList.add("active");
    }
  });
}

function setBtnVisibility() {
  // Esconder mostrar botões conforme a posição
  if (slidePosition === 0) {
    prevBtn.style.display = "none";
    nextBtn.style.display = "inline-flex";
    submitBtn.style.display = "none";
  } else if (slidePosition === totalSlides) {
    prevBtn.style.display = "inline-flex";
    nextBtn.style.display = "none";
    submitBtn.style.display = "inline-flex";
  } else {
    prevBtn.style.display = "inline-flex";
    nextBtn.style.display = "inline-flex";
    submitBtn.style.display = "none";
  }
}

function updateSlide() {
  // Esconder todos os campos
  contentFields.forEach(field => {
    field.style.display = "none";
    field.style.opacity = "0";
    field.style.transform = "translateX(20px)";
  });
  
  // Mostrar apenas os campos relevantes para a etapa atual
  let fieldsToShow = [];
  
  switch(slidePosition) {
    case 0: // Etapa 1: Título e descrição
      fieldsToShow = [0, 1];
      break;
    case 1: // Etapa 2: Plantas
      fieldsToShow = [2];
      break;
    case 2: // Etapa 3: Datas e Prioridade
      fieldsToShow = [3, 4];
      break;
  }
  
  // Animar a entrada dos campos
  fieldsToShow.forEach((fieldIndex, index) => {
    setTimeout(() => {
      contentFields[fieldIndex].style.display = "flex";
      setTimeout(() => {
        contentFields[fieldIndex].style.opacity = "1";
        contentFields[fieldIndex].style.transform = "translateX(0)";
      }, 50);
    }, index * 100);
  });
  
  // Atualizar botões e indicador
  setBtnVisibility();
  updateStepIndicator();
}

// Inicializar
document.addEventListener("DOMContentLoaded", () => {
  // Estilo inicial para animação
  contentFields.forEach(field => {
    field.style.transition = "opacity 0.3s ease, transform 0.3s ease";
  });
  
  updateSlide();
});

// Event Listeners
prevBtn.addEventListener("click", (e) => {
  e.preventDefault();
  if (slidePosition > 0) {
    slidePosition--;
    updateSlide();
  }
});

nextBtn.addEventListener("click", (e) => {
  e.preventDefault();
  
  // Validar campos da etapa atual antes de avançar
  let canProceed = true;
  
  if (slidePosition === 0) {
    const title = document.getElementById("taskTitle").value.trim();
    const content = document.getElementById("taskContent").value.trim();
    
    if (!title) {
      alert("Por favor, insira um título para a atividade");
      document.getElementById("taskTitle").focus();
      canProceed = false;
    } else if (!content) {
      alert("Por favor, insira o conteúdo da atividade");
      document.getElementById("taskContent").focus();
      canProceed = false;
    }
  }
  
  if (canProceed && slidePosition < totalSlides) {
    slidePosition++;
    updateSlide();
  }
});

// Adicionar navegação por teclado
document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft" && slidePosition > 0) {
    slidePosition--;
    updateSlide();
  } else if (e.key === "ArrowRight" && slidePosition < totalSlides) {
    slidePosition++;
    updateSlide();
  }
});