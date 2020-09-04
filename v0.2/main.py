import os
import time
import mido
from KATANA import KATANA

# Parametros iniciales

maxVolume=0x64
minVolume=0x32

def start1():
    
    msg = mido.read_syx_file('test.syx')
    list1 = [[] for x in range(len(msg))]
    
    for i in range(len(msg)):
        
        list1[i]= [ None for x in range(len(msg[i].data))] 
        for j in range(len(msg[i].data)):
            print
            list1[i][j]=hex(msg[i].data[j])
        print(list1[i])    
    
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
    katana=KATANA()
    print('Conexion funcional')

    # Iniciar conexión con el katana
    connectionState = 'Unplugged'    
    while connectionState=='Unplugged':
        x=katana.initConnection(input='KATANA 0', output='KATANA 1')
        if x==1:
            connectionState = 'plugged'
        else:
            print('NO se encuentra KATANA')
            time.sleep(5)

    first=katana.readData([0x60, 0x00, 0x03, 0x7C],[0x00,0x00,0x00,0x04])
    print('first:')
    print(first)
    second=katana.readData([0x60, 0x00, 0x04, 0x00],[0x00,0x00,0x00,0x07])
    print('second')
    print(second) 

    full=katana.readData([0x60, 0x00, 0x03, 0x7C],[0x00,0x00,0x00,0x0B]) 
    print('full:')
    print(full)        
    
if __name__ == '__main__':
    start()
    