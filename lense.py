memory = {"total":"","available":"", "percent_used":""}
LOG_FILE = "matrix.log"
CPU = ""
process = {"active":"", "gt_memory":"", "top_memory":"", "top_cpu":""}
system = {
		"uptime":"",
		"memory":memory,
		"CPU":CPU,
		"process":process,
		"USB": "",
		"house_id":"",
		"pi":"",
		"name":""
		}
import json, time
import psutil
import logging
import const
import requests
# from common import logger
from pprint import pprint as pp
logging.basicConfig(filename=LOG_FILE, level = logging.DEBUG)

with open("config.json") as f:
    config = json.load(f)

def house_info():
	system["house_id"] = config["house_id"]
	system["pi"] = config["pi_aviator"]
	system["name"] = config["name"]


while True:
	def memory_stats():
		mem = psutil.virtual_memory()
		memory["total"] = mem.total
		memory["available"] = mem.available
		memory["percent_used"] = mem.percent
		global MEM_THRESHOLD
		MEM_THRESHOLD = config["memory_stats"]["MEM_THRESHOLD_PER"]
		if memory["percent_used"] >= MEM_THRESHOLD:
			pass
			# logger.warning("Memory usage crosses threshold of "+str(MEM_THRESHOLD)+"%, Current usage = "+str(memory["percent_used"]))

	def cpu_stats():
		global cpu
		cpu = psutil.cpu_percent(interval=0.2, percpu=False)
		"""interval is configured to get cpu usage for an instance"""
		CPU = str(cpu)
		# if cpu >= config["cpu_stats"]["CPU_THRESHOLD"]:
		# 	logger.warning("CPU usage:"+ str(cpu) +"%"+" crosses threshold")
		
	def process_stats():
		process["active"] = [(p.pid, p.info) for p in psutil.process_iter(attrs=["name", "status"]) if p.info["status"] == psutil.STATUS_RUNNING][-config["process_stats"]["limit"]:]

		process["gt_memory"] = [(p.pid, p.info["name"], p.info["memory_info"].rss) for p in psutil.process_iter(attrs=["name", "memory_info"]) if p.info["memory_info"].rss > config["process_stats"]["memory_gt"] * 1024 * 1024][-config["process_stats"]["limit"]:]

		process["top_memory"] = [(p.pid, p.info) for p in sorted(psutil.process_iter(attrs=["name", "memory_percent"]), key=lambda p: p.info["memory_percent"])][-config["process_stats"]["limit"]:]

		process["top_cpu"] = [(p.pid, p.info["name"], sum(p.info["cpu_times"])) for p in sorted(psutil.process_iter(attrs=["name", "cpu_times"]), key=lambda p: sum(p.info["cpu_times"][:2]))][-config["process_stats"]["limit"]:]	
		
		# if memory["percent_used"] >= MEM_THRESHOLD and cpu >= config["cpu_stats"]["CPU_THRESHOLD"]:
		# 	logger.info(process)


	def sys_boot_time():
		if config["sys_boot_time"]["choose"]:
			import datetime
			system["uptime"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

	def detect_usb_presence():
		import subprocess
		import os
		user = os.popen("whoami").read()
		rpistr = "ls /media/"+user+" > usbs.txt"
		usb = os.popen("ls /media/"+user).read()
		system["USB"] = usb.split("\n")
		# logger.warning("New mounted drive in system are: "+str(system["USB"]))
		p=subprocess.Popen(rpistr,shell=True, preexec_fn=os.setsid)

	def update_lense_server():

		data = system
		response = requests.put(const.LENSE_END_POINT + '/update/' ,json=data)
		if response.status_code == 200:
			return json.loads(response.content.decode('utf-8'))
		else:
			return response.status_code
    

	house_info()
	memory_stats()
	cpu_stats()
	process_stats()
	sys_boot_time()
	detect_usb_presence()
	# print(update_lense_server())
	# response = json.dump(update_lense_server())
	print(system)

	for key,value in memory.iteritems():
		pp((key,value))
	time.sleep(5)
