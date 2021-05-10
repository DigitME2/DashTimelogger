var timer;
var start = new Date;
var job = new Object();
var setTime;

var jobID = '';
var minPrice = 10;
var maxPrice = 100000;
var minUnits = 1;
var maxUnits = 2000;

var successNum = 0;
var errorsNum = 0;

var localURL = 'http://192.168.174.129/'

$(document).ready(function () {
	$('#takeywords').val("");
	$('#fromDateInput, #toDateInput').val(new Date().toISOString().substr(0, 10))

	function genID() {
		var date = new Date().getTime();
		var id = Math.random(date).toString(36).substr(2, 10);
		date = new Date().getTime();
		var id2 = Math.random(date).toString(36).substr(2, 10);
		return id + id2;
	}

	$('#cOnOff').change(function () {
		if (this.checked) {
			start = new Date();
			timer = setInterval(interavl1s, 1000);
			var mini = parseInt($('#mins').val());
			var maxi = parseInt($('#maxs').val());
			setTime = Math.floor(Math.random() * (maxi - mini + 1)) + mini;
			$('#timerSetVal').text(setTime)
		} else {
			$('#timerVal').text('0' + " Seconds");
			clearInterval(timer);
		}
	});

	function resetTimer() {
		$('#cOnOff').click();
		$('#cOnOff').click();
	}

	function interavl1s() {
		$('#timerVal').text(parseInt((new Date() - start) / 1000) + " Seconds");
		var curSec = parseInt($('#timerVal').text());
		if (curSec >= parseInt(setTime)) {
			$('#bgen').click();
			resetTimer();
		}
	}

	$('#prodButton').click(function () {
		setRandomProduct();
		setRandomRouteName();
		loadRoute();
	})

	$('#bgen').click(function () {
		jobID = genID();
		setRandomProduct();
		setRandomRouteName();
		updateJobsTable();
		if(jQuery.isEmptyObject(job))
		{
			console.log('job empty');
		}
		else
		{
			sendJob(job);
		}
	})

	$('#textIPURL').on('input', function() {
		localURL = $(this).val()
		loadInitialRoutesData();
		loadProducts();
		setRandomProduct();
		setRandomRouteName();
		console.log('url: ', localURL);
	})

	localURL = $('#textIPURL').val();
	loadInitialRoutesData();
	loadProducts();
	setRandomProduct();
	setRandomRouteName();
})

function sendJob(jobObj)
{
	$.ajax({
		url: localURL + "timelogger/scripts/server/add_job.php",
		type:"GET",
		dataType:"text",
		data:{
			"request":"addJob",
			"jobId":jobObj.jobID,
			"expectedDuration":jobObj.expectedDuration,
			"description":jobObj.description,
			"dueDate":jobObj.dueDate,
			"routeName":jobObj.routeName,
			"totalChargeToCustomer":jobObj.jobTotalCharge,
			"unitCount":jobObj.unitCount,
			"productId":jobObj.productId,
			"priority":jobObj.priority
		},
		success:function(result){
				var res = $.parseJSON(result);
				console.log(res);
				if(res["status"] == "success"){
					successNum += 1;
				}
				else{
					errorsNum += 1;
				}
				updateStatus(successNum, errorsNum);
		},
		error: function(xhr, status, error){
			var errorMessage = xhr.status + ': ' + xhr.statusText
			alert('Error: ' + errorMessage);
		}
	});
}

function updateStatus(successNum, errorsNum)
{
	console.log('updateStatus')
	$('#bStatus').text(' Success: ' + successNum.toString() + ' Errors: ' + errorsNum.toString());
}

function getDateBetween(minDate, maxDate) {
	var date = new Date(+new Date(minDate) + Math.random() * (new Date(maxDate) - new Date(minDate)));
	var hour = 0 + Math.random() * (24 - 0) | 0;
	var minute = 0 + Math.random() * (60 - 0) | 0;
	date.setHours(hour);
	date.setMinutes(minute);
	return date;
}

function setRandomProduct() {
	var productOptions = $('#prodIdDropDown')[0];
	if (productOptions.length >= 2) {
		productOptionsIndex = Math.floor(Math.random() * (productOptions.length - 2 + 1)) + 1;
		routeName = productOptions[productOptionsIndex].value;
		$('#prodIdDropDown').val(routeName);
	}
}


function setRandomRouteName() {
	var routeOptions = $('#selectRoute')[0];
	if (routeOptions.length >= 2) {
		routeOptionIndex = Math.floor(Math.random() * (routeOptions.length - 2 + 1)) + 1;
		routeName = routeOptions[routeOptionIndex].value;
		$('#selectRoute').val(routeName);
		$('#textRouteName').val(routeName);
	}
}

function updateJobsTable() {
	
	job.jobID = jobID;
	job.description = jobID + ' description';
	job.routeName = $('#selectRoute').val();
	var randomDate = getDateBetween($('#fromDateInput').val(), $('#toDateInput').val());
	job.dueDate = randomDate.toISOString().slice(0,10);
	job.jobTotalCharge = Math.floor(Math.random() * (maxPrice - minPrice + 1)) + minPrice;
	job.unitCount = Math.floor(Math.random() * (maxUnits - minUnits + 1)) + minUnits;
	job.productId = $('#prodIdDropDown').val();
	job.priority = Math.floor(Math.random() * 5);

	var duration = (parseInt(randomDate.getHours()) * 3600) + (parseInt(randomDate.getMinutes()) * 60);	
	job.expectedDuration = duration;
	
	var objJSON = JSON.stringify(job);
	console.log('objJSON', objJSON);

	var label = [];
	var jobsPriorities = {};

	var dueDateMillis = new Date(job.dueDate).getTime();
	var nowMillis = Date.now();
	var daysDiff = Math.floor((dueDateMillis - nowMillis) / (1000 * 60 * 60 * 24));
	if (daysDiff < 0) {
		priority = 6
	} else if (daysDiff >= 0 && daysDiff <= 5) {
		priority = 5
	}
	jobsPriorities[priority] = (jobsPriorities[priority] || 0) + 1
	$('#jobsTableBody').append("<tr class=" + '"' + priorityToCss(priority) +  "\"><td>" + job.jobID + "</td><td>" + job.description + "</td><td>" + job.routeName + "</td><td>" + job.dueDate +
		"</td><td>" + job.jobTotalCharge + "</td><td>" + job.unitCount + "</td><td>" + job.productId +
		"</td><td>" + job.priority + "</td><td>" + job.expectedDuration + "</td></tr>")

}

function priorityToCss(priority) {
    priority = parseInt(priority, 10);
    switch (priority) {
		case 0:
			return 'priority_None'
        case 1:
            return 'priority_Low'
        case 2:
            return 'priority_Medium'
        case 3:
            return 'priority_High'
        case 4:
            return 'priority_Urgent'
        case 5:
            return 'row_late_risk'
        case 6:
            return 'row_overdue'
        default:
            return 'priority_Low'
    }
}

function loadProducts() {
	$.ajax({
		url: localURL + "timelogger/scripts/server/products.php",
		type: "GET",
		dataTtype: "text",
		data: {
			"request": "getProductsList"
		},

		success: function (result) {
			console.log(result);
			var resultJson = $.parseJSON(result);

			if (resultJson.status != "success") {
				alert(resultJson.result);
			} else {
				var productsList = resultJson["result"];
				$("#prodIdDropDown").empty();
				var placeHolder = $("<option>")
					.text("Select a Product...")
					.attr("value", "");
				$("#prodIdDropDown").append(placeHolder);
				for (var i = 0; i < productsList.length; i++) {
					var newOption = $("<option>")
						.text(productsList[i])
						.attr("value", productsList[i]);
					$("#prodIdDropDown").append(newOption);
				}
			}
		}
	});
}

function loadInitialRoutesData() {
	$.ajax({
		url: localURL + "timelogger/scripts/server/routes.php",
		type: "GET",
		dataTtype: "text",
		data: {
			"request": "getInitialData"
		},
		success: function (result) {
			console.log(result);
			var resultJson = $.parseJSON(result);

			if (resultJson.status != "success") {
				alert(resultJson.result);
			} else {
				var stationNames = resultJson.result.stationNames;
				$("#selectStationNames").empty();
				for (var i = 0; i < stationNames.length; i++) {
					var newOption = $("<option>")
						.text(stationNames[i])
						.attr("value", stationNames[i]);
					$("#selectStationNames").append(newOption);
				}

				var routeNames = resultJson.result.routeNames;
				$("#selectRoute").empty();
				var placeHolder = $("<option>")
					.text("Select a route...")
					.attr("value", "");
				$("#selectRoute").append(placeHolder);
				for (var i = 0; i < routeNames.length; i++) {
					var newOption = $("<option>")
						.text(routeNames[i])
						.attr("value", routeNames[i]);
					$("#selectRoute").append(newOption);
				}
			}
		}
	});
}

function loadRoute() {
	var routeName = $("#selectRoute").val();

	if (routeName != "noSelection") {
		$.ajax({
			url: localURL + "timelogger/scripts/server/routes.php",
			type: "GET",
			dataTtype: "text",
			data: {
				"request": "getRoute",
				"routeName": routeName
			},
			success: function (result) {
				console.log(result);
				var resultJson = $.parseJSON(result);

				if (resultJson.status != "success") {
					alert(resultJson.result);
				} else {
					$("#textRouteName").val(routeName);

					var routeParts = resultJson.result.split(",");

					$("#textRouteDesc").val("");
					for (var i = 0; i < routeParts.length - 1; i++) {
						$("#textRouteDesc").val(
							$("#textRouteDesc").val() + routeParts[i] + "\n"
						);
					}
					// add the last line with no trailing newline
					$("#textRouteDesc").val(
						$("#textRouteDesc").val() + routeParts[routeParts.length - 1]
					);
				}
			}
		});
	}
}