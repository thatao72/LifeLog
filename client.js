const weeklyData = google.script.run.withSuccessHandler(displayData).getWeeklyData();

function displayData(weeklyData) {
  window.addEventListener('DOMContentLoaded', function() {
    for (const targetDateStr in weeklyData) {
      const safeTargetDateId = String(targetDateStr).replace(/\//g, '-');
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
  });
}
