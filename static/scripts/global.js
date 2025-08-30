
  const body = document.body;
  const navParagraphs = document.querySelectorAll('aside .nav-link p');

  function updateLayout() {
    const width = window.innerWidth;

    if (width <= 767) {
      // MOBILE
      body.style.gridTemplateAreas = `"header" "main" "footer"`;
      body.style.gridTemplateColumns = "1fr";
      body.style.gridTemplateRows = "88px 1fr 60px";
      navParagraphs.forEach(p => {
  p.style.display = 'block';
});

    } else if (width >= 768 && width <= 1124) {
      // INTERMEDIÁRIO (aside estreito)
      body.style.gridTemplateAreas = `"aside header" "aside main"`;
      body.style.gridTemplateColumns = "90px 1fr";
      body.style.gridTemplateRows = "70px 1fr";
      body.style.gap = "10px";

      navParagraphs.forEach(p => {
  p.style.display = 'none';
});

    } else {
      // DESKTOP AMPL0
      body.style.gridTemplateAreas = `"aside header" "aside main"`;
      body.style.gridTemplateColumns = "260px 1fr";
      body.style.gridTemplateRows = "70px 1fr";
      body.style.gap = "10px";
      navParagraphs.forEach(p => {
  p.style.display = 'block';
});
    }
  }

  // Executa ao carregar
  updateLayout();

  // Atualiza ao redimensionar
  window.addEventListener("resize", updateLayout);
