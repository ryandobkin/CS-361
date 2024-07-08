
// Calls python to update location_text with receive_search(input)
async function getDataFromPython(input) {
    document.getElementById('location_text').innerText = await eel.receive_search(input)();
}

// Checks if enter is pressed while search is highlighted
document.getElementById('search_input').addEventListener('keydown', (event) => {
    if (event.defaultPrevented) {
        return;
    }
    if (event.key === "Enter") {
         getDataFromPython(document.getElementById('search_input').value);
         getRainDataFromPython()
    } else {
        return;
    }
    event.preventDefault();
}, true);

// Updates rain % on day 0 when above is called
async function getRainDataFromPython() {
    document.getElementById('rain_percent_0').innerText = await eel.get_rain_percentage()();
}
