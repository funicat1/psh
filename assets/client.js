activetab = null

function newtabadd() {
    var page = document.createElement("div")
    var term = new Terminal();
    page.classList.add("page")
    term.open(page)
    term.write("guhh")
    document.getElementById("views").appendChild(page)
}
newtabadd()