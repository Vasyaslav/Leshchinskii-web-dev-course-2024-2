'use strict';

// Скрипт для перенаправления на url для удаления при удалении характеристики

function modalShown(event) {
    let button = event.relatedTarget;
    let characteristicId = button.dataset.characteristicId;
    let newUrl = `/products/${characteristicId}/delete_characteristic`;
    let form = document.getElementById('deleteModalForm');
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);