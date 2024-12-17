const weeklyData = google.script.run.withSuccessHandler(displayData).getWeeklyData();

function displayData(weeklyData) {
  window.addEventListener('load', function() {
    for (const targetDateStr in weeklyData) {
      const safeTargetDateId = String(targetDateStr).replace(/\//g, '-');
      const targetData = weeklyData[targetDateStr];
      const tableData = [];
      for (const sundayStr in targetData.weeks) {
        const week = targetData.weeks[sundayStr];

        let activityBubbles = "";
        if (week.runDistance > 0) activityBubbles += '<span class="bubble run">Run: ' + week.runDistance.toFixed(2) + 'km, ' + week.runTimeFormatted + '</span>';
        if (week.bikeDistance > 0) activityBubbles += '<span class="bubble bike">Bike: ' + week.bikeDistance.toFixed(2) + 'km, ' + week.bikeTimeFormatted + '</span>';
        if (week.bikeIndoorPower > 0) activityBubbles += '<span class="bubble bike">Bike Indoor: ' + week.bikeIndoorPower.toFixed(0) + 'W, ' + week.bikeTimeFormatted + '</span>';
        if (week.swimDistance > 0) activityBubbles += '<span class="bubble swim">Swim: ' + week.swimDistance.toFixed(2) + 'km, ' + week.swimTimeFormatted + '</span>';

        let eventBubbles = "";
        if (Array.isArray(week.events)) {
          week.events.forEach(event => {
            eventBubbles += '<span class="bubble event">' + event + '</span>';
          });
        }

        tableData.push({
          sunday: week.sunday, // Directly use the string
          countdown: week.countdown,
          activity: activityBubbles,
          events: eventBubbles
        });
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
