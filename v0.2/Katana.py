import os
import time
import csv
import json
import mido

class Katana:

    initialTupleSysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]        # """ Katana ID """
    readDataSysex = [0x11]                                          # bite para lectura de datos
    setDataSysex = [0x12]                                           # byte para escritura de datos
    currentDirectory = os.getcwd()                                  # Directorio actual
    katanaOUT = None                                                # Canal Midi de salida del amplificador
    katanaIN = None                                                 # Canal Midi de entrada del amplificador
    
    groupNames = []                                                 # Vector con los nombres de cada grupo
    numberOfGroups = 0                                              # Numero de grupos
    bankNames = [[]]                                                # Matriz con los nombres de cada banco de cada grupo
    numberOfBanks = []                                              # Vector con el numero de bancos de cada Grupo
    
    chainMatrix = [[]]                                              # Matriz con las 4 custom chains de cada grupo
    patchChainMatrix = [[[]]]                                       # Matriz 3D con la chain asignada a cada patch de cada banco de cada grupo (0, 1, 2, 3, 4(Panel (default 2 con postEQ y preEXP)))                                     

    patchesNames = [[[]]]                                           # Matriz 3D con los nombres de los patches de cada banco de cada grupo
    numberOfPatches = [[]]                                          # Matriz con el numero de patches de cada banco de cada grupo          
    patchesMatrix = [[[[]]]]                                        # Matriz 4D con los patches de cada banco de cada grupo    
    patchEnableFXMatrix = [[[{}]]]                                  # Matriz 3D con un diccionario en su interior, que contiene el estado de los efectos de cada patch Enable de cada banco de cada grupo                    
        
    
    #presetsNames = [[[]]]                                           # Matriz 3D con los nombres de los presets de cada banco de cada grupo
    #numberOfPresets = [[]]                                          # Matriz con el numero de presets de cada banco de cada grupo 
    #presetsMatrix = [[[[]]]]                                        # Matriz presets...       


    currentChain = None                                             # define cual de las 4 (5 con panel) cadenas del grupo corresponde el patch actual 
    currentGroup = None                                             # define el grupo actual  
    currentBank = None                                              # define el banco actual
    currentPach = None                                              # define el patch actual
    #currentPreset = None                                           # define el preset actual    
    currentLoadedGroup = None                                       # define cual grupo se encuentra cargado en el amplificador
    presetMaxVolume = 100                                           # Define el boost de volumen
    presetMinVolume = 60                                            # Define el valor minimo de volumen


    presetOperations = None                                         # Operaciones default para los presets
    defaultPreset = None                                            # Preset default
    defaultPatch = None
    defaultChain = None
    defaultEnable = {}
    currentPreset = None                                            # referencia a preset seleccionado
    currentPresetNumberOfPages = None                               # Numero de paginas del preset
    currentPresetPage = None
    currentPresetLatchEnable = [[]]                                 # Enable para los comandos LATCH
    currentPresetEXGroups = [[]]                                    # Grupos exclusivos de comandos del preset actual 



    def __init__(self):
        
        # Carga de presetOperations

        with open("presetOperations.json", "r") as f:
            self.presetOperations = json.load(f)
    
        #print(self.presetOperations)
        
        #print(type(self.defaultPresetOperations))
        #print(len(self.defaultPresetOperations))

        #print(self.defaultPresetOperations["PedalFXEnable"])
        #print(self.defaultPresetOperations["PedalFXEnable"].keys())

        #for distro in distros_dict:
        #    print(distro["type"])
        
        
        # Carga de preset default:
        with open("defaultPreset.json", "r") as f:
            self.defaultPreset = json.load(f)
    
        print(self.defaultPreset)

        self.currentPreset = self.defaultPreset
        self.currentPresetPage = 0
        self.currentPresetNumberOfPages = len(self.defaultPreset)


        currentPresetPage = 0

        # Carga de patch default y su enable
        
        self.defaultPatch=mido.read_syx_file(self.currentDirectory + "\defaultPatch.syx")
        with open(self.currentDirectory + "\defaultEnable.csv", "r") as file :
            for row in csv.reader(file):
                self.defaultEnable[row[0]]=int(row[1])

        # Carga de Panel Chain (default)

        self.defaultChain=mido.read_syx_file(self.currentDirectory + "\defaultChain.syx")


        # Ajuste de tamaños de matrices y listas
    

        self.groupNames = os.listdir(self.currentDirectory + "/GroupPresets")
        self.numberOfGroups = len(self.groupNames)        

        self.patchChainMatrix = [[[]] for x in range(self.numberOfGroups)]
        self.chainMatrix = [[] for x in range(self.numberOfGroups)]

        self.bankNames = [[] for x in range(self.numberOfGroups)]
        self.numberOfBanks = [0 for x in range(self.numberOfGroups)]



        self.patchesNames = [[[]] for x in range(self.numberOfGroups)] 
        self.numberOfPatches = [[] for x in range(self.numberOfGroups)]
        self.patchesMatrix = [[[[]]] for x in range(self.numberOfGroups)]
        self.patchEnableFXMatrix = [[[{}]] for x in range(self.numberOfGroups)]



        #self.presetsNames = [[[]] for x in range(self.numberOfGroups)] 
        #self.numberOfPresets = [[] for x in range(self.numberOfGroups)]
        #self.presetsMatrix = [[[[]]] for x in range(self.numberOfGroups)]


        #print(self.groupNames)    

        for i in range (self.numberOfGroups):
             
            self.bankNames[i] = os.listdir(self.currentDirectory + "/GroupPresets/" + self.groupNames[i] +"/Banks")
            self.bankNames[i].sort()
            self.numberOfBanks[i]=len(self.bankNames[i])
            
            #print(self.bankNames[i]) 

            self.patchChainMatrix[i] = [0 for x in range(self.numberOfBanks[i])]


            self.patchesNames[i] = [[] for x in range(self.numberOfBanks[i])]             
            self.numberOfPatches[i] = [0 for x in range(self.numberOfBanks[i])]
            self.patchesMatrix[i] = [[[]] for x in range(self.numberOfBanks[i])]
            self.patchEnableFXMatrix[i] = [[{}] for x in range(self.numberOfBanks[i])]

            # Carga de chains

            self.chainMatrix[i] = [None for x in range(4)] 
                
            localChainList = os.listdir(self.currentDirectory + "/GroupPresets/" + self.groupNames[i] + "/Chains/")
            localChainList.sort()
            #print(localChainList)
            for j in localChainList:
                self.chainMatrix[i][int(j[0])] = mido.read_syx_file(self.currentDirectory +  "/GroupPresets/" + self.groupNames[i] + "/Chains/" + j[0] +".syx")[0]
 

            for j in range (self.numberOfBanks[i]):
                
                self.patchesNames[i][j] = os.listdir(self.currentDirectory + "/GroupPresets/" + self.groupNames[i] + "/Banks/" + self.bankNames[i][j] + "/patches" )  
                self.patchesNames[i][j].sort()
                self.numberOfPatches[i][j] = len(self.patchesNames[i][j])
                #print(self.patchesNames[i][j])
                
                self.patchesMatrix[i][j] = [[] for x in range(self.numberOfPatches[i][j])]
                
                self.patchChainMatrix[i][j] = [None for x in range(self.numberOfPatches[i][j])]
                
                self.patchEnableFXMatrix[i][j] = [{} for x in range(self.numberOfPatches[i][j])]


                # Lectura de chainConfig (Que cadena le corresponde a cada pàtch)
                
                with open(self.currentDirectory + "/GroupPresets/" + self.groupNames[i] + "/Banks/" + self.bankNames[i][j] + "/chainConfig.csv", "r") as file :
                    for row in csv.reader(file):
                        self.patchChainMatrix[i][j] = row
                

                for k in range(len(self.patchChainMatrix[i][j])):
                    self.patchChainMatrix[i][j][k] = int(self.patchChainMatrix[i][j][k])

                # Lectura de patches
                
                for k in range (self.numberOfPatches[i][j]):

                    auxList = list(self.patchesNames[i][j][k])
                    auxList.pop()
                    auxList.pop()
                    auxList.pop()
                    auxList.pop()
                    
                    self.patchesNames[i][j][k] = "".join(auxList)

                    #print(self.patchesNames[i][j][k])
                    
                    self.patchesMatrix[i][j][k]=mido.read_syx_file(self.currentDirectory+ "/GroupPresets/" + self.groupNames[i] + "/Banks/" + self.bankNames[i][j] + "/patches/" + self.patchesNames[i][j][k] + ".syx")
                    
                      
                    # Lectura del chainEnable de los patches  
                    
                    with open(self.currentDirectory+ "/GroupPresets/" + self.groupNames[i] + "/Banks/" + self.bankNames[i][j] + "/enable/" + self.patchesNames[i][j][k] + ".csv", "r") as file :
                        for row in csv.reader(file):
                            self.patchEnableFXMatrix[i][j][k][row[0]]=int(row[1])
                            #print(row)    

                    #print(self.patchEnableFXMatrix[i][j][k])    
                    
                    #print(len(self.patchesMatrix[i][j][k]))

               
                   

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
                                  
    def initConnection(self, input="KATANA MIDI 1", output="KATANA MIDI 1"):
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

        msg = mido.Message("sysex", data=(self.initialTupleSysex + self.setDataSysex + address + data + self.checkSum(address,data)))
        self.katanaOUT.send(msg)

    def setRawData(self, data):

        msg = mido.Message("sysex", data=data)
        self.katanaOUT.send(msg)

    def readData(self, address, offset):

        msg = mido.Message("sysex", data=(self.initialTupleSysex + self.readDataSysex + address + offset + self.checkSum(address,offset)))
        self.katanaOUT.send(msg)
        msg = self.katanaIN.receive()
        value = msg.bytes()
        value.pop()
        value.pop()
        del value[0:12]
        return value

    # Funciones de control

    # type

    def executeCommand(self, command):
        listOfCommands = self.currentPreset[str(self.currentPresetPage)][str(command)][1]
        for i in listOfCommands:
            cmd = self.presetOperations[i]
            
            # Evaluar tipo de mensaje y ejecutarlo
            if cmd["type"] == "PAGE":
                if self.currentPresetNumberOfPages > 1:
                    if cmd["size"] == 1: # siguiente pagina
                        #self.currentPresetPage = 1 
                        self.currentPresetPage = (self.currentPresetPage+1) % self.currentPresetNumberOfPages
                    else: # pagina anterior 
                        if self.currentPresetPage == 0:
                            self.currentPresetPage = self.currentPresetNumberOfPages - 1
                        else:             
                            self.currentPresetPage = (self.currentPresetPage-1) % self.currentPresetNumberOfPages
            elif cmd["type"] == "LATCH":
                self.sendMSG(cmd["MIDIType"],cmd["address"],cmd[""] )
                print("TODO")
                
    #   MIDI type
    
    def sendMSG(self, type: str, address, data) -> None:

        if type == "SysEx":

            self.setData(address, data)

        elif type == "MIDI_CH":

            msg = mido.Message("program_change", program=data)
            self.katanaOUT.send(msg)
        
        elif type == "MIDI_CC":
            
            msg = mido.Message("control_change", control=data)
            self.katanaOUT.send(msg)
        

    # Activación y desactivación de efectos
    



   

    # FUNCIONES CON AJUSTE DE PARAMETROS

    def setVolumeBoost(self, state):

        if state=="ON":
            self.setData([0x60,0x00,0x07,0x10],[self.presetMaxVolume])
        elif state=="OFF":
            self.setData([0x60,0x00,0x07,0x10],[self.presetMinVolume])

    def setDELAY1Tempo(self, tempo):
        if tempo<0:
            tempo=0
        elif tempo>2000:
            tempo=2000
        self.setData([0x60,0x00,0x05,0x62], [tempo>>7,tempo%128])

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
            
        msg = mido.Message("program_change", program=data)
        self.katanaOUT.send(msg)
        
       
    def loadPatch(self, group, bank, patch):    
    
        #self.setData([0x60,0x00,0x11,0x11],[0x00])

        
        if self.currentLoadedGroup != group:    
            
            print("Cambio de grupo")
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

        
    def setChainOnKatana(self, group, chain):
        
        self.changeChannel(chain)
        #print(self.chainMatrix[group][chain])
        self.katanaOUT.send( self.chainMatrix[group][chain])        # Mandar cadena
        name =[0x43, 0x68, 0x61, 0x69, 0x6e, 0x3a, 0x20, 0x30 + chain ] + [0x0 for x in range(8)]
        self.setData([0x60,0x00,0x00,0x00],name)
        channel=""
        if chain==0:
            channel = "CH1"
        elif chain==1:
            channel = "CH2"
        elif chain==2:
            channel = "CH1"
        elif chain==3:
            channel = "CH2"
        
        print("Presione por 3 segundos el botón " + channel)
        

def main():
    print("Todo")

if __name__ == "__main__":
    main()
    