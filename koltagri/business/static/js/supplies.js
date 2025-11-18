
  // exemplo: abrir modal de criação ao clicar em add-supply (deixe conforme sua implementação)
  document.addEventListener('click', function(e){
    const a = e.target.closest('.add-supply');
    if(!a) return;
    e.preventDefault();
    // abrir modal ou navegar para a página de criação
    console.log('abrir criação de insumo');
  });
