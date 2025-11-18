
    const modalOverlay = document.getElementById("modal-overlay");
    const climateCard = document.getElementById("climate-card");
    const climateAlert = document.getElementById("climate-alert");
    const closebtn =  document.getElementById("close-btn");
    const forecast = document.getElementById("forecast");
    const weatherAlert = document.getElementById("weather-alert")

    climateAlert.addEventListener("click", (e) => {
        modalOverlay.style.display = "flex";
        forecast.style.display = "none";
        weatherAlert.style.display = "flex"
    })

    climateCard.addEventListener("click", (e) => {
        modalOverlay.style.display = "flex";
        forecast.style.display = "flex";
        weatherAlert.style.display = "none"
    })

    closebtn.addEventListener("click", (e) =>{
        modalOverlay.style.display = "none";
    })



    
