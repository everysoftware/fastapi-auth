import {authClient} from './dependencies.js';

(function () {
    'use strict'

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async function (event) {
        event.preventDefault()
        if (!form.checkValidity()) {
            event.stopPropagation()
            form.classList.add('was-validated')
            return;
        }
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const response = await authClient.login(email, password);
        if (response) {
            alert("Successfully logged in!");
        }
    }, false)

    document.getElementById("loginBtn").addEventListener("click", function (event) {
        document.getElementById("loginForm").requestSubmit();
    });
})()
