memory = {'total':'','available':'', 'percent_used':''}
LOG_FILE = 'matrix.log'
CPU = {'usage_percent':''}
process = {'active':'', 'gt_memory':'', 'top3memory':'', 'top3cpu':''}
system = {'uptime':'','memory':memory, 'CPU':CPU, 'process':process, 'USB': ''}
import json
import psutil
import logging
from pprint import pprint as pp
logging.basicConfig(filename=LOG_FILE, level = logging.DEBUG)

with open('config.json') as f:
    config = json.load(f)


while True:
	

	def memory_stats():
		mem = psutil.virtual_memory()
		memory['total'] = mem.total
		memory['available'] = mem.available
		memory['percent_used'] = mem.percent
		MEM_THRESHOLD = config["memory_stats"]["mem_consumption"] * 1024 * 1024
		if memory['available'] <= MEM_THRESHOLD:
			logging.warning('Memory available crosses threshold')

	def cpu_stats():
		cpu = psutil.cpu_percent(interval=0.2, percpu=False)
		CPU['usage_percent'] = str(cpu)
		if cpu >= config["cpu_stats"]["CPU_THRESHOLD"]:
			logging.warning('CPU usage:'+ str(cpu) +"%"+" crosses threshold")
		
	def process_stats():
		process['active'] = [(p.pid, p.info) for p in psutil.process_iter(attrs=['name', 'status']) if p.info['status'] == psutil.STATUS_RUNNING][-config["process_stats"]["limit"]:]

		process['gt_memory'] = [(p.pid, p.info['name'], p.info['memory_info'].rss) for p in psutil.process_iter(attrs=['name', 'memory_info']) if p.info['memory_info'].rss > config["process_stats"]["memory_gt"] * 1024 * 1024][-config["process_stats"]["limit"]:]

		process['top3memory'] = [(p.pid, p.info) for p in sorted(psutil.process_iter(attrs=['name', 'memory_percent']), key=lambda p: p.info['memory_percent'])][-config["process_stats"]["limit"]:]

		process['top3cpu'] = [(p.pid, p.info['name'], sum(p.info['cpu_times'])) for p in sorted(psutil.process_iter(attrs=['name', 'cpu_times']), key=lambda p: sum(p.info['cpu_times'][:2]))][-config["process_stats"]["limit"]:]	
		
	def sys_boot_time():
		if config["sys_boot_time"]["choose"]:
			import datetime
			system['uptime'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')

	def detect_usb_presence():
		import subprocess
		import os
		user = os.popen('whoami').read()
		rpistr = "ls /media/"+user+" > usbs.txt"
		usb = os.popen('ls /media/'+user).read()
		system['USB'] = usb.split('\n')
		p=subprocess.Popen(rpistr,shell=True, preexec_fn=os.setsid)

	memory_stats()
	cpu_stats()
	process_stats()
	sys_boot_time()
	detect_usb_presence()
	pp(system)
	time.sleep(5)
