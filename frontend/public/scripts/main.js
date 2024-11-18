function showError(message) {
  const errorMessage = document.getElementById('formErrorMessage');
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  setTimeout(() => {
    errorMessage.style.display = 'none';
  }, 5000);
}

// Function to format numbers with spaces
function formatNumber(num) {
  const [integerPart, decimalPart] = num.toString().split('.');
  const formattedIntegerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return `${formattedIntegerPart}.${decimalPart || '000'}`;
}

// Function to update block counter
function updateBlocksCounter(userBalance) {
  const blocksCounter = document.getElementById("blocksCounter");
  blocksCounter.textContent = formatNumber(userBalance.toFixed(3));
}

// Function for receiving and processing data when loading a page
async function fetchInitialData() {
  try {
    const response = await fetch("http://127.0.0.1:8000/auth/me", {
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

      clicksPerSec = clicks_per_sec || 0;
      blocksPerClick = blocks_per_click || 0.001;

      updateBlocksCounter(blocks_balance);

      return { blocks_balance, clicks_per_sec: clicksPerSec, blocks_per_click: blocksPerClick };
    } else {
      const errorData = await response.json();
      showError(errorData.detail || "Failed to fetch data.");
    }
  } catch (error) {
    showError("An error occurred.");
  }
}
