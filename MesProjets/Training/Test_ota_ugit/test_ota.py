# CyberDog 
# Kevin McAleer
# September 2022

import json

from phew import logging, template, server, access_point, dns
from phew.template import  render_template
from phew.server import redirect
import gc
gc.threshold(50000) # setup garbage collection

DOMAIN = "test_ota" # This is the address that is shown on the Captive Portal

@server.route("/", methods=['GET','POST'])
def index(request):
    """ Render the Index page and respond to form requests """
    if request.method == 'GET':
        logging.debug("Get request")
        return render_template("index.html")
    if request.method == 'POST':
        data['OTA']['Actif']=True
        with open("Conf.json", "w") as write_file:
            json.dump(data, write_file)
        print('redémarrage pour mise a jour')
        import machine
        machine.reset()
        logging.debug(f'posted message: {text}')
        return render_template("index.html", text=text)

@server.route("/wrong-host-redirect", methods=["GET"])
def wrong_host_redirect(request):
  # if the client requested a resource at the wrong host then present 
  # a meta redirect so that the captive portal browser can be sent to the correct location
  body = "<!DOCTYPE html><head><meta http-equiv=\"refresh\" content=\"0;URL='http://" + DOMAIN + "'/ /></head>"
  logging.debug("body:",body)
  return body

@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    """ Redirect to the Index Page """
    return render_template("index.html")

@server.catchall()
def catch_all(request):
    """ Catch and redirect requests """
    if request.headers.get("host") != DOMAIN:
        return redirect("http://" + DOMAIN + "/wrong-host-redirect")
    
#test pour voir si le fichier de conf existe
def test_ota():
    data = {
        "OTA": {
            "Actif": False,
            "Version": "1.0"
        }
    }

    try:
        with open("Conf.json", "rb") as read_file:
            data=json.load(read_file)
    except:
        with open("Conf.json", "w") as write_file:
            json.dump(data, write_file)
#ici je détecte une demande d'ota au redémarrage je suis senser lancer la mise a jour
    if data['OTA']['Actif']==True:
        data['OTA']['Actif']=False
        with open("Conf.json", "w") as write_file:
            json.dump(data, write_file)
        print('redémarrage suite a ota')
        import machine
        machine.reset()
    else:
#ici j'ai redemarrer et tout est retour a la normal
        print(data)
        
# Set to Accesspoint mode
# ap = access_point("test_ota")  # Change this to whatever Wifi SSID you wish
# ip = ap.ifconfig()[0]                   # Grab the IP address and store it
# logging.info(f"starting DNS server on {ip}")
# dns.run_catchall(ip)                    # Catch all requests and reroute them
# server.run()                            # Run the server
# logging.info("Webserver Started")