async function verifyEmail() {
    const urlParams = new URLSearchParams(window.location.search);
    const mailConfirmCode = urlParams.get('code');
    const spinner = document.getElementById('spinner');
    const message = document.getElementById('message');
    const formContent = document.getElementById('formContent');

    if (!mailConfirmCode) {
        message.innerText = 'Verification code not provided.';
        message.classList.remove('hidden');
        spinner.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/auth/verify/${mailConfirmCode}`, {
            method: 'GET',
            credentials: 'include',
        });

        const data = await response.json();

        if (response.ok) {
            spinner.classList.add('hidden');
            formContent.classList.remove('hidden');
        } else if (response.status === 301) {
            window.location.href = `/index.html`;
        } else {
            message.innerText = data.detail || 'Verification error.';
            message.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    } catch (error) {
        message.innerText = 'An error occurred while confirming.';
        message.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

function redirectToIndex() {
    window.location.href = `/index.html`;
}

window.onload = verifyEmail;