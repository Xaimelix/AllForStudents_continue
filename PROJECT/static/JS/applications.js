// URL API эндпоинта для получения всех заявок
    const serverBaseUrl = "{{ server_url }}"; 
    const apiUrl = `${serverBaseUrl}api/application_requests`; // URL для получения всех заявок
    
    // URL API эндпоинта для обновления статуса заявки (PUT запрос по ID)
    // Он должен соответствовать маршруту ApplicationRequestItemResource: /api/application_requests/<int:request_id>
    const updateStatusApiUrl_application_requests = `${serverBaseUrl}api/application_requests/`; // Базовый URL, к которому добавим ID заявки
    const updateStatusApiUrl_room = `${serverBaseUrl}api/rooms/`; // Базовый URL для изменения комнаты, к которому добавим ID заявки


    // Функция для получения и отображения заявок со статусом 0
    async function fetchAndDisplayPendingApplicationRequests() {
        // Ищем элемент списка ВНУТРИ функции
        const applicationRequestsListElement = document.getElementById('applicationRequestsList');

        // Проверяем, найден ли элемент. Если нет, выводим ошибку и останавливаемся.
        if (!applicationRequestsListElement) {
            console.error("HTML элемент с ID 'applicationRequestsList' не найден на странице!");
            const body = document.querySelector('body');
            if (body) {
                const errorDiv = document.createElement('div');
                errorDiv.style.color = 'red';
                errorDiv.textContent = "Ошибка загрузки: элемент для списка заявок не найден!";
                body.prepend(errorDiv);
            }
            return; // Прекращаем выполнение функции
        }

        // Очищаем текущее содержимое элемента списка и ставим сообщение о загрузке
        applicationRequestsListElement.innerHTML = '<p>Загрузка заявок...</p>';


        try {
            console.log(`Выполняется GET запрос к: ${apiUrl}`);
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            console.log('Получен HTTP статус ответа:', response.status);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Ответ сервера при ошибке:', errorText);
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }

            const data = await response.json();

            console.log('Данные получены от API:', data);
            console.log('Тип data:', typeof data);


            if (data && typeof data === 'object' && Array.isArray(data.requests)) {
                applicationRequestsListElement.innerHTML = ''; // Очищаем сообщение о загрузке

                console.log('Исходный список заявок (data.requests):', data.requests);


                // Фильтруем заявки по статусу 0
                const pendingRequests = data.requests.filter(request => {
                    console.log(`Проверяем заявку ID ${request.id}: статус "${request.status}" (тип: ${typeof request.status})`);
                    return request.status === '0';
                });


                console.log('Отфильтрованный список заявок (pendingRequests):', pendingRequests);


                if (pendingRequests.length === 0) {
                    applicationRequestsListElement.innerHTML = '<p>Нет заявок на переселение в статусе "0".</p>';
                } else {
                    // Перебираем отфильтрованные заявки и создаем HTML для их отображения
                    pendingRequests.forEach(request => {
                        console.log('Генерируем HTML для заявки ID:', request.id);

                        const requestElement = document.createElement('div');
                        requestElement.classList.add('application-request-item');
                        requestElement.dataset.requestId = request.id;
                        requestElement.dataset.roomId = request.room_id;
                        requestElement.dataset.studentId = request.student_id;
                        


                        requestElement.innerHTML = `
                            <div class="request-info">
                                <h3>Заявка #${request.id}</h3>
                                <p data-status="${request.status}">Статус: ${request.status}</p>
                                <p data-entr="${request.date_entr}">Дата въезда: ${request.date_entr || 'Не указана'}</p>
                                <p data-exit="${request.date_exit}">Дата выезда: ${request.date_exit || 'Не указана'}</p>
                                <p data-room-id="${request.room_id}">ID комнаты: ${request.room_id}</p>
                                <p data-student-id="${request.student_id}">ID студента: ${request.student_id}</p>
                                <h4>Коменнтарий (заполнятеся при отказе):</h4>
                                <textarea placeholder="Все хорошо"></textarea>
                            </div>
                                
                            <div class="request-actions">
                                <button class="approve-button" data-request-id="${request.id}">Одобрить</button>
                                <button class="reject-button" data-request-id="${request.id}">Отклонить</button>
                            </div>
                        `;

                        applicationRequestsListElement.appendChild(requestElement);
                    });

                    // Добавляем слушателей событий для кнопок после того, как все заявки добавлены
                    // ПЕРЕДАЕМ applicationRequestsListElement КАК АРГУМЕНТ
                    attachButtonListeners(applicationRequestsListElement);

                }

            } else {
                console.error('Неверный формат данных от API:', data);
                applicationRequestsListElement.innerHTML = '<p>Не удалось загрузить данные заявок из-за ошибки формата.</p>';
            }

        } catch (error) {
            console.error('Ошибка при получении или обработке заявок:', error);
            if (applicationRequestsListElement) {
                applicationRequestsListElement.innerHTML = `<p>Произошла ошибка при загрузке или обработке заявок: ${error.message}</p>`;
            } else {
                console.error('Не удалось отобразить ошибку на странице, так как элемент списка не найден.');
            }
        }
    }

    // Функция для добавления обработчиков кликов на кнопки
    // ФУНКЦИЯ ТЕПЕРЬ ПРИНИМАЕТ АРГУМЕНТ listElement
    function attachButtonListeners(listElement) {
         // Используем переданный listElement для поиска кнопок внутри него
        const approveButtons = listElement.querySelectorAll('.approve-button');
        approveButtons.forEach(button => {
            // Удаляем старые слушатели, чтобы избежать их дублирования при повторных вызовах fetchAndDisplayPendingApplicationRequests
            button.removeEventListener('click', handleApproveClick);
            button.addEventListener('click', handleApproveClick);
        });

        const rejectButtons = listElement.querySelectorAll('.reject-button');
        rejectButtons.forEach(button => {
             // Удаляем старые слушатели
            button.removeEventListener('click', handleRejectClick);
            button.addEventListener('click', handleRejectClick);
        });
    }

    // Функции для обработки кликов по кнопкам Одобрить/Отклонить
    async function handleApproveClick(event) {
        const requestId = event.target.dataset.requestId;
        const requestElement = event.target.closest('.application-request-item');
        const room_id = requestElement.dataset.roomId;
        const student_id = requestElement.dataset.studentId;

        console.log(`Approve clicked. Request ID: ${requestId}, Room ID: ${room_id}`);

        try {
            // 1. Получаем данные комнаты
            const getRoomResponse = await fetch(`${updateStatusApiUrl_room}${room_id}`);
            if (!getRoomResponse.ok) {
                throw new Error(`Ошибка получения комнаты: ${await getRoomResponse.text()}`);
            }
            const roomData = await getRoomResponse.json();

            // 2. Получаем данные студента
            const getStudentResponse = await fetch(`${serverBaseUrl}api/students/${student_id}`);
            if (!getStudentResponse.ok) {
                throw new Error(`Ошибка получения студента: ${await getStudentResponse.text()}`);
            }
            const studentData = await getStudentResponse.json();

            // 3. Проверки
            if (roomData['room'].cur_cnt_student >= roomData['room'].max_cnt_student) {
                alert("Нельзя одобрить заявку: в комнате уже максимальное количество жильцов.");
                return;
            }
            if (roomData['room'].sex !== studentData['student'].sex) {
                alert(`Нельзя одобрить заявку: пол студента (${studentData.sex}) не совпадает с полом комнаты (${roomData.gender}).`);
                return;
            }

            // 4. Обновляем статус заявки
            const approveResponse = await fetch(`${updateStatusApiUrl_application_requests}${requestId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: '1' })
            });
            if (!approveResponse.ok) {
                throw new Error(`Ошибка при обновлении статуса: ${await approveResponse.text()}`);
            }

            // 5. Увеличиваем количество жильцов
            const updateRoomResponse = await fetch(`${updateStatusApiUrl_room}${room_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cur_cnt_student: Number(roomData['room'].cur_cnt_student) + 1
                })
            });
            if (!updateRoomResponse.ok) {
                throw new Error(`Ошибка при обновлении комнаты: ${await updateRoomResponse.text()}`);
            }

            requestElement.remove();
            alert(`Заявка ${requestId} одобрена и жильцы обновлены.`);
        } catch (error) {
            console.error(error);
            alert(`Ошибка обработки заявки: ${error.message}`);
        }
    }

    async function handleRejectClick(event) {
        const requestId = event.target.dataset.requestId; // Получаем ID заявки из атрибута data-request-id
        console.log(`Нажата кнопка "Отклонить" для заявки ID: ${requestId}`);
        const comment_admin = event.target.closest('.application-request-item').querySelector('textarea').value; // Получаем комментарий из текстового поля
        if (comment_admin.trim() === '') { // Проверяем, что комментарий не пустой
            alert('Пожалуйста, введите комментарий перед отклонением заявки.');
            return; // Прекращаем выполнение функции, если комментарий пустой
        }
        console.log(`Комментарий администратора: ${comment_admin}`); // Логгируем комментарий
        try {
            // Отправляем PUT запрос к API для изменения статуса заявки на "2" (отклонено)
            console.log(`Отправка PUT запроса для отклонения заявки ID ${requestId}`); // Логгирование запроса
            const response = await fetch(`${updateStatusApiUrl_application_requests}${requestId}`, { // Используем базовый URL + ID
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json' // Указываем, что отправляем JSON
                },
                body: JSON.stringify({ status: '2', comment: comment_admin }) // Отправляем JSON с новым статусом '2'
            });

            console.log(`Получен ответ на PUT запрос для отклонения заявки ID ${requestId}. Статус: ${response.status}`); // Логгирование ответа

            // Проверяем, успешен ли был запрос
            if (response.ok) {
                console.log(`Заявка ${requestId} отклонена.`);
                // Обновить интерфейс: удалить этот блок заявки с страницы
                const requestElement = event.target.closest('.application-request-item'); // Находим родительский элемент заявки
                 if (requestElement) {
                     requestElement.remove(); // Удаляем элемент
                 }
                  alert(`Заявка ${requestId} отклонена.`); // Оповещение пользователя
            } else {
                 // Получаем сообщение об ошибке от сервера
                const errorData = await response.json();
                const errorMessage = errorData.message || `Ошибка HTTP: ${response.status}`;
                console.error(`Ошибка при отклонении заявки ${requestId}: ${errorMessage}`);
                 alert(`Не удалось отклонить заявку ${requestId}. ${errorMessage}`); // Показываем ошибку пользователю
            }

        } catch (error) {
            console.error('Ошибка при выполнении запроса на отклонение:', error);
             alert(`Произошла ошибка при отклонении заявки ${requestId}: ${error.message}`); // Показываем ошибку пользователю
        }
    }


    // Вызываем функцию для загрузки и отображения заявок со статусом 0, когда страница загрузится
    document.addEventListener('DOMContentLoaded', fetchAndDisplayPendingApplicationRequests);
