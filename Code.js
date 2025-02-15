function doGet(e) {
  let page = e.parameter.page;
  if (page === 'charts') {
    let template = HtmlService.createTemplateFromFile('charts');
    template.chartData = getWeeklyChartData();

    return template.evaluate()
        .setTitle('Weekly Charts')
        .setSandboxMode(HtmlService.SandboxMode.IFRAME);
  } else {
    let template = HtmlService.createTemplateFromFile('index');
    template.weeklyData = getWeeklyData();

    return template.evaluate()
        .setTitle('Weekly Summary')
        .setSandboxMode(HtmlService.SandboxMode.IFRAME);
  }
}

function getWeeklyData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Data');
  const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 13).getValues(); // Assuming header row

  const weeklyData = {};

  data.forEach(row => {
    const date = row[0];
    const targetDate = row[1];
    const countdown = row[2];
    const events = row[3] ? row[3].split(',').map(s => s.trim()) : [];
    const walk = row[4];
    const runDistance = row[5];
    const runTime = row[6];
    const bikeDistance = row[7];
    const bikeIndoorPower = row[8];
    const bikeTime = row[9];
    const swimDistance = row[10];
    const swimTime = row[11];
    const gym = row[12];

    if (!targetDate) return; // Skip rows without target date

    const targetDateStr = targetDate.toLocaleDateString();
    if (!weeklyData[targetDateStr]) {
      weeklyData[targetDateStr] = {
        eventName: events.find(e => e.includes("Triathlon")),
        weeks: {}
      };
    }

    const dayOfDate = date.getDay();
    const sunday = new Date(date.getTime() + (dayOfDate === 0 ?  0 : 7 - dayOfDate) * 24 * 60 * 60 * 1000);
    const monday = new Date(date.getTime() + (dayOfDate === 0 ?  -6 : 1 - dayOfDate) * 24 * 60 * 60 * 1000);
    const weekStr = `${monday.toLocaleDateString()} - ${sunday.toLocaleDateString()}`;
    if (!weeklyData[targetDateStr].weeks[weekStr]) {
      weeklyData[targetDateStr].weeks[weekStr] = {
        week: weekStr,
        countdown: countdown,
        runDistance: 0,
        runTime: 0,
        runDistancePlan: 0,
        bikeDistance: 0,
        bikeTime: 0,
        bikeIndoorPower: 0,
        bikeIndoorTime: 0,
        bikeDistancePlan: 0,
        swimDistance: 0,
        swimTime: 0,
        swimDistancePlan: 0,
        totalActivity: 0,
        totalActivityPlan: 0,
        events: []
      };
    }
 
    if (runDistance) {
      if (runTime) {
        weeklyData[targetDateStr].weeks[weekStr].runDistance += runDistance;
        weeklyData[targetDateStr].weeks[weekStr].runTime += timeToSeconds(runTime);
        weeklyData[targetDateStr].weeks[weekStr].totalActivity += runDistance / 40 / 3;
      } else {
        weeklyData[targetDateStr].weeks[weekStr].runDistancePlan += runDistance;
        weeklyData[targetDateStr].weeks[weekStr].totalActivityPlan += runDistance / 40 / 3;
      }
    }

    if (bikeDistance) {
      if (bikeTime) {
        weeklyData[targetDateStr].weeks[weekStr].bikeDistance += bikeDistance;
        weeklyData[targetDateStr].weeks[weekStr].bikeTime += timeToSeconds(bikeTime);
        weeklyData[targetDateStr].weeks[weekStr].totalActivity += bikeDistance / 180 / 3;
      } else {
        weeklyData[targetDateStr].weeks[weekStr].bikeDistancePlan += bikeDistance;
        weeklyData[targetDateStr].weeks[weekStr].totalActivityPlan += bikeDistance / 180 / 3;
      }
    }

    if (bikeIndoorPower) {
      if (bikeTime) {
        weeklyData[targetDateStr].weeks[weekStr].bikeIndoorPower += bikeIndoorPower;
        weeklyData[targetDateStr].weeks[weekStr].bikeIndoorTime += timeToSeconds(bikeTime);
        weeklyData[targetDateStr].weeks[weekStr].totalActivity += bikeIndoorPower * timeToSeconds(bikeTime) / 3600 * 40 / 120 / 180 / 3;
      }
    }

    if (swimDistance) {
      if (swimTime) {
        weeklyData[targetDateStr].weeks[weekStr].swimDistance += swimDistance;
        weeklyData[targetDateStr].weeks[weekStr].swimTime += timeToSeconds(swimTime);
        weeklyData[targetDateStr].weeks[weekStr].totalActivity += swimDistance / 4 / 3;
      } else {
        weeklyData[targetDateStr].weeks[weekStr].swimDistancePlan += swimDistance;
        weeklyData[targetDateStr].weeks[weekStr].totalActivityPlan += swimDistance / 4 / 3;
      }
    }

    const filteredEvents = events.filter(event => !event.includes("Triathlon"));
    filteredEvents.forEach(event => {
      if (weeklyData[targetDateStr].weeks[weekStr].events.indexOf(event) === -1) {
        weeklyData[targetDateStr].weeks[weekStr].events.push(event);
      }
    });
  });

  const jsonString = JSON.stringify(weeklyData);
  return jsonString;
}

function getWeeklyChartData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Data');
  const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 13).getValues(); // Assuming header row

  const fileId = PropertiesService.getScriptProperties().getProperty('HEALTH_CSV_FILE_ID');
  const csvFile = DriveApp.getFileById(fileId);
  const blob = csvFile.getBlob();
  const csvContent = blob.getDataAsString();
  const csvData = Utilities.parseCsv(csvContent);

  const healthDataByDate = {};
  for (let i = 1; i < csvData.length; i++) {
    const healthRow = csvData[i];
    const dateObj = new Date(healthRow[0]);
    const healthDate = dateObj.toLocaleDateString();
    healthDataByDate[healthDate] = {
      restingHeartRate: parseFloat(healthRow[1]),
      sleepScore: parseFloat(healthRow[2]),
      stress: parseFloat(healthRow[3]),
      bodyBatteryHigh: parseFloat(healthRow[4]),
      bodyBatteryLow: parseFloat(healthRow[5]),
      weight: parseFloat(healthRow[6]),
      activityTrainingLoad: parseFloat(healthRow[7])
    };
  }

  const today = new Date();
  const currentWeekEnding = getSunday(today);
  currentWeekEnding.setHours(0, 0, 0, 0);

  const weeksEndingOnTargetDate = [];
  const weeksEndingOnYearEnd = [];
  const weeklyHealthData = {};

  data.forEach(row => {
    const date = row[0];
    const dateStr = date.toLocaleDateString();
    const targetDate = row[1];
    const runDistance = row[5];
    const runTime = row[6];
    const bikeDistance = row[7];
    const bikeIndoorPower = row[8];
    const bikeTime = row[9];
    const swimDistance = row[10];
    const swimTime = row[11];

    if (!targetDate) return;

    const dayOfDate = date.getDay();
    const sunday = new Date(date.getTime() + (dayOfDate === 0 ? 0 : 7 - dayOfDate) * 24 * 60 * 60 * 1000);
    sunday.setHours(0, 0, 0, 0);

    if (sunday > currentWeekEnding) return;

    const monday = new Date(date.getTime() + (dayOfDate === 0 ? -6 : 1 - dayOfDate) * 24 * 60 * 60 * 1000);
    const weekStr = `${monday.toLocaleDateString()} - ${sunday.toLocaleDateString()}`;
    const targetDateStr = targetDate.toLocaleDateString();

    if (date.getDay() === 0 && sunday.toLocaleDateString() === targetDateStr) {
      weeksEndingOnTargetDate.push(weekStr);
    }

    const lastSundayOfYear = new Date(sunday.getFullYear(), 11, 31);
    lastSundayOfYear.setDate(31 - (lastSundayOfYear.getDay()));

    if (date.getDay() === 0 && sunday.toLocaleDateString() === lastSundayOfYear.toLocaleDateString()) {
      weeksEndingOnYearEnd.push(weekStr);
    }

    if (!weeklyHealthData[weekStr]) {
      weeklyHealthData[weekStr] = {
        restingHeartRates: [],
        sleepScores: [],
        stresses: [],
        bodyBatteryHighs: [],
        bodyBatteryLows: [],
        weights: [],
        averageRestingHeartRate: null,
        averageSleepScore: null,
        averageStress: null,
        averageBodyBatteryHigh: null,
        averageBodyBatteryLow: null,
        averageWeight: null,
        totalActivity: null,
        totalLoad: null,
        targetDateStr: targetDateStr
      };
    }

    (runTime && runDistance) && (weeklyHealthData[weekStr].totalActivity += runDistance / 40 / 3);
    (bikeTime && bikeDistance) && (weeklyHealthData[weekStr].totalActivity += bikeDistance / 180 / 3);
    (bikeTime && bikeIndoorPower) && (weeklyHealthData[weekStr].totalActivity += bikeIndoorPower * timeToSeconds(bikeTime) / 3600 * 40 / 120 / 180 / 3);
    (swimTime && swimDistance) && (weeklyHealthData[weekStr].totalActivity += swimDistance / 4 / 3);

    const healthDataForDate = healthDataByDate[dateStr];

    if (healthDataForDate) {
      (healthDataForDate.restingHeartRate) && weeklyHealthData[weekStr].restingHeartRates.push(healthDataForDate.restingHeartRate);
      (healthDataForDate.sleepScore) && weeklyHealthData[weekStr].sleepScores.push(healthDataForDate.sleepScore);
      (healthDataForDate.stress) && weeklyHealthData[weekStr].stresses.push(healthDataForDate.stress);
      (healthDataForDate.bodyBatteryHigh) && weeklyHealthData[weekStr].bodyBatteryHighs.push(healthDataForDate.bodyBatteryHigh);
      (healthDataForDate.bodyBatteryLow) && weeklyHealthData[weekStr].bodyBatteryLows.push(healthDataForDate.bodyBatteryLow);
      (healthDataForDate.weight) && weeklyHealthData[weekStr].weights.push(healthDataForDate.weight);
      (healthDataForDate.activityTrainingLoad) && (weeklyHealthData[weekStr].totalLoad += healthDataForDate.activityTrainingLoad / 1000);
    }
  });

  const annualAverages = {};
  const targetEventPeriodAverages = {};

  for (const weekStr in weeklyHealthData) {
    const weekData = weeklyHealthData[weekStr];

    weekData.averageRestingHeartRate = calculateAverage(weekData.restingHeartRates);
    weekData.averageSleepScore = calculateAverage(weekData.sleepScores);
    weekData.averageStress = calculateAverage(weekData.stresses);
    weekData.averageBodyBatteryHigh = calculateAverage(weekData.bodyBatteryHighs);
    weekData.averageBodyBatteryLow = calculateAverage(weekData.bodyBatteryLows);
    weekData.averageWeight = calculateAverage(weekData.weights);

    const year = new Date(weekStr.split(' - ')[1]).getFullYear();
    if (!annualAverages[year]) {
      annualAverages[year] = {
        restingHeartRates: [],
        sleepScores: [],
        stresses: [],
        totalActivities: [],
        totalLoads: []
      };
    }
    if(weekData.averageRestingHeartRate) annualAverages[year].restingHeartRates.push(weekData.averageRestingHeartRate);
    if(weekData.averageSleepScore) annualAverages[year].sleepScores.push(weekData.averageSleepScore);
    if(weekData.averageStress) annualAverages[year].stresses.push(weekData.averageStress);
    if(weekData.totalActivity) annualAverages[year].totalActivities.push(weekData.totalActivity);
    if(weekData.totalLoad) annualAverages[year].totalLoads.push(weekData.totalLoad);

    if (!targetEventPeriodAverages[weekData.targetDateStr]) {
      targetEventPeriodAverages[weekData.targetDateStr] = {
        restingHeartRates: [],
        sleepScores: [],
        stresses: [],
        totalActivities: [],
        totalLoads: []
      };
    }

    if(weekData.averageRestingHeartRate) targetEventPeriodAverages[weekData.targetDateStr].restingHeartRates.push(weekData.averageRestingHeartRate);
    if(weekData.averageSleepScore) targetEventPeriodAverages[weekData.targetDateStr].sleepScores.push(weekData.averageSleepScore);
    if(weekData.averageStress) targetEventPeriodAverages[weekData.targetDateStr].stresses.push(weekData.averageStress);
    if(weekData.totalActivity) targetEventPeriodAverages[weekData.targetDateStr].totalActivities.push(weekData.totalActivity);
    if(weekData.totalLoad) targetEventPeriodAverages[weekData.targetDateStr].totalLoads.push(weekData.totalLoad);
  }

  for (const year in annualAverages) {
    annualAverages[year] = {
      restingHeartRate: calculateAverage(annualAverages[year].restingHeartRates),
      sleepScore: calculateAverage(annualAverages[year].sleepScores),
      stress: calculateAverage(annualAverages[year].stresses),
      totalActivity: calculateAverage(annualAverages[year].totalActivities),
      totalLoad: calculateAverage(annualAverages[year].totalLoads)
    };
  }

  for (const targetDateStr in targetEventPeriodAverages) {
    targetEventPeriodAverages[targetDateStr] = {
      restingHeartRate: calculateAverage(targetEventPeriodAverages[targetDateStr].restingHeartRates),
      sleepScore: calculateAverage(targetEventPeriodAverages[targetDateStr].sleepScores),
      stress: calculateAverage(targetEventPeriodAverages[targetDateStr].stresses),
      totalActivity: calculateAverage(targetEventPeriodAverages[targetDateStr].totalActivities),
      totalLoad: calculateAverage(targetEventPeriodAverages[targetDateStr].totalLoads)
    };
  }

  const chartData = {
    labels: [],
    heartRates: [],
    sleepScores: [],
    stresses: [],
    bodyBatteryHighs: [],
    bodyBatteryLows: [],
    weights: [],
    totalActivities: [],
    totalLoads: [],
    heartRateStepLineData: [],
    sleepScoreStepLineData: [],
    stressStepLineData: [],
    totalActivitiesStepLineData: [],
    totalLoadsStepLineData: [],
    heartRateTargetEventPeriodLineData: [],
    sleepScoreTargetEventPeriodLineData: [],
    stressTargetEventPeriodLineData: [],
    totalActivitiesTargetEventPeriodLineData: [],
    totalLoadsTargetEventPeriodLineData: [],
    weeksEndingOnTargetDate: weeksEndingOnTargetDate,
    weeksEndingOnYearEnd: weeksEndingOnYearEnd
  };

  for (const weekStr in weeklyHealthData) {
    const weekData = weeklyHealthData[weekStr];

    chartData.labels.push(weekStr);
    chartData.heartRates.push(weekData.averageRestingHeartRate);
    chartData.sleepScores.push(weekData.averageSleepScore);
    chartData.stresses.push(weekData.averageStress);
    chartData.bodyBatteryHighs.push(weekData.averageBodyBatteryHigh);
    chartData.bodyBatteryLows.push(weekData.averageBodyBatteryLow);
    chartData.weights.push(weekData.averageWeight);
    chartData.totalActivities.push(weekData.totalActivity);
    chartData.totalLoads.push(weekData.totalLoad);

    const year = new Date(weekStr.split(' - ')[1]).getFullYear();
    chartData.heartRateStepLineData.push(annualAverages[year].restingHeartRate);
    chartData.sleepScoreStepLineData.push(annualAverages[year].sleepScore);
    chartData.stressStepLineData.push(annualAverages[year].stress);
    chartData.totalActivitiesStepLineData.push(annualAverages[year].totalActivity);
    chartData.totalLoadsStepLineData.push(annualAverages[year].totalLoad);

    chartData.heartRateTargetEventPeriodLineData.push(targetEventPeriodAverages[weekData.targetDateStr].restingHeartRate);
    chartData.sleepScoreTargetEventPeriodLineData.push(targetEventPeriodAverages[weekData.targetDateStr].sleepScore);
    chartData.stressTargetEventPeriodLineData.push(targetEventPeriodAverages[weekData.targetDateStr].stress);
    chartData.totalActivitiesTargetEventPeriodLineData.push(targetEventPeriodAverages[weekData.targetDateStr].totalActivity);
    chartData.totalLoadsTargetEventPeriodLineData.push(targetEventPeriodAverages[weekData.targetDateStr].totalLoad);
  }

  const jsonString = JSON.stringify(chartData);
  return jsonString;
}

function getSunday(d) {
  const date = new Date(d); // Create a copy!
  const day = date.getDay(); // 0 (Sunday) to 6 (Saturday)
  const diff = day === 0 ? 0 : 7 - day; // Corrected: Check if it's already Sunday
  const sunday = new Date(date);
  sunday.setDate(date.getDate() + diff);
  return sunday;
}

function parseDate (dateString) {
  const dateParts = dateString.split('/');
  if (dateParts.length === 3) {
    const month = parseInt(dateParts[0], 10) - 1;
    const day = parseInt(dateParts[1], 10);
    const year = parseInt(dateParts[2], 10);
    return new Date(year, month, day);
  } else {
    console.log("Invalid date format:", dateString);
    return null;
  }
}

function timeToSeconds(time) {
  if (!time) return 0;
  if (typeof time === 'number') return time * 86400;
  if (time instanceof Date) {
    return time.getHours() * 3600 + time.getMinutes() * 60 + time.getSeconds();
  }
  return 0;
}

function calculateAverage(arr) {
  if (arr.length === 0) return null;
  const validNumbers = arr.filter(Number.isFinite);
  if (validNumbers.length === 0) return null;
  const sum = validNumbers.reduce((a, b) => a + b, 0);
  return sum / validNumbers.length;
}
