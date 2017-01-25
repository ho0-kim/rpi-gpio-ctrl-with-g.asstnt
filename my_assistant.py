from flask import Flask
from flask_assistant import Assistant, tell

import aniso8601
import threading, queue

import datetime

import logging

q = queue.Queue()

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
#logging.getLogger("flask_assistant").setLevel(logging.DEBUG)

class thread_time_check(threading.Thread):
	def run(self):
		schedule = datetime.time()
		self.flag = False

		while True:
			now = datetime.datetime.now()

			try:
				schedule = q.get(True, 1)
				self.flag = True
				logging.debug("q.get() : got schedule time & flag : {}".format(self.flag))
			except queue.Empty as e:
				logging.debug("q.get() : didn't get schedule time & flag : {}".format(self.flag))
			if self.flag and now.hour == schedule.hour and now.minute == schedule.minute:
				logging.debug("######## time is done !!")
				self.flag = False

app = Flask(__name__)
assist = Assistant(app, '/')

def convert_time(time):
    try:
        return aniso8601.parse_time(time)
    except ValueError as e:
        return None


toaster_thread = thread_time_check()
toaster_thread.start()

@assist.action('my toaster')
def toaster(time, time_original):
    schedule_time = convert_time(time)
    q.put(schedule_time)
    logging.debug("############# q.put() : put schedule_time in queue")
    msg = "Okay, I'm gonna make a toast for you at {}".format(schedule_time)
    return tell(msg)

if __name__ == '__main__':
    app.run(debug=True)