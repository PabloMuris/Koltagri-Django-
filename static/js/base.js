const asides = document.getElementsByName("aside")
const asideList = document.getElementsByTagName("aside");
const aside = asideList[0];


function ChangeSideBarWidth(){
const screenWidth = window.innerWidth;

    // Define os pontos de corte (breakpoints) e as larguras desejadas
    if (screenWidth > 769 && screenWidth<1024) {
        // Exemplo: Telas pequenas (celulares), aside tem 100% da largura
        aside.style.width = '76px';
        aside.style.position = 'sticky9'; // Volta a ser um elemento normal no fluxo
    }
    else {
        if (screenWidth>=1024){
            
        }
    }
}


ChangeSideBarWidth()



window.addEventListener('resize', ChangeSideBarWidth);