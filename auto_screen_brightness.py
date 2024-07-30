import os
import time
import configparser

def backlight_target(AmbientBrightness, CurrentBacklight, config):
    global PollingRate
    global DisplayDriver

    CurrentBacklight = int(CurrentBacklight) #Convert backlight string to an int to work with

    Target = int(float(AmbientBrightness)*float(config[0])) #Backlight target aims for configurable proportion of ambient brightness
    
    if Target > CurrentBacklight:
        Increment = 1 
    elif Target < CurrentBacklight:
        Increment = -1
    else:
        Increment = 0

    NewBrightness = CurrentBacklight + Increment
    
    if check_on_AC_power() and config[3]=="true":
        with open("/sys/class/backlight/" + DisplayDriver + "/max_brightness","r") as MaximumBrightnessFile:
            NewBrightness = int(MaximumBrightnessFile.read())
            MaximumBrightnessFile.close()
            PollingRate = 1 
    else:
        if PollingRate == 1:
            NewBrightness = Target
        PollingRate = float(config[2])

    if NewBrightness < int(config[1]):
        return config[1]
    else:
        return str(NewBrightness)

def read_ambient_light():
    with open("/sys/bus/iio/devices/iio:device0/in_illuminance_raw", "r") as AmbientBrightnessFile:
        AmbientBrightness = AmbientBrightnessFile.read()
        AmbientBrightnessFile.close()
        
    return AmbientBrightness

def read_backlight_brightness():
    global DisplayDriver
    with open("/sys/class/backlight/" + DisplayDriver + "/actual_brightness", "r") as BacklightLevelFile:
        BacklightBrightness = BacklightLevelFile.read()
        BacklightLevelFile.close()
    return BacklightBrightness

def set_backlight_brightness(NewBrightness):
    global DisplayDriver
    os.system("echo " + str(NewBrightness) + " | sudo tee /sys/class/backlight/"+DisplayDriver+"/brightness > /dev/null")

def change_backlight(config):
    AmbientBrightness = read_ambient_light()
    BacklightBrightness = read_backlight_brightness()
    BacklightTarget = backlight_target(AmbientBrightness,BacklightBrightness,config)
    set_backlight_brightness(BacklightTarget)

def user_configs():
    try:
        config = configparser.ConfigParser()

        config.read("auto_brightness.conf")
        BrightnessScaling = config["DEFAULT"]["brightness_scaling"] 
        MinimumBrightness = config["DEFAULT"]["minimum_brightness"]
        PollingRate = config["DEFAULT"]["polling_rate"]
        MaxBrightnessOnAc = config["DEFAULT"]["max_brightness_on_ac"]

        RuntimeConfigs = [BrightnessScaling,MinimumBrightness,PollingRate,MaxBrightnessOnAc]
        return RuntimeConfigs
    except:
        print("Config file unavailable: creating new")
        
        config = configparser.ConfigParser()
        config['DEFAULT'] = {"brightness_scaling": "2",
                             "minimum_brightness": "30",
                             "polling_rate": "0.1",
                             "max_brightness_on_ac": "true"}
        with open("auto_brightness.conf", "w") as configfile:
            config.write(configfile)
        return user_configs()

def check_on_AC_power():
    with open("/sys/class/power_supply/ACAD/online","r") as OnAcCheck:
        if int(OnAcCheck.read()) == 1:
            OnAcCheck.close()
            return True
        else:
            OnAcCheck.close()
            return False

"""
Init
"""
DisplayDriver = os.popen("ls /sys/class/backlight").read().strip("\n")
config = user_configs()
print("Display Driver:",DisplayDriver,"\nUser Configs:\nBrightness Scaling:",config[0],"\nMinimum Brightness:",config[1],"\nPolling Rate:",config[2])
PollingRate = float(config[2])
"""
Main runtime loop
"""
print("Script Running")
while True:
    change_backlight(config)
    time.sleep(PollingRate)
