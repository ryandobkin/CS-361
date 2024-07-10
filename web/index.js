
// Checks if enter is pressed while search is highlighted
document.getElementById('search_input').addEventListener('keydown', (event) => {
    if (event.defaultPrevented) {
        return;
    }
    if (event.key === "Enter") {
        let value = document.getElementById('search_input').value;
        updateSearchQuery(value)
        document.getElementById('search_input').value = '';
        document.activeElement.blur()
    } else if (event.key === "Escape") {
        document.activeElement.blur()
    }
    else {
        return;
    }
    event.preventDefault();
}, true);

// Search Query
eel.expose(updateSearchQuery);
function updateSearchQuery(query) {
    eel.print_in_python("updateSearchQuery")
    eel.search_query(query)
}

// Updates Location Display
eel.expose(updateLocationDisplay);
function updateLocationDisplay(new_location) {
    eel.print_in_python("updateLocationDisplay");
    document.getElementById('location_text').innerText = new_location;
}

// Updates Daily Rain Percentage %
eel.expose(updateDailyRainPercent)
function updateDailyRainPercent(daily_widget_name, rain_percent) {
    eel.print_in_python("updateDailyRainPercent");
    document.getElementById(daily_widget_name).innerText = rain_percent;
}

// Updates Daily Wind Speed and Direction
eel.expose(updateDailyWind)
function updateDailyWind(daily_widget_name, new_wind_value) {
    eel.print_in_python("updateDailyWind");
    document.getElementById(daily_widget_name).innerText = new_wind_value;
}

// Updates Daily Hi and Lo display
eel.expose(updateDailyHiLo)
function updateDailyHiLo(daily_widget_name, hilo) {
    eel.print_in_python("updateDailyHiLo");
    document.getElementById(daily_widget_name).innerText = hilo;
}

// Updates Daily Weather Condition Text
eel.expose(updateDailyWeatherConditionText)
function updateDailyWeatherConditionText(daily_widget_name, weather_condition) {
    eel.print_in_python("updateDailyWeatherConditionText");
    document.getElementById(daily_widget_name).innerText = weather_condition;
}

// Updates Daily Weather Condition Graphic
// daily_widget_name, new_graphic
eel.expose(updateDailyWeatherConditionGraphic)
function updateDailyWeatherConditionGraphic(daily_widget_name, graphic_directory, width, height, offsetx, offsety) {
    eel.print_in_python("updateDailyWeatherConditionGraphic");
    let doc_element = document.getElementById(daily_widget_name);
    doc_element.src = graphic_directory;
    doc_element.width = width;
    doc_element.height = height;
    doc_element.style["left"] = offsetx;
    doc_element.style["top"] = offsety;
    //createImageElement();
}





/*
// Create Image Element
async function createImageElement() {
    var canvas = document.getElementById("weather_condition_graphic_daily_0");
    var ctx = canvas.getContext('2d');
    var image = new Image();
    eel.print_in_python("createImageElement")
    image.width = 42;
    image.height = 56;
    image.onload = function() {
        ctx.drawImage(image, 0, 0);
    };
    image.src = dir;
}
*/

