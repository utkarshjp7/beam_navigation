		var ros = new ROSLIB.Ros();
		var triesLeft = 3;

		ros.on('error', function(error) {
			document.getElementById('connecting').style.display = 'none';
			document.getElementById('connected').style.display = 'none';
			document.getElementById('closed').style.display = 'none';
			document.getElementById('error').style.display = 'inline';
			console.log(error);
		});

		ros.on('connection', function() {
			console.log('Connection made!');
			document.getElementById('connecting').style.display = 'none';
			document.getElementById('error').style.display = 'none';
			document.getElementById('closed').style.display = 'none';
			document.getElementById('connected').style.display = 'inline';
		});

		ros.on('close', function() {
			console.log('Connection closed.');
			document.getElementById('connecting').style.display = 'none';
			document.getElementById('connected').style.display = 'none';
			document.getElementById('closed').style.display = 'inline';
		});

		ros.connect('ws://localhost:9090');

		var talker = new ROSLIB.Topic({
			ros : ros,
			name : '/talker',
			messageType : 'std_msgs/String'
		});
		var a = "ALRIGHT!";
		var msg = new ROSLIB.Message({
			data : a
		});
		



		var cmdVel = new ROSLIB.Topic({
			ros : ros,
			name : '/cmd_vel',
			messageType : 'geometry_msgs/Twist'
		});

		var twist = new ROSLIB.Message({
			linear : {
				x : 0.1,
				y : 0.2,
				z : 0.3
			},
			angular : {
				x : -0.1,
				y : -0.2,
				z : -0.3
			}
		});

		$(document).ready(function(){
			$('#MyButton').click(function(){
		cmdVel.publish(twist);
		talker.publish(msg);
			});
		});


		var listener = new ROSLIB.Topic({
			ros : ros,
			name : '/listener',
			messageType : 'std_msgs/String'
		});

		listener.subscribe(function(message) {
			console.log('Received message on ' + listener.name + ': ' + message.data);
			listener.unsubscribe();
		});