// leaderboard.js

document.addEventListener('DOMContentLoaded', () => {
  const spinner = document.getElementById('spinner');
  const leaderboardContainer = document.getElementById('leaderboardContainer');

  // Show the spinner
  spinner.style.display = 'block';

  // Fetch leaders from the backend
  fetch('http://127.0.0.1:8000/auth/leaders', {
      method: 'GET',
      credentials: 'include',
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Hide the spinner
      spinner.style.display = 'none';

      // Check if data is an array
      if (Array.isArray(data)) {
        data.forEach((leader, index) => {
          // Create a div for each leader
          const leaderDiv = document.createElement('div');
          leaderDiv.classList.add('leader');

          // Rank
          const rankDiv = document.createElement('div');
          rankDiv.classList.add('rank');
          rankDiv.textContent = index + 1;

          // User Info
          const userInfoDiv = document.createElement('div');
          userInfoDiv.classList.add('user-info');
          userInfoDiv.innerHTML = `
            <div class="itemTitle">Username</div>
            <div class="itemContent">${leader.username}</div>
          `;

          // Balance Info
          const balanceInfoDiv = document.createElement('div');
          balanceInfoDiv.classList.add('balance-info');
          balanceInfoDiv.innerHTML = `
            <div class="itemTitle">Balance</div>
            <div class="itemContent">${leader.blocks_balance} blocks</div>
          `;

          // Append sections to the leaderDiv
          leaderDiv.appendChild(rankDiv);
          leaderDiv.appendChild(userInfoDiv);
          leaderDiv.appendChild(balanceInfoDiv);

          // Append leaderDiv to the leaderboardContainer
          leaderboardContainer.appendChild(leaderDiv);
        });
      } else {
        leaderboardContainer.innerHTML = 'No data available.';
      }
    })
    .catch(error => {
      // Hide the spinner and show error message
      spinner.style.display = 'none';
      leaderboardContainer.innerHTML = `Error fetching data: ${error.message}`;
    });
});
