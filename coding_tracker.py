import json
from time import strftime

import requests
from datetime import datetime


import win32gui
import win32process
import psutil

import time

from psutil import NoSuchProcess
from pynput import keyboard, mouse

from threading import Timer

from tkinter import messagebox



user = {"user_name" : "",
           "graph_id" : "",
           "token": "",
           "ide_to_track": ["pycharm64.exe","Code.exe","devenv.exe","idea64.exe"]}
try:
    with open("user_config.json", "r") as file:
        user = json.load(file)
except FileNotFoundError:
    with open ("user_config.json", "w") as file:
        json.dump(user, file, indent=4)





My_USER_NAME = user["user_name"]
MY_TOKEN = user["token"]
MY_GRAPH_ID = user["graph_id"]
PIXELA_ENDPOINT = "https://pixe.la/v1/users"
FLAG = True


WORKING_IDES = user["ide_to_track"]

HEADERS = {
        "X-USER-TOKEN": MY_TOKEN
    }




#_____________________________________Application Activity Finder________________________________
def active_application() ->tuple[str,int]:
    """Returns the current running process/window that we are working on OR we have open"""

    #retrieving HWND number
    hwnd = win32gui.GetForegroundWindow()
    #print(hwnd)

    #It returns the window  we are currently in
    #window_text = win32gui.GetWindowText(hwnd)
    #print(window_text)

    #Retrieves the identifier of the thread and process that created the specified window(HWND)
    #we only care about PID
    thread_id,pid = win32process.GetWindowThreadProcessId(hwnd)
    #print(thread_id,pid)

    #psutil.Process returns Useful info about given pid->(pid=21132, name='pycharm64.exe', status='running', started='16:39:27')
    try:
        process = psutil.Process(pid) # App failure detected (1) Unexpected 'no process found with the given pid'
    except Exception as e:
        print(e)
        process_name = "None"
    else:
        process_name = process.name()

    return process_name,pid
#_____________________________________________________________________________________________________


#___________________Mouse & Keyboard Activity Detection____________________________________________________
def keyboard_activity(key):
    global last_activity
    last_activity = time.monotonic()


def mouse_activity(x, y):
    global last_activity
    last_activity = time.monotonic()

#__________________________________________________________________________________________________________________

#____________________________________Account Related Methods For Pixela__________________________________________


def create_pixel(quantity:str):
    now = datetime.now()
    yyyymmdd = now.strftime("%Y%m%d")

    add_graph_pixel_endpoint = f"{PIXELA_ENDPOINT}/{My_USER_NAME}/graphs/{MY_GRAPH_ID}"

    pixe_config = {
        "date": yyyymmdd,
        "quantity": "2"
    }
    response = requests.post(url=add_graph_pixel_endpoint,json=pixe_config,headers=HEADERS)
    print(response.text)


def change_pixel_pixela(quantity:str,date:str|None):
    now = datetime.now()
    yyyymmdd = now.strftime("%Y%m%d")
    if date is not None:
        #my formated date is Y:M:D... Pixela accepts YMD
        yyyymmdd = date.replace(":","")
        print(yyyymmdd)

    change_pixel = {
        "quantity": quantity
    }
    change_pixel_endpoint = f"{PIXELA_ENDPOINT}/{My_USER_NAME}/graphs/{MY_GRAPH_ID}/{yyyymmdd}"
    #resent request insures that the data will be send if a problem occurs. Standar Pixela requests are rejected by 25%
    resent_request = Timer(10.0, change_pixel_pixela, (quantity, data))

    try:
        response = requests.put(url=change_pixel_endpoint,json=change_pixel,headers=HEADERS)
    except Exception as e:
        print(e)
        resent_request.start()
    else:
        print(response.text)
        resent_request.cancel()


def user_authentication():
    """Checks If the User with the specified Graph ID exists"""
    #Exception if Internet is off
    #when Pc is turned on, give it a 10 seconds wait to connect to the Internet
    time.sleep(10)
    try:
        pixela_check_name = requests.get(f"https://pixe.la/@{My_USER_NAME}").status_code
        pixela_check_graph_id = requests.get(
            f"https://pixe.la/v1/users/{My_USER_NAME}/graphs/{MY_GRAPH_ID}").status_code
    except requests.exceptions.RequestException:
        pixela_check_name = 0
        pixela_check_graph_id = 0

    if pixela_check_name == 0 or pixela_check_graph_id == 0:
        messagebox.showinfo(title="No internet ", message="Script Needs internet (when boot) to Authenticate User",
                            icon="error")
        return False
    elif pixela_check_name >= 400 or pixela_check_graph_id >= 400:
        messagebox.showinfo(title="User Authentication Error ",
                            message="Your Pixela name,graph-id or token is incorrect.\n If you dont have an account,create!",
                            icon="error")
        return False
    return True


#________________________________________________________________________________________

def day_changed(data:dict)->bool:
    """Checks if somehow day changed while you were still working. if Yes, saves all the data to the
     previous day (locally and to Pixela)."""
    date_today = datetime.now().strftime("%Y:%m:%d")
    if date_today != data["date"]:
        change_pixel_pixela(str(data["hours_coding"] / 3600), data["date"])
        #Log file is Updates every New day
        with open("log.txt", "a") as log:
            log.write(f"{data['date']} : {data['hours_coding']}\n")

        date_today = datetime.now().strftime("%Y:%m:%d")
        data["date"] = date_today
        data["hours_coding"] = 0.0
        return True
    return False

def write_to_file(data:dict):
    with open ("last_session.json", "w") as file:
        json.dump(data,file,indent=4)

def ide_closed(py_pid:int,data_save:dict):
    """This method checks if the Pycharm got closed while the .exe is running on the background.
    Checks if the pycharm's PID is changed. if it is, then that means that the program closed"""

    try:
        process = psutil.Process(py_pid)
    except NoSuchProcess:
        #that means Previous Pycharm process deleted/closed
        write_to_file(data_save)

#_________________________________MAIN_________________________________________________
keyboard_listener = keyboard.Listener(
    on_press=keyboard_activity
)

mouse_listener = mouse.Listener(
    on_move=mouse_activity,
    on_click=mouse_activity
)

keyboard_listener.start()
mouse_listener.start()

date_today = datetime.now().strftime("%Y:%m:%d")

data = {}

try:
    with open("last_session.json","r") as file:
        data = json.load(file)
except FileNotFoundError:
    with open("last_session.json" , "w") as file:

        info_to_save = {
            "date": date_today,
            "hours_coding": 0.0
        }

        json.dump(info_to_save,file,indent=4)

if not data:
    #data is empty
    data = {
        "date": date_today,
        "hours_coding": 0.0
    }


#Keep in mind that the counter is in seconds, for mins is runtime/60 for hours is runtime/3600
#The json file metric is in seconds, the name is 'codding_hours' because we need to parse it to Pixela as hours aka /3600


#Check's if For the current day there is prior info
if data["date"] == date_today and data["hours_coding"] != 0:
    #that means that for today's date there is a prior info
    run_time = data["hours_coding"]
else:
    run_time = 0


last_activity = time.monotonic()

set_idle_time = 600 #in seconds --> 10 min max idle
is_idle = 0
ide_pid = None

current_session = time.monotonic()
start_session = time.monotonic()

time_format = strftime("%H hrs: %M mins: %S sec",time.gmtime(data['hours_coding']))
print(f"Previous Data for today's day ({data['date']}) time codding: {time_format}")
# #If the Pixela user id is valid, start the script Functionality
is_user_valid = user_authentication()
try:
    while is_user_valid:
        ide_closed(ide_pid,data)
        if day_changed(data):
            write_to_file(data)


        if time.monotonic() - current_session >= 2700:
            #2700 seconds are 45 mins
            #That mean, time to Send the Data locally
            current_session = time.monotonic()
            #Update the Data in pixela
            change_pixel_pixela(str(run_time/3600),None)

            write_to_file(data)


        active_app,app_pid = active_application()
        if active_app in WORKING_IDES:
            ide_pid = app_pid
            idle_time = time.monotonic() - last_activity
            if idle_time > set_idle_time:
                print(f"You Have been Idle for more than {idle_time/60} Mins!!")
                is_idle = 1
                #print(f"current programming run time:{(run_time - is_idle * set_idle_time) / 60}")
            else:
                run_time = (run_time + 1) - is_idle * set_idle_time
                data["hours_coding"] = run_time
                is_idle= 0

        time.sleep(1)

except KeyboardInterrupt:
    print("Your IDE Closed")
    time_format = strftime("%H hrs: %M mins: %S sec", time.gmtime(data['hours_coding']))
    current_time = strftime("%H hrs: %M mins: %S sec", time.gmtime(time.monotonic()-start_session))
    print(f"Total today's Runtime ->{time_format}, Current Runtime->{current_time}")
    write_to_file(data)
