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

    const tableData = [];
    for (const sundayStr in targetData.weeks) {
      const week = targetData.weeks[sundayStr];
      tableData.push(week.tableRow);
    }
    console.log("tableData", tableData)
    new Tabulator("#table-" + safeTargetDateId, {
      data: tableData.reverse(),
      columns: [
//        { title: "Sunday", field: "sunday", sorter:"date", formatter:"datetime", formatterParams:{outputFormat:"YYYY-MM-DD"} },
        { title: "Sunday", field: "sunday" },
        { title: "Countdown", field: "countdown", sorter:"number" },
        { title: "Activity", field: "activity", formatter: "html" },
        { title: "Events", field: "events", formatter: "html" }
      ],
    });
  }
}
