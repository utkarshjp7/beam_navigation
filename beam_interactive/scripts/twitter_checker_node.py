#!/usr/bin/env python
from Tkinter import *
from std_msgs.msg import *
import rospy,roslib

class Beam_Interactive:
	def __init__(self, master):
		self.master = master
		master.title("Twitter <Beam>")
		self.send = UInt32()
		self.count = 0
		self.response_pub = rospy.Publisher('/Tweet_Checker', UInt32, queue_size=1)
		self.message = "Should I tweet?"
		self.label_text = StringVar()
		self.label_text.set(self.message)
		self.label = Label(master, textvariable=self.label_text)
		self.tweet_button = Button(master, text="Tweet", command=self.send_Tweet)
		self.reset_button = Button(master, text="Quit", command=self.quit)
		self.label.grid(row=0, column=0, columnspan=2, sticky=W+E)
		self.tweet_button.grid(row=2, column=0)
		self.reset_button.grid(row=2, column=1)

	def send_Tweet(self):
		self.send = 1
		self.count += 1
		self.response_pub.publish(self.send)
		if self.count == 1:
			suffix = False
		else:
			suffix = True
		if suffix:
			self.message = "Tweet Again? Already sent " + str(self.count) + " times"
		else:
			self.message = "Tweet Again? Already sent once"

		self.label_text.set(self.message)

	def quit(self):
		self.master.destroy()

if __name__ == '__main__':
	rospy.init_node("Twitter_Checker")
	root = Tk()
	my_gui = Beam_Interactive(root)
	root.mainloop()
