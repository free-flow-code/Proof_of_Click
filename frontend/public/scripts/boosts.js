// boosts.js

document.addEventListener("DOMContentLoaded", async () => {
  const formErrorMessage = document.getElementById("formErrorMessage");
  const boostsContainer = document.getElementById("boostsContainer");
  let { blocks_balance: userBalance, clicks_per_sec: clicksPerSec, blocks_per_click: blocksPerClick } = await fetchInitialData() || {};

  const fetchData = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/boosts", {
        method: 'GET',
        credentials: 'include',
      });

      if (response.status === 401) {
        window.location.href = '../login.html';
        return;
      }

      if (response.ok) {
        const data = await response.json();
        userBalance = data.user_balance;
        clicksPerSec = data.clicks_per_sec;
        blocksPerClick = data.blocks_per_click;
        updateBlocksCounter(userBalance);
        renderBoosts(data.boosts);
      } else {
        const errorData = await response.json();
        showError(errorData.detail || "Failed to fetch boosts.");
      }
    } catch (error) {
      showError("An error occurred.");
    }
  };

  const renderBoosts = (boosts) => {
    boostsContainer.innerHTML = "";
    boosts.forEach((boost) => {
      const [boostName, boostDetails] = Object.entries(boost)[0];
      const boostCard = document.createElement("div");
      boostCard.classList.add("boostCard");

      const boostTitleLevelContainer = document.createElement("div");
      boostTitleLevelContainer.classList.add("boostTitleLevelContainer");

      const boostTitle = document.createElement("div");
      boostTitle.classList.add("boostTitle");
      boostTitle.textContent = boostDetails.boost_title;

      const boostLevel = document.createElement("div");
      boostLevel.classList.add("boostLevel");
      boostLevel.textContent = `Level: ${boostDetails.current_level}`;

      boostTitleLevelContainer.appendChild(boostTitle);
      boostTitleLevelContainer.appendChild(boostLevel);

      const boostDescription = document.createElement("details");
      boostDescription.classList.add("boostDescription");
      const boostSummary = document.createElement("summary");
      boostSummary.textContent = "Description";
      boostDescription.appendChild(boostSummary);
      boostDescription.append(boostDetails.description);

      const boostImageDetailsContainer = document.createElement("div");
      boostImageDetailsContainer.classList.add("boostImageDetailsContainer");

      const boostImage = document.createElement("div");
      boostImage.classList.add("boostImage");
      const img = document.createElement("img");
      img.src = `/images/${boostDetails.image_id}.png`;
      boostImage.appendChild(img);

      const boostDetailsContainer = document.createElement("div");
      boostDetailsContainer.classList.add("boostDetails");

      const boostCharacteristic = document.createElement("div");
      boostCharacteristic.classList.add("boostCharacteristic");
      boostCharacteristic.textContent = boostDetails.characteristic;

      const boostProgressContainer = document.createElement("div");
      boostProgressContainer.classList.add("boostProgressContainer");

      const progressMinValue = document.createElement("div");
      progressMinValue.classList.add("progressMinValue");
      progressMinValue.textContent = "0";

      const boostProgress = document.createElement("div");
      boostProgress.classList.add("boostProgress");

      const boostProgressValue = document.createElement("div");
      boostProgressValue.classList.add("boostProgressValue");
      boostProgressValue.style.width = `${(boostDetails.current_value / boostDetails.max_value) * 100}%`;

      const boostNextLevelValue = document.createElement("div");
      boostNextLevelValue.classList.add("boostNextLevelValue");
      boostNextLevelValue.style.width = `${((boostDetails.next_lvl_value - boostDetails.current_value) / boostDetails.max_value) * 100}%`;

      const boostProgressMarkerValue = document.createElement("div");
      boostProgressMarkerValue.classList.add("boostProgressMarkerValue");
      boostProgressMarkerValue.textContent = boostDetails.current_value;
      boostProgressMarkerValue.style.left = `${(boostDetails.current_value / boostDetails.max_value) * 100}%`;

      boostProgress.appendChild(boostProgressValue);
      if (boostDetails.next_lvl_value !== null) {
        boostProgress.appendChild(boostNextLevelValue);
      }

      const progressMaxValue = document.createElement("div");
      progressMaxValue.classList.add("progressMaxValue");
      progressMaxValue.textContent = boostDetails.max_value;

      boostProgressContainer.appendChild(progressMinValue);
      boostProgressContainer.appendChild(boostProgress);
      boostProgressContainer.appendChild(progressMaxValue);
      boostProgress.appendChild(boostProgressMarkerValue);

      const boostPrice = document.createElement("div");
      boostPrice.classList.add("boostPrice");
      if (boostDetails.next_lvl_price !== null) {
        boostPrice.innerHTML = `
          <div class="priceTitle">price:</div>
          <div class="priceValue">${boostDetails.next_lvl_price}</div>
          <div class="priceCurrency">blocks</div>
        `;
      }

      const upgradeBoost = document.createElement("button");
      upgradeBoost.classList.add("upgradeBoost");
      upgradeBoost.textContent = "Upgrade Level";
      upgradeBoost.disabled = userBalance < boostDetails.next_lvl_price;

      const buyBoost = document.createElement("button");
      buyBoost.classList.add("buyBoost");
      buyBoost.textContent = `Buy max level for ${boostDetails.usdt_price} USDT`;
      if (boostDetails.next_lvl_price === null) {
        upgradeBoost.disabled = true;
        buyBoost.disabled = true;
      }

      boostDetailsContainer.appendChild(boostCharacteristic);
      boostDetailsContainer.appendChild(boostProgressContainer);
      boostDetailsContainer.appendChild(boostPrice);

      boostImageDetailsContainer.appendChild(boostImage);
      boostImageDetailsContainer.appendChild(boostDetailsContainer);

      boostCard.appendChild(boostTitleLevelContainer);
      boostCard.appendChild(boostDescription);
      boostCard.appendChild(boostImageDetailsContainer);
      boostCard.appendChild(upgradeBoost);
      boostCard.appendChild(buyBoost);

      boostsContainer.appendChild(boostCard);

      upgradeBoost.addEventListener("click", async () => {
        upgradeBoost.disabled = true;
        try {
          const response = await fetch(`http://127.0.0.1:8000/boosts/upgrade/${boostName}`, {
            method: 'GET',
            credentials: 'include',
          });
          if (response.ok) {
            fetchData();
          } else {
            const errorData = await response.json();
            showError(errorData.detail || "Failed to upgrade boost.");
          }
        } catch (error) {
          showError("An error occurred.");
        } finally {
          upgradeBoost.disabled = userBalance < boostDetails.next_lvl_price;
        }
      });

      buyBoost.addEventListener("click", async () => {
        try {
          const response = await fetch(`http://127.0.0.1:8000/boosts/buy/${boostName}`, {
            method: 'GET',
            credentials: 'include',
          });
          if (response.ok) {
            fetchData();
          } else {
            const errorData = await response.json();
            showError(errorData.detail || "Failed to buy boost.");
          }
        } catch (error) {
          showError("An error occurred.");
        }
      });
    });
  };

  fetchData();
  setInterval(() => {
    userBalance += clicksPerSec * blocksPerClick;
    updateBlocksCounter(userBalance);
    document.querySelectorAll(".upgradeBoost").forEach((button, index) => {
      const boost = boostsContainer.children[index];
      const nextLvlPrice = parseFloat(boost.querySelector(".boostPrice .priceValue").textContent);
      button.disabled = userBalance < nextLvlPrice;
    });
  }, 1000);
});
