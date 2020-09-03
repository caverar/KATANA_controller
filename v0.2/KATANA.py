import os
import time
import csv
import mido

class KATANA:
    initialTupleSysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]        # Katana ID
    readDataSysex = [0x11]                                          # bite para lectura de datos
    setDataSysex = [0x12]                                           # byte para escritura de dato
    currentDirectory = os.getcwd()                                  # Directorio actual
    katanaOUT = None                                                # Canal Midi de salida del amplificador
    katanaIN = None                                                 # Canal Midi de entrada del amplificador
    
    groupNames = []                                                 # Vector con los nombres de cada grupo
    numberOfGroups = 0                                              # Numero de grupos
    bankNames = [[]]                                                # Matriz con los nombres de cada banco de cada grupo
    numberOfBanks = []                                              # Vector con el numero de bancos de cada Grupo
    patchesNames = [[[]]]                                           # Matriz 3D con los nombres de los patches de cada banco de cada grupo
    numberOfPatches = [[]]                                          # Matriz con el numero de patches de cada banco de cada grupo          
    patchesMatrix = [[[[]]]]                                        # Matriz 4D con los patches de cada banco de cada grupo
    chainMatrix = [[]]                                              # Matriz con las 4 custom chains de cada grupo
    groupChainTypesMatrix = [[]]                                    # Matriz con el tipo de cadena de cada una de las 4 cadenas de cada grupo (0(1), 1(2), 2(3), 3(custom), 4(Panel))
    patchChainMatrix = [[[]]]                                       # Matriz 3D con la cadena asignada a cada patch de cada banco de cada grupo (0, 1, 2, 3)                                     
    

    currentChain = None                                             # define cual de las 4 (5 con panel) cadenas del grupo corresponde el patch actual 
    currentGroup = None                                             # define el grupo actual  
    currentBank = None                                              # define el banco actual
    currentPach = None                                              # define el patch actual
    #currentPreset = None                                           # define el preset actual    
    currentLoadedGroup = None                                       # define cual grupo se encuentra cargado en el amplificador
    presetMaxVolume = 100                                           # Define el boost de volumen
    presetMinVolume = 60                                            # Define el valor minimo de volumen

        
    def __init__(self):
              
        self.groupNames = os.listdir(self.currentDirectory + '/GroupPresets')
        self.numberOfGroups = len(self.groupNames)        

        self.bankNames = [[] for x in range(self.numberOfGroups)]
        self.numberOfBanks = [0 for x in range(self.numberOfGroups)]
        self.patchesNames = [[[]] for x in range(self.numberOfGroups)] 
        self.numberOfPatches = [[] for x in range(self.numberOfGroups)]
        self.patchesMatrix = [[[[]]] for x in range(self.numberOfGroups)]
        #print(self.groupNames)    
        self.groupChainTypesMatrix = [[] for x in range(self.numberOfGroups)]
        self.patchChainMatrix = [[[]] for x in range(self.numberOfGroups)]
        self.chainMatrix = [[] for x in range(self.numberOfGroups)] 
        for i in range (self.numberOfGroups): 
             
            self.bankNames[i] = os.listdir(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] +'/Banks')
            self.bankNames[i].sort()
            self.numberOfBanks[i]=len(self.bankNames[i])
            
            #print(self.bankNames[i])
            self.patchesNames[i] = [[] for x in range(self.numberOfBanks[i])]             
            self.numberOfPatches[i] = [0 for x in range(self.numberOfBanks[i])]
            self.patchesMatrix[i] = [[[]] for x in range(self.numberOfBanks[i])]
            
            
            # Carga de configuración de chains del grupo
            
            with open(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] + '/chainTypes.csv' , 'r') as file :
                for row in csv.reader(file):
                    self.groupChainTypesMatrix[i] = row                
                
            for j in range(len(self.groupChainTypesMatrix[i])):
                self.groupChainTypesMatrix[i][j] = int(self.groupChainTypesMatrix[i][j])
                    
            #print(self.groupChainTypesMatrix[i])            

            self.patchChainMatrix[i] = [[] for x in range(self.numberOfBanks[i])]
            self.chainMatrix[i] = [None for x in range(len(self.groupChainTypesMatrix[i]))] 
            
            # Carga de chains
            for j in range(len(self.groupChainTypesMatrix[i])):
                if self.groupChainTypesMatrix[i][j] == 3:                    
                    self.chainMatrix[i][j] = mido.read_syx_file(self.currentDirectory +  '/GroupPresets/' + self.groupNames[i] + '/Chains/' + str(j) +'.syx')[0]
                #print(self.chainMatrix[i][j])     
                      
            for j in range (self.numberOfBanks[i]):
                
                self.patchesNames[i][j] = os.listdir(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] + '/Banks/' + self.bankNames[i][j] + '/patches' )  
                self.patchesNames[i][j].sort()
                self.numberOfPatches[i][j] = len(self.patchesNames[i][j])
                #print(self.patchesNames[i][j])
                
                self.patchesMatrix[i][j] = [[] for x in range(self.numberOfPatches[i][j])]
               
                
                # Lectura de chainConfig
                
                with open(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] + '/Banks/' + self.bankNames[i][j] + '/chainConfig.csv', 'r') as file :
                    for row in csv.reader(file):
                        self.patchChainMatrix[i][j] = row
                for k in range(len(self.patchChainMatrix[i][j])):
                    self.patchChainMatrix[i][j][k] = int(self.patchChainMatrix[i][j][k])
                          
                #print(self.patchChainMatrix[i][j]) 
                
                for k in range (self.numberOfPatches[i][j]):
                    
                    self.patchesMatrix[i][j][k]=mido.read_syx_file(self.currentDirectory+ '/GroupPresets/' + self.groupNames[i] + '/Banks/' + self.bankNames[i][j] + '/patches/' + self.patchesNames[i][j][k])
                    #print(len(self.patchesMatrix[i][j][k]))
                    
                    # Remplazo de cabecera de FxFloor por KATANA
                    for l in range(len(self.patchesMatrix[i][j][k])):
                        if l==18:    
                            tempSysex = list(self.patchesMatrix[i][j][k][l].data)                    
                            del tempSysex[0:11]                  
                            self.patchesMatrix[i][j][k][l]=mido.Message('sysex', data = self.initialTupleSysex + self.setDataSysex +[0x60, 0x00, 0x13, 0x00] +tempSysex)
                        else:
                            tempSysex = list(self.patchesMatrix[i][j][k][l].data)                 
                            del tempSysex[0:6]
                            self.patchesMatrix[i][j][k][l]=mido.Message('sysex', data = self.initialTupleSysex + self.setDataSysex + tempSysex)
        
        # Estado de preset actual                                              
        self.currentGroup = 0                                             
        self.currentLoadedGroup = 0
        self.currentBank = 0                                              
        self.currentPach = 0                                             
        self.currentChain = self.patchChainMatrix[self.currentGroup][self.currentBank][self.currentPach]
        #print(self.currentChain)
        #self.currentPreset = None  
        
        # Parametros del preset
        
        self.presetMaxVolume = 100
        self.presetMinVolume = 60                                        
                                               
            
    # Conexión y lectura/escritura de datos    
                                  
    def initConnection(self, input='KATANA MIDI 1', output='KATANA MIDI 1'):
        try:
            self.katanaOUT = mido.open_output(output)
            self.katanaIN = mido.open_input(input)   
            return 1
        except:
            return 0
    
    def checkSum(self, address, data):
        vals=address+data
        accum = 0
        for val in vals:
            accum = (accum + val) & 0x7F
            cksum = (128 - accum) & 0x7F
        return [cksum]


    def setData(self, address, data):

        msg = mido.Message('sysex', data=(self.initialTupleSysex + self.setDataSysex + address + data + self.checkSum(address,data)))
        self.katanaOUT.send(msg)

    def setRawData(self, data):

        msg = mido.Message('sysex', data=data)
        self.katanaOUT.send(msg)

    def readData(self, address, offset):

        msg = mido.Message('sysex', data=(self.initialTupleSysex + self.readDataSysex + address + offset + self.checkSum(address,offset)))
        self.katanaOUT.send(msg)
        msg = self.katanaIN.receive()
        value = msg.bytes()
        value.pop()
        value.pop()
        del value[0:12]
        return value

    # Activación y desactivación de efectos


    def readBoost(self):
        value = self.readData([0x60,0x00,0x00,0x30],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setBoost(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x00,0x30],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x00,0x30],[0x00])

    def readMOD(self):
        value = self.readData([0x60,0x00,0x01,0x40],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setMOD(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x01,0x40],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x01,0x40],[0x00])

    def readFX(self):
        value = self.readData([0x60,0x00,0x03,0x4C],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setFX(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x03,0x4C],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x03,0x4C],[0x00])

    def readDELAY1(self):
        value = self.readData([0x60,0x00,0x05,0x60],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setDELAY1(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x05,0x60],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x05,0x60],[0x00])

    def readREVERB(self):
        value = self.readData([0x60,0x00,0x06,0x10],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setREVERB(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x06,0x10],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x06,0x10],[0x00])


    def readDELAY2(self):
        value = self.readData([0x60,0x00,0x10,0x4E],[0x00,0x00,0x00,0x01])
        if value==[0]:
            return 'OFF'
        if value==[1]:
            return 'ON'

    def setDELAY2(self, state):
        if state=='ON':
            self.setData([0x60,0x00,0x10,0x4E],[0x01])
        elif state=='OFF':
            self.setData([0x60,0x00,0x10,0x4E],[0x00])
            

    # FUNCIONES CON AJUSTE DE PARAMETROS

    def setVolumeBoost(self, state):

        if state=='ON':
            self.setData([0x60,0x00,0x07,0x10],[self.presetMaxVolume])
        elif state=='OFF':
            self.setData([0x60,0x00,0x07,0x10],[self.presetMinVolume])

    def setDELAY2Tempo(self, tempo):
        if tempo<0:
            tempo=0
        elif tempo>2000:
            tempo=2000
        self.setData([0x60,0x00,0x10,0x50], [tempo>>7,tempo%128])
    
    
    def changeChannel(self, channel):
        if channel==4:
            data=4
        elif channel==0:
            data=0
        elif channel==1:
            data=1
        elif channel==2:
            data=5
        elif channel==3:
            data=6
            
        msg = mido.Message('program_change', program=data)
        self.katanaOUT.send(msg)
        
       
    def loadPatch(self, group, bank, patch):    
    
        #self.setData([0x60,0x00,0x11,0x11],[0x00])

        
        if self.currentLoadedGroup != group:    
            
            print('Cambio de grupo')
            if self.groupChainTypesMatrix[self.currentGroup][self.currentChain] != self.groupChainTypesMatrix[group][self.patchChainMatrix[group][bank][patch]]:     # si el preset es de un tipo distinto
                self.katanaOUT.send(self.chainMatrix[group][self.patchChainMatrix[group][bank][patch]])     # cargar la cadena
                
            elif self.currentChain == 4:                                                                                                                             # si esta seleccionado panel
                self.katanaOUT.send(self.chainMatrix[group][self.patchChainMatrix[group][bank][patch]])     # cargar la cadena
                
            elif self.chainMatrix[self.currentGroup][self.currentChain].data != self.chainMatrix[group][self.patchChainMatrix[group][bank][patch]].data:             # si la cadena custom no es la misma
                
                self.katanaOUT.send(self.chainMatrix[group][self.patchChainMatrix[group][bank][patch]])     # cargar la cadena
          
                   
        else:
            self.changeChannel(self.patchChainMatrix[group][bank][patch]) 
                   
        list1 = self.patchesMatrix[group][bank][patch]
        for i in range(len(list1)-5):
            self.katanaOUT.send(
                list1[i])
            
        self.currentGroup = group
        self.currentChain = self.patchChainMatrix[group][bank][patch]
        self.currentBank = bank
        self.currentPach = patch
            
        #self.setData([0x60,0x00,0x0A,0x18],[0x01])
        
    def saveChain(self, group, chain):
        
        self.changeChannel(chain)
        #print(self.chainMatrix[group][chain])
        self.katanaOUT.send( self.chainMatrix[group][chain])        # Mandar cadena
        name =[0x43, 0x68, 0x61, 0x69, 0x6e, 0x3a, 0x20, 0x30 +chain ] + [0x0 for x in range(8)]
        self.setData([0x60,0x00,0x00,0x00],name)
        channel=''
        if chain==0:
            channel = 'CH1'
        elif chain==1:
            channel = 'CH2'
        elif chain==2:
            channel = 'CH1'
        elif chain==3:
            channel = 'CH2'
        
        print('Presione por el 3 segundos el botón ' + channel)
        

        