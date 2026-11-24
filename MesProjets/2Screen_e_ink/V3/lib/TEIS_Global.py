import utime
import sauve_parametre.TEIS_Preferences as Preferences
import TEIS_DateTimePc as DateTimePc
import TEIS_TouchScreen as Touch
import TEIS_Render as Render

def init():
    global theme,sys_font,font_name,font_size
    #init de tous les module en un seul appel dans le global
    #je charge les préférence utilisateurs
    Preferences.charge_prefs()
    
    sys_font=f"fonts/{Preferences.get_pref('police_sys')}"
    font_name=f"fonts/{Preferences.get_pref('font_name')}"
    font_size=Preferences.get_pref('font_size')
    theme=f"themes/{Preferences.get_pref('theme')}"

    
    Preferences.sauve_prefs()

    DateTimePc.init_bat() #lecture des batterie
    DateTimePc.init_rtc() #lancement de l'horloge RTC
    Touch.init_touch() #lancement du touchscreen
    Render.init_screen()#init de l'écran
    Render.set_font(sys_font)

    
def mesure_time(label=None):

    def decorator(func):
        name = label or func.__name__

        def wrapper(*args, **kwargs):
            start = utime.ticks_us()
            result = func(*args, **kwargs)
            end = utime.ticks_us()

            print("[TIME] {} -> {} ms".format(
                name,
                utime.ticks_diff(end, start)/1000
            ))

            return result

        return wrapper

    return decorator