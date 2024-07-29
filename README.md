## CS 361 Course Project
## Weather Application

### Sprint 1
### Main Program: 
#### GUI Manager (gui_manager.py)
### Microservices:
#### Forecast Service (forecast_service.py) | Frontend Manager (frontend_manager.py)

## Usage:

To use the program, first install all files in requirements.txt.

After dependencies are installed, run each of the following programs:
- gui_manager.py
- frontend_manager.py
- forecast_service.py

In addition, in order to actually use the Google Places (New) API, you must have a valid API Key.
I do not want to upload it to GitHub in case it's used maliciously, so I have attached it in the assignment submission at the end of the file.
Don't worry about using the key for normal use though, as I have 50k+ requests on my free trial.

To use the API key, please go into the file called GLOBALS.py, then paste the API key where it says 'INSERT_API_KEY'.



## Development:

I'm done with sprint 1! 

Remaining TODOs (not required for sprint 1): 
- transition to zmq
- transition to React
- fix search dropdown format
- Fix dropdown buttons being selectable when not focused
- switch main screen data when given day is selected
- add data input to widget popup
- add hourly forecast functionality


## Requirements:

Please see requirements.txt