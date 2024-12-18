console.log("client.js is loaded!");
const weeklyData = google.script.run.withSuccessHandler(displayData).getWeeklyData();
console.log("weeklyData is ready!");

function displayData(weeklyData) {
  window.addEventListener('DOMContentLoaded', function() {
    for (const targetDateStr in weeklyData) {
      const safeTargetDateId = String(targetDateStr).replace(/\//g, '-');
      const targetData = weeklyData[targetDateStr];
      const tableData = [];
      for (const sundayStr in targetData.weeks) {
        const week = targetData.weeks[sundayStr];
        console.log("week contents is taken " + week.tableRow)
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
