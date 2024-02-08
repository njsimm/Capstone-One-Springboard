// URL for the Flask app
const url = "http://127.0.0.1:5000/";

// Comparison form in the DOM
const comparisonForm = document.getElementById("comparison-form");

// Prevents the form from submitting and sends a POST request to the server. If the request is successful, the results are displayed on the page, the form is reset, and the history is updated. If the request fails, an error message is displayed.
async function handleFormSubmit(evt) {
  evt.preventDefault();

  // Gets the asset type and ticker value from the form. The csrf token is obtained from the hidden input field in the form.
  const assetType1 = getAssetType(1);
  const assetType2 = getAssetType(2);
  const ticker1 = getTicker("ticker_1");
  const ticker2 = getTicker("ticker_2");
  const csrfToken = document.querySelector('input[name="csrf_token"]').value;

  try {
    // Sends a POST request to the server with the form data.
    const response = await axios.post(`${url}handle_comparison`, {
      asset_type_1: assetType1,
      ticker_1: ticker1,
      asset_type_2: assetType2,
      ticker_2: ticker2,
      csrf_token: csrfToken,
    });
    // Displays result on the page.
    showResults(response.data.results, ticker1, ticker2);

    // Resets the form.
    comparisonForm.reset();

    // Updates the history list.
    await getUserHistory();
  } catch (error) {
    // Handles Errors during form submission.
    handleError(error);
  }
}

// Gets the asset type from the form based on the asset type number.
function getAssetType(assetTypeNumber) {
  const assetType0 = document.getElementById(`asset_type_${assetTypeNumber}-0`);
  const assetType1 = document.getElementById(`asset_type_${assetTypeNumber}-1`);

  return assetType0.checked ? assetType0.value : assetType1.value;
}

// Gets the ticker value from the form, converts it to uppercase in order to standardize the input, and returns it.
function getTicker(tickerFormId) {
  return document.getElementById(tickerFormId).value.toUpperCase();
}

// Uses results from the server response and the tickers from the form. Creates a new list element, sets the innerHTML to the msg, sets the innerHTML of the UL element to empty to clear the previous results, and appends the new list element to the UL element.
function showResults(results, ticker1, ticker2) {
  const { multiple, percentage_change: percentChange } = results;
  const msg =
    percentChange < 0
      ? `${ticker2}'s Market Cap is ${percentChange}% of ${ticker1}'s. ${ticker2} would have to perform a ${multiple}x to reach ${ticker1}'s current valuation.`
      : `${ticker2}'s Market Cap is ${percentChange}% greater than ${ticker1}'s. ${ticker1} would have to perform a ${multiple}x to reach ${ticker2}'s current valuation.`;

  const newResultsLi = document.createElement("li");
  newResultsLi.innerHTML = msg;
  const resultsUl = document.querySelector("#results");
  resultsUl.innerHTML = "";
  resultsUl.appendChild(newResultsLi);
}

// Logs the error to the console and displays an alert with the error message.
function handleError(error) {
  console.log(error.response.data.message);
  alert(error.response.data.message);
}

// If the comparison form exists, add an event listener to it that calls handleFormSubmit when the form is submitted.
if (comparisonForm) {
  comparisonForm.addEventListener("submit", handleFormSubmit);
}

// When the window loads, get the user's history and display it on the page.
window.addEventListener("load", async () => {
  if (document.getElementById("history")) await getUserHistory();
});

// Sends a GET request to the server to get the user's history. If the request is successful, calls updateHistory with the history data. If not, logs the error to the console and displays an alert with the error message.
async function getUserHistory() {
  try {
    const response = await axios.get(`${url}get_user_history`);
    const history = response.data.history;
    updateHistory(history);
  } catch (error) {
    handleError(error);
  }
}

// Clears the history list, gets the most recent 5 comparisons, creates a new list element for each comparison, sets the innerHTML to the comparison data, and appends it to the history list.
function updateHistory(history) {
  const historyUl = document.querySelector("#history");
  historyUl.innerHTML = "";
  const recentFiveHistory = history.slice(0, 5);

  for (let comparison of recentFiveHistory) {
    const newHistoryLi = document.createElement("li");
    newHistoryLi.innerHTML = `Date: ${comparison.comparison_timestamp} | ${comparison.name_1} compared to ${comparison.name_2} | Percent Change: ${comparison.name_1} to ${comparison.name_2} is ${comparison.percent_difference}%`;
    historyUl.appendChild(newHistoryLi);
  }
}
