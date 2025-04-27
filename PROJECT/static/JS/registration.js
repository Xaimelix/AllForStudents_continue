document.getElementById('registrationForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Сбор данных из формы
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeatPassword').value;
    const name = document.getElementById('name').value;
    const surname = document.getElementById('surname').value;

    // Клиентская валидация
    if (password !== repeatPassword) {
        showError('Пароли не совпадают');
        return;
    }

    try {
        const response = await fetch('/api/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                login: email,
                hashed_password: password, // Хэширование должно быть на бэкенде!
                name: name,
                surname: surname
            })
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = '/success'; // Перенаправление
        } else {
            showError(data.message || 'Ошибка регистрации');
        }
    } catch (error) {
        showError('Сетевая ошибка');
    }
});

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}