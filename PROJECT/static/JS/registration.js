
    const form = document.getElementById('registrationForm');
    const messageDiv = document.getElementById('message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Очистка предыдущих сообщений
        messageDiv.style.display = 'none';
        
        // Получение значений
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const name = document.getElementById('name').value;
        const surname = document.getElementById('surname').value;
        const gender = document.getElementById('gender').value;

        // Валидация
        if (password !== confirmPassword) {
            showMessage('Пароли не совпадают!', 'error');
            return;
        }

        try {
            // Подготовка данных для отправки
            const formData = {
                login: email,       // Используем email как логин
                hashed_password: password, // ВНИМАНИЕ: нужно хэшировать на сервере!
                name: name,
                surname: surname,
                sex: gender === 'M' // Преобразуем в boolean (M -> true, F -> false)
            };

            // Отправка запроса на сервер
            const response = await fetch('/api/students', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Ошибка регистрации');
            }

            // Очистка формы
            form.reset();
            
            // Показать сообщение об успехе
            showMessage('Регистрация прошла успешно!', 'success');
            
            // Перенаправление или другие действия после успешной регистрации
            setTimeout(() => {
                window.location.href = '/login.html'; // Пример перенаправления
            }, 1500);

        } catch (error) {
            showMessage(error.message || 'Произошла ошибка при регистрации', 'error');
        }
    });

    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
    }
