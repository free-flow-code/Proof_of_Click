document.addEventListener('DOMContentLoaded', async () => {
  const spinner = document.getElementById('spinner');
  const leaderboardContainer = document.getElementById('leaderboardContainer');

  // Show spinner
  spinner.style.display = 'block';

  try {
    // Request to server to get leaders
    const response = await fetch('http://127.0.0.1:8000/auth/leaders', {
      method: 'GET',
      credentials: 'include',
    });

    // Checking if a request was successful
    if (!response.ok) {
      const errorData = await response.json();
      showError(errorData.detail || 'Network response was not ok');
      throw new Error(errorData.detail || 'Network response was not ok');
    }

    // Converting response to JSON
    const data = await response.json();

    // Hide spinner
    spinner.style.display = 'none';

    // Check if response is an array
    if (Array.isArray(data)) {
      data.forEach((leader, index) => {
        // Create a div for each leader
        const leaderDiv = document.createElement('div');
        leaderDiv.classList.add('leader');

        // Rank
        const rankDiv = document.createElement('div');
        rankDiv.classList.add('rank');
        rankDiv.textContent = index + 1;

        // User information
        const userInfoDiv = document.createElement('div');
        userInfoDiv.classList.add('user-info');
        userInfoDiv.innerHTML = `
          <div class="itemTitle">Username</div>
          <div class="itemContent">${leader.username}</div>
        `;

        // Balance information
        const balanceInfoDiv = document.createElement('div');
        balanceInfoDiv.classList.add('balance-info');
        balanceInfoDiv.innerHTML = `
          <div class="itemTitle">Balance</div>
          <div class="itemContent">${leader.blocks_balance} blocks</div>
        `;

        // Adding sections to leaderDiv
        leaderDiv.appendChild(rankDiv);
        leaderDiv.appendChild(userInfoDiv);
        leaderDiv.appendChild(balanceInfoDiv);

        // Adding leaderDiv to leaderboardContainer
        leaderboardContainer.appendChild(leaderDiv);
      });
    } else {
      leaderboardContainer.innerHTML = 'No data available.';
    }
  } catch (error) {
    // Hide spinner and show error message
    spinner.style.display = 'none';
    showError(`Error fetching data: ${error.message}`);
    leaderboardContainer.innerHTML = `Error fetching data: ${error.message}`;
  }

  // Declaring the userBalance variable and getting initial data
  let userBalance = 0;
  const userData = await fetchInitialData();

  if (userData) {
    const { blocks_balance, clicks_per_sec, blocks_per_click } = userData;
    userBalance = blocks_balance || 0;

    // Update counter with initial value
    updateBlocksCounter(userBalance);

    // Start interval to update counter every second
    setInterval(() => {
      userBalance += clicks_per_sec * blocks_per_click;
      updateBlocksCounter(userBalance);
    }, 1000);
  }
});
