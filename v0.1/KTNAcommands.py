import os
import time
import mido

initialTupleSysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]
readDataSysex = [0x11]
setDataSysex = [0x12]
currentDirectory = os.getcwd()


def initKTNAController():
    global bankNames
    global numberOfBanks
    global patchesMatrix
    global chainMatrix
    global chainModeMatrix
    global katanaOUT
    global katanaIN
    global BankSizes 
    global currentChain 
    global currentBank
    global currentPach
    global currentChannel 
    global currentChainMode                                                             # 'Custom', '1', '2' '3'
    
    katanaOUT = mido.open_output('KATANA MIDI 1')
    katanaIN = mido.open_input('KATANA MIDI 1')    
    
    bankNames=os.listdir(currentDirectory+'/presets')                                   # Nombre de cada banco
    numberOfBanks=len(bankNames)                                                        # Numero de bancos
    patchesMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]              # Matriz que contiene .sys de cada banco
    chainMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]                # Matriz que contiene Sysex de la cadena custom de cada patch
    chainModeMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]            # Matriz que contiene el tipo de cadena de efectos, default o custom
    BankSizes=[0,0]                                                                     # numero de presets por banco 
    
    # Carga de presets, patches y chains
    for i in range(numberOfBanks):
        
        #Patches
        
        patchesMatrix[i][0]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/patchCHA1.syx')
        patchesMatrix[i][1]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/patchCHA2.syx') 
        patchesMatrix[i][2]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/patchCHB1.syx') 
        patchesMatrix[i][3]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/patchCHB2.syx')
        
        # Remplazo de cabecera de FxFloor por KATANA
        for j in range(len(patchesMatrix[i])):
            for k in range(len(patchesMatrix[i][j])):
                if k==18:
                    tempSysex= list(patchesMatrix[i][j][k].data)                    
                    del tempSysex[0:10]
                    chainModeMatrix[i][j]=tempSysex[0]
                    print(chainModeMatrix[i][j])
                    del tempSysex[0]                    
                    patchesMatrix[i][j][k]=mido.Message('sysex', data=initialTupleSysex + setDataSysex +[0x60, 0x00, 0x13, 0x00] +tempSysex)
                else: 
                    
                    tempSysex= list(patchesMatrix[i][j][k].data)                    
                    del tempSysex[0:6]
                    patchesMatrix[i][j][k]=mido.Message('sysex', data=initialTupleSysex + setDataSysex + tempSysex)
        # Chains
        chainMatrixTemp=[[None for x in range(4)] for y in range(numberOfBanks)]
        chainMatrixTemp[i][0]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/chainCHA1.syx')
        chainMatrixTemp[i][1]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/chainCHA2.syx') 
        chainMatrixTemp[i][2]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/chainCHB1.syx') 
        chainMatrixTemp[i][3]=mido.read_syx_file(currentDirectory+'/presets/'+bankNames[i]+'/patches/chainCHB2.syx')
        
        for j in range(len(patchesMatrix[i])):
            if chainMatrixTemp[i][j] != []:
                chainMatrix[i][j] = chainMatrixTemp[i][j][0]
                chainModeMatrix[i][j] = 'Custom'
                

        
        # Esto se debe leer de los temporales de la app-TODO
        
        currentChannel='CHA1'
        currentPach=0 
        currentBank=0                
        currentChainMode='1'
        currentChain='NA'        
        changeChannel(currentChannel)
        setChain(currentBank, currentPach)
    
       
       
# Parace ser necesario crear un objeto, o tal vez un diccionario para cada parche


def checkSum(address,data):
    vals=address+data
    accum = 0
    for val in vals:
        accum = (accum + val) & 0x7F
        cksum = (128 - accum) & 0x7F
    return [cksum]


def setData(address,data):

    msg = mido.Message('sysex', data=(initialTupleSysex + setDataSysex+ address +data +checkSum(address,data)))
    katanaOUT.send(msg)

def setRawData(data):

    msg = mido.Message('sysex', data=(initialTupleSysex + setDataSysex +data))
    katanaOUT.send(msg)

def readData(address, offset):

    msg = mido.Message('sysex', data=(initialTupleSysex + readDataSysex + address +offset+checkSum(address,offset)))
    katanaOUT.send(msg)
    msg=katanaIN.receive()
    value=msg.bytes()
    value.pop()
    value.pop()
    del value[0:12]
    return value

# Activacion y deactivacion de efectos


def readBoost():
    value=readData([0x60,0x00,0x00,0x30],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setBoost(state):
    if state=='ON':
        setData([0x60,0x00,0x00,0x30],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x00,0x30],[0x00])

def readMOD():
    value=readData([0x60,0x00,0x01,0x40],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setMOD(state):
    if state=='ON':
        setData([0x60,0x00,0x01,0x40],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x01,0x40],[0x00])

def readFX():
    value=readData([0x60,0x00,0x03,0x4C],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setFX(state):
    if state=='ON':
        setData([0x60,0x00,0x03,0x4C],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x03,0x4C],[0x00])

def readDELAY1():
    value=readData([0x60,0x00,0x05,0x60],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setDELAY1(state):
    if state=='ON':
        setData([0x60,0x00,0x05,0x60],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x05,0x60],[0x00])

def readREVERB():
    value=readData([0x60,0x00,0x06,0x10],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setREVERB(state):
    if state=='ON':
        setData([0x60,0x00,0x06,0x10],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x06,0x10],[0x00])


def readDELAY2():
    value=readData([0x60,0x00,0x10,0x4E],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return 'OFF'
    if value==[1]:
        return 'ON'

def setDELAY2(state):
    if state=='ON':
        setData([0x60,0x00,0x10,0x4E],[0x01])
    elif state=='OFF':
        setData([0x60,0x00,0x10,0x4E],[0x00])
        

# FUNCIONES CON AJUSTE DE PARAMETROS

def setVolumeBoost(state, minVolume, maxVolume):

    if state=='ON':
        setData([0x60,0x00,0x07,0x10],[maxVolume])
    elif state=='OFF':
        setData([0x60,0x00,0x07,0x10],[minVolume])

def setDELAY2Tempo(tempo):
    if tempo<0:
        tempo=0
    elif tempo>2000:
        tempo=2000
    setData([0x60,0x00,0x10,0x50], [tempo>>7,tempo%128])
    
# Funciones Avanzadas

def changeChannel(channel):
    if channel=='PANEL':
        data=4
    elif channel=='CHA1':
        data=0
        currentPach=0
    elif channel=='CHA2':
        data=1
        currentPach=1
    elif channel=='CHB1':
        data=5
        currentPach=2
    elif channel=='CHB2':
        data=6
        currentPach=3
    currentChainMode=chainModeMatrix[currentBank][currentPach]
    msg = mido.Message('program_change', program=data)
    katanaOUT.send(msg)

def loadPatch(bank, patch):
    
    
    setData([0x60,0x00,0x11,0x11],[0x00])
    currentBank=bank
    currentPach=patch
    
    if chainModeMatrix[bank][patch]=='Custom':
        if chain
        setChain(bank, patch)
    elif chainModeMatrix[bank][patch] == currentChainMode:
          
           
    for i in patchesMatrix[bank][patch]:
        katanaOUT.send(i)
            
            
    # if customChainEnabledMatrix[bank][patch]=='Enable':
    #     for i in range(len(patchesMatrix[bank][patch])):
    #         listHEX=[]
    #         x=0
    #         for j in (patchesMatrix[bank][patch][i]).data:
    #             listHEX.insert(x,hex(j))
    #             x=x+1
    #         print(listHEX) 
    # else:

        
    setData([0x60,0x00,0x0A,0x18],[0x01])
    
        
    
def setChain(bank, patch):
    global currentChain
    if currentChainMode == 'Custom':
        if  currentChain != chainMatrix[bank][patch].data :
            katanaOUT.send(chainMatrix[bank][patch])
            currentChain=chainMatrix[bank][patch].data
    else: 
        currentChain = 'NA'


            
def savePatch(channel, bank, patch):

    changeChannel(channel)   
    channelAddress=0x01
    
    if channel=='CHA1':
        channelAddress=0x01
    elif channel=='CHA2':
        channelAddress=0x02
    elif channel=='CHB1':
        channelAddress=0x05  
    elif channel=='CHB2':
        channelAddress=0x06
     
    address=[0x10, channelAddress]
    
    #if patch==3:
    katanaOUT.send(chainMatrix[bank][patch])
    
    for i in patchesMatrix[bank][patch]:
        data=list(i.data)
        data.pop()
        del data[0:9]
        msg = mido.Message('sysex', data=(initialTupleSysex + setDataSysex + address + data + checkSum(address,data)))
        katanaOUT.send(msg)
     
         
    setData([0x7F,0x00,0x00,0x01],[0x01])                   # Entrar en modo de configuracion
    time.sleep(0.1)                                         # Espera de 100ms    
    setData([0x7F,0x00,0x01,0x04],[0x00, channelAddress])   # Guardar patch en su respectivo canal               
    setData([0x7F,0x00,0x00,0x01],[0x00])                   # Salir del modo de configuracion 
    