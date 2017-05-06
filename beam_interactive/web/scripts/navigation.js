var ros = new ROSLIB.Ros();

ros.on('error', function(error) {
	console.log(error);
});

ros.on('connection', function() {
	console.log('Connection made!');
});

ros.on('close', function() {
	console.log('Connection closed.');
});

ros.connect('ws://localhost:9090');
function set(){
var goal = new ROSLIB.Topic({
	ros : ros,
	name : '/navigate',
	messageType : 'std_msgs/String'
});

var location = String(document.getElementById("txtName").value);
if ( location )
{
var txtOutput = document.getElementById("txtOutput");
txtOutput.value = "Okay! I will go to \"" + location+"\"";

var msg = new ROSLIB.Message({
	data : location
});
goal.publish(msg);
}

else
{
	alert("No input!");
}
}