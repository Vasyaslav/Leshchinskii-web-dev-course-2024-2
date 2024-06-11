'use strict';

// Скрипт для перенаправления на url для удаления при удалении профиля

function modalShown(event) {
    console.log(12312)
    let button = event.relatedTarget;
    let userId = button.dataset.userId;
    let newUrl = `/users/${userId}/delete`;
    let form = document.getElementById('deleteUserModalForm');
    form.action = newUrl;
}

let userModal = document.getElementById('deleteUserModal');
userModal.addEventListener('show.bs.modal', modalShown);