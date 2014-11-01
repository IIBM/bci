#!/usr/bin/python
from PyQt4  import QtGui, uic
from os import makedirs, path
from ConfigParser import ConfigParser
import time 
from PyQt4  import QtCore 

USER_CONFIG_FILE = path.join(path.dirname(path.abspath(path.dirname(__file__))), "user_config.ini")
DEFAULT_CONFIG_FILE = path.join(path.dirname(path.abspath(path.dirname(__file__))),"user_config_DEFAULT.ini")
DEFAULT_FOLDER = path.expanduser('~') + "/bci_registros/"
freq_availables = [1,2.5,5,10,15,20,25,30] #in kHz
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
save_file = DEFAULT_FOLDER + time.asctime()


def config_editor():    
    #app = QtGui.QApplication([])
    #config.set('FILE','generic_file',QtGui.QFileDialog.getSaveFileName())

    dialog = Config_dialog()
    dialog.setWindowIcon(QtGui.QIcon('Graphics/icon_config.png'))

    dialog.show()
    if dialog.exec_() == QtGui.QDialog.Accepted:
        return config, save_file, CONFIG_PARSER
    else:
        QtCore.QCoreApplication.instance().quit()
        return None

class Config_dialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uic.loadUi(uifile, self)
        
        self.default_files = True
        
        self.fs_line.setValidator(QtGui.QIntValidator())
         
        #self.channels_line.setText(config.get('GENERAL','channels'))
        self.channels_line.setValidator(QtGui.QIntValidator())
        
        self.data_pack_line.setText(config.get('GENERAL','data_package'))
        self.adc_scale.setText(config.get('GENERAL','adc_scale'))
        self.fs_line.setText(config.get('GENERAL','fs'))
        self.channels_line.setText(config.get('GENERAL','channels'))
        
        
        self.data_pack_line.setValidator(QtGui.QIntValidator())
        
        
        self.adc_scale.setValidator(QtGui.QDoubleValidator())
        
        
        self.save_file_label.setText(save_file)
                
        self.rows_cb.setValue(config.getint('GRAPHICS','rows_display'))
        self.two_win_cb.setChecked(config.getboolean('GRAPHICS','two_windows'))

        for i in xrange(len(win_availables)):
            if win_availables[i] == config.get('SIGNAL_PROCESSING','window_type'):
                aux=i
            self.cb_win.addItem(win_availables[i])   
                
        self.cb_win.setCurrentIndex(aux)
        
        self.hp_line.setText(config.get('SIGNAL_PROCESSING','fmin'))
        self.hp_line.setValidator(QtGui.QIntValidator())
        self.filter_l_line.setText(config.get('SIGNAL_PROCESSING', 'length_filter'))
        self.filter_l_line.setValidator(QtGui.QIntValidator())
        
        self.lp_line.setText(config.get('SIGNAL_PROCESSING', 'fmax'))
        self.lp_line.setValidator(QtGui.QIntValidator())
        self.band_pass_cb.setChecked(config.getboolean('SIGNAL_PROCESSING','band_pass'))
        self.change_filter_mode(self.band_pass_cb.isChecked())
        
        #AUNQ PODRIAN CARGARSE POR DEFECTO DE CONFIG FS,CHANN,ADC,ONLINE_MODE
        self.format_config = ConfigParser() 
        self.update_from_loadf_file(path.abspath(config.get('FILE','format_file')))
        

    def My_accept(self):
        if self.check():
            self.update_config()
            config.write(open(USER_CONFIG_FILE,'w'))
            
            self.accept()
    
    def update_config(self):
        
        config.set('GENERAL', 'data_package', str(self.data_pack_line.text()))
        config.set('GENERAL', 'fs', str(self.fs_line.text()))
        config.set('GENERAL', 'channels', str(self.channels_line.text()))
        config.set('GENERAL', 'adc_scale', str(self.adc_scale.text()))
        config.set('GENERAL', 'format',self.format_config.get('GENERAL','format') )
        config.set('GENERAL', 'online_mode',str(not self.offline_mode))
        config.set('GENERAL', 'filtered',self.format_config.get('GENERAL','filtered') )
        
       #? online save in some place?
        config.set('GRAPHICS', 'rows_display', str(self.rows_cb.value()))
        config.set('GRAPHICS', 'two_windows', str(self.two_win_cb.isChecked()))
        
        if self.default_files == True:
            if not path.exists(DEFAULT_FOLDER):
                makedirs(DEFAULT_FOLDER)
                
        config.set('FILE', 'generic_file', str(self.save_file_label.text()))
        config.set('FILE', 'format_file', str(self.format_file_label.text()))
        
        config.set('SIGNAL_PROCESSING', 'band_pass', str(self.band_pass_cb.isChecked()))
        config.set('SIGNAL_PROCESSING', 'fmin', str(self.hp_line.text()))
        config.set('SIGNAL_PROCESSING', 'fmax', str(self.lp_line.text()))
        config.set('SIGNAL_PROCESSING', 'length_filter', str(self.filter_l_line.text()))
        config.set('SIGNAL_PROCESSING', 'window_type', str(win_availables[self.cb_win.currentIndex()]))
        

    def check(self):        
        
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
        
        self.format_file_label.setText(format_config_file)
        f= open(format_config_file, 'r')
        self.info_text.setText(f.read())
        f.close()
        self.format_config.read(format_config_file)
    
        self.fs_line.setText(self.format_config.get('GENERAL','fs'))
        self.channels_line.setText(self.format_config.get('GENERAL','channels'))
        self.offline_mode = not self.format_config.getboolean('GENERAL','online')
        self.adc_scale.setText(self.format_config.get('GENERAL','adc_scale'))
        
        self.change_mode(self.offline_mode)
        global CONFIG_PARSER
        CONFIG_PARSER = Config2Dicc(self.format_config, path.dirname(format_config_file))

    def change_load_file(self):
        load_file =str(QtGui.QFileDialog.getOpenFileName())
        if (load_file !=  ''):
            self.update_from_loadf_file(load_file)
        
        #Falta mostrar info
        
        
    def change_filter_mode(self,pass_band):
        self.lp_line.setEnabled(pass_band)
        
        
    
    
def Config2Dicc(parser_config,dirname):
    thedict = {}
    for section in parser_config.sections():
        thedict[section] = {}
        for key, val in parser_config.items(section):
            thedict[section][key] = val
    thedict["FOLDER"] = dirname
    return thedict
    
if __name__ == '__main__':
    app = QtGui.QApplication([])
    #app.setWindowIcon(QtGui.QIcon('icon_config.png'))
    #config = config_editor()
    dialog = Config_dialog()
    dialog.setWindowIcon(QtGui.QIcon('icon_config.png'))
    dialog.show()
    dialog.exec_()

