'use strict';

//Скрипт для удаления поля характеристики при добавлении или изменении товара

let characteristic_group_sample = document.body.querySelector('div.input-group').cloneNode(true);

function delete_characteristic_group(event) {
    console.log(event);

    event.target.parentNode.remove();
}


function add_characteristic_group(event) {
    let last_characteristic = document.body.querySelectorAll('div.input-group')[document.body.querySelectorAll('div.input-group').length - 1];
    let last_characteristic_number;
    let sample = characteristic_group_sample.cloneNode(true);
    if (last_characteristic == null) {
        last_characteristic = document.getElementById('characteristics_header');
        last_characteristic_number = 1;
    }
    else {
        last_characteristic_number = Number(last_characteristic.firstElementChild.id.split('_')[3]);
    }
    console.log(sample);
    console.log(last_characteristic_number);
    sample.children[0].id = `product_characteristic_select_${last_characteristic_number + 1}`;
    sample.children[0].name = `product_characteristic_select_${last_characteristic_number + 1}`;
    sample.children[1].id = `product_characteristic_input_${last_characteristic_number + 1}`;
    sample.children[1].name = `product_characteristic_input_${last_characteristic_number + 1}`;
    sample.children[2].id = `product_characteristic_button_${last_characteristic_number + 1}`;
    sample.children[2].onclick = delete_characteristic_group;
    console.log(sample);
    last_characteristic.after(sample);
}

for (let i = 0; i < document.body.querySelectorAll("button.deleteBtn").length; i++) {
    document.body.querySelectorAll("button.deleteBtn")[i].onclick = delete_characteristic_group;
}

document.getElementById('product_characteristic_button_1').onclick = delete_characteristic_group;
document.getElementById('product_characteristic_add_button').onclick = add_characteristic_group;
