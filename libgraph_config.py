#!/usr/bin/python
#Graphics configuration
import os
import config

FFT_L=8192*2 #largo del vector con el q se realiza fft
FFT_N=4  #cantidad de ffts q se promedian
FFT_L_PAQ=3 #cantidad de paqueques q se concatenan para fft
ROWS_DISPLAY=3
TIME_SPIKE_COUNT=1 #ventana de tiempo donde se estima la frec de disparo.Aprox: secons 
DISPLAY_LIMY=200
