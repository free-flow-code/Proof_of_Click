// main.js

// Функция для отображения ошибок
function showError(message) {
  const errorMessage = document.getElementById('formErrorMessage');
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  setTimeout(() => {
    errorMessage.style.display = 'none';
  }, 5000);
}

// Функция для обновления счетчика блоков
function updateBlocksCounter(userBalance) {
  const blocksCounter = document.getElementById("blocksCounter");
  blocksCounter.textContent = userBalance.toFixed(3);
}

// Функция для получения и обработки данных при загрузке страницы
async function fetchInitialData() {
  try {
    const response = await fetch("http://127.0.0.1:8000/clicks/get_data", {
      method: 'GET',
      credentials: 'include',
    });

    if (response.status === 401) {
      window.location.href = '../login.html';
      return;
    }

    if (response.ok) {
      const data = await response.json();
      const { blocks_balance, clicks_per_sec, blocks_per_click } = data;

      // Подставляем значения в счетчик и другие переменные
      updateBlocksCounter(blocks_balance);
      return { blocks_balance, clicks_per_sec, blocks_per_click };
    } else {
      const errorData = await response.json();
      showError(errorData.detail || "Failed to fetch data.");
    }
  } catch (error) {
    showError("An error occurred.");
  }
}

// Вызов функции для получения данных при загрузке страницы
document.addEventListener("DOMContentLoaded", fetchInitialData);
