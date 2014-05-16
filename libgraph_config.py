#!/usr/bin/python
#Graphics configuration
import os
import config

BEEP_FREQ="700" #Hz (str)       
ch_colors=['r','y','g','c']
NOT_SAVING_MESSAGE='Without Saving'
SAVING_MESSAGE='Writing in:'
FFT_L=8192*2 #largo del vector con el q se realiza fft
FFT_N=4  #cantidad de ffts q se promedian
FFT_L_PAQ=3 #cantidad de paqueques q se concatenan para fft
ROWS_DISPLAY=3
MESSAGE_TIME=5 #duration message display
TIME_SPIKE_COUNT=1 #ventana de tiempo donde se estima la frec de disparo.Aprox: secons 
DISPLAY_LIMY=200

        
uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui.ui')
        
if config.TWO_WINDOWS:
    second_win_file = os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)),'second_window.ui')
