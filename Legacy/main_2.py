import mido

initialTupleSysex=[0x41, 0x00, 0x00, 0x00, 0x00, 0x33]
readDataSysex=[0x11]
setDataSysex=[0x12]
katanaOUT = mido.open_output("KATANA MIDI 1")
katanaIN = mido.open_input("KATANA MIDI 1")

def checkSum(address,data):
    vals=address+data
    accum = 0
    for val in vals:
        accum = (accum + val) & 0x7F
        cksum = (128 - accum) & 0x7F
    return [cksum]

def changeChannel(channel):     
    data=0;
    if channel=="PANEL":
        data=4
    elif channel=="CHA1":
        data=0
    elif channel=="CHA2":
        data=1
    elif channel=="CHB1":
        data=5
    elif channel=="CHB2":
        data=6
    msg = mido.Message("program_change", program=data)
    katanaOUT.send(msg)
    
def setData(address,data):

    msg = mido.Message("sysex", data=(initialTupleSysex + setDataSysex+ address +data +checkSum(address,data)))
    katanaOUT.send(msg)
    
def readData(address, offset):

    msg = mido.Message("sysex", data=(initialTupleSysex + readDataSysex + address +offset+checkSum(address,offset)))
    katanaOUT.send(msg)
    msg=katanaIN.receive()
    value=msg.bytes()
    value.pop()
    value.pop()
    del value[0:12]
    return value

# FUNCIONES SYSEX, ACTIVACION Y DESACTIVACION DE EFECTOS
def readBoost():
    value=readData([0x60,0x00,0x00,0x30],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setBoost(state):
    if state=="ON":
        setData([0x60,0x00,0x00,0x30],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x00,0x30],[0x00])

def readMOD():
    value=readData([0x60,0x00,0x01,0x40],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setMOD(state):
    if state=="ON":
        setData([0x60,0x00,0x01,0x40],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x01,0x40],[0x00])
        
def readFX():
    value=readData([0x60,0x00,0x03,0x4C],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setFX(state):
    if state=="ON":
        setData([0x60,0x00,0x03,0x4C],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x03,0x4C],[0x00])

def readDELAY1():
    value=readData([0x60,0x00,0x05,0x60],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setDELAY1(state):
    if state=="ON":
        setData([0x60,0x00,0x05,0x60],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x05,0x60],[0x00])
        
def readREVERB():
    value=readData([0x60,0x00,0x06,0x10],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setREVERB(state):
    if state=="ON":
        setData([0x60,0x00,0x06,0x10],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x06,0x10],[0x00])
        
        
def readDELAY2():
    value=readData([0x60,0x00,0x10,0x4E],[0x00,0x00,0x00,0x01])
    if value==[0]:
        return "OFF"
    if value==[1]:
        return "ON"
    
def setDELAY2(state):
    if state=="ON":
        setData([0x60,0x00,0x10,0x4E],[0x01])
    elif state=="OFF":
        setData([0x60,0x00,0x10,0x4E],[0x00])
        
# FUNCIONES CON AJUSTE DE PARAMETROS
def setVolumeBoost(state):
    # Valor de 0 a 64 hexadecimal
    
    # ajustado un 10% de boost
    if state=="ON":
        setData([0x60,0x00,0x07,0x10],[0x64])
    elif state=="OFF":
        setData([0x60,0x00,0x07,0x10],[0x50])
    
def setDELAY2Tempo(tempo):
    if tempo<0:
        tempo=0
    elif tempo>2000:
        tempo=2000    
    setData([0x60,0x00,0x10,0x50], [tempo>>7,tempo%128])


#changeChannel("CHA2")
#offBoost()

#msg = mido.Message("sysex", data=(initialTupleSysex + readDataSysex+[0x00,0x00,0x04,0x10]+[0x00,0x00,0x00,0x01]+checkSum([0x00,0x00,0x04,0x10],[0x00,0x00,0x00,0x01])))
#print(msg.bytes())


#print(msg)
#print(checkSum([0x60, 0x00, 0x12, 0x14], [0x1]))
#print(checkSum([0x00,0x00,0x04],[0x10]))

#print(readData([0x00,0x00,0x04,0x20],[0x00,0x00,0x00,0x01]))

#setData([0x60,0x00,0x00,0x30],[0x01])
#print(readData([0x00,0x00,0x04,0x10],[0x00,0x00,0x00,0x01]))
#setDELAY2("OFF")
#print(readDELAY2())
#setDELAY2("ON")
#print(readDELAY2())
#setVolumeBoost("ON")
#setDELAY2Tempo(128)
#print(readData([0x60,0x00,0x10,0x50], [0x00,0x00,0x00,0x01]))
x=0

while x<10:
    x=int(input("Ingrese ampli "))
    print(x)
    if x==0: ## DRY
        setBoost("ON")
        setFX("OFF")
        setMOD("OFF")
        setDELAY2("OFF")
        setREVERB("OFF")
        setVolumeBoost("OFF")
        
    elif x==1: ## ChOrus
        setFX("ON")
        setMOD("OFF")
        setDELAY2("OFF")
        setREVERB("OFF")
        setVolumeBoost("OFF")
    elif x==2: ## Violin
        setFX("OFF")
        setMOD("ON")
        setDELAY2("OFF")
        setREVERB("OFF")
        setVolumeBoost("OFF")
    elif x==3: ##solo
        setFX("OFF")
        setMOD("OFF")
        setDELAY2("ON")
        setREVERB("ON")
        setVolumeBoost("ON")
