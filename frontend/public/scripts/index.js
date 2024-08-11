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

async function initializePage() {
  const data = await fetchInitialData();

  if (data) {
    const { blocks_balance, clicks_per_sec, blocks_per_click } = data;

    // Use the values obtained from main.js
    blocksBalance = blocks_balance;
    clicksPerSec = clicks_per_sec;
    blocksPerClick = blocks_per_click;

    updateBlocksCounter(blocksBalance);
    mineSpeed.textContent = `${(clicksPerSec * blocksPerClick).toFixed(3)} blocks/sec.`;

    // Update the counter every second
    setInterval(() => {
      blocksBalance += (clicksPerSec * blocksPerClick);
      updateBlocksCounter(blocksBalance);

      const animationValue = clicksPerSec * blocksPerClick * 1000;
      const plusOne = document.createElement('div');
      plusOne.textContent = '+' + animationValue.toFixed(0);
      plusOne.classList.add('plusOne');
      plusOne.style.left = (clickImage.offsetLeft + (clickImage.offsetWidth / 2)) + 'px';
      plusOne.style.top = (clickImage.offsetTop - 40) + 'px';
      clickImageContainer.appendChild(plusOne);

      plusOne.addEventListener('animationend', () => {
        plusOne.remove();
      });
    }, 1000);
  } else {
    showError('Failed to initialize page data.');
  }
}

function handleClick(event) {
  console.log('Click registered');
  const clickValue = blocksPerClick;
  localClicks += 1;
  blocksBalance += clickValue;
  updateBlocksCounter(blocksBalance);

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

  plusOne.addEventListener('animationend', () => {
    plusOne.remove();
  });
}

// Use mousedown and mouseup instead of click
clickImage.addEventListener('mousedown', handleClick);

function updateCounter() {
  console.log('Counter updated');
  requestId = null;
}

// Send clicks to the server every 3 seconds
setInterval(() => {
  sendClicks();
}, 3000);

socket.on('clickAcknowledged', (data) => {
  if (data.status !== 'accepted') {
    showError(data.message);
  }
});

initializePage();
