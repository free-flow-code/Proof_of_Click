document.getElementById('loginForm').addEventListener('submit', async function(event) {
  event.preventDefault();

  const submitButton = document.querySelector('input[type="submit"]');
  const spinner = document.getElementById('spinner');
  const username = document.getElementById('username').value;
  const login = document.getElementById('login').value;
  const password = document.getElementById('password').value;
  const activeTab = document.querySelector('.active').id;

  // Additional client-side validation (for demonstration)
  const usernameError = document.getElementById('usernameError');
  const passwordError = document.getElementById('passwordError');

  usernameError.textContent = '';
  passwordError.textContent = '';

  // Validate username
  if (activeTab === 'signUpTab') {
    if (activeTab === 'signUpTab' && !/^.{4,20}$/.test(username)) {
      usernameError.textContent = 'Username must be 4-20 characters long and cannot contain spaces';
      return;
    }
  }

  // Validate password
  if (!/^\S{6,50}$/.test(password)) {
    passwordError.textContent = 'Password must be 6-50 characters long and cannot contain spaces';
    return;
  }

  const url = activeTab === 'signInTab'
    ? 'http://127.0.0.1:8000/auth/login'
    : 'http://127.0.0.1:8000/auth/register';

  const payload = activeTab === 'signInTab'
    ? { mail: login, password: password }
    : { username: username, mail: login, password: password };

  // Show spinner and disable submit button
  spinner.classList.remove('spinner-hidden');
  submitButton.disabled = true;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      credentials: 'include' // Enable cookies
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Request successful:', data);
      window.location.href = 'index.html';
    } else {
      const errorData = await response.json();
      console.error('Request failed:', errorData);
      if (response.status === 422) {
        showError('Invalid email format');
      } else {
        showError(errorData.detail);
      }
    }
  } catch (error) {
    console.error('Request failed:', error);
    showError('An error occurred while processing your request');
  } finally {
    // Hide spinner and enable submit button
    spinner.classList.add('spinner-hidden');
    submitButton.disabled = false;
  }
});
