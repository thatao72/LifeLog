function displayData(weeklyData) {
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
    for (const weekStr in targetData.weeks) {
      const week = targetData.weeks[weekStr];
      tableData.push(week);
    }

    console.log("tableData", tableData)
    new Tabulator("#table-" + safeTargetDateId, {
      data: tableData,
      layout: "fitData",
      columns: [
        { title: "Week", field: "week" },
        { title: "Countdown", field: "countdown", sorter:"number" },
        {
          title: "Activity",
          field: "activity",
          formatter: function(cell) { // Custom formatter for activity bubbles
            let activityBubbles = "";
            const data = cell.getRow().getData();
            const bikeIndoorPower = data.bikeIndoorTime !== 0 ? data.bikeIndoorPower.toFixed(0)/data.bikeIndoorTime : 10000;
            if (data.runDistance > 0) activityBubbles += `<span class="bubble run">Run: ${data.runDistance.toFixed(2)}km, ${formatTime(data.runTime)}</span>`;
            if (data.bikeDistance > 0) activityBubbles += `<span class="bubble bike">Bike: ${data.bikeDistance.toFixed(2)}km, ${formatTime(data.bikeTime)}</span>`;
            if (data.bikeIndoorPower > 0) activityBubbles += `<span class="bubble bike">Bike Indoor: ${bikeIndoorPower.toFixed(0)}W, ${formatTime(data.bikeIndoorTime)}</span>`;
            if (data.swimDistance > 0) activityBubbles += `<span class="bubble swim">Swim: ${data.swimDistance.toFixed(2)}km, ${formatTime(data.swimTime)}</span>`;
            if (data.runDistancePlan > 0) activityBubbles += `<span class="bubble run-plan">Run: ${data.runDistancePlan.toFixed(2)}km</span>`;
            if (data.bikeDistancePlan > 0) activityBubbles += `<span class="bubble bike-plan">Bike: ${data.bikeDistancePlan.toFixed(2)}km</span>`;
            if (data.swimDistancePlan > 0) activityBubbles += `<span class="bubble swim-plan">Swim: ${data.swimDistancePlan.toFixed(2)}km</span>`;
            return activityBubbles;
          }
        },
        {
          title: "Total Activity",
          field: "totalActivity",
          formatter: "html", // Allow HTML
          formatter: function(cell) {
            const data = cell.getRow().getData();
            const actual = data.totalActivity || 0;
            const planned = data.totalActivityPlan || 0;

            if (actual === 0 && planned === 0) {
              return "";
            }

            const maxTotal = 1.2; // maxTotal to be 1.2 Ironman Equivalent
            const total = actual + planned;
            const actualWidth = total > 0 ? (actual / maxTotal) * 100 : 0;
            const plannedWidth = total > 0 ? (planned / maxTotal) * 100 : 0;
                
            return `
            <div class="bar-container">
              ${actual > 0 ? `<div class="bar actual-bar" style="width: ${actualWidth}%;"><span class="bar-label">${actual.toFixed(2)}</span></div>` : ""}
              ${planned > 0 ? `<div class="bar planned-bar" style="width: ${plannedWidth}%;">` : ""}
            </div>
          `;
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

  const h = Math.floor(seconds / 3600).toString();
  const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');

  return `${h}:${m}`;
}
