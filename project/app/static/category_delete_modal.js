'use strict';

// Скрипт для перенаправления на url для удаления при удалении характеристики

function modalShown(event) {
    let button = event.relatedTarget;
    let categoryId = button.dataset.categoryId;
    let newUrl = `/products/${categoryId}/delete_category`;
    let form = document.getElementById('deleteModalForm');
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);