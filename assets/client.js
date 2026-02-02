activetab = null
const client = supabase.createClient('https://lfetrsnlliovdavlnejg.supabase.co', 'sb_publishable_H_1KsFUculPC6j78TcMAdg_0sXxxnTl')
var vertex = null
mapping = {}
idmap = {}
function newtabadd() {
	var page = document.createElement("div")
	var term = new Terminal({
	theme: {
		background: '#1a1c27', // base
		foreground: '#cdd6f4', // text
		cursor: '#f5e0dc',     // rosewater
		selection: 'rgba(245, 224, 220, 0.3)',

		// ANSI colors (normal)
		black: '#45475a',   // surface0
		red: '#f38ba8CC',     // red
		green: '#a6e3a1CC',   // green
		yellow: '#f9e2afCC',  // yellow
		blue: '#89b4faCC',    // blue
		magenta: '#f5c2e7CC', // magenta
		cyan: '#94e2d5CC',    // cyan
		white: '#bac2deCC',   // subtext1

		// Bright ANSI colors
		brightBlack: '#585b70', // surface1
		brightRed: '#f38ba8',
		brightGreen: '#a6e3a1',
		brightYellow: '#f9e2af',
		brightBlue: '#89b4fa',
		brightMagenta: '#f5c2e7',
		brightCyan: '#94e2d5',
		brightWhite: '#a6adc8'  // subtext0
	}
	});
	var tab = document.createElement("div")
	var img = document.createElement("img")
	var title = document.createElement("div")
	var close = document.createElement("button")
	var id = crypto.randomUUID()
	title.classList.add("title")
	close.classList.add("close")
	close.innerText = "X"
	title.innerText = "Tab"
	tab.classList.add("tab")
	img.src = "assets/terminal.svg"
	img.classList.add("icon")
	tab.append(img,title,close)
	var things = document.getElementsByClassName("active")

	for (let i = things.length - 1; i >= 0; i--) {
	  things[i].classList.remove("active")
	}

	tab.classList.add("active")
	document.getElementById("tabs2").appendChild(tab)
	page.classList.add("page","active")
	term.open(page)
	idmap[id] = term
	mapping[tab] = page
	term.onData(data => {
		var b64 = btoa(data)
		vertex.send({
			type: "broadcast",
			event: "action",
			payload: { "type": "write", "id": id, "text": b64 }, // send base64 to server.
		})
	});
	tab.onclick = function() {
	  	var things = document.getElementsByClassName("active")
		
	  	for (let i = things.length - 1; i >= 0; i--) {
			things[i].classList.remove("active")
	  	}
	  	tab.classList.add("active")
	  	page.classList.add("active")
		fitAddon.fit() // re-fit
		vertex.send({
			type: "broadcast",
			event: "action",
			payload: { "type": "resize", "id": id, "w": term.cols, "h": term.rows },
		})
	}
	close.onclick = function(e) {
	  	e.stopPropagation();
	  	term.dispose()
	  	tab.remove()
	  	page.remove()
	  	// no active tabs?
	  	if (document.getElementsByClassName("active").length == 0) {
			// last tab should be active.
			document.getElementById("tabs2").lastChild.classList.add("active")
			document.getElementById("views").lastChild.classList.add("active")
	  	}
		vertex.send({
			type: "broadcast",
			event: "action",
			payload: { "type": "delete", "id": id }, // deletion
		})
	}
	const fitAddon = new FitAddon.FitAddon();
	term.loadAddon(fitAddon);
	vertex.send({
		type: "broadcast",
		event: "action",
		payload: { "type": "new", "id": id }, // Client provides the id, not server.
	})
	prevrows = 0
	prevcols = 0
	document.getElementById("views").appendChild(page)
	window.addEventListener("resize",function() {
		fitAddon.fit()
		if (term.rows !== prevrows || term.cols !== prevcols) {
			vertex.send({
				type: "broadcast",
				event: "action",
				payload: { "type": "resize", "id": id, "w": term.cols, "h": term.rows }, // Resize
			})
		}
	})
	requestAnimationFrame(function() {
		fitAddon.fit()
		vertex.send({
			type: "broadcast",
			event: "action",
			payload: { "type": "resize", "id": id, "w": term.cols, "h": term.rows },
		})
	})
}

document.getElementById("connectbtn").onclick = function() {
	var code = document.getElementById("code").value
	if (code.length !== 8) {
		alert("Code too short.")
	} else if (!(/^\d+$/.test(code))) {
		alert("Code must be all numbers.")
	} else {
		document.getElementById("content1").classList.add("transition")
		document.getElementById("content2").classList.add("transition")
		const channel = client.channel(code)
		channel.on("broadcast", { event: "token" }, (payload) => {
			console.log(payload)
			vertex = client.channel(payload["payload"]["token"])
			// disconnect from first
			client.removeChannel(channel)
			vertex.on("broadcast", { event: "contentupd" }, (payload) => {
				id = payload["payload"]["id"]
				content = payload["payload"]["content"]
				idmap[id].write(content)
			}).subscribe((status) => {
				if (status === "SUBSCRIBED") {
					newtabadd()
					document.getElementById("connectmodalbg").style.display = "none"
					setInterval(function() {
						vertex.send({
							type: "broadcast",
							event: "beat",
							payload: { },
						})
					},3000)

				}
			})
		}).subscribe((status) => {
		if (status === "SUBSCRIBED") {
			channel.send({
				type: "broadcast",
				event: "join",
				payload: { },
			});
		}
		});
	}
	
}