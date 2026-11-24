import json

#nom du fichiers de pref global
_FILE = "sauve_parametre/preferences.json"

#valeur par defauts ou en cas de plantage (valeur usine en gros)
_defaults = {
    "font_size": 30,
    "font_name": "default",
    "marge":12,
    "last_book": None,
    "last_position": 0,
    "wifi_ssid": "",
    "wifi_pass": "",
    "ftp_user": "2EinkEbook",
    "ftp_pass": "MyBook",
    "orientation":90,
    "theme":"defaut",
    "police_sys":"HersheySansMed"
}

#version active qui est sauvegarder ensuite
_MyPrefs = {}

#on charge les infos dans data
def charge_prefs():
    global _MyPrefs
    try:
        with open(_FILE, "r") as f:
            stored = json.load(f)
        _MyPrefs = dict(_defaults)
        _MyPrefs.update(stored)
    except:
        _MyPrefs = dict(_defaults)


def sauve_prefs():
    #on sauvegarde a chaque changement par exemple
    with open(_FILE, "w") as f:
        json.dump(_MyPrefs, f)

def get_pref(key):
    #pour récupérer les infos a la fois de la valeurs actuel, mais aussi de la valeur usine si il y a un problème
    return _MyPrefs.get(key, _defaults.get(key))

def set_pref(key, value):
    #pour affecter un valeurs
    _MyPrefs[key] = value

def reset_defauts():
    #remise des paramètre usine
    global _MyPrefs
    _MyPrefs = dict(_defaults)
    sauve_prefs()

if __name__=="__main__":
    charge_prefs()
    print(get_pref("font_size"))
    sauve_prefs()
    set_pref("font_size",40)
    sauve_prefs()
    print(get_pref("font_size"))
    reset_defauts()
    print(get_pref("font_size"))