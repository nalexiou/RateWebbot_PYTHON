from threading import Thread
import sys
from Queue import Queue
import mechanize
from BeautifulSoup import BeautifulSoup
import threading
import time

# lock to serialize console output
lock = threading.Lock()

def do_work(item):
	contractid=item
	national = "http://nationalcar.com/"
	br = mechanize.Browser()
	br.set_handle_robots(False) # ignore robots
	br.open(national)
	response = br.response()
	for link in br.links():
		if link.url == "/home.do":
			response= br.follow_link(link)
			break
	br.select_form("m_logonForm")
	br.form['username']='username'
	br.form['password']='password'
	response = br.submit()
	br.open("https://www.somewebsite.com/home.do")
	br.select_form("rentalInfoForm")
	br.form['contractId']=contractid
	br.form['couponId']='somecouponcode'
	br.form['pickUpDropOffDetailForm.pickupStationName']='LAST01'
	br.form['pickUpDropOffDetailForm.pickupMonthYear']=['SEP-2014']
	br.form['pickUpDropOffDetailForm.pickupDay']=['22']
	br.form['pickUpDropOffDetailForm.pickupTime']=['8:00 AM']
	br.form['pickUpDropOffDetailForm.dropoffStationName']='LAST01'
	br.form['pickUpDropOffDetailForm.dropoffMonthYear']=['SEP-2014']
	br.form['pickUpDropOffDetailForm.dropoffDay']=['24']
	br.form['pickUpDropOffDetailForm.dropoffTime']=['8:00 AM']
	response = br.submit()
	html = BeautifulSoup(br.response().read())
	fo = open("rates.txt", "a")
	try:
		myrate = html.find("table", {"class": "total"}).find("div").text
		fo.write( contractid+" " + str(myrate) +"\n");

	except:
		fo.write( contractid+" Rate not found "+"\n");
		fo.close()
	
    # Make sure the whole print completes or threads can mix up output in one line.
	#with lock:
	#	print(threading.current_thread().name,item)

# The worker thread pulls an item from the queue and processes it

def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()

# Create the queue and thread pool.
q = Queue()
for i in range(20):
     t = threading.Thread(target=worker)
     t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
     t.start()

# stuff work items on the queue (in this case, just a number).
#start = time.perf_counter()
open('rates.txt', 'w').close()
with open('contractIDs.txt','r') as f:
	for line in f:
		for word in line.split():
			q.put(word)
q.join()       # block until all tasks are done

# "Work" took .1 seconds per task.
# 20 tasks serially would be 2 seconds.
# With 4 threads should be about .5 seconds (contrived because non-CPU intensive "work")
#print('time:',time.perf_counter() - start)