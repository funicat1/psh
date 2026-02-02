logo = """
█████▄  ▄▄▄  ▄▄  ▄▄ ▄▄ ▄▄ ▄▄ ▄▄▄▄▄ ▄▄▄▄  ▄▄▄▄▄▄ ▄▄▄   
██▄▄█▀ ██▀██ ██  ▀███▀ ██▄██ ██▄▄  ██▄█▄   ██  ██▀██  
██     ▀███▀ ██▄▄▄ █    ▀█▀  ██▄▄▄ ██ ██   ██  ██▀██  
"""
import os,base64,threading
import asyncio,secrets,sys,random,time
from supabase import acreate_client, AsyncClient
import supabase as sb
import logging
from rich.logging import RichHandler


log = logging.getLogger("Polyverta")
log.setLevel(logging.INFO)
log.propagate = False

if not log.hasHandlers():
    handler = RichHandler()
    formatter = logging.Formatter("[Polyverta] %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

# silence
for lib in ["websockets", "httpx", "urllib3", "supabase"]:
    logging.getLogger(lib).setLevel(logging.WARNING)
colors = [
    "\033[91m",  # red
    "\033[93m",  # yellow
    "\033[92m",  # green
    "\033[96m",  # cyan
    "\033[94m",  # blue
    "\033[95m",  # magenta
]

reset = "\033[0m"

def rainbow(text):
    result = ""
    for i, char in enumerate(text):
        result += colors[i % len(colors)] + char
    result += reset
    return result

print(rainbow(logo))

url: str = "https://lfetrsnlliovdavlnejg.supabase.co"
key: str = "sb_publishable_H_1KsFUculPC6j78TcMAdg_0sXxxnTl" # publishable key.

async def create_supabase():
	supabase: AsyncClient = await acreate_client(url, key)
	return supabase

if sys.platform == "win32":
	from winpty import PTY
elif sys.platform == "linux":
	pass
else:
	raise SystemError("Unknown OS, Polyverta cant run.")

class Winpty: # Windows PTY.
	def __init__(self,pty: PTY):
		self.pty = pty
		self.pty.spawn(r'C:\windows\system32\cmd.exe')
	def resize(self,w,h):
		self.pty.set_size(w,h)
	def dispose(self):
		del self.pty
	def write(self,bytes):
		self.pty.write(bytes)
	def read(self):
		return self.pty.read()
		

def newpty():
	if sys.platform == "win32":
		log.info("Running on win32 - using winpty to create a pty.")
		return Winpty(PTY(80, 25))
	elif sys.platform == "linux":
		log.info("Running on linux - using pty to create a pty.")
	else:
		raise SystemError("Unknown OS, cant create a pty.")

async def main():
	log.info("Hello, World!")
	log.info("Initializing supabase")
	supabase = await create_supabase()
	code = random.SystemRandom().randint(10000000,99999999)
	sch = supabase.channel(str(code))
	def handle_joins(e):
		terminals = {} # <id>: <pty>
		def reader(id):
			nonlocal terminals
			while id in terminals:
				content = terminals[id].read() # might block, thats why we use a thread for this
				asyncio.create_task(vch.send_broadcast(
					"contentupd",
					{"id": id,
	  				 "content": content}
				))
				time.sleep(1/50) # 1/50th of a second delay so supabase is happy
		def handle(payload):
			nonlocal terminals
			print(payload)
			if payload["payload"]["type"] == "new":
				terminals["payload"]["id"] = newpty()
				threading.Thread(reader,daemon=True,args=(terminals["payload"]["id"],)).start()
			elif payload["payload"]["type"] == "resize":
				for i in terminals:
					terminals[i].resize(int(payload["payload"]["w"]),int(payload["payload"]["h"]))
			elif payload["payload"]["type"] == "delete":
				if payload["payload"]["id"] in terminals:
					terminals[payload["payload"]["id"]].dispose()
					del terminals[payload["payload"]["id"]]
			elif payload["payload"]["type"] == "write":
				if payload["payload"]["id"] in terminals:
					terminals[payload["payload"]["id"]].write(base64.b64decode(payload["payload"]["text"]))
				else:
					pass #??????????????????????????????????????????????
		def handle_leave(key, current_presence, left_presence):
			nonlocal terminals
			for i in terminals: # dispose all terminals.
				terminals[i].dispose()
				del terminals[i]
		def onsub_vert(status, err):
			if status == "SUBSCRIBED":
				asyncio.create_task(sch.send_broadcast(
					"token",
					{"token": vertex}
				))
				log.info(f"Sent token")
		vertex = secrets.token_hex(24)
		log.info("A client just joined!")
		vch = supabase.channel(vertex)
		asyncio.create_task(vch.on_presence_leave(callback=handle_leave).on_broadcast(event="action", callback=handle).subscribe(onsub_vert))
	def onsub(status, err):
		if status == "SUBSCRIBED":
			log.info(f"Ready")
			log.info(f"Code: {code}")
	log.info("Creating server")
	await sch.on_broadcast(event="join", callback=handle_joins).subscribe(onsub)
	while True:
		try:	
			await asyncio.sleep(1)
		except KeyboardInterrupt:
			log.info("Exiting")
			await supabase.remove_all_channels()
			raise SystemExit()
asyncio.run(main())