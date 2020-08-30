import os
import time
import mido

class KATANA:
    
    initialTupleSysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]        # Katana ID
    readDataSysex = [0x11]                                          # bite para lectura de datos
    setDataSysex = [0x12]                                           # byte para escritura de dato
    currentDirectory = os.getcwd()                                  # Directorio actual
    groupNames = []                                                 # Vector con los nombres de cada grupo
    numberOfGroups = 0                                              # Numero de grupos
    bankNames = [[]]                                                # Matriz con los nombres de cada banco de cada grupo
    numberOfBanks = []                                              # Vector con el numero de bancos de cada Grupo
    patchesNames = [[[]]]                                           # Matriz 3D con los nombres de los patches de cada banco de cada grupo
    numberOfPatches = [[]]                                          # Matriz con el numero de patches de cada banco de cada grupo          
    #patchesMatrix = [[[[]]]]                                        # Matriz 4D con los patches de cada banco de cada grupo
    #patchChainMatrix = [[[]]]                                       # Matriz 3D con la cadena asignada a cada patch de cada banco de cada grupo                                       
    #chainMatrix = [[]]                                              # Matriz con las 4 custom chains o default chains de cada grupo
    #chainModeMatrix = [[]]                                          # Matriz con el tipo de cadena de cada una de las 4 cadenas de cada grupo (custom, 1, 2, 3)
    katanaOUT = None                                                # Canal Midi de salida del amplificador
    katanaIN = None                                                 # Canal Midi de entrada del amplificador
    #BankPatchSizes = [[[]]]                                         # Matriz 3d con la cantidad de Patches de cada banco de cada grupo 
    #BanksPresetSizes = [[]]                                         # Matriz 3d con la cantidad de presets de cada banco de cada grupo 
    #currentChain = None                                             # define cual de las 4 cadenas corresponde el patch actual 
    #currentBank = None                                              # define el banco actual
    #currentPach = None                                              # define el patch actual
    #currentGroup = None                                             # define el grupo actual  
    #currentLoadedGroup = None                                       # define cual grupo se encuentra cargado en el amplificador
    

        
    def __init__(self):
              
        self.groupNames = os.listdir(self.currentDirectory + '/GroupPresets')
        self.numberOfGroups = len(self.groupNames)        

        self.bankNames = [[] for x in range(self.numberOfGroups)]
        self.numberOfBanks = [0 for x in range(self.numberOfGroups)]
        self.patchesNames = [[[]] for x in range(self.numberOfGroups)] 
        self.numberOfPatches = [[] for x in range(self.numberOfGroups)]
        
        print(self.groupNames)
        
        for i in range (self.numberOfGroups): 
             
            self.bankNames[i] = os.listdir(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] +'/Banks')
            self.bankNames[i].sort()
            self.numberOfBanks[i]=len(self.bankNames[i])
            
            print(self.bankNames[i])
            self.patchesNames[i] = [[] for x in range(self.numberOfBanks[i])]             
            self.numberOfPatches[i] = [0 for x in range(self.numberOfBanks[i])]
            
            for j in range (self.numberOfBanks[i]):
                
                self.patchesNames[i][j] = os.listdir(self.currentDirectory + '/GroupPresets/' + self.groupNames[i] +'/Banks/' + self.bankNames[i][j] + '/patches' )  
                self.patchesNames[i][j].sort()
                self.numberOfPatches[i][j] = len(self.patchesNames[i][j])
                print(self.patchesNames[i][j])
                

                                                           
        self.patchesMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]              # Matriz que contiene .sys de cada banco
        self.chainMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]                # Matriz que contiene Sysex de la cadena custom de cada patch
        self.chainModeMatrix=[[None for x in range(4)] for y in range(numberOfBanks)]            # Matriz que contiene el tipo de cadena de efectos, default o custom
        self.BankSizes=[0,0] 
        
         

    def initConnection(self):
        try:
            katanaOUT = mido.open_output('KATANA MIDI 1')
            katanaIN = mido.open_input('KATANA MIDI 1')   
            return 1
        except ValueError:
            return 0