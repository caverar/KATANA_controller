import os
import time
import csv
import mido
class KTNAReader:
    
    # Objetos de conexion

    initialTupleSysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]        # Katana ID
    readDataSysex = [0x11]                                          # bite para lectura de datos
    setDataSysex = [0x12]                                           # byte para escritura de dato
    currentDirectory = os.getcwd()                                  # Directorio actual
    katanaOUT = None                                                # Canal Midi de salida del amplificador
    katanaIN = None                                                 # Canal Midi de entrada del amplificador
    
    # Utilidades de codigo

    pedalList = ['PedalFX','Boost', 'Amp','NoiseSup', 'Volume', 'Eq', 'Delay1', 'Delay2', 'Reverb', 'FX', 'MOD', 'GlobalEq', 'Cab']

    # Obligatorios:
    pedalEnableAddressDirectory = {}                                                    # Direcciones de habilitación de efectos 
    pedalSelectorAddressDirectory = {}                                                  # Direcciones de selección de efectos
    noiseSupList = []                                                                   # Datos del supresor del ruido
    volumeList = []                                                                     # Datos del controlador de volumen
    globalEqDictionary = {}                                                             # Datos del Eq global
    EXPAssignList = []                                                                  # Asignador de parametro controlado por el pedal de expresión
    chainList = []                                                                      # Lista con registros y numero de datos del orden de la cadena de efectos


    # Revisables:
    pedalFXDictionary = {}                                                              # Tipo de pedalFX (Wah, pitch Bend): lista con pares de dirección y numero de datos que le corresponden al efecto
    boostDictionary = {}                                                                # Tipo de boost: lista con pares de dirección y numero de datos que le corresponden al efecto
    ampDictionary = {}                                                                  # Tipo de amp: lista con pares de dirección y numero de datos que le corresponden al efecto
    eqDictionary = {}                                                                   # Tipo de Eq: lista con pares de dirección y numero de parametros que le corresponden al efecto
    delay1Dictionary = {}                                                               # Tipo de Delay1: lista con pares de dirección y numero de parametros que le corresponden al efecto
    delay2Dictionary = {}                                                               # Tipo de Delay2: lista con pares de dirección y numero de parametros que le corresponden al efecto
    reverbDictionary = {}                                                               # Tipo de Reverb: lista con pares de dirección y numero de parametros que le corresponden al efecto
    FXDictionary = {}                                                                   # Tipo de FX: lista con pares de dirección y numero de parametros que le corresponden al efecto
    MODDictionary = {}                                                                  # Tipo de MOD: lista con pares de dirección y numero de parametros que le corresponden al efecto
    EXPAssignDictionary = {}                                                            # Parametros de cada tipo de asignación del pedal de expresión, agrupados en un diccionario, para cada tipo de asignación
    
    # PatchData (midi SysEx messages)
    patchChain = None
    patchChainMsg = None
    patchEnableDirectory = {}                                                           # Directorio con el estado de habilitación de cada tipo de efectos de la cadena
    voidSysExMsg =mido.Message('program_change', program=0)                             # Mensaje con la cadena del patch
    patchData = [None for x in range(50)]                                               # Conjunto de mensajes con el parche
    patchPedalFXType = None                                                               
    patchBoostType = None
    patchAmpType = None
    patchEqType = None
    patchDelay1Type = None
    patchDelay2Type = None 
    patchReverbType = None
    patchFXType = None
    patchMODType = None
    patchGlobalEqType = None
  
    # CurrentData    

    
    
    def __init__(self):
        
        self.patchData = [self.voidSysExMsg for x in range(40)]  


        self.chainList = [[0x60, 0x00, 0x07, 0x20], 20]                                 # Cadena de efectos


        self.pedalEnableAddressDirectory['PedalFX'] = [[0x60, 0x00, 0x06, 0x20], 1]     # off, on, (0,1)
        self.pedalEnableAddressDirectory['Boost'] = [[0x60, 0x00, 0x00, 0x30], 1]       # off, on, (0,1)
        self.pedalEnableAddressDirectory['NoiseSup'] = [[0x60, 0x00, 0x06, 0x63], 1]    # off, on, (0,1)
        self.pedalEnableAddressDirectory['Eq'] = [[0x60, 0x00, 0x01, 0x30], 1]          # off, on, (0,1)
        self.pedalEnableAddressDirectory['Delay1'] = [[0x60, 0x00, 0x05, 0x60], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['Delay2'] = [[0x60, 0x00, 0x10, 0x4E], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['Reverb'] = [[0x60, 0x00, 0x06, 0x10], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['GlobalEq'] = [[0x00, 0x00, 0x04, 0x32], 1]    # off, on, (0,1)
        self.pedalEnableAddressDirectory['MOD'] = [[0x60, 0x00, 0x01, 0x40], 1]         # off, on, (0,1)
        self.pedalEnableAddressDirectory['FX'] = [[0x60, 0x00, 0x03, 0x4C], 1]          # off, on, (0,1)



        self.pedalSelectorAddressDirectory['PedalFX'] = [[0x60, 0x00, 0x11, 0x11], 1]   # Tipo de Pedal
        self.pedalSelectorAddressDirectory['Boost'] = [[0x60, 0x00, 0x00, 0x31], 1]     # Tipo de Boost
        self.pedalSelectorAddressDirectory['Amp'] = [[0x60, 0x00, 0x00, 0x51], 1]       # Tipo de Amp
        self.pedalSelectorAddressDirectory['Eq'] = [[0x60, 0x00, 0x11, 0x04], 1]        # Tipo de eq
        self.pedalSelectorAddressDirectory['Delay1'] = [[0x60, 0x00, 0x05, 0x61], 1]    # Tipo de Delay1
        self.pedalSelectorAddressDirectory['Delay2'] = [[0x60, 0x00, 0x10, 0x4F], 1]    # Tipo de Delay1
        self.pedalSelectorAddressDirectory['Reverb'] = [[0x60, 0x00, 0x06, 0x11], 1]    # Tipo de Reverb
        self.pedalSelectorAddressDirectory['GlobalEq'] = [[0x00, 0x00, 0x04, 0x3E], 2]  # Tipo de GlobalEq
        self.pedalSelectorAddressDirectory['Cab'] = [[0x00, 0x00, 0x04, 0x31], 1]       # Tipo de Cabina
        self.pedalSelectorAddressDirectory['MOD'] = [[0x60, 0x00, 0x01, 0x41], 1]       # Tpoo de MOD
        self.pedalSelectorAddressDirectory['FX'] = [[0x60, 0x00, 0x03, 0x4D], 1]        # Tipo de FX
        
        
        

        self.EXPAssignList = [[0x60, 0x00, 0x12, 0x1F],[1]]                             # Retorna el parametro que se puede controlar mediante el pedal de expresión
                
                # 0x00 : Volume --
                # 0x01 : Foot Volume --
                # 0x02 : Foot Volume / Pedal FX --
                # 0x03 : Booster
                # 0x04 : MOD
                # 0x05 : Delay 1
                # 0x06 : FX
                # 0x07 : Delay 2
                # 0x08 : Reverb
                # 0x09 : Pedal FX --


        self.EXPAssignDictionary = [{} for x in range (9)]
        self.EXPAssignDictionary[0x03][0x00] = [[[0x60, 0x00, 0x13, 0x00],
                                                 [0x60, 0x00, 0x13, 0x20]],[1,2]]       # 0x03: Parametros de asignación de Booster
        
        

        self.EXPAssignDictionary[0x05][0x00] = [[[0x60, 0x00, 0x13, 0x01],
                                                 [0x60, 0x00, 0x13, 0x22]],[1,4]]       # 0x05: Parametros de asignación de Delay 1
        self.EXPAssignDictionary[0x07][0x00] = [[[0x60, 0x00, 0x13, 0x01],
                                                 [0x60, 0x00, 0x13, 0x22]],[1,4]]       # 0x07: Parametros de asignación de Delay 2
        self.EXPAssignDictionary[0x08][0x00] = [[[0x60, 0x00, 0x13, 0x02],
                                                 [0x60, 0x00, 0x13, 0x26]],[1,4]]       # 0x08: Parametros de asignación de Reverb

        
        # 0x04: Asignación para cada una las 30 modulaciones

        
        self.EXPAssignDictionary[0x04][0x00] = [[[0x60, 0x00, 0x13, 0x0F],
                                                 [0x60, 0x00, 0x13, 0x42]],[1,2]]       # 0x00 T Wah        
        self.EXPAssignDictionary[0x04][0x01] = [[[0x60, 0x00, 0x13, 0x10],
                                                 [0x60, 0x00, 0x13, 0x44]],[1,2]]       # 0x01 Auto Wah     
        self.EXPAssignDictionary[0x04][0x02] = [[[0x60, 0x00, 0x13, 0x11],
                                                 [0x60, 0x00, 0x13, 0x46]],[1,2]]       # 0x02 Sub Wah                      
        self.EXPAssignDictionary[0x04][0x03] = [[[0x60, 0x00, 0x13, 0x0D],
                                                 [0x60, 0x00, 0x13, 0x3E]],[1,2]]       # 0x03 Compressor   
        self.EXPAssignDictionary[0x04][0x04] = [[[0x60, 0x00, 0x13, 0x0E],
                                                 [0x60, 0x00, 0x13, 0x40]],[1,2]]       # 0x04 Limiter          
        self.EXPAssignDictionary[0x04][0x06] = [[[0x60, 0x00, 0x13, 0x12],
                                                 [0x60, 0x00, 0x13, 0x48]],[1,2]]       # 0x06 Graphic EQ       
        self.EXPAssignDictionary[0x04][0x07] = [[[0x60, 0x00, 0x13, 0x13],
                                                 [0x60, 0x00, 0x13, 0x4A]],[1,2]]       # 0x07 Param EQ         
        self.EXPAssignDictionary[0x04][0x09] = [[[0x60, 0x00, 0x13, 0x14],
                                                 [0x60, 0x00, 0x13, 0x4C]],[1,2]]       # 0x09 Guitar Sim    
        self.EXPAssignDictionary[0x04][0x0A] = [[[0x60, 0x00, 0x13, 0x0B],
                                                 [0x60, 0x00, 0x13, 0x3A]],[1,2]]       # 0x0A SlowGear         
        self.EXPAssignDictionary[0x04][0x0C] = [[[0x60, 0x00, 0x13, 0x17],
                                                 [0x60, 0x00, 0x13, 0x52]],[1,2]]       # 0x0C Wave Synth       
        self.EXPAssignDictionary[0x04][0x0E] = [[[0x60, 0x00, 0x13, 0x18],
                                                 [0x60, 0x00, 0x13, 0x54]],[1,2]]       # 0x0E Octave          
        self.EXPAssignDictionary[0x04][0x0F] = [[[0x60, 0x00, 0x13, 0x19],
                                                 [0x60, 0x00, 0x13, 0x56]],[1,4]]       # 0x0F Pitch Shifter    
        self.EXPAssignDictionary[0x04][0x10] = [[[0x60, 0x00, 0x13, 0x1A],
                                                 [0x60, 0x00, 0x13, 0x5A]],[1,4]]       # 0x10 Harmonist
        self.EXPAssignDictionary[0x04][0x12] = [[[0x60, 0x00, 0x13, 0x16],
                                                 [0x60, 0x00, 0x13, 0x50]],[1,2]]       # 0x12 Acoustic Processor
        self.EXPAssignDictionary[0x04][0x13] = [[[0x60, 0x00, 0x13, 0x05],
                                                 [0x60, 0x00, 0x13, 0x2E]],[1,2]]       # 0x13 Phaser
        self.EXPAssignDictionary[0x04][0x14] = [[[0x60, 0x00, 0x13, 0x04],
                                                 [0x60, 0x00, 0x13, 0x2C]],[1,2]]       # 0x14 Flanger
        self.EXPAssignDictionary[0x04][0x15] = [[[0x60, 0x00, 0x13, 0x07],
                                                 [0x60, 0x00, 0x13, 0x32]],[1,2]]       # 0x15 Tremolo
        self.EXPAssignDictionary[0x04][0x16] = [[[0x60, 0x00, 0x13, 0x09],
                                                 [0x60, 0x00, 0x13, 0x36]],[1,2]]       # 0x16 Rotary 1
        self.EXPAssignDictionary[0x04][0x17] = [[[0x60, 0x00, 0x13, 0x06],
                                                 [0x60, 0x00, 0x13, 0x30]],[1,2]]       # 0x16 Uni-V
        self.EXPAssignDictionary[0x04][0x19] = [[[0x60, 0x00, 0x13, 0x0C],
                                                 [0x60, 0x00, 0x13, 0x3C]],[1,2]]       # 0x19 Slicer
        self.EXPAssignDictionary[0x04][0x1A] = [[[0x60, 0x00, 0x13, 0x08],
                                                 [0x60, 0x00, 0x13, 0x34]],[1,2]]       # 0x1A Vibrato
        self.EXPAssignDictionary[0x04][0x1B] = [[[0x60, 0x00, 0x13, 0x0A],
                                                 [0x60, 0x00, 0x13, 0x38]],[1,2]]       # 0x1B Ring Mod
        self.EXPAssignDictionary[0x04][0x1C] = [[[0x60, 0x00, 0x13, 0x1B],
                                                 [0x60, 0x00, 0x13, 0x5E]],[1,2]]       # 0x1C Humanizer
        self.EXPAssignDictionary[0x04][0x1D] = [[[0x60, 0x00, 0x13, 0x03],
                                                 [0x60, 0x00, 0x13, 0x2A]],[1,2]]       # 0x1D 2x2 Chorus
        self.EXPAssignDictionary[0x04][0x1F] = [[[0x60, 0x00, 0x13, 0x15],
                                                 [0x60, 0x00, 0x13, 0x4E]],[1,2]]       # 0x1F Acoustic Guitar Simulator
        self.EXPAssignDictionary[0x04][0x23] = [[[0x60, 0x00, 0x13, 0x1C],
                                                 [0x60, 0x00, 0x13, 0x60]],[1,2]]       # 0x23 Phaser 90E
        self.EXPAssignDictionary[0x04][0x24] = [[[0x60, 0x00, 0x13, 0x1D],
                                                 [0x60, 0x00, 0x13, 0x62]],[1,2]]       # 0x24 Flanger 117E
        self.EXPAssignDictionary[0x04][0x25] = [[[0x60, 0x00, 0x13, 0x1E],
                                                 [0x60, 0x00, 0x13, 0x64]],[1,2]]       # 0x25 WAH 95E
        self.EXPAssignDictionary[0x04][0x26] = [[[0x60, 0x00, 0x13, 0x1F],
                                                 [0x60, 0x00, 0x13, 0x66]],[1,4]]       # 0x26 DC30
        self.EXPAssignDictionary[0x04][0x27] = [[[0x60, 0x00, 0x13, 0x6A]],[3]]         # 0x27 Heavy Octave
                                        

        self.EXPAssignDictionary[0x06] = self.EXPAssignDictionary[0x04]                 # 0x06: Asignación para cada uno los 30 FX post


        
        self.pedalFXDictionary[0x00] = [[[0x60, 0x00, 0x06, 0x26]],[6]]                 # 00-WAH
        self.pedalFXDictionary[0x01] = [[[0x60, 0x00, 0x06, 0x22]],[4]]                 # 01-Pedal Bend
        self.pedalFXDictionary[0x02] = [[[0x60, 0x00, 0x11, 0x12]],[5]]                 # 02-Wah 95E  

        self.boostDictionary[0x00] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 00-Mid Boost
        self.boostDictionary[0x01] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 01-Clean Boost
        self.boostDictionary[0x02] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 02-Treble Boost
        self.boostDictionary[0x03] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 03-Crunch
        self.boostDictionary[0x04] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 04-Natural OD
        self.boostDictionary[0x05] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 05-Warm OD
        self.boostDictionary[0x06] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 06-Fat DS
        self.boostDictionary[0x07] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 07-Lead DS
        self.boostDictionary[0x08] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 08-Metal DS
        self.boostDictionary[0x09] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 09-OCT Fuzz
        self.boostDictionary[0x0A] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 10-Blues OD
        self.boostDictionary[0x0B] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 11-OD-1
        self.boostDictionary[0x0C] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 12-Tubescreamer
        self.boostDictionary[0x0D] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 13-Turbo OD
        self.boostDictionary[0x0E] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 14-Dist
        self.boostDictionary[0x0F] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 15-Rat
        self.boostDictionary[0x10] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 16-GuV DS
        self.boostDictionary[0x11] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 17-DST+
        self.boostDictionary[0x12] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 18-Metal Zone
        self.boostDictionary[0x13] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 19-'60s Fuzz
        self.boostDictionary[0x14] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                   # 10-Muff Fuzz
        self.boostDictionary[0x15] = [[[0x60, 0x00, 0x00, 0x32]],[13]]                  # 21-Custom


        self.ampDictionary[0x00] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 00-Natural Clean
        self.ampDictionary[0x01] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 01-[Acoustic] Full Range
        self.ampDictionary[0x02] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 02-Combo Crunch
        self.ampDictionary[0x03] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 03-Stack Crunch
        self.ampDictionary[0x04] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 04-HiGain Stack
        self.ampDictionary[0x05] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 05-Power Drive
        self.ampDictionary[0x06] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 06-Extreme Lead
        self.ampDictionary[0x07] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 07-Core Metal
        self.ampDictionary[0x08] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 08-[Clean] JC-120
        self.ampDictionary[0x09] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 09-Clean Twin
        self.ampDictionary[0x0A] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 10-Pro Crunch
        self.ampDictionary[0x0B] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 11-[Crunch] Tweed
        self.ampDictionary[0x0C] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 12-Deluxe Crunch
        self.ampDictionary[0x0D] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 13-VO Drive
        self.ampDictionary[0x0E] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 14-VO Lead
        self.ampDictionary[0x0F] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 15-Match Drive
        self.ampDictionary[0x10] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 16-BG Lead
        self.ampDictionary[0x11] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 17-BG Drive
        self.ampDictionary[0x12] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 18-MS-1959 I
        self.ampDictionary[0x13] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 19-MS-1959 I+II
        self.ampDictionary[0x14] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 10-R-Fier Vintage
        self.ampDictionary[0x15] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 21-R-Fier Modern
        self.ampDictionary[0x16] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 22-T-Amp Lead
        self.ampDictionary[0x17] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 23-[BROWN] SLDN
        self.ampDictionary[0x18] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 24-[LEAD] 5150 Drive
        self.ampDictionary[0x19] = [[[0x60, 0x00, 0x00, 0x52],
                                     [0x60, 0x00, 0x00, 0x63]],[8,8]]                   # 25-Custom
        
        self.noiseSupList = [[0x60, 0x00, 0x06, 0x64],2]                                # Datos del supresor
        
        self.volumeList = [[[0x60, 0x00, 0x06, 0x33],
                            [0x60, 0x00, 0x07, 0x10]],[1,1]]                            # Datos de volumen
                
        self.eqDictionary[0x00] = [[[0x60, 0x00, 0x01, 0x31]],[11]]                     # 0x00: Eq Parametric
        self.eqDictionary[0x01] = [[[0x60, 0x00, 0x11, 0x05]],[11]]                     # 0x00: Eq Graphic
        

        self.delay1Dictionary[0x00] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x00 Digital
        self.delay1Dictionary[0x01] = [[[0x60, 0x00, 0x05, 0x62]],[11]]                 # 0x01 Pan        
        self.delay1Dictionary[0x02] = [[[0x60, 0x00, 0x05, 0x62]],[11]]                 # 0x02 Stereo
        self.delay1Dictionary[0x03] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x03 N/A
        self.delay1Dictionary[0x04] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x04 N/A
        self.delay1Dictionary[0x05] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x05 N/A
        self.delay1Dictionary[0x06] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x06 Reverse
        self.delay1Dictionary[0x07] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x07 Analog
        self.delay1Dictionary[0x08] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x08 Tape Echo
        self.delay1Dictionary[0x09] = [[[0x60, 0x00, 0x05, 0x62],
                                        [0x60, 0x00, 0x05, 0x73]],[6,2]]                # 0x09 Modulate
        self.delay1Dictionary[0x0A] = [[[0x60, 0x00, 0x05, 0x62],
                                        [0x60, 0x00, 0x05, 0x73],
                                        [0x60, 0x00, 0x10, 0x49]],[6,2,5]]              # 0x0A SDE-3000
        
        
        self.delay2Dictionary[0x00] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x00 Digital
        self.delay2Dictionary[0x01] = [[[0x60, 0x00, 0x10, 0x50]],[11]]                 # 0x01 Pan        
        self.delay2Dictionary[0x02] = [[[0x60, 0x00, 0x10, 0x50]],[11]]                 # 0x02 Stereo
        self.delay2Dictionary[0x03] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x03 N/A
        self.delay2Dictionary[0x04] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x04 N/A
        self.delay2Dictionary[0x05] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x05 N/A
        self.delay2Dictionary[0x06] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x06 Reverse
        self.delay2Dictionary[0x07] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x07 Analog
        self.delay2Dictionary[0x08] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x08 Tape Echo
        self.delay2Dictionary[0x09] = [[[0x60, 0x00, 0x10, 0x50],
                                        [0x60, 0x00, 0x10, 0x61]],[6,2]]                # 0x09 Modulate
        self.delay2Dictionary[0x0A] = [[[0x60, 0x00, 0x10, 0x50],
                                        [0x60, 0x00, 0x10, 0x61],],[6,7]]               # 0x0A SDE-3000


        self.reverbDictionary[0x00] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x00 Ambiance
        self.reverbDictionary[0x01] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x01 Room
        self.reverbDictionary[0x02] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x02 Hall 1
        self.reverbDictionary[0x03] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x03 Hall 2
        self.reverbDictionary[0x04] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x04 Plate
        self.reverbDictionary[0x05] = [[[0x60, 0x00, 0x06, 0x12]],[9]]                  # 0x05 Spring
        self.reverbDictionary[0x06] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x06 Modulate


        self.globalEqDictionary[0x00] = [[[0x00, 0x00, 0x04, 0x33]],[11]]               # 0x00 Eq parametrico
        self.globalEqDictionary[0x01] = [[[0x00, 0x00, 0x04, 0x40]],[11]]               # 0x01 Eq grafico




        self.MODDictionary[0x00] = [[[0x60, 0x00, 0x01, 0x4C]],[7]]                     # 0x00 T Wah
        self.MODDictionary[0x01] = [[[0x60, 0x00, 0x01, 0x54]],[7]]                     # 0x01 Auto Wah  
        self.MODDictionary[0x02] = [[[0x60, 0x00, 0x01, 0x5C]],[6]]                     # 0x02 Sub Wah
        self.MODDictionary[0x03] = [[[0x60, 0x00, 0x01, 0x63]],[5]]                     # 0x03 Compressor
        self.MODDictionary[0x04] = [[[0x60, 0x00, 0x01, 0x69]],[6]]                     # 0x04 Limiter
        self.MODDictionary[0x06] = [[[0x60, 0x00, 0x01, 0x69]],[11]]                    # 0x06 Graphic EQ
        self.MODDictionary[0x07] = [[[0x60, 0x00, 0x01, 0x7C]],[11]]                    # 0x07 Param EQ
        self.MODDictionary[0x09] = [[[0x60, 0x00, 0x02, 0x0E]],[5]]                     # 0x09 Guitar Sim
        self.MODDictionary[0x0A] = [[[0x60, 0x00, 0x02, 0x14]],[3]]                     # 0x0A SlowGear
        self.MODDictionary[0x0C] = [[[0x60, 0x00, 0x02, 0x20]],[8]]                     # 0x0C Wave Synth
        self.MODDictionary[0x0E] = [[[0x60, 0x00, 0x02, 0x31]],[3]]                     # 0x0E Octave
        self.MODDictionary[0x0F] = [[[0x60, 0x00, 0x02, 0x35]],[15]]                    # 0x0F Pitch Shifter
        self.MODDictionary[0x10] = [[[0x60, 0x00, 0x02, 0x45],
                                     [0x60, 0x00, 0x07, 0x18]],[35,1]]                  # 0x10 Harmonist 
        self.MODDictionary[0x12] = [[[0x60, 0x00, 0x02, 0x6E]],[7]]                     # 0x12 Acoustic Processor
        self.MODDictionary[0x13] = [[[0x60, 0x00, 0x02, 0x75]],[8]]                     # 0x13 Phaser
        self.MODDictionary[0x14] = [[[0x60, 0x00, 0x02, 0x7E]],[8]]                     # 0x14 Flanger
        self.MODDictionary[0x15] = [[[0x60, 0x00, 0x03, 0x07]],[4]]                     # 0x15 Tremolo
        self.MODDictionary[0x16] = [[[0x60, 0x00, 0x03, 0x0E]],[5]]                     # 0x16 Rotary 1
        self.MODDictionary[0x17] = [[[0x60, 0x00, 0x03, 0x14]],[3]]                     # 0x16 Uni-V
        self.MODDictionary[0x19] = [[[0x60, 0x00, 0x03, 0x1F]],[5]]                     # 0x19 Slicer
        self.MODDictionary[0x1A] = [[[0x60, 0x00, 0x03, 0x25]],[5]]                     # 0x1A Vibrato
        self.MODDictionary[0x1B] = [[[0x60, 0x00, 0x03, 0x2B]],[4]]                     # 0x1B Ring Mod
        self.MODDictionary[0x1C] = [[[0x60, 0x00, 0x03, 0x30]],[8]]                     # 0x1C Humanizer
        self.MODDictionary[0x1D] = [[[0x60, 0x00, 0x03, 0x39]],[9]]                     # 0x1D 2x2 Chorus
        self.MODDictionary[0x1F] = [[[0x60, 0x00, 0x10, 0x10]],[4]]                     # 0x1F Acoustic Guitar Simulator
        self.MODDictionary[0x23] = [[[0x60, 0x00, 0x10, 0x3D]],[2]]                     # 0x23 Phaser 90E
        self.MODDictionary[0x24] = [[[0x60, 0x00, 0x10, 0x3F]],[4]]                     # 0x24 Flanger 117E
        self.MODDictionary[0x25] = [[[0x60, 0x00, 0x10, 0x68]],[5]]                     # 0x25 WAH 95E
        self.MODDictionary[0x26] = [[[0x60, 0x00, 0x10, 0x6D]],[9]]                     # 0x26 DC30
        self.MODDictionary[0x27] = [[[0x60, 0x00, 0x11, 0x17]],[3]]                     # 0x27 Heavy Octave



        self.FXDictionary[0x00] = [[[0x60, 0x00, 0x03, 0x58]],[7]]                      # 0x00 T Wah           
        self.FXDictionary[0x01] = [[[0x60, 0x00, 0x03, 0x60]],[7]]                      # 0x01 Auto Wah              
        self.FXDictionary[0x02] = [[[0x60, 0x00, 0x03, 0x68]],[6]]                      # 0x02 Sub Wah           
        self.FXDictionary[0x03] = [[[0x60, 0x00, 0x03, 0x6F]],[5]]                      # 0x03 Compressor             
        self.FXDictionary[0x04] = [[[0x60, 0x00, 0x03, 0x75]],[6]]                      # 0x04 Limiter            
        self.FXDictionary[0x06] = [[[0x60, 0x00, 0x03, 0x7C]],[11]]                     # 0x06 Graphic EQ             
        self.FXDictionary[0x07] = [[[0x60, 0x00, 0x04, 0x08]],[11]]                     # 0x07 Param EQ        
        self.FXDictionary[0x09] = [[[0x60, 0x00, 0x04, 0x1A]],[5]]                      # 0x09 Guitar Sim
        self.FXDictionary[0x0A] = [[[0x60, 0x00, 0x04, 0x20]],[3]]                      # 0x0A SlowGear      
        self.FXDictionary[0x0C] = [[[0x60, 0x00, 0x04, 0x2C]],[8]]                      # 0x0C Wave Synth     
        self.FXDictionary[0x0E] = [[[0x60, 0x00, 0x04, 0x3D]],[3]]                      # 0x0E Octave      
        self.FXDictionary[0x0F] = [[[0x60, 0x00, 0x04, 0x41]],[15]]                     # 0x0F Pitch Shifter
        self.FXDictionary[0x10] = [[[0x60, 0x00, 0x04, 0x51],
                                    [0x60, 0x00, 0x07, 0x18]],[35,1]]                   # 0x10 Harmonist        
        self.FXDictionary[0x12] = [[[0x60, 0x00, 0x04, 0x79]],[7]]                      # 0x12 Acoustic Processor       
        self.FXDictionary[0x13] = [[[0x60, 0x00, 0x05, 0x01]],[8]]                      # 0x13 Phaser       
        self.FXDictionary[0x14] = [[[0x60, 0x00, 0x05, 0x0A]],[8]]                      # 0x14 Flanger     
        self.FXDictionary[0x15] = [[[0x60, 0x00, 0x05, 0x13]],[4]]                      # 0x15 Tremolo     
        self.FXDictionary[0x16] = [[[0x60, 0x00, 0x05, 0x1A]],[5]]                      # 0x16 Rotary 1      
        self.FXDictionary[0x17] = [[[0x60, 0x00, 0x05, 0x20]],[3]]                      # 0x16 Uni-V    
        self.FXDictionary[0x19] = [[[0x60, 0x00, 0x05, 0x2B]],[5]]                      # 0x19 Slicer    
        self.FXDictionary[0x1A] = [[[0x60, 0x00, 0x05, 0x31]],[5]]                      # 0x1A Vibrato
        self.FXDictionary[0x1B] = [[[0x60, 0x00, 0x05, 0x37]],[4]]                      # 0x1B Ring Mod
        self.FXDictionary[0x1C] = [[[0x60, 0x00, 0x05, 0x3C]],[8]]                      # 0x1C Humanizer    
        self.FXDictionary[0x1D] = [[[0x60, 0x00, 0x05, 0x45]],[9]]                      # 0x1D 2x2 Chorus
        self.FXDictionary[0x1F] = [[[0x60, 0x00, 0x10, 0x1F]],[4]]                      # 0x1F Acoustic Guitar Simulator
        self.FXDictionary[0x23] = [[[0x60, 0x00, 0x10, 0x43]],[2]]                      # 0x23 Phaser 90E
        self.FXDictionary[0x24] = [[[0x60, 0x00, 0x10, 0x45]],[4]]                      # 0x24 Flanger 117E
        self.FXDictionary[0x25] = [[[0x60, 0x00, 0x10, 0x76]],[5]]                      # 0x25 WAH 95E
        self.FXDictionary[0x26] = [[[0x60, 0x00, 0x10, 0x7B]],[9]]                      # 0x26 DC30
        self.FXDictionary[0x27] = [[[0x60, 0x00, 0x11, 0x1A]],[3]]                      # 0x27 Heavy Octave



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



    def readData(self, address, offset):

        msg = mido.Message('sysex', data=(self.initialTupleSysex + self.readDataSysex + address + offset + self.checkSum(address,offset)))
        self.katanaOUT.send(msg)
        msg = self.katanaIN.receive()
        value = msg.bytes()
        value.pop()
        value.pop()
        del value[0:12]
        return value   

    
    def readFullData(self, address, offset):

        msg = mido.Message('sysex', data=(self.initialTupleSysex + self.readDataSysex + address + offset + self.checkSum(address,offset)))
        self.katanaOUT.send(msg)
        msg = self.katanaIN.receive()
        postData = list(msg.bytes())
        postData.pop()
        postData.pop()
        del postData[0:12]
        rawData = list(msg.bytes())
        rawData.pop()
        del rawData[0]
        return [postData,rawData] 

    def readRawData(self, address, offset):

        msg = mido.Message('sysex', data=(self.initialTupleSysex + self.readDataSysex + address + offset + self.checkSum(address,offset)))
        self.katanaOUT.send(msg)
        msg = self.katanaIN.receive()
        value = msg.bytes()
        value.pop()
        del value[0]
        return value       


    def readCurrentPatchFromKatana(self):

            print('Reading Patch...')

            # --Cadena de efectos------------------------------------------------------

            self.patchChain = self.readRawData(self.chainList[0], [0x00,0x00,0x00, self.chainList[1]])
            self.patchChain[6] = self.setDataSysex[0] 
            self.patchChainMsg = mido.Message('sysex',data=self.patchChain)
   
            # --Lectura de tipos de pedales--------------------------------------------

            # Tipo de PedalFX
            address = self.pedalSelectorAddressDirectory['PedalFX'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['PedalFX'][1]]
            msg = self.readFullData(address,offset)
            self.patchPedalFXType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[0] = mido.Message('sysex',data=msg[1]) 

            # Tipo de Boost
            address = self.pedalSelectorAddressDirectory['Boost'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Boost'][1]]
            msg = self.readFullData(address,offset)
            self.patchBoostType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[1] = mido.Message('sysex',data=msg[1])

            # Tipo de Amp
            address = self.pedalSelectorAddressDirectory['Amp'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Amp'][1]]
            msg = self.readFullData(address,offset)
            self.patchAmpType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[2] = mido.Message('sysex',data=msg[1])

            # Tipo de Eq
            address = self.pedalSelectorAddressDirectory['Eq'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Eq'][1]]
            msg = self.readFullData(address,offset)
            self.patchEqType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[3] = mido.Message('sysex',data=msg[1])

            # Tipo de Delay1
            address = self.pedalSelectorAddressDirectory['Delay1'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Delay1'][1]]
            msg = self.readFullData(address,offset)
            self.patchDelay1Type = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[4] = mido.Message('sysex',data=msg[1])
    
            # Tipo de Delay2
            address = self.pedalSelectorAddressDirectory['Delay2'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Delay2'][1]]
            msg = self.readFullData(address,offset)
            self.patchDelay2Type = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[5] = mido.Message('sysex',data=msg[1])

            # Tipo de Reverb
            address = self.pedalSelectorAddressDirectory['Reverb'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Reverb'][1]]
            msg = self.readFullData(address,offset)
            self.patchReverbType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[6] = mido.Message('sysex',data=msg[1])

            # Tipo de GlobalEq
            address = self.pedalSelectorAddressDirectory['GlobalEq'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['GlobalEq'][1]]
            msg = self.readFullData(address,offset)
            self.patchGlobalEqType = msg[0][1]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[7] = mido.Message('sysex',data=msg[1])

            # Tipo de Cab
            address = self.pedalSelectorAddressDirectory['Cab'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['Cab'][1]]
            msg = self.readRawData(address,offset)
            msg[6] = self.setDataSysex[0]
            self.patchData[8] = mido.Message('sysex',data=msg)

            # Tipo de MOD
            address = self.pedalSelectorAddressDirectory['MOD'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['MOD'][1]]
            msg = self.readFullData(address,offset)
            self.patchMODType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[9] = mido.Message('sysex',data=msg[1])

            # Tipo de FX
            address = self.pedalSelectorAddressDirectory['FX'][0]
            offset = [0x00, 0x00, 0x00, self.pedalSelectorAddressDirectory['FX'][1]]
            msg = self.readFullData(address,offset)
            self.patchFXType = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[10] = mido.Message('sysex',data=msg[1])

            
            # --Estado de efectos------------------------------------------------------

            # Enable PedalFX
            address = self.pedalEnableAddressDirectory['PedalFX'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['PedalFX'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['PedalFX'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[11] = mido.Message('sysex',data=msg[1])
            
            # Enable Boost
            address = self.pedalEnableAddressDirectory['Boost'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['Boost'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['Boost'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[12] = mido.Message('sysex',data=msg[1])
            
            # Enable NoiseSup
            address = self.pedalEnableAddressDirectory['NoiseSup'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['NoiseSup'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['NoiseSup'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[13] = mido.Message('sysex',data=msg[1])

            # Enable Eq
            address = self.pedalEnableAddressDirectory['Eq'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['Eq'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['Eq'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[14] = mido.Message('sysex',data=msg[1])

            # Enable Delay1
            address = self.pedalEnableAddressDirectory['Delay1'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['Delay1'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['Delay1'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[15] = mido.Message('sysex',data=msg[1])

            # Enable Delay2
            address = self.pedalEnableAddressDirectory['Delay2'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['Delay2'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['Delay2'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[16] = mido.Message('sysex',data=msg[1])

            # Enable Reverb
            address = self.pedalEnableAddressDirectory['Reverb'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['Reverb'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['Reverb'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[17] = mido.Message('sysex',data=msg[1])

            # Enable GlobalEq
            address = self.pedalEnableAddressDirectory['GlobalEq'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['GlobalEq'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['GlobalEq'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[18] = mido.Message('sysex',data=msg[1])

            # Enable MOD
            address = self.pedalEnableAddressDirectory['MOD'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['MOD'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['MOD'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[19] = mido.Message('sysex',data=msg[1])

            # Enable FX
            address = self.pedalEnableAddressDirectory['FX'][0]
            offset = [0x00, 0x00, 0x00, self.pedalEnableAddressDirectory['FX'][1]]
            msg = self.readFullData(address,offset)
            self.patchEnableDirectory['FX'] = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[20] = mido.Message('sysex',data=msg[1])
            

            # --Asignacion de EXP------------------------------------------------------            

            address = self.EXPAssignList[0]
            offset = [0x00, 0x00, 0x00, self.EXPAssignList[1][0]]
            msg = self.readFullData(address,offset)
            expAssign = msg[0][0]
            msg[1][6] = self.setDataSysex[0]
            self.patchData[21] = mido.Message('sysex',data=msg[1])

            self.index = 22
            if expAssign >2 and expAssign <9:
                expIndex = 0
                if expAssign==4:
                    expIndex = self.patchMODType
                elif expAssign==6:
                    expIndex = self.patchFXType

                address = self.EXPAssignDictionary[expAssign][expIndex][0]
                offset = [[0x00, 0x00, 0x00, self.EXPAssignDictionary[expAssign][expIndex][1][x]] for x in range(len(self.EXPAssignDictionary[expAssign][expIndex][1]))]
                msg = [self.readRawData(address[x],offset[x]) for x in range (len(address)) ] 
                
                for i in range(len(msg)):
                    msg[i][6] = self.setDataSysex[0]
                    self.patchData[self.index] = mido.Message('sysex',data=msg[i])
                    self.index += 1

            # --PedalFX Type-----------------------------------------------------------

            address = self.pedalFXDictionary[self.patchPedalFXType][0]
            offset = [[0x00, 0x00, 0x00, self.pedalFXDictionary[self.patchPedalFXType][1][x]] for x in range(len(self.pedalFXDictionary[self.patchPedalFXType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            
            # --Boost Type-------------------------------------------------------------

            address = self.boostDictionary[self.patchBoostType][0]
            offset = [[0x00, 0x00, 0x00, self.boostDictionary[self.patchBoostType][1][x]] for x in range(len(self.boostDictionary[self.patchBoostType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1
            
            # --Amp Type---------------------------------------------------------------
            
            address = self.ampDictionary[self.patchAmpType][0]
            offset = [[0x00, 0x00, 0x00, self.ampDictionary[self.patchAmpType][1][x]] for x in range(len(self.ampDictionary[self.patchAmpType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --noiseSup---------------------------------------------------------------

            address = self.noiseSupList[0]
            offset = [0x00, 0x00, 0x00, self.noiseSupList[1]]
            msg = self.readRawData(address,offset)
            msg[6] = self.setDataSysex[0]
            self.patchData[self.index] = mido.Message('sysex',data=msg)
            self.index += 1

            # --volume-----------------------------------------------------------------
           
            address = self.volumeList[0]
            offset = [[0x00, 0x00, 0x00, self.volumeList[1][x]] for x in range(len(self.volumeList[1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --Eq Type----------------------------------------------------------------

            address = self.eqDictionary[self.patchEqType][0]
            offset = [[0x00, 0x00, 0x00, self.eqDictionary[self.patchEqType][1][x]] for x in range(len(self.eqDictionary[self.patchEqType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --Delay1 Type------------------------------------------------------------

            address = self.delay1Dictionary[self.patchDelay1Type][0]
            offset = [[0x00, 0x00, 0x00, self.delay1Dictionary[self.patchDelay1Type][1][x]] for x in range(len(self.delay1Dictionary[self.patchDelay1Type][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --Delay2 Type------------------------------------------------------------

            address = self.delay2Dictionary[self.patchDelay2Type][0]
            offset = [[0x00, 0x00, 0x00, self.delay2Dictionary[self.patchDelay2Type][1][x]] for x in range(len(self.delay2Dictionary[self.patchDelay2Type][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --Reverb Type------------------------------------------------------------

            address = self.reverbDictionary[self.patchReverbType][0]
            offset = [[0x00, 0x00, 0x00, self.reverbDictionary[self.patchReverbType][1][x]] for x in range(len(self.reverbDictionary[self.patchReverbType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --globalEq Type----------------------------------------------------------

            address = self.globalEqDictionary[self.patchGlobalEqType][0]
            offset = [[0x00, 0x00, 0x00, self.globalEqDictionary[self.patchGlobalEqType][1][x]] for x in range(len(self.globalEqDictionary[self.patchGlobalEqType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --Mod Type---------------------------------------------------------------

            address = self.MODDictionary[self.patchMODType][0]
            offset = [[0x00, 0x00, 0x00, self.MODDictionary[self.patchMODType][1][x]] for x in range(len(self.MODDictionary[self.patchMODType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1


            address = self.FXDictionary[self.patchFXType][0]
            offset = [[0x00, 0x00, 0x00, self.FXDictionary[self.patchFXType][1][x]] for x in range(len(self.FXDictionary[self.patchFXType][1]))]
            
            for i in range(len(address)):
                msg = self.readRawData(address[i],offset[i])
                msg[6] = self.setDataSysex[0]
                self.patchData[self.index] = mido.Message('sysex',data=msg)
                self.index += 1

            # --END--------------------------------------------------------------------



            
            print('Patch Reading complete')

    
    def saveToTempData(self):
        
        mido.write_syx_file('tempPatch.syx', self.patchData)
        mido.write_syx_file('tempChain.syx', [self.patchChainMsg])
        
        print(self.patchEnableDirectory)

        with open('tempPatchEnableDirectory.csv', 'w') as f:
            for key in self.patchEnableDirectory.keys():
                f.write("%s,%s\n"%(key,self.patchEnableDirectory[key]))



#    def readCurrentData(self):
#        self.groupNames = os.listdir(self.currentDirectory + '/GroupPresets')
#        
#        #currentDirectory 
#
#    def newGroup(self):
#        print('TODO')
#    
#    def newBank(self):
#        print('TODO')
#
#    def newChian(self):
#        print('TODO')
#    
#    def newPatch(self):
#        print('TODO')


if __name__ == "__main__":

    ktnaReader=KTNAReader()
 
    # Iniciar conexión con el katana
    connectionState = 'Unplugged'

    while connectionState =='Unplugged':

        x=ktnaReader.initConnection(input='KATANA 0', output='KATANA 1')
        if x==1:
            connectionState = 'plugged'
        else:
            print('NO se encuentra KATANA')
            time.sleep(5)
    
    ktnaReader.readCurrentPatchFromKatana()
    ktnaReader.saveToTempData()
    
    # Lectura de prueba
    #ktnaReader.readCurrentPatchFromKatana()
    #value = ktnaReader.readData([0x60,0x00,0x12,0x1F],[0x00,0x00,0x00,0x01])
    #print(value)
    # Escritura de prueba
    # msg = mido.Message('program_change', program=4)
    # x = input('Cambie el parche actual  y presione Enter')
    # ktnaReader.katanaOUT.send(msg)
    # for x in ktnaReader.patchData:        
       # ktnaReader.katanaOUT.send(x)





        
        
        
        
