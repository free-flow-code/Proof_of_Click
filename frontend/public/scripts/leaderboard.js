// leaderboard.js

document.addEventListener('DOMContentLoaded', async () => {
  const spinner = document.getElementById('spinner');
  const leaderboardContainer = document.getElementById('leaderboardContainer');

  // Показать спиннер
  spinner.style.display = 'block';

  try {
    // Запрос на сервер для получения лидеров
    const response = await fetch('http://127.0.0.1:8000/auth/leaders', {
      method: 'GET',
      credentials: 'include',
    });

    // Проверка на успешность запроса
    if (!response.ok) {
      const errorData = await response.json();
      showError(errorData.detail || 'Network response was not ok');
      throw new Error(errorData.detail || 'Network response was not ok');
    }

    // Преобразование ответа в JSON
    const data = await response.json();

    // Скрыть спиннер
    spinner.style.display = 'none';

    // Проверка, является ли ответ массивом
    if (Array.isArray(data)) {
      data.forEach((leader, index) => {
        // Создание div для каждого лидера
        const leaderDiv = document.createElement('div');
        leaderDiv.classList.add('leader');

        // Ранг
        const rankDiv = document.createElement('div');
        rankDiv.classList.add('rank');
        rankDiv.textContent = index + 1;

        // Информация о пользователе
        const userInfoDiv = document.createElement('div');
        userInfoDiv.classList.add('user-info');
        userInfoDiv.innerHTML = `
          <div class="itemTitle">Username</div>
          <div class="itemContent">${leader.username}</div>
        `;

        // Информация о балансе
        const balanceInfoDiv = document.createElement('div');
        balanceInfoDiv.classList.add('balance-info');
        balanceInfoDiv.innerHTML = `
          <div class="itemTitle">Balance</div>
          <div class="itemContent">${leader.blocks_balance} blocks</div>
        `;

        // Добавление разделов в leaderDiv
        leaderDiv.appendChild(rankDiv);
        leaderDiv.appendChild(userInfoDiv);
        leaderDiv.appendChild(balanceInfoDiv);

        // Добавление leaderDiv в контейнер leaderboardContainer
        leaderboardContainer.appendChild(leaderDiv);
      });
    } else {
      leaderboardContainer.innerHTML = 'No data available.';
    }
  } catch (error) {
    // Скрыть спиннер и показать сообщение об ошибке
    spinner.style.display = 'none';
    showError(`Error fetching data: ${error.message}`);
    leaderboardContainer.innerHTML = `Error fetching data: ${error.message}`;
  }

  // Объявление переменной userBalance и получение начальных данных
  let userBalance = 0;
  const userData = await fetchInitialData();

  if (userData) {
    const { blocks_balance, clicks_per_sec, blocks_per_click } = userData;
    userBalance = blocks_balance || 0;

    // Обновление счётчика с начальным значением
    updateBlocksCounter(userBalance);

    // Запуск интервала для обновления счётчика каждую секунду
    setInterval(() => {
      userBalance += clicks_per_sec * blocks_per_click;
      updateBlocksCounter(userBalance);
    }, 1000);
  }
});
