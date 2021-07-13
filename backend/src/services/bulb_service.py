import os, json, time
import requests
import services.ssm_service as ssm

# Move to dynamo
devices=[
    dict(name="shiny", id="103", on_color="setHue/33", off_color="setHue/99"),
    dict(name="home_office", id="74")
]



def turn_on(device_name: str):
    config = json.loads(ssm.get_ssm_parameter(os.environ["SECRET_PARAM"]) )
    print(config)
    device = next((stat for stat in devices if stat["name"] == device_name), None)
    API_ENDPOINT = "http://{}/apps/293/devices/{}/on?access_token={}".format(config.get("host"), device.get("id") ,config.get("token") )
    response = requests.get(url = API_ENDPOINT)
    print("RESPONSE STATUS ON: %s"%response.status_code)
    print(f'Reponse => {response.text}')

    if device.get("on_color", None) != None:
        set_color(device.get("id"), device.get("on_color"), config)
    set_level(device.get("id"), "85", config)

def turn_off(device_name: str):
    config = json.loads(ssm.get_ssm_parameter(os.environ["SECRET_PARAM"]) )
    device = next((stat for stat in devices if stat["name"] == device_name), None)
    if device.get("off_color", None) != None:
        set_color(device.get("id"), device.get("off_color"), config)
    else:        
        API_ENDPOINT = "http://{}/apps/293/devices/{}/off?access_token={}".format(config.get("host"), device.get("id") ,config.get("token") )
        response = requests.get(url = API_ENDPOINT)
        print("RESPONSE STATUS OFF: %s"%response.status_code) 

def set_level(device_id: str, level_val: str, config: dict):
    API_ENDPOINT = "http://{}/apps/293/devices/{}/setLevel/{}?access_token={}".format(config.get("host"), device_id , level_val, config.get("token") )
    response = requests.get(url = API_ENDPOINT)
    print("RESPONSE STATUS LEVEL: %s"%response.status_code)

def set_color(device_id: str, color_val: str, config: dict):
    API_ENDPOINT = "http://{}/apps/293/devices/{}/{}?access_token={}".format(config.get("host"), device_id , color_val, config.get("token") )

    response = requests.get(url = API_ENDPOINT)
    print("RESPONSE STATUS COLOR: %s"%response.status_code)    

 




# venv_linux/bin/python -m pip install requests
# venv_linux/bin/python bulb_service.py
if __name__ == "__main__":
    # /devices/1/setLevel/50
    os.environ["SECRET_PARAM"] = '/Connect/dev/local'
    turn_on("shiny")
    turn_on("home_office")
    time.sleep(3)
    turn_off("shiny")
    turn_off("home_office")
 