const room_id_js = window.AppConfig.roomId
const user_id_js = window.AppConfig.userId
const server_url = window.AppConfig.serverUrl;
// const apiUrl = `${server_url}/api/rooms/${room_id_js}`;

async function submitBooking(roomId, userId) {
    const bookingApiUrl = `${server_url}/api/application_requests`; // Убедитесь, что этот URL правильный для создания заявки
    const bookingData = {
        room_id: roomId,
        student_id: userId,
        status: '0'
    };
    console.log('Отправка данных бронирования:', bookingData, 'на URL:', bookingApiUrl);
    try {
        const response = await fetch(bookingApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(bookingData)
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ошибка ответа сервера:', response.status, errorText);
            try {
                const errorJson = JSON.parse(errorText);
                throw new Error(`Ошибка сервера: ${response.status} - ${errorJson.message || errorText}`);
            } catch (e) {
                throw new Error(`Ошибка сервера: ${response.status} - ${errorText}`);
            }
        }
        const result = await response.json();
        console.log('Успешный ответ от сервера:', result);
        // Отображаем сообщение об успехе или ошибке в <p> тегах
        document.getElementById('success_message').textContent = `Заявка успешно создана! ID: ${result.request_id}`;
        document.getElementById('success_message').style.visibility = 'visible '; // Показываем сообщение об успехе
        document.getElementById('error_message').textContent = ''; // Очищаем сообщение об ошибке
        document.getElementById('error_message').style.visibility = 'hidden'; // Скрываем сообщение об ошибке, если оно было
        return { success: true, data: result };
    } catch (error) {
        console.error('Ошибка при отправке POST-запроса:', error);
        document.getElementById('error_message').textContent = `Ошибка: ${error.message}`;
        document.getElementById('error_message').style.visibility = 'visible';
        document.getElementById('success_message').textContent = ''; // Очищаем сообщение об успехе
        document.getElementById('success_message').style.visibility = 'hidden'; // Скрываем сообщение об успехе
        return { success: false, message: error.message };
    }
}

// async function fetchAndDisplayPendingRoom() {
// // Ищем элемент списка ВНУТРИ функции
// const RoomElement = document.getElementById('room_info');
// try {
//     console.log(`Выполняется GET запрос к: ${apiUrl}`);
//     const response = await fetch(apiUrl, {
//         method: 'GET',
//         headers: {
//             'Accept': 'application/json'
//             // TODO: Добавь заголовок авторизации, если он нужен
//         }
//     });

//     console.log('Получен HTTP статус ответа:', response.status);
//     if (!response.ok) {
//         const errorText = await response.text();
//         console.error('Ответ сервера при ошибке:', errorText);
//         throw new Error(`Ошибка HTTP: ${response.status}`);
//     }

//     const data = await response.json();

//     console.log('Данные получены от API:', data);
//     console.log('Тип data:', typeof data);

//             // Перебираем отфильтрованные заявки и создаем HTML для их отображения
//     console.log('Генерируем HTML');

// } catch (error) {
//     console.error('Ошибка при получении данных:', error);
//     if (RoomElement) {
//         RoomElement.innerHTML = `<p>Произошла ошибка: ${error.message}</p>`;
//     } else {
//             console.error('Не удалось отобразить ошибку на странице, так как элемент списка не найден.');
//     }
// }
// }
window.onload = function() {
    // fetchAndDisplayPendingRoom(); // Загрузка информации о комнате

    // Заполняем поля формы значениями из JavaScript (если это нужно)
    // Это полезно, если пользователь не должен их менять, или для удобства
    // document.getElementById('room_id').value = room_id_js;
    // document.getElementById('user_id').value = user_id_js;


    // Находим форму
    const bookingForm = document.querySelector('form[action="/"]'); // Более точный селектор
    if (bookingForm) {
        bookingForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            // Получаем значения из полей формы (на случай, если они были изменены пользователем)
            // или используем значения из JS, если поля скрыты/только для чтения
            const currentRoomId = document.getElementById('room_id').value;
            const currentUserId = document.getElementById('user_id').value;

            // Вызываем нашу функцию для отправки данных
            // Можно использовать room_id_js и user_id_js, если поля формы не предназначены для редактирования
            const result = await submitBooking(parseInt(currentRoomId), parseInt(currentUserId));

            if (result.success) {
                // Действия при успехе (например, можно очистить форму или перенаправить)
                console.log("Бронирование успешно:", result.data);
                // bookingForm.reset(); // Очистить форму
            } else {
                // Действия при ошибке (сообщение уже отображено в submitBooking)
                console.log("Ошибка бронирования:", result.message);
            }
        });
    }
};