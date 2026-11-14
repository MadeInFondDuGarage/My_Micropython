#description du projet
#ce projet est làpour gérer mon ensemble puit canadien avec ma double flux ainsi que la récupération de chaleur du poele a bois

# le systeme, récupère 5 température
# la température extérieur
# la t° in du en provenance du pc vers la df
# la t° out en départ vers l'intérieur de la maison
# la t° in en provenance de la maison
# le t° out en sortie de la df vers l'extérieur
# 
# il y 3 sorties vers l'ensemble
# un pilotage tout ou rien de basculement entre le puit et l'extérieur
# un pilotage pour activer ou pas l'échangeur de la df
# un pilotage éventuel pour modifier la vitesse des ventilateurs et pouvoir éventuellement mettre des plage horaires pour surventiler

# Fonctionnement:
#     on passe sur le puit quand:
#         le t° extérieur est inférieur a une consigne de 12°c ou supérieur a la consigne intérieur 21°C
#         entre les 2 on est sur l'aspiration extérieur
#         
#     on bypass l'échangeur quand:
#         on a besoin de refroidir l'intérieur, donc lorsque la t° de l'extérieur est supérieur a la consigne intérieur
        
# Donc j'ai besoin de 2 consigne:
#     t° intérieur
#     t° de basculement
#     un mode automatique/manuel pour que les basculements
#     une vitesse de ventilateur

import Servo
servo_1=Servo.Servo(12)
servo_1.move(80)

