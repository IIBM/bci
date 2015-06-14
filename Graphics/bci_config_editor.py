#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

@author: Fernando J. Chaure
"""


from PyQt4  import QtGui, uic
from os import makedirs, path
from ConfigParser import ConfigParser
import time 
from PyQt4  import QtCore 

USER_CONFIG_FILE = path.join(path.dirname(path.abspath(path.dirname(__file__))), "user_config.ini")
DEFAULT_CONFIG_FILE = path.join(path.dirname(path.abspath(path.dirname(__file__))),"user_config_DEFAULT.ini")
DEFAULT_FOLDER = path.expanduser('~') + "/bci_registros/"
freq_availables = [1,2.5,5,10,15,20,25,30] #in kHz
pconfig_availables = ['Single', 'Stereotrode','Tetrode']

win_availables = ['boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 'parzen', 'bohman', 'blackmanharris', 'nuttall', 'barthann']
config = ConfigParser()
load_file_folder = path.expanduser('~') + "/bci_registros/"

if path.isfile(USER_CONFIG_FILE) and  (path.getmtime(DEFAULT_CONFIG_FILE) < path.getmtime(USER_CONFIG_FILE)): 
    config.read(USER_CONFIG_FILE)
else:
    config.read(DEFAULT_CONFIG_FILE)

uifile = path.join(
    path.abspath(
        path.dirname(__file__)),'bciui_config.ui')

CONFIG_PARSER = {}
ltime = time.localtime()
save_file = DEFAULT_FOLDER + '{}{}_{}_{}{}'.format(ltime.tm_year,ltime.tm_mon,ltime.tm_mday,ltime.tm_hour,ltime.tm_min)


def config_editor():    
    #app = QtGui.QApplication([])
    #config.set('FILE','generic_file',QtGui.QFileDialog.getSaveFileName())

##
##
    if not config.getboolean('GRAPHICS','open_conf_editor'):
    	format_conf = Config2Dicc(path.abspath(config.get('FILE','format_file')))
        config.set('FILE', 'generic_file',save_file)
        config.set('GENERAL', 'format',format_conf['GENERAL']['format'])
    	##si es online deberian leerse y forzarse desde la conf del registro:
    	##fs = 20000
    	##channels = 24
    	##adc_scale=1
    	##filtered=False
        return config, save_file, format_conf


    dialog = Config_dialog(config)
#    dialog.setWindowIcon(QtGui.QIcon('Graphics/icon_config.png'))

    dialog.show()
    if dialog.exec_() == QtGui.QDialog.Accepted:
        return config, save_file, CONFIG_PARSER
    else:
        QtCore.QCoreApplication.instance().quit()
        return None

class ConfigCBX(QtGui.QComboBox):
    """ framework between ConfigParser and QComboBox
    """
    def set_conf(self,availables,section,item,update_signal,config):
        self.availables = availables
        self.section = section
        self.item = item
        self.config = config

        for l in range(len(availables)):
            self.addItem(availables[l])
        self.update()
        update_signal.connect(self.update)
        self.currentIndexChanged.connect(self.update_conf)
    
    def update_conf(self,new_index):
        self.config.set(self.section,self.item,self.availables[new_index])
        
    def update(self):
        for l in range(len(self.availables)):
            if self.config.get(self.section,self.item) == self.availables[l]:
                self.setCurrentIndex(l)

class ConfigLE(QtGui.QLineEdit):    
    """ framework between ConfigParser and QLineEdit
    """
    def set_conf(self,var_type,section,item,update_signal,config):
        self.section = section
        self.item = item
        self.config = config

        if var_type == int:
            self.setValidator(QtGui.QIntValidator())
            
        elif var_type == float:
            self.setValidator(QtGui.QDoubleValidator())
        
        self.update()
        update_signal.connect(self.update)
        self.textEdited.connect(self.update_conf)
    
    def update_conf(self,new_index):
        self.config.set(self.section,self.item,str(self.text()))
        
    def update(self):
        self.setText(self.config.get(self.section,self.item))


class Config_dialog(QtGui.QDialog):
    conf_updated_signal = QtCore.pyqtSignal()
    def __init__(self,config):
        QtGui.QDialog.__init__(self)
        uic.loadUi(uifile, self)
        self.config = config
        self.default_files = True
        
        self.prob_cong_cb.set_conf(pconfig_availables,'GENERAL','probes_config',self.conf_updated_signal,self.config)
        self.win_confg_cb.set_conf(win_availables,'SIGNAL_PROCESSING','window_type',self.conf_updated_signal,self.config)
        
        self.fs_line.set_conf(int,'GENERAL','fs',self.conf_updated_signal,self.config)
        self.channels_line.set_conf(int,'GENERAL','channels',self.conf_updated_signal,self.config)
        self.data_pack_line.set_conf(int,'GENERAL','data_package',self.conf_updated_signal,self.config)
        self.adc_scale.set_conf(float,'GENERAL','adc_scale',self.conf_updated_signal,self.config)
        self.hp_line.set_conf(float,'SIGNAL_PROCESSING','fmin',self.conf_updated_signal,self.config)
        self.filter_l_line.set_conf(int,'SIGNAL_PROCESSING','length_filter',self.conf_updated_signal,self.config)
        self.lp_line.set_conf(float,'SIGNAL_PROCESSING','fmax',self.conf_updated_signal,self.config)

        self.rows_cb.setValue(config.getint('GRAPHICS','rows_display'))
        self.two_win_cb.setChecked(config.getboolean('GRAPHICS','two_windows'))        
        
        self.band_pass_cb.setChecked(config.getboolean('SIGNAL_PROCESSING','band_pass'))
        self.change_filter_mode(self.band_pass_cb.isChecked())
        
        self.save_file_label.setText(save_file)
        self.update_from_loadf_file(path.abspath(config.get('FILE','format_file')))

    def My_accept(self):
        if self.check():
            self.update_config()
            config.write(open(USER_CONFIG_FILE,'w'))
            self.accept()
    
    def update_config(self):
        
        config.set('GENERAL', 'format',self.config.get('GENERAL','format'))
        config.set('GENERAL', 'online_mode',str(not self.offline_mode))
        config.set('GENERAL', 'filtered',self.config.get('GENERAL','filtered'))
        
       #? online save in some place?
        config.set('GRAPHICS', 'rows_display', str(self.rows_cb.value()))
        config.set('GRAPHICS', 'two_windows', str(self.two_win_cb.isChecked()))
        
        if self.default_files == True:
            if not path.exists(DEFAULT_FOLDER):
                makedirs(DEFAULT_FOLDER)
                
        config.set('FILE', 'generic_file', str(self.save_file_label.text()))
        config.set('FILE', 'format_file', str(self.format_file_label.text()))


    def check(self):        
        
        if self.band_pass_cb.isChecked():
            if int(self.hp_line.text()) >= int(self.lp_line.text()):
                self.error.setText("Error: High pass freq > Low pass freq")
                return False
                
            if float(self.fs_line.text()) <= 2*float(self.lp_line.text()):
                self.error.setText("Error: Low pass freq > Fs/2")
                return False
            
        elif float(self.fs_line.text()) <= 2*float(self.hp_line.text()):
            self.error.setText("Error: high-pass freq > Fs/2")
            return False
       
        elif (int(self.filter_l_line.text())%2) == 0:
            self.error.setText("Error: High pass with <br>   even number of coefficients")
            return False

        return True        
    
    def change_save_file(self):
        global save_file
        save_file = QtGui.QFileDialog.getSaveFileName()
        self.save_file_label.setText(save_file)
        self.default_files = False

    def change_mode(self, offline):               
        self.channels_line.setEnabled(not offline)
        self.fs_line.setEnabled(not offline)

    def update_from_loadf_file(self,format_config_file):
        global CONFIG_PARSER
        CONFIG_PARSER = Config2Dicc(format_config_file)
        
        self.format_file_label.setText(format_config_file)
        
        f= open(format_config_file, 'r')
        self.info_text.setText(f.read())
        f.close()

        self.config.read(format_config_file)
        
        self.offline_mode = not self.config.getboolean('GENERAL','online')
        
        self.change_mode(self.offline_mode)
        self.conf_updated_signal.emit()
        
    def change_load_file(self):
        load_file =str(QtGui.QFileDialog.getOpenFileName())
        if (load_file !=  ''):
            self.update_from_loadf_file(load_file)
        
        #Falta mostrar info
        
        
    def change_filter_mode(self,pass_band):
        self.lp_line.setEnabled(pass_band)
        
        
    
def Config2Dicc(format_config_file):
    parser_config = ConfigParser()
    parser_config.read(format_config_file)
    thedict = {}
    for section in parser_config.sections():
        thedict[section] = {}
        for key, val in parser_config.items(section):
            thedict[section][key] = val
    thedict["FOLDER"] = path.dirname(format_config_file)
    return thedict


if __name__ == '__main__':
    from os import chdir
    chdir('..')
    app = QtGui.QApplication([])

    dialog = Config_dialog(config)    
    dialog.show()
    dialog.exec_()