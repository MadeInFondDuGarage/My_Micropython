#passage par une class pour simplifier la gestion et la lisibilité vers la partie web, mais aussi en mode autonome.

class myGestion:
    def __init__(self):
        #lancement de l'initialisation des ensemble
        from Servo import myServo
        from readtemp import ReadTemp
        self._Temp_Maison=ReadTemp(32) #temp de la maison
        self._Temp_Puit=ReadTemp(18) #temp du puit
        self._Temp_Ext=ReadTemp(27) #temp Exterieur
        self._Temp_Aspiration=ReadTemp(26) #temp de l'aspiration
        self._Temp_Soufflage=ReadTemp(25) #temp de soufflage
        
        self._Valeurs={'T_Maison':0,'T_Puit':0,'T_Exterieur':0,'T_Aspiration':0,'T_Soufflage':0,'Temp_Consigne_Maison':20,'Temp_Delta':2,'Auto':True,'Puit':True,'Bypass':True}

        self._Servo_Bypass_Puit=myServo(12) #pour le servo du bypass du pc vers l'Exterieur
        self._Servo_Echangeur=myServo(14) #pour le servo du bypass de l'échangeur
        self._Servo_Vitesse_DF=myServo(5) #pour le servo de la vitesse    
       
        #j'active par defaut le puit
        self.Puit(True)
        #j'active par défaut le bypass
        self.Bypass(True)
    
    
    def Gestion(self):
        #lecture des températures
        self._Valeurs['T_Maison']=self._Temp_Maison.Read()[0]
        self._Valeurs['T_Puit']=self._Temp_Puit.Read()[0]
        self._Valeurs['T_Exterieur']=self._Temp_Ext.Read()[0]
        self._Valeurs['T_Aspiration']=self._Temp_Aspiration.Read()[0]
        self._Valeurs['T_Soufflage']=self._Temp_Soufflage.Read()[0]

        if self._Valeurs['Auto']:
            if self._Valeurs['T_Maison']<(self._Valeurs['Temp_Consigne_Maison']-self._Valeurs['Temp_Delta']):  #si la maison est plus froide que la consigne je doit réchauffer
            #il faut que je prenne la t° la plus chaude a condition que cela soit plus petit que le maxi autoriser, a savoir la T° de consigne + Delta
                if self._Valeurs['T_Exterieur']>self._Valeurs['T_Puit']: #je regarde si l'Exterieur est plus chaud que le PC je prend forcement l'ext en priorité
                    self.Puit(False)    
                else: #sinon je prend directement le puit canadien
                    self.Puit(True) 

                if self._Valeurs['T_Aspiration']< self._Valeurs['T_Soufflage']: #si la temperature aspirer est plus faible que celle de l'exterieur
                    self.Bypass(True) #j'active le bypass
                else:
                    self.Bypass(False) #je désactive le bypass
                
            if self._Valeurs['T_Maison']>(self._Valeurs['Temp_Consigne_Maison']-self._Valeurs['Temp_Delta']): #si la Temperature de la maison est plus chaude que la consigne je doit efroidir
              #il faut que je prenne la t° la plus froide entre la t° ext et la t° du pc
                if self._Valeurs['T_Exterieur']>self._Valeurs['T_Puit'] :
                    self.Puit(True)    
                else: #sinon je prend directement le puit canadien
                    self.Puit(False)

                if self._Valeurs['T_Aspiration']<self._Valeurs['T_Soufflage']: #si la temperature aspirer est plus faible que celle de l'exterieur
                    self.Bypass(False) #je désactive le bypass
                else:
                    self.Bypass(True) #je active le bypass
            #je renvoie le dic des valeurs
            return self._Valeurs

    def Puit(self,Actif):
        if Actif:
            print("basculement du puit")
            self._Servo_Bypass_Puit.set_Angle(0)
        else:
            print("basculement surl'Exterieur")
            self._Servo_Bypass_Puit.set_Angle(180)
        self._Valeurs['Puit']=Actif
        
    def Bypass(self,Actif):
        if Actif:
            print("basculement du bypass")
            self._Servo_Echangeur.set_Angle(0)
        else:
            print("désactivation du bypass")
            self._Servo_Echangeur.set_Angle(180)
        self._Valeurs['Bypass']=Actif


if __name__='__main__':
    maDF=myGestion()
    Etat_DF=maDF.Gestion()
