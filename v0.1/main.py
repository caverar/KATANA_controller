#Librerias:

import mido
import KTNAcommands
import time
# Parametros e inicializacion

maxVolume=0x64
minVolume=0x32


#changeChannel('CHA2')
#offBoost()

#msg = mido.Message('sysex', data=(initialTupleSysex + readDataSysex+[0x00,0x00,0x04,0x10]+[0x00,0x00,0x00,0x01]+checkSum([0x00,0x00,0x04,0x10],[0x00,0x00,0x00,0x01])))
#print(msg.bytes())


#print(msg)
#print(checkSum([0x60, 0x00, 0x12, 0x14], [0x1]))
#print(checkSum([0x00,0x00,0x04],[0x10]))

#print(readData([0x00,0x00,0x04,0x20],[0x00,0x00,0x00,0x01]))



# while x<10:
#     x=int(input("Ingrese ampli "))
#     print(x)
#     if x==0: ## DRY
#         KTNAcommands.setBoost('ON')
#         KTNAcommands.setFX('OFF')
#         KTNAcommands.setMOD('OFF')
#         KTNAcommands.setDELAY2('OFF')
#         KTNAcommands.setREVERB('OFF')
#         KTNAcommands.setVolumeBoost('OFF', minVolume, maxVolume)

#     elif x==1: ## ChOrus
#         KTNAcommands.setFX('ON')
#         KTNAcommands.setMOD('OFF')
#         KTNAcommands.setDELAY2('OFF')
#         KTNAcommands.setREVERB('OFF')
#         KTNAcommands.setVolumeBoost('OFF', minVolume, maxVolume)
#     elif x==2: ## Violin
#         KTNAcommands.setFX('OFF')
#         KTNAcommands.setMOD('ON')
#         KTNAcommands.setDELAY2('OFF')
#         KTNAcommands.setREVERB('OFF')
#         KTNAcommands.setVolumeBoost('OFF', minVolume, maxVolume)
#     elif x==3: ##solo
#         KTNAcommands.setFX('OFF')
#         KTNAcommands.setMOD('OFF')
#         KTNAcommands.setDELAY2('ON')
#         KTNAcommands.setREVERB('ON')
#         KTNAcommands.setVolumeBoost('ON', minVolume, maxVolume)




def start():
    KTNAcommands.initKTNAController()
    while(1):
        x=int(input("Select preset "))
        if x==0:
            KTNAcommands.loadPatch(0,0)

   
        elif x==1:
            KTNAcommands.loadPatch(0,1)

        elif x==2:
            KTNAcommands.loadPatch(0,2)

        elif x==3:
            KTNAcommands.loadPatch(0,3)

        elif x==4:
            KTNAcommands.loadPatch(1,0)
            l=KTNAcommands.readData([0x60,0x00,0x12,0x00],[0x00,0x00,0x00,0x7f])
            listHEX=[]
            x=0
            for i in l:
                listHEX.insert(x,hex(i))
                x=x+1
            print(listHEX)
            KTNAcommands.setData([0x60,0x00,0x12,0x00],[0x02])
        elif x==5:
            KTNAcommands.loadPatch(1,1)

        elif x==6:
            KTNAcommands.loadPatch(1,2)

        elif x==7:
            KTNAcommands.loadPatch(1,3)

        elif x==8:
            KTNAcommands.setChain(0,0)
        elif x==9:
            
            KTNAcommands.savePatch('CHA1',0,0)
            KTNAcommands.savePatch('CHA2',0,1)
            KTNAcommands.savePatch('CHB1',0,2)
            KTNAcommands.savePatch('CHB2',0,3)
            

    
if __name__ == '__main__':
    start()
    
