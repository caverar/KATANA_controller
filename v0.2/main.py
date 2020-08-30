import os
import time
import mido
from KATANA import *
# Parametros iniciales

maxVolume=0x64
minVolume=0x32

def start():
    # Instaciar
    katana=KATANA()
    
    # Iniciar conexión con el katana
    connectionState = 'Unplugged'    
    while connectionState=='Unplugged':        
        x=katana.initConnection()
        if x==1:
            connectionState = 'plugged'
        else:
            print('NO se encuentra KATANA')
            time.sleep(5)
    
    # Test de funcionamiento
    while(1):
        x=int(input("Select preset "))
        if x==0:
            katana.loadPatch(0,0)   
        elif x==1:
            katana.loadPatch(0,1)
        elif x==2:
            katana.loadPatch(0,2)
        elif x==3:
            katana.loadPatch(0,3)
        elif x==4:
            katana.loadPatch(1,0)
        elif x==5:
            katana.loadPatch(1,1)
        elif x==6:
            katana.loadPatch(1,2)
        elif x==7:
            katana.loadPatch(1,3)
        elif x==8:
            katana.setChain(0,0)

            
     
            
if __name__ == '__main__':
    start()
    