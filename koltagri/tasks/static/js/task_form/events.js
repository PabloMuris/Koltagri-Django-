const priorityPicker = document.getElementById("priority-picker");
const taskPrioritySelection = document.getElementById("taskPriority");


priorityPicker.addEventListener("click", (event) => {
  let target = event.target.closest(".priority-btn");
  if (target) {
    let selectedValue = target.getAttribute("data-value");
    taskPrioritySelection.value = String(selectedValue);
  }
});