// Obtener la tabla
let table = document.getElementById('cars_sold_inventary');

// Obtener las filas de la tabla
let rows = table.getElementsByTagName('tr');

// Obtener el input del usuario
let input = document.getElementById('cars_sold_search');

// Agregar un evento de escucha al input
input.addEventListener('keyup', function() {

  // Obtener el valor del input
  let filter = input.value;

  // Crear una expresión regular para buscar en todas las columnas y filas
  let regex = new RegExp(filter, 'i');

  // Recorrer todas las filas de la tabla y ocultar aquellas que no coincidan con la expresión regular
  for (let i = 1; i < rows.length; i++) {
    let cells = rows[i].getElementsByTagName('td');
    let found = false;
    for (let j = 0; j < cells.length; j++) {
      if (regex.test(cells[j].textContent)) {
        found = true;
        break;
      }
    }
    if (found) {
      rows[i].style.display = '';
    } else {
      rows[i].style.display = 'none';
    }
  }
});