import os
import time
import configparser

def backlight_target(AmbientBrightness, CurrentBacklight, config):

    CurrentBacklight = int(CurrentBacklight) #Convert backlight string to an int to work with

    Target = int(float(AmbientBrightness)*float(config[0])) #Backlight target aims for configurable proportion of ambient brightness
    
    if Target > CurrentBacklight:
        Increment = 1 
    elif Target < CurrentBacklight:
        Increment = -1
    else:
        Increment = 0
    
    NewBrightness = CurrentBacklight + Increment

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

        RuntimeConfigs = [BrightnessScaling,MinimumBrightness,PollingRate]
        return RuntimeConfigs
    except:
        print("Config file unavailable: creating new")
        
        config = configparser.ConfigParser()
        config['DEFAULT'] = {"brightness_scaling": "1",
                             "minimum_brightness": "30",
                             "polling_rate": "0.1"}
        with open("auto_brightness.conf", "w") as configfile:
            config.write(configfile)

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
quit
