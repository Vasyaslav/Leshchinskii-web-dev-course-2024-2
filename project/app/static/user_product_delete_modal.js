'use strict';

// Скрипт для перенаправления на url для удаления при удалении товара из корзины

function modalShown(event) {
    let button = event.relatedTarget;
    let productId = button.dataset.productId;
    let userId = button.dataset.userId;
    let newUrl = `/user_products/${userId}/${productId}/delete`;
    let form = document.getElementById('deleteUserProductModalForm');
    form.action = newUrl;
}

let userProductModal = document.getElementById('deleteUserProductModal');
userProductModal.addEventListener('show.bs.modal', modalShown);