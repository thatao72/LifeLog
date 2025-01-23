function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Custom Menu')
    .addItem('Open Weekly Summary', 'openWeeklySummary')
    .addItem('Open Weekly Charts', 'openWeeklyCharts')
    .addItem('Get Calendar Events', 'getCalendarEvents')
    .addToUi();
}

function getWebAppUrl() {
  return PropertiesService.getScriptProperties().getProperty('WEB_APP_URL');
}

function openWeeklySummary() {
  const webAppUrl = getWebAppUrl();
  if (webAppUrl) {
    const htmlOutput = HtmlService.createHtmlOutput('<script>window.open("' + webAppUrl + '");</script>');
    SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Weekly Summary');
  } else {
    SpreadsheetApp.getUi().alert('Web app URL not set in script properties.');
  }
}

function openWeeklyCharts() {
  const webAppUrl = getWebAppUrl() + '?page=charts';
  if (webAppUrl) {
    const htmlOutput = HtmlService.createHtmlOutput('<script>window.open("' + webAppUrl + '");</script>');
    SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Weekly Charts');
  } else {
    SpreadsheetApp.getUi().alert('Web app URL not set in script properties.');
  }
}

function getCalendarEvents() {
  // Get the active spreadsheet and sheet
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();

  // Get the last row with data in the date column (assuming column A)
  const lastRow = sheet.getLastRow();

  // Get today's date
  const today = new Date();

  // Clear the entire column (column 14) first
  sheet.getRange(2, 14, lastRow - 1, 1).clearContent(); 

  // Loop through each row with a date
  for (let i = 2; i <= lastRow; i++) {
    // Get the date from the cell
    const date = sheet.getRange(i, 1).getValue();

    // Check if the date is later than today
    if (date > today) {
      // Get all events for the date
      const events = CalendarApp.getDefaultCalendar().getEventsForDay(date);

      // Create a string to store event information
      let eventString = "";

      // Loop through each event and append to the string
      for (let j = 0; j < events.length; j++) {
        const event = events[j];
        const startTime = Utilities.formatDate(event.getStartTime(), Session.getScriptTimeZone(), "HH:mm");
        const endTime = Utilities.formatDate(event.getEndTime(), Session.getScriptTimeZone(), "HH:mm");
        eventString += startTime + " - " + endTime + " " + event.getTitle() + ", ";
      }

      // Remove the trailing comma if there are events
      if (eventString != "") {
        eventString = eventString.slice(0, -2); // Remove the last comma and space

        // Write the event string to the cell in column B only if there are events
        sheet.getRange(i, 14).setValue(eventString);
      }
    }
  }
}
