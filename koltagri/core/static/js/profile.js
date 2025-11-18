(function(){
  const properties = [
    { 
      id:1, 
      name:'Fazenda Verde', 
      loc:'Riacho de Santana • RN', 
      area:'120 ha', 
      crop:'Milho / Soja', 
      irrig:'Gotejamento',
      thumbSrc: '{% static "example_img/ananas.jpeg" %}'
    },
    { 
      id:2, 
      name:'Sítio do Sol', 
      loc:'Vale do Rio Doce • MG', 
      area:'45 ha', 
      crop:'Banana', 
      irrig:'Aspersão',
      thumbSrc: '{% static "example_img/banana.png" %}'
    },
    { 
      id:3, 
      name:'Rancho Azul', 
      loc:'Zona da Mata • MG', 
      area:'320 ha', 
      crop:'Eucalipto', 
      irrig:'Seco',
      thumbSrc: '{% static "example_img/maracuja.jpeg" %}'
    },
    { 
      id:4, 
      name:'Chácara Primavera', 
      loc:'Serra Gaúcha • RS', 
      area:'28 ha', 
      crop:'Uva', 
      irrig:'Gotejamento',
      thumbSrc: '{% static "example_img/laranjeira.png" %}'
    }
  ];

  // user demo info
  const user = { 
    name:'Pablo Souza', 
    email:'pablo@enrichthesoil.com', 
    phone:'+55 (85) 9 9999-9999', 
    role:'Gestor' 
  };

  // DOM refs
  const listEl = document.getElementById('prop-list');
  const currentName = document.getElementById('current-prop-name');
  const valPropName = document.getElementById('val-prop-name');
  const valArea = document.getElementById('val-area');
  const valCrop = document.getElementById('val-crop');
  const valIrrig = document.getElementById('val-irrig');
  const valLocation = document.getElementById('val-location');

  // build property cards
  properties.forEach((p, idx) => {
    const card = document.createElement('div');
    card.className = 'property-card';
    card.tabIndex = 0;
    card.setAttribute('role','button');
    card.dataset.id = p.id;

    const thumb = document.createElement('div');
    thumb.className = 'property-thumb';
    
    if (p.thumbSrc) {
      const img = document.createElement('img');
      img.src = p.thumbSrc;
      img.alt = p.name;
      img.onerror = function() {
        this.style.display = 'none';
        const icon = document.createElement('span');
        icon.className = 'material-icons';
        icon.textContent = 'agriculture';
        thumb.appendChild(icon);
      };
      thumb.appendChild(img);
    } else {
      const icon = document.createElement('span');
      icon.className = 'material-icons';
      icon.textContent = 'agriculture';
      thumb.appendChild(icon);
    }

    const info = document.createElement('div');
    info.className = 'property-info';
    info.innerHTML = `
      <div class="property-name">${p.name}</div>
      <div class="property-meta">${p.loc}</div>
    `;

    card.appendChild(thumb);
    card.appendChild(info);
    listEl.appendChild(card);

    function select(){
      // Remove selected class from all cards
      listEl.querySelectorAll('.property-card').forEach(c => c.classList.remove('selected'));
      
      // Add selected class to current card
      card.classList.add('selected');

      // Update profile header
      currentName.textContent = p.name;
      
      // Update property details
      valPropName.textContent = p.name;
      valArea.textContent = p.area;
      valCrop.textContent = p.crop;
      valIrrig.textContent = p.irrig;
      valLocation.textContent = p.loc;
    }

    card.addEventListener('click', select);
    card.addEventListener('keydown', (e) => {
      if(e.key === 'Enter' || e.key === ' '){
        e.preventDefault();
        select();
      }
    });


    if(idx === 0) setTimeout(() => card.click(), 50);
  });

  
  document.getElementById('btn-logout').addEventListener('click', () => {
    if(confirm('Deseja realmente sair?')) {
    
      console.log('Logout action');
    }
  });
  
  document.getElementById('btn-edit-profile').addEventListener('click', () => {
    alert('Abrir edição de perfil (implemente)');
  });
  
  document.getElementById('btn-edit-personal').addEventListener('click', () => {
    alert('Editar dados pessoais (implemente)');
  });
  
  document.getElementById('btn-prop-edit').addEventListener('click', () => {
    alert('Editar dados da propriedade (implemente)');
  });
  
  document.getElementById('btn-prop-switch').addEventListener('click', () => {
    alert('Abrir painel da propriedade (implemente)');
  });
  
  document.getElementById('btn-add-prop').addEventListener('click', () => {
    alert('Criar nova propriedade (implemente)');
  });
  
  document.getElementById('btn-manage-prop').addEventListener('click', () => {
    alert('Gerenciar propriedades (implemente)');
  });
})();
