function displayData(weeklyData) {
  console.log("displayData called!");
  const tablesDiv = document.getElementById("tables"); // Get the tables container
  console.log("sample output", weeklyData["10/6/2024"].weeks["10/6/2024"].tableRow.sunday);
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

/*     const tableData = [];
    for (const sundayStr in targetData.weeks) {
      const week = targetData.weeks[sundayStr];
      tableData.push(week.tableRow);
    }
 */
    const tableData = [];
    for (const sundayStr in targetData.weeks) {
      const week = targetData.weeks[sundayStr];
      tableData.push(week);
    }

    console.log("tableData", tableData)
    new Tabulator("#table-" + safeTargetDateId, {
      data: tableData,
      columns: [
//        { title: "Sunday", field: "sunday", sorter:"date", formatter:"datetime", formatterParams:{outputFormat:"YYYY-MM-DD"} },
        { title: "Sunday", field: "sunday" },
        { title: "Countdown", field: "countdown", sorter:"number" },
        {
          title: "Activity",
          field: "activity",
          formatter: function(cell) { // Custom formatter for activity bubbles
            let activityBubbles = "";
            const data = cell.getRow().getData();
            if (data.runDistance > 0) activityBubbles += `<span class="bubble run">Run: ${data.runDistance.toFixed(2)}km, ${formatTime(data.runTime)}</span>`;
            if (data.bikeDistance > 0) activityBubbles += `<span class="bubble bike">Bike: ${data.bikeDistance.toFixed(2)}km, ${formatTime(data.bikeTime)}</span>`;
            if (data.bikeIndoorPower > 0) activityBubbles += `<span class="bubble bike">Bike Indoor: ${data.bikeIndoorPower.toFixed(0)}W, ${formatTime(data.bikeTime)}</span>`;
            if (data.swimDistance > 0) activityBubbles += `<span class="bubble swim">Swim: ${data.swimDistance.toFixed(2)}km, ${formatTime(data.swimTime)}</span>`;
            return activityBubbles;
          }
        },
        {
          title: "Events",
          field: "events",
          formatter: function(cell) { // Custom formatter for event bubbles
            let eventBubbles = "";
            const events = cell.getValue(); // Get the array of events
            if (Array.isArray(events)) {
              events.forEach(event => {
                eventBubbles += `<span class="bubble event">${event}</span>`;
              });
            }
            return eventBubbles;
          }
        }        
      ],
    });
  }
}

function formatTime(time) {
  const seconds = time;

  const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
  const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');

  return `${h}:${m}:${s}`;
}
