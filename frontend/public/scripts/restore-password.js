document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const submitButton = document.getElementById('send');
    const email = document.getElementById('login').value;
    const formErrorMessage = document.getElementById('formErrorMessage');
    const loginForm = document.getElementById('loginForm');
    const description = document.getElementById('description');
    const icon = document.getElementById('icon');

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/restore_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mail: email }),
        credentials: 'include'
      });

      if (response.ok) {
        description.innerText = 'Within a few minutes, a message with a password will be sent to your email. If you havent received the letter, check your spam folder.';
        description.style.marginTop = '2vh';
        description.style.marginBottom = '2vh';
        icon.style.display = 'none';
        loginForm.querySelector('.form-group').style.display = 'none';
        formErrorMessage.style.display = 'none';
        submitButton.innerText = 'OK';
        submitButton.removeEventListener('click', submitButton.onclick);
        submitButton.addEventListener('click', function() {
          window.location.href = 'login.html';
        });
      } else {
        const errorData = await response.json();
        console.error('Request failed:', errorData);
        if (response.status === 422) {
          formErrorMessage.textContent = 'Incorrect email.';
        } else if (response.status === 500) {
          formErrorMessage.textContent = 'The server is temporarily unavailable. Try later.';
        } else {
          formErrorMessage.textContent = errorData.detail;
        }
        formErrorMessage.style.display = 'block';
      }
    } catch (error) {
      console.error('Request failed:', error);
      formErrorMessage.textContent = 'An error occurred while processing your request';
      formErrorMessage.style.display = 'block';
    }
  });