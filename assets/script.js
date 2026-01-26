state = 0
function change() {
    if (state == 0) {
        state = 1
        document.getElementById("pshellcardtitle").textContent = "Polyverta"
        document.getElementById("pshellcardtext").innerHTML = `Polyverta is the main server for Poly shell, and has a wide variety of options.<br><small class="text-body-secondary smoll">(and most importantly, is easy to setup!)</small>`
    } else {
        state = 0
        document.getElementById("pshellcardtitle").textContent = "Poly shell"
        document.getElementById("pshellcardtext").innerHTML = `Poly shell is SSH, but over the internet without a require for port forwarding.<br>`
    }
}