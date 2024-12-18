function displayData(weeklyData) {
  console.log("displayData called!", weeklyData);
  const tablesDiv = document.getElementById("tables"); // Get the tables container
  for (const targetDateStr in weeklyData) {
    console.log("targetDateStr", targetDateStr);
    const safeTargetDateId = targetDateStr.replace(/\//g, '-');
    const targetData = weeklyData[targetDateStr];

    // Create the h2 and div elements dynamically
    const h2 = document.createElement("h2");
    h2.textContent = targetData.eventName;
    const tableDiv = document.createElement("div");
    tableDiv.id = "table-" + safeTargetDateId;
    tablesDiv.appendChild(h2);
    tablesDiv.appendChild(tableDiv);

    const tableData = [];
    for (const sundayStr in targetData.weeks) {
      const week = targetData.weeks[sundayStr];
      tableData.push(week.tableRow);
    }
    console.log("tableData", tableData)
    new Tabulator("#table-" + safeTargetDateId, {
      data: tableData.reverse(),
      columns: [
        { title: "Sunday", field: "sunday", sorter:"date", formatter:"datetime", formatterParams:{outputFormat:"YYYY-MM-DD"} },
        { title: "Countdown", field: "countdown" },
        { title: "Activity", field: "activity", formatter: "html" },
        { title: "Events", field: "events", formatter: "html" }
      ],
    });
  }
}

function onFailure(error) {
  console.error("Error from server:", error);
  alert("An error occurred. Please check the console.");
}

// Only ONE event listener!
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM content loaded");
  google.script.run
    .withSuccessHandler(displayData)
    .withFailureHandler(onFailure)
    .getWeeklyData();
});