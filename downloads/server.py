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
	import fcntl
	import struct
	import termios
	import signal
	import select
	import errno
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
		try:
			self.pty.write(bytes.decode("utf-8"))
		except:
			pass
	def read(self):
		try:
			return self.pty.read()
		except:
			pass # race condition
				 # race: hi
				 # hi: condition
				 # condition: cat
				 # cat: funnycat
				 # funicat: hi
				 # hi: stop it
				 # it: hey, we are getting commited to a github repository, shut it
				 # github: take this repo down
				 # repo:
class LinuxPty:  # Linux PTY. i vibecoded it :3
    def __init__(self, pty=None):
        # ignore pty param, mimic api
        self.master_fd = None
        self.child_pid = None
        self.spawn('/bin/bash')

    def spawn(self, cmd):
        pid, master = os.forkpty()
        if pid == 0:
            # child
            os.execvp(cmd, [cmd])
        else:
            # parent
            self.master_fd = master
            self.child_pid = pid
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def resize(self, w, h):
        if self.master_fd is None:
            return
        # struct: rows, cols, xpix, ypix
        winsize = struct.pack("HHHH", h, w, 0, 0)
        try:
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
        except OSError:
            pass

    def dispose(self):
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None
        if self.child_pid:
            try:
                os.kill(self.child_pid, signal.SIGTERM)
            except OSError:
                pass
            try:
                os.waitpid(self.child_pid, 0)
            except OSError:
                pass
            self.child_pid = None

    def write(self, bytes_):
        if self.master_fd is None:
            return
        try:
            if isinstance(bytes_, bytes):
                os.write(self.master_fd, bytes_)
            else:
                os.write(self.master_fd, str(bytes_).encode('utf-8'))
        except OSError:
            pass

    def read(self):
        if self.master_fd is None:
            return b''
        try:
            r, _, _ = select.select([self.master_fd], [], [], 0)
            if r:
                return os.read(self.master_fd, 4096)
        except OSError as e:
            if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                pass
        return b''

def newpty():
	if sys.platform == "win32":
		return Winpty(PTY(80, 25))
	elif sys.platform == "linux":
		return LinuxPty()
	else:
		raise SystemError("Unknown OS, cant create a pty.")
loop = None
async def main():
	global loop
	loop = asyncio.get_running_loop()
	log.info("Hello, World!")
	log.info("Initializing supabase")
	supabase = await create_supabase()
	code = random.SystemRandom().randint(10000000,99999999)
	sch = supabase.channel(str(code))
	def handle_joins(e):
		terminals = {} # <id>: <pty>
		def reader(id, loop):
			nonlocal terminals
			while id in terminals:
				content = terminals[id].read() # might block, thats why we use a thread for this
				asyncio.run_coroutine_threadsafe(vch.send_broadcast(
					"contentupd",
					{"id": id,
	  				 "content": content},
				),loop)
				time.sleep(1/55) # 1/55th of a second delay so supabase is happy
		def handle(payload):
			global loop
			nonlocal terminals
			print(payload)
			if payload["payload"]["type"] == "new":
				terminals[payload["payload"]["id"]] = newpty()
				threading.Thread(target=reader,daemon=True,args=(payload["payload"]["id"],loop)).start()
			elif payload["payload"]["type"] == "resize":
				if payload["payload"]["id"] in terminals:
					terminals[payload["payload"]["id"]].resize(int(payload["payload"]["w"]),int(payload["payload"]["h"]))
			elif payload["payload"]["type"] == "delete":
				if payload["payload"]["id"] in terminals:
					terminals[payload["payload"]["id"]].dispose()
					del terminals[payload["payload"]["id"]]
			elif payload["payload"]["type"] == "write":
				if payload["payload"]["id"] in terminals:
					terminals[payload["payload"]["id"]].write(base64.b64decode(payload["payload"]["text"]))
				else:
					pass #??????????????????????????????????????????????
		def handle_beat(payload):
			nonlocal t
			# required function to know that the client LEFT.
			# cuz i cant rely on a "leave" broadcast.
			# typically, a beat is every 3s.
			t = time.time()
		def server_beat():
			nonlocal t
			# give the client a bit of time to actually start beating.
			# latency is not a mother anyway
			time.sleep(10)
			t = time.time()
			# server's local heartbeat system.
			# if no heartbeat was found in 17s, dispose all terminals
			while time.time() - t < 17:
				time.sleep(1)
			# uh oh! client left.
			handle_leave()
		def handle_leave(*e):
			nonlocal terminals
			for i in terminals.copy(): # dispose all terminals.
				terminals[i].dispose()
				del terminals[i]
			log.info("Client left.")
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
		t = time.time()
		asyncio.create_task(vch.on_presence_leave(callback=handle_leave).on_broadcast(event="beat",callback=handle_beat).on_broadcast(event="action", callback=handle).subscribe(onsub_vert))
		threading.Thread(target=server_beat).start()
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