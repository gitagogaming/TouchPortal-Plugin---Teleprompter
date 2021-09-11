#!/usr/bin/env python3
'''
The Teleprompter
'''

### WORKS KINDA SORTA

### TO DO LIST 
## 1) Create an action which allows adjustment of 'scroll' speed, instead of global settings, for loop should look at this EVERY TIME IT LOOPS
##  
## 2) Get the lines pulled from file to be limited to 75 characters per line
##
## 3) see about getting everytihng to work in a webpage so we can display as an icon with a true scroll
## Does work with webpage capture plugin via html file, but needs to be smoother, need to modify that plugin.. 
## thinking should not use it at all, defeats purpose of my own plugin
##
## 4) Make it 





import sys
import time
import TouchPortalAPI as TP
import threading
import textwrap

from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

__version__ = "1.0"

PLUGIN_ID = "gitago.teleprompt.plugin"

TP_PLUGIN_INFO = {
    'sdk': 3,
    'version': int(float(__version__) * 1),  
    'name': "Teleprompter",
    'id': PLUGIN_ID,
    'configuration': {
        'colorDark': "#FF817E",
        'colorLight': "#676767"
    }
}

TP_PLUGIN_SETTINGS = {
    'Line Speed': {
        'name': "Line Speed",
        'type': "number",
        'default': "100",
        "minvalue": 100,
        "maxvalue": 10000,
        'readOnly': False,   
    },
    'Wrap Length': {
        'name': "Wrap Length",
        'type': "number",
        'default': "75",
        "minvalue": 10,
        "maxvalue": 1000,
        'readOnly': False, 
    }
}

TP_PLUGIN_CATEGORIES = {
    "teleprompt": {
        'id': PLUGIN_ID + ".teleprompt",
        'name': "Teleprompter",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/countdown_git.png"
    }
}

TP_PLUGIN_ACTIONS = {
    'action1': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".act.set",
        'name': "Start/Stop Teleprompter",
        'prefix': TP_PLUGIN_CATEGORIES['teleprompt']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "{$gitago.teleprompt.plugin.act.teleprompt$} the Teleprompter",
        'data': {
            'hours': {
                'category': "teleprompt",
                'id': PLUGIN_ID + ".act.teleprompt",
                'type': "choice",
                'label': "start/stop",
                'default': "Start",
                'valueChoices': ["Start", "Stop", "Resume"]
            }
        }
    },
    'action2': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".act.set_speed",
        'name': "Faster/Slower",
        'prefix': TP_PLUGIN_CATEGORIES['teleprompt']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Speed {$gitago.teleprompt.plugin.act.speed$} Teleprompter",
        'data': {
            'speed control': {
                'category': "teleprompt",
                'id': PLUGIN_ID + ".act.speed",
                'type': "choice",
                'label': "up/down speed",
                'default': "Up",
                'valueChoices': ["Up", "Down"]
            }
        }
    },
}

TP_PLUGIN_STATES = {
    'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.status",
        'type': "text",
        'desc': "Teleprompt - Status",
        'default': ""
    },
    'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.line1",
        'type': "text",
        'desc': "Teleprompt - Line 1",
        'default': ""
    },
    'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.line2",
        'type': "text",
        'desc': "Teleprompt - Line 2",
        'default': ""
    },
    'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.line3",
        'type': "text",
        'desc': "Teleprompt - Line 3",
        'default': ""
    },
    'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.line4",
        'type': "text",
        'desc': "Teleprompt - Line 4",
        'default': ""
    },
        'teleprompt status': {
        'category': "teleprompt",
        'id': PLUGIN_ID + ".state.teleprompt.line5",
        'type': "text",
        'desc': "Teleprompt - Line 5",
        'default': ""
    }
}
# Plugin Event(s).
TP_PLUGIN_EVENTS = {}

try:
    TPClient = TP.Client(
        pluginId=PLUGIN_ID,  
        sleepPeriod=0.05,  
        autoClose=True, 
        checkPluginId=True,  
        maxWorkers=4,  
        updateStatesOnBroadcast=False,  
    )
except Exception as e:
    sys.exit(f"Could not create TP Client, exiting. Error was:\n{repr(e)}")
def resetlines():
    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", "")
    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", "")
    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", "")
    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", "")
    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", "")



def set_line_speed(data, data2):
    global previous_linespeed
    global new_line_speed_ms
    new_line_speed_ms = data + data2
    milliseconds = new_line_speed_ms/1000
    print("Before Adding",previous_linespeed)
    previous_linespeed_ms = new_line_speed_ms
    print("The New Previous",previous_linespeed_ms)
    previous_linespeed = new_line_speed_ms

    ### now have to make it set speed, then switch on using 'miliseconds' as an arg


###   Functions here   ####
def switch(data):
    global total_lines_left
    global total_line_count
    global lines_read
    global milliseconds

    if data == "Start":
        #OPEN THE FILE, COUNT THE LINES, SET LINE SPEED, CONVERT LINESPEED TO MILISECONDS, CLOSE FILE AND DO FOR LOOP
        resetlines()
        file ="test_prompt.txt"
        #wrapped_length = 70
        file_contents = open(file, 'r').read() 
        wrapper = textwrap.TextWrapper(width=int(wrap_length))
        lines = wrapper.wrap(text=file_contents)
        lines_read = 0
        total_line_count = len(lines)
        total_lines_left = total_line_count


        line_speed_int = int(line_speed)
        milliseconds = line_speed_int/1000
        print("switch global:", switchglobal," |  LineSpeed:", line_speed, "- MS",milliseconds)
        #file_contents.close()

        for line in lines:
            if switchglobal == "Stop":
                print("OK ITS STOPPED")
                #resumed_line = lines[total_lines_left]
                #print("We shall resume at",total_lines_left, resumed_line)
                break

            
            elif switchglobal == "Start":
                start_from = total_line_count - total_lines_left
                print(total_lines_left, "Lines Left")
                print("")
                total_lines_left -=1
                print("Lines read",lines_read, "with MS of:", milliseconds)
                lines_read = lines_read +1
                print("Current Line",line)
                if lines_read == 1:
                    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from])
                if lines_read == 2:
                    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from])
                if lines_read == 3:
                    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from])
                if lines_read == 4:
                    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from])
                if lines_read == 5:
                    TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", lines[start_from])
                if lines_read > 5:
                        TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", lines[start_from])
                        TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from-1])
                        TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from-2])
                        TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-3])
                        TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-4])

                time.sleep(milliseconds)

    if data == "Resume":
        print("THE lines_read:", lines_read)
        f = open("test_prompt.txt")


        start_from = total_line_count - total_lines_left
        lines = f.readlines()
        #TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-5])
        #TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-4])
        #TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from-3])
        #TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from-2])
        #TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", lines[start_from-1])

        while total_lines_left > 0:
            print(total_lines_left)
            print(lines[start_from])
            if lines_read == 1:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from])
            if lines_read == 2:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-1])
            if lines_read == 3:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-1])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-2])
            if lines_read == 4:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from-1])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-2])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-3])
            if lines_read == 5:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", lines[start_from])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from-1])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from-2])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-3])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-4])
                
            if lines_read > 5:
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line5", lines[start_from])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line4", lines[start_from-1])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line3", lines[start_from-2])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line2", lines[start_from-3])
                TPClient.stateUpdate("gitago.teleprompt.plugin.state.state.teleprompt.line1", lines[start_from-4])

            time.sleep(milliseconds)
            total_lines_left -=1
            start_from +=1
            lines_read +=1
            if switchglobal == "Stop":
                print("OK ITS STOPPED")
                #resumed_line = lines[total_lines_left]
                #print("We shall resume at",total_lines_left, resumed_line)
                break
        else:
            print("its over")

    if data == "Stop":
        print("")


def update_states():
    print("")
    

# TP Client event handler callbacks

# Initial connection handler
@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    global line_speed
    global wrap_length
    global previous_linespeed
    line_speed = data['settings'][0]['Line Speed']
    wrap_length = data['settings'][1]['Wrap Length']
    previous_linespeed = 0
    print(data)
    resetlines()


# Settings handler
@TPClient.on(TP.TYPES.onSettingUpdate)
def onSettingUpdate(data):
    global line_speed
    global wrap_length
    line_speed = data['settings'][0]['Line Speed']
    wrap_length = data['settings'][1]['Wrap Length']
    print(data)
    print(line_speed)





# Action handler
@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    print(data)
    global switchglobal
    global line_speed_int
    line_speed_int = ""
    on_off = TPClient.getActionDataValue(data.get("data"), "gitago.teleprompt.plugin.act.teleprompt")
    speed_action = TPClient.getActionDataValue(data.get("data"), "gitago.teleprompt.plugin.act.speed")


    if data['actionId'] == "gitago.teleprompt.plugin.act.set":
            if on_off == "Start":
                global switchglobal
                #switch(on_off)
                th = threading.Thread(target=switch, args=("Start", ))
                switchglobal = "Start"
                th.start()

                
            elif on_off == "Stop":
                th = threading.Thread(target=switch, args=("Stop", ))
                switchglobal = "Stop"
                th.start()
                #switch(on_off)

            elif on_off == "Resume":
                switchglobal = "Resume"
                switch(on_off)




    if data['actionId'] == "gitago.teleprompt.plugin.act.set_speed":   
        if speed_action =="Up":
          set_line_speed(1000, previous_linespeed)
        if speed_action == "Down":
            print("Going Down")




# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    print(data)


# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(exc)


TPClient.connect()

