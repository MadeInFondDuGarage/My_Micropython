from phew import logging, template, server, access_point, dns, 
from phew.template import  render_template
from phew.server import redirect

import uasyncio


import gc
gc.threshold(50000) # setup garbage collection

DOMAIN = "MaDoubleFlux" # This is the address that is shown on the Captive Portal
MainWebPagePC="WebPage/index_pc.html"
MainWebPageSmartphone="WebPage/index_smartphone.html"
MainWebPage=MainWebPagePC

#la partie gestion des page web ou autre
@server.route('/', methods=['GET','POST'])
def index(request):
    print(request)
    try:
        if 'Mobile' in request.headers['user-agent']:
            MainWebPage=MainWebPageSmartphone
        else:
            MainWebPage=MainWebPagePC
    except:
        return "ok",200
    #return render_template(MainWebPage, T_Maison= f" {Etat_DF['T_Maison']}", T_Ext=f" {Etat_DF['T_Exterieur']}")
    return render_template(MainWebPage)


@server.route("/wrong-host-redirect", methods=["GET"])
def wrong_host_redirect(request):
    body = "<!DOCTYPE html><head><meta http-equiv=\"refresh\" content=\"0;URL='http://" + DOMAIN + "'/ /></head>"
    return body


@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    """ Redirect to the Index Page """
    return render_template(MainWebPage)

@server.catchall()
def catch_all(request):
    """ Catch and redirect requests """
    if request.headers.get("host") != DOMAIN:
        return redirect("http://" + DOMAIN + "/wrong-host-redirect")


#partie pour l'acces web
# Set to Accesspoint mode
ap = access_point("MadeInFondduGarage")  # Change this to whatever Wifi SSID you wish
ip = ap.ifconfig()[0]                   # Grab the IP address and store it
dns.run_catchall(ip)                    # Catch all requests and reroute them
server.run()                            # Run the server
