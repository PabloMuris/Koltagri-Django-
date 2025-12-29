let slidePosition = 0;

const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");

const contentFields = document.querySelectorAll(".content-field");

function setBtnVisibility() {
    prevBtn.style.visibility = slidePosition === 0 ? "hidden" : "visible";
    nextBtn.style.visibility = slidePosition === 2 ? "hidden" : "visible";
    submitBtn.style.visibility = slidePosition === 2 ? "visible" : "hidden";
}

function updateSlide() {
    if (slidePosition == 0) {
        contentFields[0].style.display = "flex";
        contentFields[1].style.display = "flex";
        contentFields[2].style.display = "none";
        contentFields[3].style.display = "none";
        contentFields[4].style.display = "none";
        setBtnVisibility();
    }

    if (slidePosition == 1) {
        contentFields[0].style.display = "none";
        contentFields[1].style.display = "none";
        contentFields[2].style.display = "flex";
        contentFields[3].style.display = "none";
        contentFields[4].style.display = "none";
        setBtnVisibility();
    }

    if (slidePosition == 2) {
        contentFields[0].style.display = "none";
        contentFields[1].style.display = "none";
        contentFields[2].style.display = "none";
        contentFields[3].style.display = "flex";
        contentFields[4].style.display = "flex";
        setBtnVisibility();
    }
}



document.addEventListener("DOMContentLoaded", () => {
    updateSlide();
});

prevBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (slidePosition > 0 && slidePosition <= 2) {
        slidePosition -= 1;
        updateSlide();
    }
    console.log(slidePosition);
});

nextBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (slidePosition >= 0 && slidePosition < 2) {
        slidePosition += 1;
        updateSlide();
    }
    console.log(slidePosition);
});



