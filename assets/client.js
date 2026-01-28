activetab = null
function printAllColors(term) {
  const write = s => term.write(s);
  const nl = () => write('\r\n');
  const pad = n => String(n).padStart(3, ' ');

  term.clear();

  // --- 16 basic colors (fg)
  write('\x1b[1m16 colors (foreground)\x1b[0m\r\n');
  for (let i = 0; i < 16; i++) {
    write(`\x1b[38;5;${i}m ${pad(i)} fg \x1b[0m `);
    if ((i + 1) % 4 === 0) nl();
  }
  nl();

  // --- 16 basic colors (bg)
  write('\x1b[1m16 colors (background)\x1b[0m\r\n');
  for (let i = 0; i < 16; i++) {
    write(`\x1b[48;5;${i}m\x1b[38;5;${i < 8 ? 15 : 0}m ${pad(i)} bg \x1b[0m `);
    if ((i + 1) % 4 === 0) nl();
  }
  nl();

  // --- 256 color palette
  write('\x1b[1m256-color palette\x1b[0m\r\n');
  for (let i = 0; i < 256; i++) {
    const fg = i < 16 ? 15 : (i % 2 ? 0 : 15);
    write(`\x1b[48;5;${i}m\x1b[38;5;${fg}m ${pad(i)} \x1b[0m`);
    if ((i + 1) % 16 === 0) nl();
    else write(' ');
  }
  nl();

  // --- truecolor gradient (rgb sweep)
  write('\x1b[1mtruecolor rgb gradient\x1b[0m\r\n');
  for (let r = 0; r <= 255; r += 32) {
    for (let g = 0; g <= 255; g += 32) {
      for (let b = 0; b <= 255; b += 32) {
        write(`\x1b[48;2;${r};${g};${b}m   \x1b[0m`);
      }
      write(' ');
    }
    nl();
  }

  nl();
  write('\x1b[3mdone.\x1b[0m\r\n');
}
mapping = {}
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
    mapping[tab] = page

    tab.onclick = function() {
      var things = document.getElementsByClassName("active")

      for (let i = things.length - 1; i >= 0; i--) {
        things[i].classList.remove("active")
      }
      tab.classList.add("active")
      page.classList.add("active")
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
    }
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    
    term.write("guhh")
    document.getElementById("views").appendChild(page)
    window.addEventListener("resize",function() {
        fitAddon.fit()
    })
    requestAnimationFrame(function() {
        fitAddon.fit()
    })
}
newtabadd()