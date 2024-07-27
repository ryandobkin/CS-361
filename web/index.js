// Checks if enter is pressed while search is highlighted
let inp_event = document.getElementById('input_search')
inp_event.addEventListener('keydown', (event) => {
    if (event.defaultPrevented) {
        return;
    }
    if (event.key === "Enter") {
        let value = inp_event.value;
        document.activeElement.blur();
        updateSearchQuery(value, "enter");
    } else if (event.key === "Escape") {
        document.activeElement.blur();
        eel.search_blur_fix();
    }
    else {
        return;
    }
    event.preventDefault();
}, true);

let isMouseHover = false;
let isHighlight = false;
let validClick = false;
let lastLocation = "";

// Event listeners for pop up tabs
// Current Condition Tab Controller
let cc_exp = document.getElementById('cc_tab_expanded');
let cc_col = document.getElementById('cc_tab_collapsed');

cc_col.onclick = function() {
    document.getElementById('hourly_group_id').className = 'hourly_group_top';
    document.getElementById('cc_tab_collapsed').className = 'cc_hidden';
    document.getElementById('cc_expanded_group').className = 'cc_visible';

    document.getElementById('alert_tab_collapsed').className = 'alert_visible';
    document.getElementById('alert_expanded_group').className = 'alert_hidden';
}

cc_exp.onclick = function() {
    document.getElementById('hourly_group_id').className = 'hourly_group_bot';
    document.getElementById('cc_tab_collapsed').className = 'cc_visible';
    document.getElementById('cc_expanded_group').className = 'cc_hidden';
}

// Alert Tab Controller
let alert_exp = document.getElementById('alert_tab_expanded');
let alert_col = document.getElementById('alert_tab_collapsed');

alert_col.onclick = function() {
    document.getElementById('alert_tab_collapsed').className = 'alert_hidden';
    document.getElementById('alert_expanded_group').className = 'alert_visible';

    document.getElementById('hourly_group_id').className = 'hourly_group_bot';
    document.getElementById('cc_tab_collapsed').className = 'cc_visible';
    document.getElementById('cc_expanded_group').className = 'cc_hidden';
}

alert_exp.onclick = function() {
    document.getElementById('alert_tab_collapsed').className = 'alert_visible';
    document.getElementById('alert_expanded_group').className = 'alert_hidden';
}

// Event listeners for daily selectors
let current_day = 'daily_0_bg';

document.getElementById('daily_0_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_0_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(0);
}
document.getElementById('daily_1_button').onclick = function() {
    console.log("daily1button")
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_1_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(1);
}
document.getElementById('daily_2_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_2_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(2);
}
document.getElementById('daily_3_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_3_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(3);
}
document.getElementById('daily_4_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_4_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(4);
}
document.getElementById('daily_5_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_5_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(5);
}
document.getElementById('daily_6_button').onclick = function() {
    document.getElementById(current_day).className = 'bg_daily_unselected';
    current_day = 'daily_6_bg';
    document.getElementById(current_day).className = 'bg_daily_selected';
    updateCurrentDay(6);
}

// This is probably so inefficient - sorry!
//Dropdown 1 highlight handler
let dt1 = document.getElementById('dropdown_text_1_search')
dt1.addEventListener("mouseenter", event => {
    if (dt1.innerText !== '') {
        if (dt1.innerText !== 'No Data Available') {
            validClick = true;
            dt1.style.backgroundColor = '#232535';
        } else {
            validClick = false;
        }
    } else {
        validClick = false
    }
}, true);
dt1.addEventListener("mouseleave", event => {
    dt1.style.backgroundColor = null;
}, true);
dt1.onclick = function() {
    if (validClick === true) {
        updateSearchQuery(dt1.innerText, "click");
    }
}

//Dropdown 2 highlight handler
let dt2 = document.getElementById('dropdown_text_2_search')
dt2.addEventListener("mouseenter", event => {
    if (dt2.innerText !== '') {
        if (dt2.innerText !== 'No Data Available') {
            validClick = true;
            dt2.style.backgroundColor = '#232535';
        } else {
            validClick = false;
        }
    } else {
        validClick = false
    }
}, true);
dt2.addEventListener("mouseleave", event => {
    dt2.style.backgroundColor = null;
}, true);
dt2.onclick = function() {
    if (validClick === true) {
        updateSearchQuery(dt2.innerText, "click");
    }
}

//Dropdown 3 highlight handler
let dt3 = document.getElementById('dropdown_text_3_search')
dt3.addEventListener("mouseenter", event => {
    if (dt3.innerText !== '') {
        if (dt3.innerText !== 'No Data Available') {
            validClick = true;
            dt3.style.backgroundColor = '#232535';
        } else {
            validClick = false;
        }
    } else {
        validClick = false
    }
}, true);
dt3.addEventListener("mouseleave", event => {
    isMouseHover = false;
    dt3.style.backgroundColor = null;
}, true);
dt3.onclick = function() {
    if (validClick === true) {
        updateSearchQuery(dt3.innerText, "click");
    }
}

//Dropdown 4 highlight handler
let dt4 = document.getElementById('dropdown_text_4_search')
dt4.addEventListener("mouseenter", event => {
    if (dt4.innerText !== '') {
        if (dt4.innerText !== 'No Data Available') {
            validClick = true;
            dt4.style.backgroundColor = '#232535';
        } else {
            validClick = false;
        }
    } else {
        validClick = false
    }
}, true);
dt4.addEventListener("mouseleave", event => {
    isMouseHover = false;
    dt4.style.backgroundColor = null;
}, true);
dt4.onclick = function() {
    if (validClick === true) {
        updateSearchQuery(dt4.innerText, "click");
    }
}

//Dropdown 5 highlight handler
let dt5 = document.getElementById('dropdown_text_5_search')
dt5.addEventListener("mouseenter", event => {
    if (dt5.innerText !== '') {
        if (dt5.innerText !== 'No Data Available') {
            validClick = true;
            dt5.style.backgroundColor = '#232535';
        } else {
            validClick = false;
        }
    } else {
        validClick = false
    }
}, true);
dt5.addEventListener("mouseleave", event => {
    isMouseHover = false;
    dt5.style.backgroundColor = null;
}, true);
dt5.onclick = function() {
    if (validClick === true) {
        updateSearchQuery(dt5.innerText, "click");
    }
}

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

// Search widget focus/blur event listeners
document.getElementById("input_search").addEventListener("focus", event => {
    document.getElementById('alert_tab_collapsed').className = 'alert_visible';
    document.getElementById('alert_expanded_group').className = 'alert_hidden';
    document.getElementById('hourly_group_id').className = 'hourly_group_bot';
    document.getElementById('cc_tab_collapsed').className = 'cc_visible';
    document.getElementById('cc_expanded_group').className = 'cc_hidden';
    console.log("input_search_onfocus_true");
    inp_event.value = '';
    isHighlight = true;
}, true);
document.getElementById("input_search").addEventListener("blur", event => {
    if (lastLocation !== "") {
        inp_event.value = lastLocation;
    } else {
        inp_event.value = 'Search for a City';
        isHighlight = false;
    }
}, false);

// Search Query
eel.expose(updateSearchQuery);
async function updateSearchQuery(query, type) {
    eel.print_in_python("updateSearchQuery");
    eel.search_query(query, type);
    lastLocation = query;
}

// Update current selected day for widgets
eel.expose(updateCurrentDay);
function updateCurrentDay(day) {
    eel.update_current_day(day);
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
    // if (isHighlight === true) {
    //     return true
    // } else {
    //     switch (isMouseHover) {
    //         case false:
    //             return false
    //         case 1:
    //
    //     }
    // }
    // return false
}

// Updates Location Display - Which is now the search bar kinda!
eel.expose(updateSearchLocationDisplay);
function updateSearchLocationDisplay(new_location) {
    //eel.print_in_python("updateLocationDisplay");
    document.getElementById('input_search').value = new_location;
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

// Updates Alert Widget Text Displays
eel.expose(updateAlertWidget);
function updateAlertWidget(event, headline, description, instruction, source) {
    //eel.print_in_python("updateAlertWidget");
    document.getElementById("alert_event").innerText = event;
    document.getElementById("alert_headline").innerText = headline;
    document.getElementById("alert_description").innerText = description;
    document.getElementById("alert_instruction").innerText = instruction;
    document.getElementById("alert_source").innerText = source;
}

// Updates Now Widget Values
eel.expose(updateNowWidget);
function updateNowWidget(new_temp, hilo, condition, new_feels_like) {
    //eel.print_in_python("updateNowWidget");
    document.getElementById("feelslike_now").innerText = new_feels_like;
    document.getElementById("condition_text_now").innerText = condition;
    document.getElementById("hilo_now").innerText = hilo;
    document.getElementById("temp_now").innerText = new_temp;
}

