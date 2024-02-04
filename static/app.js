const url = "http://127.0.0.1:5000/";
const comparisonForm = document.getElementById("comparison-form");

if (comparisonForm) {
  comparisonForm.addEventListener("submit", async function (evt) {
    evt.preventDefault();

    let asset_type_1;
    if (document.getElementById("asset_type_1-0").checked) {
      asset_type_1 = document.getElementById("asset_type_1-0").value;
    } else if (document.getElementById("asset_type_1-1").checked) {
      asset_type_1 = document.getElementById("asset_type_1-1").value;
    }

    let asset_type_2;
    if (document.getElementById("asset_type_2-0").checked) {
      asset_type_2 = document.getElementById("asset_type_2-0").value;
    } else if (document.getElementById("asset_type_2-1").checked) {
      asset_type_2 = document.getElementById("asset_type_2-1").value;
    }

    let ticker_1 = document.getElementById("ticker_1").value.toUpperCase();
    let ticker_2 = document.getElementById("ticker_2").value.toUpperCase();

    let csrf_token = document.querySelector('input[name="csrf_token"]').value;

    try {
      const response = await axios.post(`${url}handle_comparison`, {
        asset_type_1,
        ticker_1,
        asset_type_2,
        ticker_2,
        csrf_token,
      });

      let results = response.data.results;
      let multiple = results["multiple"];
      let percentage_change = results["percentage_change"];
      console.log(multiple, percentage_change, response.data);

      let newResultsLi = document.createElement("li");
      if (percentage_change < 0) {
        newResultsLi.innerHTML = `${ticker_2}'s Market Cap is ${percentage_change}% of ${ticker_1}'s. ${ticker_2} would have to perform a ${multiple}x to reach ${ticker_1}'s current valuation.`;
      } else if (percentage_change >= 0) {
        newResultsLi.innerHTML = `${ticker_2}'s Market Cap is ${percentage_change}% greater than ${ticker_1}'s. ${ticker_1} would have to perform a ${multiple}x to reach ${ticker_2}'s current valuation.`;
      }
      const resultsUl = document.querySelector("#results");
      resultsUl.appendChild(newResultsLi);

      // Clear the form
      document.getElementById("ticker_1").value = "";
      document.getElementById("ticker_2").value = "";
      document.getElementById("asset_type_1-0").checked = false;
      document.getElementById("asset_type_1-1").checked = false;
      document.getElementById("asset_type_2-0").checked = false;
      document.getElementById("asset_type_2-1").checked = false;

      await getUserHistory();
    } catch (error) {
      console.log(error.response.data.message);
    }
  });
}

window.addEventListener("load", async function (evt) {
  if (document.getElementById("history")) await getUserHistory();
});

async function getUserHistory() {
  try {
    const response = await axios.get(`${url}get_user_history`);
    let history = response.data.history;

    const historyUl = document.querySelector("#history");
    historyUl.innerHTML = "";

    for (let i = 0; i < 9; i++) {
      let newHistoryLi = document.createElement("li");
      newHistoryLi.innerHTML = `Date: ${history[i].comparison_timestamp} | ${history[i].name_1} compared to ${history[i].name_2} | Percent Change: ${history[i].name_1} to ${history[i].name_2} is ${history[i].percent_difference}%`;
      historyUl.appendChild(newHistoryLi);
      console.log(history);
    }
  } catch (error) {
    console.log(error.response.data.message);
  }
}
