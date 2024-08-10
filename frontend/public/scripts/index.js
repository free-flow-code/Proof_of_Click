// index.js

// Function for showing error messages
function showError(message) {
  const errorMessage = document.getElementById('formErrorMessage');
  if (errorMessage) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
      errorMessage.style.display = 'none';
    }, 5000);
  }
}

// Function for updating the blocks counter
function updateBlocksCounter(balance) {
  const counter = document.getElementById('counter');
  if (counter) {
    counter.textContent = `Blocks: ${formatNumber(balance.toFixed(3))}`;
  }
}

// Function for sending clicks to the server
async function sendClicks() {
  if (localClicks > 0) {
    try {
      const response = await fetch('http://127.0.0.1:8000/clicks', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ clicks: localClicks })
      });

      if (response.status === 401) {
        // If the token has expired, redirect to the login page
        window.location.href = '../login.html';
        return;
      }

      if (response.status === 500) {
        const errorData = await response.json();
        showError(errorData.detail);
        throw new Error(errorData.detail);
      }

      const data = await response.json();

      if (data && data.status !== 'accepted') {
        showError(`Click rejected: ${data.message}`);
      }
    } catch (error) {
      console.error('Error:', error);
      showError('Server is currently unavailable. Please try again later.');
    }

    localClicks = 0;
  }
  isSending = false;
}

// Clicks processing
const socket = io();
let localClicks = 0;
let isSending = false;
let requestId = null;

// Elements
const clickImage = document.getElementById('clickImage');
const counter = document.getElementById('counter');
const mineSpeed = document.getElementById('mineSpeed');
const clickImageContainer = document.getElementById('clickImageContainer');
let clicksPerSec = 0;
let blocksPerClick = 0;
let blocksBalance = 0;  // Use let here instead of const

// Fetch initial data
async function fetchInitialData() {
  try {
    const response = await fetch('http://127.0.0.1:8000/clicks/get_data', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.status === 401) {
      window.location.href = '../login.html';
      return null;
    }

    if (!response.ok) {
      const errorData = await response.json();
      showError(errorData.detail || 'Failed to fetch initial data.');
      throw new Error(errorData.detail || 'Failed to fetch initial data.');
    }

    return await response.json();
  } catch (error) {
    showError(`Error fetching initial data: ${error.message}`);
    return null;
  }
}

// Initialize page data
async function initializePage() {
  const data = await fetchInitialData();

  if (data) {
    const { blocks_balance, clicks_per_sec, blocks_per_click } = data;

    // Update initial values
    blocksBalance = blocks_balance;
    clicksPerSec = clicks_per_sec || 1;  // Ensure clicksPerSec is at least 1
    blocksPerClick = blocks_per_click || 1;  // Ensure blocksPerClick is at least 1

    updateBlocksCounter(blocksBalance);
    mineSpeed.textContent = `${(clicksPerSec * blocksPerClick).toFixed(3)} blocks/sec.`;

    // Update counter every second based on clicks_per_sec and blocks_per_click
    setInterval(() => {
      blocksBalance += (clicksPerSec * blocksPerClick);
      updateBlocksCounter(blocksBalance);

      // Show animation with value (clicks_per_sec * blocks_per_click * 1000)
      const animationValue = clicksPerSec * blocksPerClick * 1000;
      const plusOne = document.createElement('div');
      plusOne.textContent = '+' + animationValue.toFixed(0);
      plusOne.classList.add('plusOne');
      plusOne.style.left = (clickImage.offsetLeft + (clickImage.offsetWidth / 2)) + 'px';
      plusOne.style.top = (clickImage.offsetTop - 40) + 'px';
      clickImageContainer.appendChild(plusOne);

      // Remove the element after the animation ends
      plusOne.addEventListener('animationend', () => {
        plusOne.remove();
      });
    }, 1000);
  }
}

function handleClick(event) {
  console.log('Click registered');
  const clickValue = blocksPerClick;
  localClicks += clickValue;
  blocksBalance += clickValue;  // Update blocks balance immediately
  updateBlocksCounter(blocksBalance);  // Reflect change immediately in counter
  if (!requestId) {
    requestId = requestAnimationFrame(updateCounter);
  }

  // Adding animation
  const plusOne = document.createElement('div');
  plusOne.textContent = '+' + (blocksPerClick * 1000).toFixed(0);
  plusOne.classList.add('plusOne');
  plusOne.style.left = event.clientX + 'px';
  plusOne.style.top = (event.clientY - 80) + 'px';
  document.body.appendChild(plusOne);

  // Removing the element after the animation ends
  plusOne.addEventListener('animationend', () => {
    plusOne.remove();
  });
}

// Using mousedown and mouseup instead of click
clickImage.addEventListener('mousedown', handleClick);

function updateCounter() {
  console.log('Counter updated');
  // No longer updating a separate counter display
  requestId = null;
}

// Sending clicks to FastAPI backend every 3 seconds
setInterval(() => {
  sendClicks();
}, 3000);

socket.on('clickAcknowledged', (data) => {
  if (data.status !== 'accepted') {
    showError(data.message);
  }
});

function formatNumber(num) {
  const [integerPart, decimalPart] = num.split('.');
  const formattedIntegerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return `${formattedIntegerPart}.${decimalPart}`;
}

// Initialize the page
initializePage();
