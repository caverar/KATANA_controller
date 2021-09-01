import os
import time
import csv
import mido

class KatanaReader:

    # Objetos de conexión

    initial_tuple_sysex = [0x41, 0x00, 0x00, 0x00, 0x00, 0x33]  # Katana ID
    read_data_sysex = [0x11]                                    # byte de lectura MIDI
    set_data_sysex = [0x12]                                     # byte de escritura MIDI
    current_directory = os.getcwd()                             # Directorio actual
    katana_out = None                                           # Canal Midi de salida
    katana_in = None                                            # Canal Midi de entrada

    # Utilidades de código

    pedal_list = ["PedalFX","Boost", "Amp","NoiseSup", "Volume", "Eq", "Delay1", 
                  "Delay2", "Reverb", "FX", "MOD", "GlobalEq", "Cab"]

    # Obligatorios:

    pedal_enable_address_directory = {}                         # Direcciones para activar efectos 
    pedal_selector_address_directory = {}                       # Direcciones de selección efectos
    noise_suppressor_list = []                                  # Datos del supresor del ruido
    volume_list = []                                            # Datos del controlador de volumen
    global_eq_dictionary = {}                                   # Datos del Eq global
    exp_assign_list = []                                        # Parametro controlado por EXP
    chain_list = []                                             # Registros y numero de datos del chain

    # Opcionales: listas con pares de dirección y numero de datos que le corresponden al efecto

    exp_pedal_dictionary = {}                                   # Tipo de pedalFX (Wah, pitch Bend)
    boost_dictionary = {}                                       # Tipo de boost
    amp_dictionary = {}                                         # Tipo de Amp 
    eq_dictionary = {}                                          # Tipo de Eq 
    delay1_dictionary = {}                                      # Tipo de Delay1 
    delay2_dictionary = {}                                      # Tipo de Delay2
    reverb_dictionary = {}                                      # Tipo de Reverb
    fx_dictionary = {}                                          # Tipo de FX
    mod_dictionary = {}                                         # Tipo de MOD

    # Parametros de cada tipo de asignación del pedal de expresión, agrupados en un diccionario, para cada tipo de asignación
    
    exp_assign_dictionary = {}                                    
    
    # Patch Data(midi SysEx messages):

    patch_chain = None
    patch_chain_message = None

    # Estado de habilitación de cada tipo de efectos de la cadena
    patch_enable_directory = {}                                 

    # Mensaje con la cadena del patch
    void_SysEx_message = mido.Message("program_change", program = 0)
    
    # Conjunto de mensajes con el parche
    patch_data = [None for x in range(50)]                       

    patch_exp_pedal_type = None                                                               
    patch_boost_type = None
    patch_amp_type = None
    patch_eq_type = None
    patch_delay1_type = None
    patch_delay2_type = None 
    patch_reverb_type = None
    patch_fx_type = None
    patch_mod_type = None
    patch_global_eq_type = None
  
    # Current Data    

    
    
    def __init__(self) -> None:
        
        self.patch_data = [self.void_SysEx_message for x in range(40)]  

        # Dirección de 32 bits, cantidad de datos

        self.chain_list = [[0x60, 0x00, 0x07, 0x20], 20]                                    # Cadena de efectos


        self.pedal_enable_address_directory["PedalFX"] = [[0x60, 0x00, 0x06, 0x20], 1]      # off, on, (0,1)
        self.pedal_enable_address_directory["Boost"] = [[0x60, 0x00, 0x00, 0x30], 1]        # off, on, (0,1)
        self.pedal_enable_address_directory["NoiseSup"] = [[0x60, 0x00, 0x06, 0x63], 1]     # off, on, (0,1)
        self.pedal_enable_address_directory["Eq"] = [[0x60, 0x00, 0x01, 0x30], 1]           # off, on, (0,1)
        self.pedal_enable_address_directory["Delay1"] = [[0x60, 0x00, 0x05, 0x60], 1]       # off, on, (0,1)
        self.pedal_enable_address_directory["Delay2"] = [[0x60, 0x00, 0x10, 0x4E], 1]       # off, on, (0,1)
        self.pedal_enable_address_directory["Reverb"] = [[0x60, 0x00, 0x06, 0x10], 1]       # off, on, (0,1)
        self.pedal_enable_address_directory["GlobalEq"] = [[0x00, 0x00, 0x04, 0x32], 1]     # off, on, (0,1)
        self.pedal_enable_address_directory["MOD"] = [[0x60, 0x00, 0x01, 0x40], 1]          # off, on, (0,1)
        self.pedal_enable_address_directory["FX"] = [[0x60, 0x00, 0x03, 0x4C], 1]           # off, on, (0,1)



        self.pedal_selector_address_directory["PedalFX"] = [[0x60, 0x00, 0x11, 0x11], 1]    # Tipo de Pedal
        self.pedal_selector_address_directory["Boost"] = [[0x60, 0x00, 0x00, 0x31], 1]      # Tipo de Boost
        self.pedal_selector_address_directory["Amp"] = [[0x60, 0x00, 0x00, 0x51], 1]        # Tipo de Amp
        self.pedal_selector_address_directory["Eq"] = [[0x60, 0x00, 0x11, 0x04], 1]         # Tipo de eq
        self.pedal_selector_address_directory["Delay1"] = [[0x60, 0x00, 0x05, 0x61], 1]     # Tipo de Delay1
        self.pedal_selector_address_directory["Delay2"] = [[0x60, 0x00, 0x10, 0x4F], 1]     # Tipo de Delay1
        self.pedal_selector_address_directory["Reverb"] = [[0x60, 0x00, 0x06, 0x11], 1]     # Tipo de Reverb
        self.pedal_selector_address_directory["GlobalEq"] = [[0x00, 0x00, 0x04, 0x3E], 2]   # Tipo de GlobalEq
        self.pedal_selector_address_directory["Cab"] = [[0x00, 0x00, 0x04, 0x31], 1]        # Tipo de Cabina
        self.pedal_selector_address_directory["MOD"] = [[0x60, 0x00, 0x01, 0x41], 1]        # Tipo de MOD
        self.pedal_selector_address_directory["FX"] = [[0x60, 0x00, 0x03, 0x4D], 1]         # Tipo de FX
        
        
        

        self.exp_assign_list = [[0x60, 0x00, 0x12, 0x1F],[1]]                               # Retorna el parametro que se puede controlar mediante el pedal de expresión
                
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


        self.exp_assign_dictionary = [{} for x in range (9)]
        self.exp_assign_dictionary[0x03][0x00] = [[[0x60, 0x00, 0x13, 0x00],
                                                   [0x60, 0x00, 0x13, 0x20]],[1,2]]     # 0x03: Parametros de asignación de Booster
        
        

        self.exp_assign_dictionary[0x05][0x00] = [[[0x60, 0x00, 0x13, 0x01],
                                                   [0x60, 0x00, 0x13, 0x22]],[1,4]]     # 0x05: Parametros de asignación de Delay 1
        self.exp_assign_dictionary[0x07][0x00] = [[[0x60, 0x00, 0x13, 0x01],
                                                   [0x60, 0x00, 0x13, 0x22]],[1,4]]     # 0x07: Parametros de asignación de Delay 2
        self.exp_assign_dictionary[0x08][0x00] = [[[0x60, 0x00, 0x13, 0x02],
                                                   [0x60, 0x00, 0x13, 0x26]],[1,4]]     # 0x08: Parametros de asignación de Reverb

        
        # 0x04: Asignación para cada una las 30 modulaciones

        
        self.exp_assign_dictionary[0x04][0x00] = [[[0x60, 0x00, 0x13, 0x0F],
                                                   [0x60, 0x00, 0x13, 0x42]],[1,2]]     # 0x00 T Wah        
        self.exp_assign_dictionary[0x04][0x01] = [[[0x60, 0x00, 0x13, 0x10],
                                                   [0x60, 0x00, 0x13, 0x44]],[1,2]]     # 0x01 Auto Wah     
        self.exp_assign_dictionary[0x04][0x02] = [[[0x60, 0x00, 0x13, 0x11],
                                                   [0x60, 0x00, 0x13, 0x46]],[1,2]]     # 0x02 Sub Wah                      
        self.exp_assign_dictionary[0x04][0x03] = [[[0x60, 0x00, 0x13, 0x0D],
                                                   [0x60, 0x00, 0x13, 0x3E]],[1,2]]     # 0x03 Compressor   
        self.exp_assign_dictionary[0x04][0x04] = [[[0x60, 0x00, 0x13, 0x0E],
                                                   [0x60, 0x00, 0x13, 0x40]],[1,2]]     # 0x04 Limiter          
        self.exp_assign_dictionary[0x04][0x06] = [[[0x60, 0x00, 0x13, 0x12],
                                                   [0x60, 0x00, 0x13, 0x48]],[1,2]]     # 0x06 Graphic EQ       
        self.exp_assign_dictionary[0x04][0x07] = [[[0x60, 0x00, 0x13, 0x13],
                                                   [0x60, 0x00, 0x13, 0x4A]],[1,2]]     # 0x07 Param EQ         
        self.exp_assign_dictionary[0x04][0x09] = [[[0x60, 0x00, 0x13, 0x14],
                                                   [0x60, 0x00, 0x13, 0x4C]],[1,2]]     # 0x09 Guitar Sim    
        self.exp_assign_dictionary[0x04][0x0A] = [[[0x60, 0x00, 0x13, 0x0B],
                                                   [0x60, 0x00, 0x13, 0x3A]],[1,2]]     # 0x0A SlowGear         
        self.exp_assign_dictionary[0x04][0x0C] = [[[0x60, 0x00, 0x13, 0x17],
                                                   [0x60, 0x00, 0x13, 0x52]],[1,2]]     # 0x0C Wave Synth       
        self.exp_assign_dictionary[0x04][0x0E] = [[[0x60, 0x00, 0x13, 0x18],
                                                   [0x60, 0x00, 0x13, 0x54]],[1,2]]     # 0x0E Octave          
        self.exp_assign_dictionary[0x04][0x0F] = [[[0x60, 0x00, 0x13, 0x19],
                                                   [0x60, 0x00, 0x13, 0x56]],[1,4]]     # 0x0F Pitch Shifter    
        self.exp_assign_dictionary[0x04][0x10] = [[[0x60, 0x00, 0x13, 0x1A],
                                                   [0x60, 0x00, 0x13, 0x5A]],[1,4]]     # 0x10 Harmonist
        self.exp_assign_dictionary[0x04][0x12] = [[[0x60, 0x00, 0x13, 0x16],
                                                   [0x60, 0x00, 0x13, 0x50]],[1,2]]     # 0x12 Acoustic Processor
        self.exp_assign_dictionary[0x04][0x13] = [[[0x60, 0x00, 0x13, 0x05],
                                                   [0x60, 0x00, 0x13, 0x2E]],[1,2]]     # 0x13 Phaser
        self.exp_assign_dictionary[0x04][0x14] = [[[0x60, 0x00, 0x13, 0x04],
                                                   [0x60, 0x00, 0x13, 0x2C]],[1,2]]     # 0x14 Flanger
        self.exp_assign_dictionary[0x04][0x15] = [[[0x60, 0x00, 0x13, 0x07],
                                                   [0x60, 0x00, 0x13, 0x32]],[1,2]]     # 0x15 Tremolo
        self.exp_assign_dictionary[0x04][0x16] = [[[0x60, 0x00, 0x13, 0x09],
                                                   [0x60, 0x00, 0x13, 0x36]],[1,2]]     # 0x16 Rotary 1
        self.exp_assign_dictionary[0x04][0x17] = [[[0x60, 0x00, 0x13, 0x06],
                                                   [0x60, 0x00, 0x13, 0x30]],[1,2]]     # 0x16 Uni-V
        self.exp_assign_dictionary[0x04][0x19] = [[[0x60, 0x00, 0x13, 0x0C],
                                                   [0x60, 0x00, 0x13, 0x3C]],[1,2]]     # 0x19 Slicer
        self.exp_assign_dictionary[0x04][0x1A] = [[[0x60, 0x00, 0x13, 0x08],
                                                   [0x60, 0x00, 0x13, 0x34]],[1,2]]     # 0x1A Vibrato
        self.exp_assign_dictionary[0x04][0x1B] = [[[0x60, 0x00, 0x13, 0x0A],
                                                   [0x60, 0x00, 0x13, 0x38]],[1,2]]     # 0x1B Ring Mod
        self.exp_assign_dictionary[0x04][0x1C] = [[[0x60, 0x00, 0x13, 0x1B],
                                                   [0x60, 0x00, 0x13, 0x5E]],[1,2]]     # 0x1C Humanizer
        self.exp_assign_dictionary[0x04][0x1D] = [[[0x60, 0x00, 0x13, 0x03],
                                                   [0x60, 0x00, 0x13, 0x2A]],[1,2]]     # 0x1D 2x2 Chorus
        self.exp_assign_dictionary[0x04][0x1F] = [[[0x60, 0x00, 0x13, 0x15],
                                                   [0x60, 0x00, 0x13, 0x4E]],[1,2]]     # 0x1F Acoustic Guitar Simulator
        self.exp_assign_dictionary[0x04][0x23] = [[[0x60, 0x00, 0x13, 0x1C],
                                                   [0x60, 0x00, 0x13, 0x60]],[1,2]]     # 0x23 Phaser 90E
        self.exp_assign_dictionary[0x04][0x24] = [[[0x60, 0x00, 0x13, 0x1D],
                                                   [0x60, 0x00, 0x13, 0x62]],[1,2]]     # 0x24 Flanger 117E
        self.exp_assign_dictionary[0x04][0x25] = [[[0x60, 0x00, 0x13, 0x1E],
                                                   [0x60, 0x00, 0x13, 0x64]],[1,2]]     # 0x25 WAH 95E
        self.exp_assign_dictionary[0x04][0x26] = [[[0x60, 0x00, 0x13, 0x1F],
                                                   [0x60, 0x00, 0x13, 0x66]],[1,4]]     # 0x26 DC30
        self.exp_assign_dictionary[0x04][0x27] = [[[0x60, 0x00, 0x13, 0x6A]],[3]]       # 0x27 Heavy Octave
                                        

        self.exp_assign_dictionary[0x06] = self.exp_assign_dictionary[0x04]             # 0x06: Asignación para cada uno los 30 FX post


        
        self.exp_pedal_dictionary[0x00] = [[[0x60, 0x00, 0x06, 0x26]],[6]]              # 00-WAH
        self.exp_pedal_dictionary[0x01] = [[[0x60, 0x00, 0x06, 0x22]],[4]]              # 01-Pedal Bend
        self.exp_pedal_dictionary[0x02] = [[[0x60, 0x00, 0x11, 0x12]],[5]]              # 02-Wah 95E  

        self.boost_dictionary[0x00] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 00-Mid Boost
        self.boost_dictionary[0x01] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 01-Clean Boost
        self.boost_dictionary[0x02] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 02-Treble Boost
        self.boost_dictionary[0x03] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 03-Crunch
        self.boost_dictionary[0x04] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 04-Natural OD
        self.boost_dictionary[0x05] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 05-Warm OD
        self.boost_dictionary[0x06] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 06-Fat DS
        self.boost_dictionary[0x07] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 07-Lead DS
        self.boost_dictionary[0x08] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 08-Metal DS
        self.boost_dictionary[0x09] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 09-OCT Fuzz
        self.boost_dictionary[0x0A] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 10-Blues OD
        self.boost_dictionary[0x0B] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 11-OD-1
        self.boost_dictionary[0x0C] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 12-Tubescreamer
        self.boost_dictionary[0x0D] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 13-Turbo OD
        self.boost_dictionary[0x0E] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 14-Dist
        self.boost_dictionary[0x0F] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 15-Rat
        self.boost_dictionary[0x10] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 16-GuV DS
        self.boost_dictionary[0x11] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 17-DST+
        self.boost_dictionary[0x12] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 18-Metal Zone
        self.boost_dictionary[0x13] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 19-"60s Fuzz
        self.boost_dictionary[0x14] = [[[0x60, 0x00, 0x00, 0x32]],[7]]                  # 10-Muff Fuzz
        self.boost_dictionary[0x15] = [[[0x60, 0x00, 0x00, 0x32]],[13]]                 # 21-Custom


        self.amp_dictionary[0x00] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 00-Natural Clean
        self.amp_dictionary[0x01] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 01-[Acoustic] Full Range
        self.amp_dictionary[0x02] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 02-Combo Crunch
        self.amp_dictionary[0x03] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 03-Stack Crunch
        self.amp_dictionary[0x04] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 04-HiGain Stack
        self.amp_dictionary[0x05] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 05-Power Drive
        self.amp_dictionary[0x06] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 06-Extreme Lead
        self.amp_dictionary[0x07] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 07-Core Metal
        self.amp_dictionary[0x08] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 08-[Clean] JC-120
        self.amp_dictionary[0x09] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 09-Clean Twin
        self.amp_dictionary[0x0A] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 10-Pro Crunch
        self.amp_dictionary[0x0B] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 11-[Crunch] Tweed
        self.amp_dictionary[0x0C] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 12-Deluxe Crunch
        self.amp_dictionary[0x0D] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 13-VO Drive
        self.amp_dictionary[0x0E] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 14-VO Lead
        self.amp_dictionary[0x0F] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 15-Match Drive
        self.amp_dictionary[0x10] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 16-BG Lead
        self.amp_dictionary[0x11] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 17-BG Drive
        self.amp_dictionary[0x12] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 18-MS-1959 I
        self.amp_dictionary[0x13] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 19-MS-1959 I+II
        self.amp_dictionary[0x14] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 10-R-Fier Vintage
        self.amp_dictionary[0x15] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 21-R-Fier Modern
        self.amp_dictionary[0x16] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 22-T-Amp Lead
        self.amp_dictionary[0x17] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 23-[BROWN] SLDN
        self.amp_dictionary[0x18] = [[[0x60, 0x00, 0x00, 0x52]],[8]]                    # 24-[LEAD] 5150 Drive
        self.amp_dictionary[0x19] = [[[0x60, 0x00, 0x00, 0x52],
                                      [0x60, 0x00, 0x00, 0x63]],[8,8]]                  # 25-Custom
        
        self.noise_suppressor_list = [[0x60, 0x00, 0x06, 0x64],2]                       # Datos del supresor de ruido
        
        self.volume_list = [[[0x60, 0x00, 0x06, 0x33],
                             [0x60, 0x00, 0x07, 0x10]],[1,1]]                           # Datos de volumen
                
        self.eq_dictionary[0x00] = [[[0x60, 0x00, 0x01, 0x31]],[11]]                    # 0x00: Eq Parametric
        self.eq_dictionary[0x01] = [[[0x60, 0x00, 0x11, 0x05]],[11]]                    # 0x00: Eq Graphic
        

        self.delay1_dictionary[0x00] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x00 Digital
        self.delay1_dictionary[0x01] = [[[0x60, 0x00, 0x05, 0x62]],[11]]                 # 0x01 Pan        
        self.delay1_dictionary[0x02] = [[[0x60, 0x00, 0x05, 0x62]],[11]]                 # 0x02 Stereo
        self.delay1_dictionary[0x03] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x03 N/A
        self.delay1_dictionary[0x04] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x04 N/A
        self.delay1_dictionary[0x05] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x05 N/A
        self.delay1_dictionary[0x06] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x06 Reverse
        self.delay1_dictionary[0x07] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x07 Analog
        self.delay1_dictionary[0x08] = [[[0x60, 0x00, 0x05, 0x62]],[6]]                  # 0x08 Tape Echo
        self.delay1_dictionary[0x09] = [[[0x60, 0x00, 0x05, 0x62],
                                         [0x60, 0x00, 0x05, 0x73]],[6,2]]                # 0x09 Modulate
        self.delay1_dictionary[0x0A] = [[[0x60, 0x00, 0x05, 0x62],
                                         [0x60, 0x00, 0x05, 0x73],
                                         [0x60, 0x00, 0x10, 0x49]],[6,2,5]]              # 0x0A SDE-3000
        
        
        self.delay2_dictionary[0x00] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x00 Digital
        self.delay2_dictionary[0x01] = [[[0x60, 0x00, 0x10, 0x50]],[11]]                 # 0x01 Pan        
        self.delay2_dictionary[0x02] = [[[0x60, 0x00, 0x10, 0x50]],[11]]                 # 0x02 Stereo
        self.delay2_dictionary[0x03] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x03 N/A
        self.delay2_dictionary[0x04] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x04 N/A
        self.delay2_dictionary[0x05] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x05 N/A
        self.delay2_dictionary[0x06] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x06 Reverse
        self.delay2_dictionary[0x07] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x07 Analog
        self.delay2_dictionary[0x08] = [[[0x60, 0x00, 0x10, 0x50]],[6]]                  # 0x08 Tape Echo
        self.delay2_dictionary[0x09] = [[[0x60, 0x00, 0x10, 0x50],
                                         [0x60, 0x00, 0x10, 0x61]],[6,2]]                # 0x09 Modulate
        self.delay2_dictionary[0x0A] = [[[0x60, 0x00, 0x10, 0x50],
                                         [0x60, 0x00, 0x10, 0x61],],[6,7]]               # 0x0A SDE-3000


        self.reverb_dictionary[0x00] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x00 Ambiance
        self.reverb_dictionary[0x01] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x01 Room
        self.reverb_dictionary[0x02] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x02 Hall 1
        self.reverb_dictionary[0x03] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x03 Hall 2
        self.reverb_dictionary[0x04] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x04 Plate
        self.reverb_dictionary[0x05] = [[[0x60, 0x00, 0x06, 0x12]],[9]]                  # 0x05 Spring
        self.reverb_dictionary[0x06] = [[[0x60, 0x00, 0x06, 0x12]],[8]]                  # 0x06 Modulate


        self.global_eq_dictionary[0x00] = [[[0x00, 0x00, 0x04, 0x33]],[11]]             # 0x00 Eq parametrico
        self.global_eq_dictionary[0x01] = [[[0x00, 0x00, 0x04, 0x40]],[11]]             # 0x01 Eq gráfico




        self.mod_dictionary[0x00] = [[[0x60, 0x00, 0x01, 0x4C]],[7]]                     # 0x00 T Wah
        self.mod_dictionary[0x01] = [[[0x60, 0x00, 0x01, 0x54]],[7]]                     # 0x01 Auto Wah  
        self.mod_dictionary[0x02] = [[[0x60, 0x00, 0x01, 0x5C]],[6]]                     # 0x02 Sub Wah
        self.mod_dictionary[0x03] = [[[0x60, 0x00, 0x01, 0x63]],[5]]                     # 0x03 Compressor
        self.mod_dictionary[0x04] = [[[0x60, 0x00, 0x01, 0x69]],[6]]                     # 0x04 Limiter
        self.mod_dictionary[0x06] = [[[0x60, 0x00, 0x01, 0x69]],[11]]                    # 0x06 Graphic EQ
        self.mod_dictionary[0x07] = [[[0x60, 0x00, 0x01, 0x7C]],[11]]                    # 0x07 Param EQ
        self.mod_dictionary[0x09] = [[[0x60, 0x00, 0x02, 0x0E]],[5]]                     # 0x09 Guitar Sim
        self.mod_dictionary[0x0A] = [[[0x60, 0x00, 0x02, 0x14]],[3]]                     # 0x0A SlowGear
        self.mod_dictionary[0x0C] = [[[0x60, 0x00, 0x02, 0x20]],[8]]                     # 0x0C Wave Synth
        self.mod_dictionary[0x0E] = [[[0x60, 0x00, 0x02, 0x31]],[3]]                     # 0x0E Octave
        self.mod_dictionary[0x0F] = [[[0x60, 0x00, 0x02, 0x35]],[15]]                    # 0x0F Pitch Shifter
        self.mod_dictionary[0x10] = [[[0x60, 0x00, 0x02, 0x45],
                                      [0x60, 0x00, 0x07, 0x18]],[35,1]]                  # 0x10 Harmonist 
        self.mod_dictionary[0x12] = [[[0x60, 0x00, 0x02, 0x6E]],[7]]                     # 0x12 Acoustic Processor
        self.mod_dictionary[0x13] = [[[0x60, 0x00, 0x02, 0x75]],[8]]                     # 0x13 Phaser
        self.mod_dictionary[0x14] = [[[0x60, 0x00, 0x02, 0x7E]],[8]]                     # 0x14 Flanger
        self.mod_dictionary[0x15] = [[[0x60, 0x00, 0x03, 0x07]],[4]]                     # 0x15 Tremolo
        self.mod_dictionary[0x16] = [[[0x60, 0x00, 0x03, 0x0E]],[5]]                     # 0x16 Rotary 1
        self.mod_dictionary[0x17] = [[[0x60, 0x00, 0x03, 0x14]],[3]]                     # 0x16 Uni-V
        self.mod_dictionary[0x19] = [[[0x60, 0x00, 0x03, 0x1F]],[5]]                     # 0x19 Slicer
        self.mod_dictionary[0x1A] = [[[0x60, 0x00, 0x03, 0x25]],[5]]                     # 0x1A Vibrato
        self.mod_dictionary[0x1B] = [[[0x60, 0x00, 0x03, 0x2B]],[4]]                     # 0x1B Ring Mod
        self.mod_dictionary[0x1C] = [[[0x60, 0x00, 0x03, 0x30]],[8]]                     # 0x1C Humanizer
        self.mod_dictionary[0x1D] = [[[0x60, 0x00, 0x03, 0x39]],[9]]                     # 0x1D 2x2 Chorus
        self.mod_dictionary[0x1F] = [[[0x60, 0x00, 0x10, 0x10]],[4]]                     # 0x1F Acoustic Guitar Simulator
        self.mod_dictionary[0x23] = [[[0x60, 0x00, 0x10, 0x3D]],[2]]                     # 0x23 Phaser 90E
        self.mod_dictionary[0x24] = [[[0x60, 0x00, 0x10, 0x3F]],[4]]                     # 0x24 Flanger 117E
        self.mod_dictionary[0x25] = [[[0x60, 0x00, 0x10, 0x68]],[5]]                     # 0x25 WAH 95E
        self.mod_dictionary[0x26] = [[[0x60, 0x00, 0x10, 0x6D]],[9]]                     # 0x26 DC30
        self.mod_dictionary[0x27] = [[[0x60, 0x00, 0x11, 0x17]],[3]]                     # 0x27 Heavy Octave



        self.fx_dictionary[0x00] = [[[0x60, 0x00, 0x03, 0x58]],[7]]                     # 0x00 T Wah           
        self.fx_dictionary[0x01] = [[[0x60, 0x00, 0x03, 0x60]],[7]]                     # 0x01 Auto Wah              
        self.fx_dictionary[0x02] = [[[0x60, 0x00, 0x03, 0x68]],[6]]                     # 0x02 Sub Wah           
        self.fx_dictionary[0x03] = [[[0x60, 0x00, 0x03, 0x6F]],[5]]                     # 0x03 Compressor             
        self.fx_dictionary[0x04] = [[[0x60, 0x00, 0x03, 0x75]],[6]]                     # 0x04 Limiter            
        self.fx_dictionary[0x06] = [[[0x60, 0x00, 0x03, 0x7C]],[11]]                    # 0x06 Graphic EQ             
        self.fx_dictionary[0x07] = [[[0x60, 0x00, 0x04, 0x08]],[11]]                    # 0x07 Param EQ        
        self.fx_dictionary[0x09] = [[[0x60, 0x00, 0x04, 0x1A]],[5]]                     # 0x09 Guitar Sim
        self.fx_dictionary[0x0A] = [[[0x60, 0x00, 0x04, 0x20]],[3]]                     # 0x0A SlowGear      
        self.fx_dictionary[0x0C] = [[[0x60, 0x00, 0x04, 0x2C]],[8]]                     # 0x0C Wave Synth     
        self.fx_dictionary[0x0E] = [[[0x60, 0x00, 0x04, 0x3D]],[3]]                     # 0x0E Octave      
        self.fx_dictionary[0x0F] = [[[0x60, 0x00, 0x04, 0x41]],[15]]                    # 0x0F Pitch Shifter
        self.fx_dictionary[0x10] = [[[0x60, 0x00, 0x04, 0x51],
                                     [0x60, 0x00, 0x07, 0x18]],[35,1]]                  # 0x10 Harmonist        
        self.fx_dictionary[0x12] = [[[0x60, 0x00, 0x04, 0x79]],[7]]                     # 0x12 Acoustic Processor       
        self.fx_dictionary[0x13] = [[[0x60, 0x00, 0x05, 0x01]],[8]]                     # 0x13 Phaser       
        self.fx_dictionary[0x14] = [[[0x60, 0x00, 0x05, 0x0A]],[8]]                     # 0x14 Flanger     
        self.fx_dictionary[0x15] = [[[0x60, 0x00, 0x05, 0x13]],[4]]                     # 0x15 Tremolo     
        self.fx_dictionary[0x16] = [[[0x60, 0x00, 0x05, 0x1A]],[5]]                     # 0x16 Rotary 1      
        self.fx_dictionary[0x17] = [[[0x60, 0x00, 0x05, 0x20]],[3]]                     # 0x16 Uni-V    
        self.fx_dictionary[0x19] = [[[0x60, 0x00, 0x05, 0x2B]],[5]]                     # 0x19 Slicer    
        self.fx_dictionary[0x1A] = [[[0x60, 0x00, 0x05, 0x31]],[5]]                     # 0x1A Vibrato
        self.fx_dictionary[0x1B] = [[[0x60, 0x00, 0x05, 0x37]],[4]]                     # 0x1B Ring Mod
        self.fx_dictionary[0x1C] = [[[0x60, 0x00, 0x05, 0x3C]],[8]]                     # 0x1C Humanizer    
        self.fx_dictionary[0x1D] = [[[0x60, 0x00, 0x05, 0x45]],[9]]                     # 0x1D 2x2 Chorus
        self.fx_dictionary[0x1F] = [[[0x60, 0x00, 0x10, 0x1F]],[4]]                     # 0x1F Acoustic Guitar Simulator
        self.fx_dictionary[0x23] = [[[0x60, 0x00, 0x10, 0x43]],[2]]                     # 0x23 Phaser 90E
        self.fx_dictionary[0x24] = [[[0x60, 0x00, 0x10, 0x45]],[4]]                     # 0x24 Flanger 117E
        self.fx_dictionary[0x25] = [[[0x60, 0x00, 0x10, 0x76]],[5]]                     # 0x25 WAH 95E
        self.fx_dictionary[0x26] = [[[0x60, 0x00, 0x10, 0x7B]],[9]]                     # 0x26 DC30
        self.fx_dictionary[0x27] = [[[0x60, 0x00, 0x11, 0x1A]],[3]]                     # 0x27 Heavy Octave



    def init_connection(self, input: str = "KATANA MIDI 1", output: str = "KATANA MIDI 1") -> int:
        try:
            self.katana_out = mido.open_output(output)
            self.katana_in = mido.open_input(input)   
            return 1
        except:
            return 0
    

    def checksum(self, address: list, data: list) -> list:
        values = address + data
        accumulator = 0
        for value in values:
            accumulator = (accumulator + value) & 0x7F
            checksum = (128 - accumulator) & 0x7F
        return [checksum]



    def read_data(self, address: list, offset: list) -> list:

        msg = mido.Message("sysex", data=(self.initial_tuple_sysex + self.read_data_sysex + address + 
                            offset + self.checksum(address,offset)))
        self.katana_out.send(msg)
        msg = self.katana_in.receive()
        value = msg.bytes()
        value.pop()
        value.pop()
        del value[0:12]
        return value   

    
    def read_full_data(self, address: list, offset: list) -> list:

        msg = mido.Message("sysex", data=(self.initial_tuple_sysex + self.read_data_sysex + address + 
                            offset + self.checksum(address,offset)))
        self.katana_out.send(msg)
        msg = self.katana_in.receive()
        headerless_data = list(msg.bytes())
        headerless_data.pop()
        headerless_data.pop()
        del headerless_data[0:12]
        raw_data = list(msg.bytes())
        raw_data.pop()
        del raw_data[0]
        return [headerless_data,raw_data] 

    def read_raw_data(self, address: list, offset: list) -> list:

        msg = mido.Message("sysex", data=(self.initial_tuple_sysex + self.read_data_sysex + address + 
                            offset + self.checksum(address,offset)))
        self.katana_out.send(msg)
        msg = self.katana_in.receive()
        value = msg.bytes()
        value.pop()
        del value[0]
        return value       


    def read_current_patch_from_katana(self) -> None:

            print("Reading Patch...")

            # --Cadena de efectos------------------------------------------------------

            self.patch_chain = self.read_raw_data(self.chain_list[0], [0x00,0x00,0x00, self.chain_list[1]])
            self.patch_chain[6] = self.set_data_sysex[0] 
            self.patch_chain_message = mido.Message("sysex", data = self.patch_chain)
   
            # --Lectura de tipos de pedales--------------------------------------------

            # Tipo de Exp Pedal
            address = self.pedal_selector_address_directory["PedalFX"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["PedalFX"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_exp_pedal_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[0] = mido.Message("sysex", data = msg[1]) 

            # Tipo de Boost
            address = self.pedal_selector_address_directory["Boost"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Boost"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_boost_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[1] = mido.Message("sysex", data = msg[1])

            # Tipo de Amp
            address = self.pedal_selector_address_directory["Amp"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Amp"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_amp_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[2] = mido.Message("sysex", data = msg[1])

            # Tipo de Eq
            address = self.pedal_selector_address_directory["Eq"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Eq"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_eq_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[3] = mido.Message("sysex", data = msg[1])

            # Tipo de Delay1
            address = self.pedal_selector_address_directory["Delay1"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Delay1"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_delay1_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[4] = mido.Message("sysex", data = msg[1])
    
            # Tipo de Delay2
            address = self.pedal_selector_address_directory["Delay2"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Delay2"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_delay2_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[5] = mido.Message("sysex", data = msg[1])

            # Tipo de Reverb
            address = self.pedal_selector_address_directory["Reverb"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Reverb"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_reverb_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[6] = mido.Message("sysex", data = msg[1])

            # Tipo de GlobalEq
            address = self.pedal_selector_address_directory["GlobalEq"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["GlobalEq"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_global_eq_type = msg[0][1]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[7] = mido.Message("sysex", data = msg[1])

            # Tipo de Cab
            address = self.pedal_selector_address_directory["Cab"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["Cab"][1]]
            msg = self.read_full_data(address,offset)
            msg[6] = self.set_data_sysex[0]
            self.patch_data[8] = mido.Message("sysex", data = msg)

            # Tipo de MOD
            address = self.pedal_selector_address_directory["MOD"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["MOD"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_mod_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[9] = mido.Message("sysex", data = msg[1])

            # Tipo de FX
            address = self.pedal_selector_address_directory["FX"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_selector_address_directory["FX"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_fx_type = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[10] = mido.Message("sysex", data = msg[1])

            
            # --Estado de efectos------------------------------------------------------

            # Enable PedalFX
            address = self.pedal_enable_address_directory["PedalFX"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["PedalFX"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["PedalFX"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[11] = mido.Message("sysex", data = msg[1])
            
            # Enable Boost
            address = self.pedal_enable_address_directory["Boost"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["Boost"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["Boost"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[12] = mido.Message("sysex", data = msg[1])
            
            # Enable NoiseSup
            address = self.pedal_enable_address_directory["NoiseSup"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["NoiseSup"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["NoiseSup"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[13] = mido.Message("sysex", data = msg[1])

            # Enable Eq
            address = self.pedal_enable_address_directory["Eq"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["Eq"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["Eq"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[14] = mido.Message("sysex", data = msg[1])

            # Enable Delay1
            address = self.pedal_enable_address_directory["Delay1"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["Delay1"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["Delay1"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[15] = mido.Message("sysex", data = msg[1])

            # Enable Delay2
            address = self.pedal_enable_address_directory["Delay2"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["Delay2"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["Delay2"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[16] = mido.Message("sysex", data = msg[1])

            # Enable Reverb
            address = self.pedal_enable_address_directory["Reverb"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["Reverb"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["Reverb"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[17] = mido.Message("sysex", data = msg[1])

            # Enable GlobalEq
            address = self.pedal_enable_address_directory["GlobalEq"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["GlobalEq"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["GlobalEq"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[18] = mido.Message("sysex", data = msg[1])

            # Enable MOD
            address = self.pedal_enable_address_directory["MOD"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["MOD"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["MOD"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[19] = mido.Message("sysex", data = msg[1])

            # Enable FX
            address = self.pedal_enable_address_directory["FX"][0]
            offset = [0x00, 0x00, 0x00, self.pedal_enable_address_directory["FX"][1]]
            msg = self.read_full_data(address,offset)
            self.patch_enable_directory["FX"] = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[20] = mido.Message("sysex", data = msg[1])
            

            # --Asignación de EXP------------------------------------------------------            

            address = self.exp_assign_list[0]
            offset = [0x00, 0x00, 0x00, self.exp_assign_list[1][0]]
            msg = self.read_full_data(address,offset)
            exp_assign = msg[0][0]
            msg[1][6] = self.set_data_sysex[0]
            self.patch_data[21] = mido.Message("sysex", data = msg[1])

            self.index = 22
            if exp_assign>2 and exp_assign<9:
                expIndex = 0
                if exp_assign == 4:
                    expIndex = self.patch_mod_type
                elif exp_assign == 6:
                    expIndex = self.patch_fx_type

                address = self.exp_assign_dictionary[exp_assign][expIndex][0]
                offset = [[0x00, 0x00, 0x00, self.exp_assign_dictionary[exp_assign][expIndex][1][x]] 
                          for x in range(len(self.exp_assign_dictionary[exp_assign][expIndex][1]))]
                msg = [self.read_raw_data(address[x],offset[x]) for x in range (len(address)) ] 
                
                for i in range(len(msg)):
                    msg[i][6] = self.set_data_sysex[0]
                    self.patch_data[self.index] = mido.Message("sysex", data = msg[i])
                    self.index += 1

            # --EXP Pedal Type---------------------------------------------------------

            address = self.exp_pedal_dictionary[self.patch_exp_pedal_type][0]
            offset = [[0x00, 0x00, 0x00, self.exp_pedal_dictionary[self.patch_exp_pedal_type][1][x]] 
                      for x in range(len(self.exp_pedal_dictionary[self.patch_exp_pedal_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            
            # --Boost Type-------------------------------------------------------------

            address = self.boost_dictionary[self.patch_boost_type][0]
            offset = [[0x00, 0x00, 0x00, self.boost_dictionary[self.patch_boost_type][1][x]] 
                      for x in range(len(self.boost_dictionary[self.patch_boost_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1
            
            # --Amp Type---------------------------------------------------------------
            
            address = self.amp_dictionary[self.patch_amp_type][0]
            offset = [[0x00, 0x00, 0x00, self.amp_dictionary[self.patch_amp_type][1][x]] 
                      for x in range(len(self.amp_dictionary[self.patch_amp_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --noiseSup---------------------------------------------------------------

            address = self.noise_suppressor_list[0]
            offset = [0x00, 0x00, 0x00, self.noise_suppressor_list[1]]
            msg = self.read_raw_data(address,offset)
            msg[6] = self.set_data_sysex[0]
            self.patch_data[self.index] = mido.Message("sysex", data = msg)
            self.index += 1

            # --Volume-----------------------------------------------------------------
           
            address = self.volume_list[0]
            offset = [[0x00, 0x00, 0x00, self.volume_list[1][x]] for x in range(len(self.volume_list[1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --Eq Type----------------------------------------------------------------

            address = self.eq_dictionary[self.patch_eq_type][0]
            offset = [[0x00, 0x00, 0x00, self.eq_dictionary[self.patch_eq_type][1][x]] 
                      for x in range(len(self.eq_dictionary[self.patch_eq_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --Delay1 Type------------------------------------------------------------

            address = self.delay1_dictionary[self.patch_delay1_type][0]
            offset = [[0x00, 0x00, 0x00, self.delay1_dictionary[self.patch_delay1_type][1][x]] 
                      for x in range(len(self.delay1_dictionary[self.patch_delay1_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --Delay2 Type------------------------------------------------------------

            address = self.delay2_dictionary[self.patch_delay2_type][0]
            offset = [[0x00, 0x00, 0x00, self.delay2_dictionary[self.patch_delay2_type][1][x]] 
                      for x in range(len(self.delay2_dictionary[self.patch_delay2_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --Reverb Type------------------------------------------------------------

            address = self.reverb_dictionary[self.patch_reverb_type][0]
            offset = [[0x00, 0x00, 0x00, self.reverb_dictionary[self.patch_reverb_type][1][x]] 
                      for x in range(len(self.reverb_dictionary[self.patch_reverb_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --globalEq Type----------------------------------------------------------

            address = self.global_eq_dictionary[self.patch_global_eq_type][0]
            offset = [[0x00, 0x00, 0x00, self.global_eq_dictionary[self.patch_global_eq_type][1][x]] 
                      for x in range(len(self.global_eq_dictionary[self.patch_global_eq_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --Mod Type---------------------------------------------------------------

            address = self.mod_dictionary[self.patch_mod_type][0]
            offset = [[0x00, 0x00, 0x00, self.mod_dictionary[self.patch_mod_type][1][x]] 
                      for x in range(len(self.mod_dictionary[self.patch_mod_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1


            address = self.fx_dictionary[self.patch_fx_type][0]
            offset = [[0x00, 0x00, 0x00, self.fx_dictionary[self.patch_fx_type][1][x]] 
                      for x in range(len(self.fx_dictionary[self.patch_fx_type][1]))]
            
            for i in range(len(address)):
                msg = self.read_raw_data(address[i],offset[i])
                msg[6] = self.set_data_sysex[0]
                self.patch_data[self.index] = mido.Message("sysex", data = msg)
                self.index += 1

            # --END--------------------------------------------------------------------



            
            print("Patch Reading complete")

    
    def saveToTempData(self) -> None:
        
        mido.write_syx_file("tempPatch.syx", self.patch_data)
        mido.write_syx_file("tempChain.syx", [self.patch_chain_message])
        
        print(self.patch_enable_directory)

        with open("tempPatchEnableDirectory.csv", "w") as f:
            for key in self.patch_enable_directory.keys():
                f.write("%s,%s\n"%(key,self.patch_enable_directory[key]))



#    def readCurrentData(self):
#        self.groupNames = os.listdir(self.current_directory + "/GroupPresets")
#        
#        #current_directory 
#
#    def newGroup(self):
#        print("TODO")
#    
#    def newBank(self):
#        print("TODO")
#
#    def newChian(self):
#        print("TODO")
#    
#    def newPatch(self):
#        print("TODO")


def main():

    katana_reader=KatanaReader()
 
    # Iniciar conexión con el katana
    connection_state = "Unplugged"

    while connection_state =="Unplugged":

        # Linux
        # x = katana_reader.init_connection(input="KATANA 0", output="KATANA 1")    
        # Windows
        x = katana_reader.init_connection(input="KATANA MIDI 1", output="KATANA MIDI 1")                  
        
        if x == 1:
            connection_state = "plugged"
        else:
            print("NO se encuentra KATANA")
            time.sleep(5)
    
    katana_reader.read_current_patch_from_katana()
    katana_reader.saveToTempData()
    
    # Lectura de prueba
    #katana_reader.read_current_patch_from_katana()
    #value = katana_reader.readData([0x60,0x00,0x12,0x1F],[0x00,0x00,0x00,0x01])
    #print(value)
    # Escritura de prueba
    # msg = mido.Message("program_change", program=4)
    # x = input("Cambie el parche actual  y presione Enter")
    # katana_reader.katana_out.send(msg)
    # for x in katana_reader.patch_data:        
       # katana_reader.katana_out.send(x)



if __name__ == "__main__":
    main()

        
        
        
        
