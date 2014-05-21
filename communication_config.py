#Frame configuration

L_TRAMA=40 #in 16bits words
COUNTER_POS=1
CHANNELS_POS=4
HASH_POS=39

# Trama 
# byte alto   byte bajo
#0 0xFF        Nro de canales
#1 H_contador  L_contador
#2 config      config
#3 config      config
#4 C0_H        C0_L
# ...         ...
#35 C31_H       C31_L 
#36 AUX1_H      AUX1_L
#37 AUX2_H      AUX2_L
#38 VCC_H       VCC_L
#39 CRC_H       CRC_L