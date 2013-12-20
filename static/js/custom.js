var pieChart = function(title, data, div, titleField, valueField){
    // PIE CHART
    var chart = new AmCharts.AmPieChart();
    chart.addTitle(title, 16);
    chart.dataProvider = data;
    chart.titleField = titleField;
    chart.valueField = valueField;
    chart.sequencedAnimation = true;
    chart.innerRadius = "30%";
    chart.startDuration = 1;
    // this makes the chart 3D
    chart.depth3D = 10;
    chart.angle = 25;

    // WRITE
    chart.write(div);
}