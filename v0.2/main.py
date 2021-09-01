#import os
import time
import mido
from Katana import Katana

# Parametros iniciales

maxVolume=0x64
minVolume=0x32

def start1():
    
    msg = mido.read_syx_file("test.syx")
    list1 = [[] for x in range(len(msg))]
    
    for i in range(len(msg)):
        
        list1[i]= [ None for x in range(len(msg[i].data))] 
        for j in range(len(msg[i].data)):
            #print(" ")
            list1[i][j]=hex(msg[i].data[j])
        print(list1[i])    
    
    # Instaciar
    katana=Katana()
    
    # Iniciar conexión con el katana
    connectionState = "Unplugged"    
    while connectionState=="Unplugged":        
        x=katana.initConnection()
        if x==1:
            connectionState = "plugged"
        else:
            print("NO se encuentra KATANA")
            time.sleep(5)
    
    #katana.saveChain(0, 0)
    
    # Test de funcionamiento
    while(1):
        x=int(input("Select preset "))
        if x==0:
            katana.loadPatch(0, 0, 0)   
        elif x==1:
            katana.loadPatch(0, 0, 1)
        elif x==2:
            katana.loadPatch(0, 0, 2)
        elif x==3:
            katana.loadPatch(0, 0, 3)
        elif x==4:
            katana.loadPatch(0, 1, 0)
        elif x==5:
            katana.loadPatch(0, 1, 1)
        elif x==6:
            katana.loadPatch(0, 1, 2)
        elif x==7:
            katana.loadPatch(0, 1, 3)
        elif x==8:
            katana.changeChannel(0)
        elif x==9:
            katana.changeChannel(1)

def start():
    # Cargar Presets
    katana=Katana() 
    
        
#    # Iniciar conexión con el katana
#    connectionState = "Unplugged"    
#    while connectionState=="Unplugged":
#        x=katana.initConnection(input="KATANA 0", output="KATANA 1")
#        if x==1:
#            print("Conexión funcional")
#            connectionState = "plugged"
#        else:
#            print("NO se encuentra KATANA")
#            time.sleep(5)
      
    
    # Test para ejecución de comandos

    while(1):

        #Imprimir comandos:
        #count=0
        #print(katana.currentPreset)
        for a,b in katana.currentPreset[str(katana.currentPresetPage)].items():
            print( a + ": " + b[0])
        command = input("Introduzca el numero de comando: ") 
        katana.executeCommand(command)

if __name__ == "__main__":
    start()
    