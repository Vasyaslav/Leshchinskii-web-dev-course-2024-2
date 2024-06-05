'use strict';

// Скрипт для перенаправления на url для удаления при удалении товара

function modalShown(event) {
    let button = event.relatedTarget;
    let userId = button.dataset.productId;
    let newUrl = `/products/${userId}/delete`;
    let form = document.getElementById('deleteModalForm');
    form.action = newUrl;
    console.log(newUrl)
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);