google.script.run
  .withSuccessHandler(displayData)
  .withFailureHandler(onFailure)
  .getWeeklyData();

function displayData(weeklyData) {
  console.log("displayData called!");
  window.addEventListener('DOMContentLoaded', function() {
    console.log("window load event");
    for (const targetDateStr in weeklyData) {
      console.log("Inside for loop");
      const safeTargetDateId = String(targetDateStr).replace(/\//g, '-');
      const targetData = weeklyData[targetDateStr];
      const tableData = [];
      for (const sundayStr in targetData.weeks) {
        const week = targetData.weeks[sundayStr];
        tableData.push(week.tableRow);
      }
      
      console.log("#table-" + safeTargetDateId);
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
  });
}

function onFailure(error) {
  console.error("Error from server:", error); // Log the error
  // Optionally display an error message to the user
  alert("An error occurred. Please check the console.");
}
