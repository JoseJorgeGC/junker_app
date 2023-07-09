const btn_agregar = document.getElementById('add-parts');
console.log(btn_agregar)
btn_agregar.addEventListener("click", function( ){
    //crear el div que contiene los 2 sub-divs
    const div_principal = D.create('div', {id:"showtires", className:'grid grid-cols-6 gap-6 '});
    
    
    //crear el div para el span e input del part-type
    const div_part_type = D.create('div', {className:'col-span-6 sm:col-span-3'});

    //crear el div para el span e input del quantity
    const div_quantity = D.create('div', {className:'col-span-6 sm:col-span-1'});

    //crear el div para el span e input del price
    const div_price = D.create('div', {className:'col-span-6 sm:col-span-1'});

    //crear el div para el span e input del Add-Car-ID
    const div_add_car_id = D.create('div', {className:"col-span-6 sm:col-span-1 mt-9", id:"carId_toggle"});
    const subdiv_add_car_id = D.create('div', {className:"flex cursor-pointer", innerHTML:"Add Car ID"});

    
    //crear los label de type quantity and price
    const label_part_type = D.create('label', { innerHTML: 'Part Type',for:'part-type', className:"block text-sm font-medium leading-6 text-gray-900" } );
    const label_quantity = D.create('label', { innerHTML: 'Quantity',for:'quantity', className:"block text-sm font-medium leading-6 text-gray-900" });
    const label_price = D.create('label', { innerHTML: 'Price', for:'price',className:"block text-sm font-medium leading-6 text-gray-900" });

    //crear los inputs de type quantity and price
    const input_part_type = D.create('input', { type: 'text', id:'part-type', name: 'part_type', autocomplete: 'off', className:'mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', min: '1'} );

    const input_quantity = D.create('input', { type: 'number', id:'quantity', name: 'quantity', autocomplete: 'off', className:"mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6", min: '1'});

    const input_price = D.create('input', { type: 'number', id:'price', name: 'price', autocomplete: 'off', className:"mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6", min: '1'});
    
    //crear un botoncito de eliminar este div 
    const borrar = D.create('a', { href: 'javascript:void(0)', innerHTML: 'x', onclick: function( ){ D.remove(div_principal); } } );

    //agregar cada etiqueta a su nodo padre
    D.append([label_part_type, input_part_type], div_part_type);
    D.append([label_quantity, input_quantity], div_quantity);
    D.append([label_price, input_price], div_price);
    D.append([subdiv_add_car_id], div_add_car_id);

    D.append([div_part_type, div_quantity, div_price, div_add_car_id, borrar], div_principal);
    
    //agregar el div del primer comentario al contenedor con id #container
    D.append(div_principal, D.id('parts-container') );
} );
/*


                        <div id="showtires" class="grid grid-cols-6 gap-6 ">                           
                            <div class="col-span-6 sm:col-span-3">
                              <label for="part_type" class="block text-sm font-medium leading-6 text-gray-900">Part type:</label>
                              <input type="text" name="part_type" id="part_type" autocomplete="quantity" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" min="1" max="{{stock.tires}}">
                            </div>
              
                            <div class="col-span-6 sm:col-span-1">
                              <label for="amount" class="block text-sm font-medium leading-6 text-gray-900">Quantity:</label>
                              <input type="number" name="amount" id="amount" autocomplete="family-name" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" min="1">
                            </div>

                            <div class="col-span-6 sm:col-span-1">
                                <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Price:</label>
                                <input type="text" name="name" id="name" autocomplete="family-name" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                            </div>                          
                            
                            <div class="col-span-6 sm:col-span-1 mt-9" id="carId_toggle">
                              <div class="flex cursor-pointer">                                 
                                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  Add car ID
                              </div>    
                            </div>

                            //Car ID
                            <div class="hidden sm:col-start-3 grid grid-cols-2 gap-6 w-80 transition-all duration-300 ease-out" id="add_id">
                                <div class="col-span-6 sm:col-span-1">
                                  <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Car ID:</label>
                                  <input type="text" name="name" id="name" autocomplete="family-name" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                                </div>           
                                <div class="col-span-6 sm:col-span-1">
                                  <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Quantity Parts:</label>
                                  <input type="text" name="name" id="name" autocomplete="family-name" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                                </div>     
                            </div>
                        </div>
*/