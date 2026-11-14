from phew import logging, template, server, access_point, dns, 
from phew.template import  render_template
from phew.server import redirect
from machine import Pin,Timer
from Gestion import myGestion
import uasyncio


import gc
gc.threshold(50000) # setup garbage collection

DOMAIN = "MaDoubleFlux" # This is the address that is shown on the Captive Portal
MainWebPage="WebPage/index.html"

#led de la carte pour voir si tout est ok
led=Pin(2,Pin.OUT)
maDF=myGestion()
Etat_DF=maDF.Gestion()

#la partie gestion des page web ou autre
@server.route('/', methods=['GET','POST'])
def index(request):
    return render_template(MainWebPage, T_Maison= f" {Etat_DF['T_Maison']}", T_Ext=f" {Etat_DF['T_Exterieur']}")


@server.route("/wrong-host-redirect", methods=["GET"])
def wrong_host_redirect(request):
    body = "<!DOCTYPE html><head><meta http-equiv=\"refresh\" content=\"0;URL='http://" + DOMAIN + "'/ /></head>"
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


async def Gestion_DF():
    while True:
        led.on()
        global Etat_DF
        Etat_DF=maDF.Gestion()
        led.off()
        await uasyncio.sleep_ms(5000)


#mise en place de la tache pour la gestion de la double flux a faire toutes les  10 secondes en gros (pas besoin de plus)
loop=uasyncio.get_event_loop()
loop.create_task(Gestion_DF())

#partie pour l'acces web
# Set to Accesspoint mode
ap = access_point("MadeInFondduGarage")  # Change this to whatever Wifi SSID you wish
ip = ap.ifconfig()[0]                   # Grab the IP address and store it
dns.run_catchall(ip)                    # Catch all requests and reroute them
server.run()                            # Run the server
