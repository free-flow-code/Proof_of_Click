function showError(message) {
      const errorMessage = document.getElementById('formErrorMessage');
      errorMessage.textContent = message;
      errorMessage.style.display = 'block';
      setTimeout(() => {
        errorMessage.style.display = 'none';
      }, 10000);
    }

    // Function for sending clicks to the server
    function sendClicks() {
        if (localClicks > 0) {
            fetch('http://127.0.0.1:8000/clicks', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({clicks: localClicks})
            })
            .then(response => {
                if (response.status === 401) {
                    // If the token has expired, redirect to the login page
                    window.location.href = '../login.html';
                    return;
                }
                if (response.status === 500) {
                    return response.json().then(errorData => {
                        showError(errorData.detail);
                        throw new Error(errorData.detail);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data && data.status !== 'accepted') {
                    showError(`Click rejected: ${data.message}`);
                }
            })
            .catch(error => console.error('Error:', error));

            localClicks = 0;
        }
        isSending = false;
    }

    // Clicks processing
    const socket = io();
    let clickCount = 0;
    let localClicks = 0;
    let isSending = false;
    let requestId = null;

    const clickImage = document.getElementById('clickImage');
    const counter = document.getElementById('counter');

    function handleClick(event) {
        console.log('Click registered');
        localClicks += 0.001;
        clickCount += 0.001;
        if (!requestId) {
            requestId = requestAnimationFrame(updateCounter);
        }

        // Adding animation +1
        const plusOne = document.createElement('div');
        plusOne.textContent = '+1';
        plusOne.classList.add('plusOne');
        plusOne.style.left = event.clientX + 'px';
        plusOne.style.top = (event.clientY - 40) + 'px';
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
        counter.childNodes[0].nodeValue = `Blocks: ${formatNumber(clickCount.toFixed(3))}`;
        requestId = null;
    }

    // Sending clicks to FastAPI backend every 2 seconds
    setInterval(() => {
        const roundedClicks = parseFloat(localClicks.toFixed(3));
        sendClicks();
    }, 2000);

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