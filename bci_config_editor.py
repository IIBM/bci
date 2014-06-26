#!/usr/bin/python


from PyQt4  import QtGui,uic
import os
from ConfigParser import ConfigParser
import time 
from scipy import signal


USER_CONFIG_FILE=os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config.ini")

DEFAULT_FOLDER=os.path.expanduser('~')+"/bci_registros/"
freq_availables=[1,2.5,5,10,15,20,25,30] #in kHz
win_availables=['boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 'parzen', 'bohman', 'blackmanharris', 'nuttall', 'barthann']
config=ConfigParser()
save_file=DEFAULT_FOLDER+time.asctime()


if os.path.isfile(USER_CONFIG_FILE):
    config.read(USER_CONFIG_FILE)
    
else:
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config_DEFAULT.ini"))

uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui_config.ui')

def config_editor():    
    #app = QtGui.QApplication([])
    #config.set('FILE','generic_file',QtGui.QFileDialog.getSaveFileName())
    dialog=Config_dialog()
    dialog.show()
    if dialog.exec_() == QtGui.QDialog.Accepted:
        return config
    else:
        exit()
    

class Config_dialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(uifile, self)
        for i in xrange(len(freq_availables)):
            if freq_availables[i]*1000 == config.getint('GENERAL','fs'):
                aux=i
            self.cb_freq.addItem(str(freq_availables[i])+'kHz')
        self.cb_freq.setCurrentIndex(aux)  
        self.default_files=True
         
        self.channels_line.setText(config.get('GENERAL','channels'))
        self.channels_line.setValidator(QtGui.QIntValidator())
        self.data_pack_line.setText(config.get('GENERAL','data_package'))
        self.data_pack_line.setValidator(QtGui.QIntValidator())
        self.data_pack_line.setText(config.get('GENERAL','data_package'))
        self.data_pack_line.setValidator(QtGui.QIntValidator())
        self.offline_mode_cb.setChecked(not config.getboolean('GENERAL','online_mode'))
        self.change_mode(self.offline_mode_cb.isChecked())
        
        self.load_file=config.get('FILE','load_file')
        self.load_file_label.setText(self.load_file)
        self.save_file_label.setText(save_file)
        
        self.rows_cb.setValue(config.getint('GRAPHICS','rows_display'))
        self.two_win_cb.setChecked(config.getboolean('GRAPHICS','two_windows'))
        
        self.frame_l.setText(config.get('DATA_FRAME','l_frame'))
        self.frame_l.setValidator(QtGui.QIntValidator())
        self.counter_pos.setText(config.get('DATA_FRAME','counter_pos'))
        self.counter_pos.setValidator(QtGui.QIntValidator())
        self.channels_pos.setText(config.get('DATA_FRAME','channels_pos'))
        self.channels_pos.setValidator(QtGui.QIntValidator())
        self.xor_pos.setText(config.get('DATA_FRAME','hash_pos'))
        self.xor_pos.setValidator(QtGui.QIntValidator())
        self.ampcount.setText(config.get('DATA_FRAME','ampcount'))
        self.ampcount.setValidator(QtGui.QIntValidator())
        
        
        for i in xrange(len(win_availables)):
            if win_availables[i] == config.get('SIGNAL_PROCESSING','window_type'):
                aux=i
            self.cb_win.addItem(win_availables[i])   
                
        self.cb_win.setCurrentIndex(aux)
        
        self.hp_line.setText(config.get('SIGNAL_PROCESSING','fmin'))
        self.hp_line.setValidator(QtGui.QIntValidator())
        self.filter_l_line.setText(config.get('SIGNAL_PROCESSING','length_filter'))
        self.filter_l_line.setValidator(QtGui.QIntValidator())
        
        self.lp_line.setText(config.get('SIGNAL_PROCESSING','fmax'))
        self.lp_line.setValidator(QtGui.QIntValidator())
        self.band_pass_cb.setChecked(config.getboolean('SIGNAL_PROCESSING','band_pass'))
        self.change_filter_mode(self.band_pass_cb.isChecked())



    def My_accept(self):
        if self.check():
            self.update_config()
            config.write(open(USER_CONFIG_FILE,'w'))
            self.accept()
    
    def update_config(self):
        config.set('FILE','load_file',self.load_file)
        
        
        config.set('GENERAL','online_mode',str(not self.offline_mode_cb.isChecked()))
        config.set('GENERAL','fs',str(freq_availables[self.cb_freq.currentIndex()]*1000))
        config.set('GENERAL','channels',str(self.channels_line.text()))
        config.set('GENERAL','data_package',str(self.data_pack_line.text()))
        
        config.set('GRAPHICS','rows_display',str(self.rows_cb.value()))
        config.set('GRAPHICS','two_windows',str(self.two_win_cb.isChecked()))
        
        if self.default_files == True:
            if not os.path.exists(DEFAULT_FOLDER):
                os.makedirs(DEFAULT_FOLDER)
        config.set('FILE','generic_file',str(self.save_file_label.text()))
        
        config.set('DATA_FRAME','l_frame',str(self.frame_l.text()))
        config.set('DATA_FRAME','counter_pos',str(self.counter_pos.text()))
        config.set('DATA_FRAME','channels_pos',str(self.channels_pos.text()))
        config.set('DATA_FRAME','hash_pos',str(self.xor_pos.text()))
        config.set('DATA_FRAME','ampcount',str(self.ampcount.text()))
        
        config.set('SIGNAL_PROCESSING','band_pass',str(self.band_pass_cb.isChecked()))
        config.set('SIGNAL_PROCESSING','fmin',str(self.hp_line.text()))
        config.set('SIGNAL_PROCESSING','fmax',str(self.lp_line.text()))
        config.set('SIGNAL_PROCESSING','length_filter',str(self.filter_l_line.text()))
        config.set('SIGNAL_PROCESSING','window_type',str(win_availables[self.cb_win.currentIndex()]))
        
    def check(self):
        if int(self.frame_l.text()) < (int(self.channels_line.text())  + int(self.channels_pos.text())):
            self.error.setText("Error: # channels/long frame/channel pos")
            return False
        
        
        if self.band_pass_cb.isChecked():
            if int(self.hp_line.text()) >= int(self.lp_line.text()):
                self.error.setText("Error: High pass freq > Low pass freq")
                return False
                
            if freq_availables[self.cb_freq.currentIndex()]*1000 <= 2*int(self.lp_line.text()):
                self.error.setText("Error: Low pass freq > Fs/2")
                return False
            
       
        elif (int(self.filter_l_line.text())%2) == 0:
            self.error.setText("Error: High pass with <br>   even number of coefficients")
            return False
            
        if freq_availables[self.cb_freq.currentIndex()]*1000 <= 2*int(self.hp_line.text()):
            self.error.setText("Error: High pass freq > Fs/2")
            return False
        
        return True        
    
    def change_save_file(self):
        save_file=QtGui.QFileDialog.getSaveFileName()
        self.save_file_label.setText(save_file)
        self.default_files=False
        
    def change_mode(self,offline):
        #if offline:
            #self.cb_freq.addItem("new FS!!!!!!!!!") #cargar de archivo
            #self.cb_freq.setCurrentIndex(self.cb_freq.count()-1)
        #else:
            #self.cb_freq.removeItem(self.cb_freq.count()-1)
        #self.channels_line.setEnabled(not offline)
        #self.cb_freq.setEnabled(not offline)
        pass
        
    def change_load_file(self):
        self.load_file=QtGui.QFileDialog.getSaveFileName()
        self.load_file_label.setText(self.load_file)
   
    def change_filter_mode(self,pass_band):
        self.lp_line.setEnabled(pass_band)
