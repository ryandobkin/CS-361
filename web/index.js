// Checks if enter is pressed while search is highlighted
let inp_event = document.getElementById('input_search')
inp_event.addEventListener('keydown', (event) => {
    if (event.defaultPrevented) {
        return;
    }
    if (event.key === "Enter") {
        let value = inp_event.value;
        document.activeElement.blur();
        updateSearchQuery(value);
    } else if (event.key === "Escape") {
        document.activeElement.blur();
        eel.search_blur_fix();
    }
    else {
        return;
    }
    event.preventDefault();
}, true);

// Set Dropdown Opacity
eel.expose(setSearchDropdownOpacity);
function setSearchDropdownOpacity(opacity) {
    document.getElementById('dropdown_search').style.opacity = opacity;
}

// Update dropdown text fields
eel.expose(updateSearchAutocompleteDropdownFields);
function updateSearchAutocompleteDropdownFields(autocomplete_list) {
    document.getElementById('dropdown_text_1_search').innerText = autocomplete_list[0];
    document.getElementById('dropdown_text_2_search').innerText = autocomplete_list[1];
    document.getElementById('dropdown_text_3_search').innerText = autocomplete_list[2];
    document.getElementById('dropdown_text_4_search').innerText = autocomplete_list[3];
    document.getElementById('dropdown_text_5_search').innerText = autocomplete_list[4];
}

// Search Query
eel.expose(updateSearchQuery);
async function updateSearchQuery(query) {
    //eel.print_in_python("updateSearchQuery");
    eel.search_query(query)();
}

// Search Autocomplete Update
eel.expose(updateSearchAutocomplete);
function updateSearchAutocomplete() {
    return document.getElementById('input_search').value;
}

// Check if search in focus
eel.expose(updateSearchInFocus);
function updateSearchInFocus() {
    return document.activeElement === document.getElementById("input_search");
}

// Updates Location Display - Which is now the search bar kinda!
eel.expose(updateSearchLocationDisplay);
function updateSearchLocationDisplay(new_location) {
    //eel.print_in_python("updateLocationDisplay");
    document.getElementById('input_search').innerText = new_location;
}

// Updates Daily Rain Percentage %
eel.expose(updateDailyRainPercent);
function updateDailyRainPercent(daily_widget_name, rain_percent) {
    //eel.print_in_python("updateDailyRainPercent");
    document.getElementById(daily_widget_name).innerText = rain_percent;
}

// Updates Daily Wind Speed and Direction
eel.expose(updateDailyWind);
function updateDailyWind(daily_widget_name, new_wind_value) {
    //eel.print_in_python("updateDailyWind");
    document.getElementById(daily_widget_name).innerText = new_wind_value;
}

// Updates Daily Hi display
eel.expose(updateDailyHi);
function updateDailyHi(daily_widget_name, hi) {
    //eel.print_in_python("updateDailyHi");
    document.getElementById(daily_widget_name).innerText = hi;
}

// Updates Daily Lo display
eel.expose(updateDailyLo);
function updateDailyLo(daily_widget_name, lo) {
    //eel.print_in_python("updateDailyLo");
    document.getElementById(daily_widget_name).innerText = lo;
}

// Updates Daily Weather Condition Text
eel.expose(updateDailyWeatherConditionText);
function updateDailyWeatherConditionText(daily_widget_name, weather_condition) {
    //eel.print_in_python("updateDailyWeatherConditionText");
    document.getElementById(daily_widget_name).innerText = weather_condition;
}

// Updates Daily Weather Condition Graphic
eel.expose(updateDailyWeatherConditionGraphic);
function updateDailyWeatherConditionGraphic(daily_widget_name, graphic_directory, width, height, offsetx, offsety) {
    //eel.print_in_python("updateDailyWeatherConditionGraphic");
    let doc_element = document.getElementById(daily_widget_name);
    doc_element.src = graphic_directory;
    doc_element.width = width;
    doc_element.height = height;
    doc_element.style["left"] = offsetx;
    doc_element.style["top"] = offsety;
}

// Updates Daily Date Display
eel.expose(updateDailyDate);
function updateDailyDate(daily_widget_name, date) {
    //eel.print_in_python("updateDailyDate");
    document.getElementById(daily_widget_name).innerText = date;
}

// Updates Hourly Widget Temp
eel.expose(updateHourlyWidgetTemp);
function updateHourlyWidgetTemp(hour, temp) {
    //eel.print_in_python("updateHourlyWidgetTemp");
    document.getElementById(hour).innerText = temp;
}

// Updates Hourly Widget Time
eel.expose(updateHourlyWidgetTime);
function updateHourlyWidgetTime(hour, time) {
    //eel.print_in_python("updateHourlyWidgetTime");
    document.getElementById(hour).innerText = time;
}

// Updates Hourly Widget Graphic
eel.expose(updateHourlyWidgetGraphic);
function updateHourlyWidgetGraphic(hourly_widget_name, graphic_directory, width, height, offsetx, offsety) {
    //eel.print_in_python("updateHourlyWidgetGraphic");
    let doc_element = document.getElementById(hourly_widget_name);
    doc_element.src = graphic_directory;
    doc_element.width = width;
    doc_element.height = height;
    doc_element.style["left"] = offsetx;
    doc_element.style["top"] = offsety;
}

// Updates Sun Widget Values
eel.expose(updateSunWidgetValues);
function updateSunWidgetValues(sunrise, sunset, dawn, dusk) {
    //eel.print_in_python("updateSunWidgetValues");
    document.getElementById("sunrise_value_sun").innerText = sunrise;
    document.getElementById("sunset_value_sun").innerText = sunset;
    document.getElementById("dawn_value_sun").innerText = dawn;
    document.getElementById("dusk_value_sun").innerText = dusk;
}

// Updates UV Widget Values
eel.expose(updateUVWidgetValues);
function updateUVWidgetValues(uv, status) {
    //eel.print_in_python("updateUVWidgetValues");
    document.getElementById("value_uv").innerText = uv;
    document.getElementById("status_uv").innerText = status;
}

// Updates Wind Widget Values
eel.expose(updateWindWidgetValues);
function updateWindWidgetValues(speed, status) {
    //eel.print_in_python("updateWindWidgetValues");
    document.getElementById("speed_wind").innerText = speed;
    document.getElementById("status_wind").innerText = status;
}

// Updates Humidity Widget Values
eel.expose(updateHumidityWidgetValues);
function updateHumidityWidgetValues(humidity, dew) {
    //eel.print_in_python("updateHumidityWidgetValues");
    document.getElementById("value_humidity").innerText = humidity;
    document.getElementById("dew_humidity").innerText = dew;
}

// Updates Pressure Widget Values
eel.expose(updatePressureWidgetValues);
function updatePressureWidgetValues(pressure) {
    //eel.print_in_python("updatePressureWidgetValues");
    document.getElementById("value_pressure").innerText = pressure;
}

// Updates Alert Widget Visibility
eel.expose(updateAlertWidgetVisibility);
function updateAlertWidgetVisibility(visible) {
    //eel.print_in_python("updateAlertWidgetVisibility");
    document.getElementById("widget_alert").style["opacity"] = visible;
}

// Updates Alert Widget Text Displays
eel.expose(updateAlertWidget);
function updateAlertWidget(head, body, source) {
    eel.print_in_python("updateAlertWidget");
    document.getElementById("header_alert").innerText = head;
    document.getElementById("body_alert").innerText = body;
    document.getElementById("source_alert").innerText = source;
}

// Updates Now Widget Values
eel.expose(updateNowWidget);
function updateNowWidget(new_temp, hilo, condition, new_feels_like, graphic_directory, width, height, offx, offy) {
    //eel.print_in_python("updateNowWidget");
    document.getElementById("feelslike_now").innerText = new_feels_like;
    document.getElementById("condition_text_now").innerText = condition;
    document.getElementById("hilo_now").innerText = hilo;
    document.getElementById("temp_now").innerText = new_temp;
    let doc_element = document.getElementById("condition_graphic_now");
    doc_element.src = graphic_directory;
    doc_element.width = width;
    doc_element.height = height;
    doc_element.style["left"] = offx;
    doc_element.style["top"] = offy;
}

