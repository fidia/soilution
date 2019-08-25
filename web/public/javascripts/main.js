// Initialize websocket connection
var socket = io.connect('lbdigi-1475976782.us-east-1.elb.amazonaws.com:3000');

// Katagori
var vSuhu = 0;
var vKelembapan = 0;
var vPH = 0;

// Rata-Rata Line Chart

var avgChart;
var avgChartData = [
    {
      values: [],      //representasi nilai titik x dan y
      key: 'Rata-Rata Suhu', //Nilai serinya di chart
      color: '#7cb342'
    }
    ];

nv.addGraph(function(){
    avgChart = nv.models.lineChart()
                  .margin({left: 50, right: 30})
                  .useInteractiveGuideline(true)
                  .showLegend(true)
                  .showYAxis(true)
                  .showXAxis(true);

    avgChart.xAxis
            .axisLabel('Time')
            .tickFormat(function(d){return d3.time.format('%H:%M:%S')(new Date(d));});

    avgChart.yAxis
            .axisLabel('Rata-Rata Suhu')
            .tickFormat(d3.format('.2f'));

    d3.select('#avgSuhu')
        .append('svg')
        .datum(avgChartData)
        .transition().duration(100)
        .call(avgChart);

    nv.utils.windowResize(function() { avgChart.update(); });
    return avgChart;
});

var maxValueChart;
var maxValueChartData = [
    {
      values: [],      //values - represents the array of {x,y} data points
      key: 'Rata-Rata Kelembapan', //key  - the name of the series.
      color: '#7cb342'  //color - optional: choose your own line color.
    }
    ];

nv.addGraph(function(){
    maxValueChart = nv.models.lineChart()
                  .margin({left: 50, right: 30})
                  .useInteractiveGuideline(true)
                  .showLegend(true)
                  .showYAxis(true)
                  .showXAxis(true);

    maxValueChart.xAxis
            .axisLabel('Time')
            .tickFormat(function(d){return d3.time.format('%H:%M:%S')(new Date(d));});

    maxValueChart.yAxis
            .axisLabel('Rata-Rata Kelembapan')
            .tickFormat(d3.format('.2f'));

    d3.select('#avgKelembapan')
        .append('svg')
        .datum(maxValueChartData)
        .transition().duration(100)
        .call(maxValueChart);

    nv.utils.windowResize(function() { maxValueChart.update(); });
    return maxValueChart;
});

var minValueChart;
var minValueChartData = [
    {
      values: [],      //values - represents the array of {x,y} data points
      key: 'Rata-Rata pH', //key  - the name of the series.
      color: '#7cb342'  //color - optional: choose your own line color.
    }
    ];

nv.addGraph(function(){
    minValueChart = nv.models.lineChart()
                  .margin({left: 50, right: 30})
                  .useInteractiveGuideline(true)
                  .showLegend(true)
                  .showYAxis(true)
                  .showXAxis(true);

    minValueChart.xAxis                                                                                                                                                                              
            .axisLabel('Time')
            .tickFormat(function(d){return d3.time.format('%H:%M:%S')(new Date(d));});

    minValueChart.yAxis
            .axisLabel('Rata-Rata pH')
            .tickFormat(d3.format('.2f'));

    d3.select('#avgPH')
        .append('svg')
        .datum(minValueChartData)
        .transition().duration(100)
        .call(minValueChart);

    nv.utils.windowResize(function() { minValueChart.update(); });
    return minValueChart;
});

//--------------------------------------Socket.io event handlers------------------------------------

// Rata-Rata Chart
socket.on('avgsuhu', function (data) {
        var msg = JSON.parse(data);
	avgChartData[0].values.push({x: new Date(msg[0]), y: Number(msg[1])});
  var su = Number(msg[1]);
  if (su <22) {vSuhu = 3;}
  else if (su < 24) {vSuhu = 2;}
  else if (su < 29) {vSuhu = 1;}
  else if (su < 32) {vSuhu =2;}
  else if (su > 32) {vSuhu =3;}
	if(avgChartData[0].values.length > 30) {
		avgChartData[0].values.shift();
	}
  avgChart.update();
});

socket.on('avgkelembapan', function (data) {
        var msg = JSON.parse(data);
	maxValueChartData[0].values.push({x: new Date(msg[0]), y: Number(msg[1])});
  var lembab = Number(msg[1]);
  if (lembab <30) {vKelembapan = 3;}
  else if (lembab < 33) {vKelembapan = 2;}
  else if (lembab < 90) {vKelembapan = 1;}
  else if (lembab > 90) {vKelembapan =3;}
	if(maxValueChartData[0].values.length > 30) {
		maxValueChartData[0].values.shift();
	}
  maxValueChart.update();
});

socket.on('avgpH', function (data) {
        var msg = JSON.parse(data);
	minValueChartData[0].values.push({x: new Date(msg[0]), y: Number(msg[1])});
  var pH = Number(msg[1]);
  if (pH <4) {vPH = 3;}
  else if (pH < 5) {vPH = 2;}
  else if (pH < 7) {vPH = 1;}
  else if (pH < 8) {vPH =2;}
  else if (pH > 8) {vPH =3;}
	if(minValueChartData[0].values.length > 30) {
		minValueChartData[0].values.shift();
	}
  minValueChart.update();
});

setInterval(function(){
    setKategori();
  }, 5000);

function setKategori(){
  var vKat = vSuhu + vKelembapan + vPH
  var temp
  if (vKat < 4) {temp = 'S1'} 
  else if (vKat < 7){temp ='S2'}
  else if (vKat < 10){temp ='S3'}
  document.getElementById("katagori").innerHTML = "Kategori = "+temp;
}
