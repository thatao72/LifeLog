function displayData(weeklyData) {
  console.log("displayData called!", weeklyData); // Confirm function call
  console.log("weeklyData", weeklyData)
  for (const targetDateStr in weeklyData) {
      console.log("targetDateStr", targetDateStr)
      const safeTargetDateId = targetDateStr.replace(/\//g, '-');
      const targetData = weeklyData[targetDateStr];
      const tableData = [];
      for (const sundayStr in targetData.weeks) {
        const week = targetData.weeks[sundayStr];
        tableData.push(week.tableRow);
      }

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
  console.error("Error from server:", error); // Log the error
  // Optionally display an error message to the user
  alert("An error occurred. Please check the console.");
}

// Set up the event listener *outside* of displayData
window.addEventListener('load', function() {
  console.log("window load event");
  google.script.run
    .withSuccessHandler(displayData)
    .withFailureHandler(onFailure)
    .getWeeklyData();
});
