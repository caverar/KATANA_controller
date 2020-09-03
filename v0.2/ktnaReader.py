#import mido

class KTNAReader:
    # Utilidades de codigo

    pedalList = ['Pedal','Boost', 'Amp','NoiseSup', 'Volume', 'Eq', 'Delay1', 'Delay2', 'Reverb', 'FX', 'MOD', 'GlobalEq', 'Cab']

    # Obligatorios:
    pedalEnableAddressDirectory = {}                                                    # Direcciones de habilitacion de efectos 
    pedalSelectorAddressDirectory = {}                                                  # Direcciones de seleccion de efectos
    noiseSupList = []                                                                   # Datos del supresor del ruido
    volumeDictionary = {}                                                               # Datos del controlador de volumen
    globalEqDictionary = {}                                                             # Datos del Eq global

    # Revisables:
    pedalDictionary = {}                                                                # Tipo de pedal: lista con pares de direccion y numero de datos que le corresponden al efecto
    boostDictionary = {}                                                                # Tipo de boost: lista con pares de direccion y numero de datos que le corresponden al efecto
    ampDictionary = {}                                                                  # Tipo de amp: lista con pares de direccion y numero de datos que le corresponden al efecto
    eqDictionary = {}                                                                   # Tipo de Eq: lista con pares de direccion y numero de parametros que le corresponden al efecto
    delay1Dictionary = {}                                                               # Tipo de Delay1: lista con pares de direccion y numero de parametros que le corresponden al efecto
    delay2Dictionary = {}                                                               # Tipo de Delay2: lista con pares de direccion y numero de parametros que le corresponden al efecto
    reverbDictionary = {}                                                               # Tipo de Reverb: lista con pares de direccion y numero de parametros que le corresponden al efecto
    FXDictionary = {}                                                                   # Tipo de FX: lista con pares de direccion y numero de parametros que le corresponden al efecto
    MODDictionary = {}                                                                  # Tipo de MOD: lista con pares de direccion y numero de parametros que le corresponden al efecto

    # No olvidar eq Global
    def __init__(self):
        

        self.pedalEnableAddressDirectory['Pedal'] = [[0x60, 0x00, 0x06, 0x20], 1]       # off, on, (0,1)
        self.pedalEnableAddressDirectory['Boost'] = [[0x60, 0x00, 0x00, 0x30], 1]       # off, on, (0,1)
        self.pedalEnableAddressDirectory['NoiseSup'] = [[0x60, 0x00, 0x06, 0x63], 1]    # off, on, (0,1)
        self.pedalEnableAddressDirectory['Eq'] = [[0x60, 0x00, 0x01, 0x30], 1]          # off, on, (0,1)
        self.pedalEnableAddressDirectory['Delay1'] = [[0x60, 0x00, 0x05, 0x60], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['Delay2'] = [[0x60, 0x00, 0x10, 0x4E], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['Reverb'] = [[0x60, 0x00, 0x06, 0x10], 1]      # off, on, (0,1)
        self.pedalEnableAddressDirectory['GlobalEq'] = [[0x00, 0x00, 0x04, 0x32], 1]    # off, on, (0,1)
        self.pedalEnableAddressDirectory['MOD'] = [[0x00, 0x00, 0x01, 0x40], 1]         # off, on, (0,1)
        self.pedalEnableAddressDirectory['FX'] = [[0x00, 0x00, 0x03, 0x4C], 1]          # off, on, (0,1)



        self.pedalSelectorAddressDirectory['Pedal'] = [[0x60, 0x00, 0x11, 0x11], 1]     # Tipo de Pedal
        self.pedalSelectorAddressDirectory['Boost'] = [[0x60, 0x00, 0x00, 0x31], 1]     # Tipo de Boost
        self.pedalSelectorAddressDirectory['Amp'] = [[0x60, 0x00, 0x00, 0x51], 1]       # Tipo de Amp
        self.pedalSelectorAddressDirectory['Eq'] = [[0x60, 0x00, 0x11, 0x04], 1]        # Tipo de eq
        self.pedalSelectorAddressDirectory['Delay1'] = [[0x60, 0x00, 0x05, 0x61], 1]    # Tipo de Delay1
        self.pedalSelectorAddressDirectory['Delay2'] = [[0x60, 0x00, 0x10, 0x4F], 1]    # Tipo de Delay1
        self.pedalSelectorAddressDirectory['Reverb'] = [[0x60, 0x00, 0x06, 0x11], 1]    # Tipo de Reverb
        self.pedalSelectorAddressDirectory['GlobalEq'] = [[0x00, 0x00, 0x04, 0x3E], 2]  # Tipo de GlobalEq
        self.pedalSelectorAddressDirectory['Cab'] = [[0x00, 0x00, 0x04, 0x31], 1]       # Tipo de Cabina
        self.pedalSelectorAddressDirectory['MOD'] = [[0x00, 0x00, 0x01, 0x41], 1]       # Tpoo de MOD
        self.pedalSelectorAddressDirectory['FX'] = [[0x00, 0x00, 0x03, 0x4D], 1]        # Tipo de FX
        
        
        self.pedalDictionary[0x00] = [[[0x60, 0x00, 0x06, 0x26]],[6]]                   # 00-WAH
        self.pedalDictionary[0x01] = [[[0x60, 0x00, 0x06, 0x22]],[4]]                   # 01-Pedal Bend
        self.pedalDictionary[0x02] = [[[0x60, 0x00, 0x11, 0x12]],[5]]                   # 02-Wah 95E        
        

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
        self.ampDictionary[0x10] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 10-Pro Crunch
        self.ampDictionary[0x11] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 11-[Crunch] Tweed
        self.ampDictionary[0x12] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 12-Deluxe Crunch
        self.ampDictionary[0x13] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 13-VO Drive
        self.ampDictionary[0x14] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 14-VO Lead
        self.ampDictionary[0x15] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 15-Match Drive
        self.ampDictionary[0x16] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 16-BG Lead
        self.ampDictionary[0x17] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 17-BG Drive
        self.ampDictionary[0x18] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 18-MS-1959 I
        self.ampDictionary[0x19] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 19-MS-1959 I+II
        self.ampDictionary[0x20] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 10-R-Fier Vintage
        self.ampDictionary[0x21] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 21-R-Fier Modern
        self.ampDictionary[0x22] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 22-T-Amp Lead
        self.ampDictionary[0x23] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 23-[BROWN] SLDN
        self.ampDictionary[0x24] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                     # 24-[LEAD] 5150 Drive
        self.ampDictionary[0x25] = [[[0x60, 0x00, 0x00, 0x52],
                                     [0x60, 0x00, 0x00, 0x63]],[8,8]]                   # 25-Custom
        
        self.noiseSupList = [[0x60, 0x00, 0x06, 0x64],2]                                # Datos del supresor
        
        self.volumeDictionary[0x00] = [[[0x60, 0x00, 0x06, 0x33],
                                        [0x60, 0x00, 0x07, 0x10]],[1,1]]                # Datos de volumen
                
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
        self.globalEqDictionary[0x00] = [[[0x00, 0x00, 0x04, 0x40]],[11]]               # 0x01 Eq grafico

if __name__ == "__main__":
   ktnaReader=KTNAReader()
   print('El lector funciona') 


        
        
        
        