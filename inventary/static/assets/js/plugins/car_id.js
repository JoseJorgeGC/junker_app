const boton = document.querySelector('#carId_toggle');
const menu = document.querySelector('#add_id');

boton.addEventListener('click', () => {
    console.log('click')
    menu.classList.toggle('hidden')

    // Agregar animación al mostrar el elemento
  if (!menu.classList.contains('hidden')) {
    menu.classList.add('animate-fadeIn');
  }
  
  // Retrasar y agregar animación al ocultar el elemento
  setTimeout(() => {
    if (menu.classList.contains('hidden')) {
      menu.classList.remove('animate-fadeIn');
    }
  }, 300);
})