#!/usr/bin/python


from PyQt4  import QtGui,uic
import os
from ConfigParser import ConfigParser
import time 

USER_CONFIG_FILE=os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config.ini")
freq_availables=[1,2.5,5,10,15,20,25,30] #in kHz
config=ConfigParser()
save_file=time.asctime()


if os.path.isfile(USER_CONFIG_FILE):
    config.read(USER_CONFIG_FILE)
    
else:
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"user_config_DEFAULT.ini"))

uifile = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)),'bciui_config.ui')

def config_editor():    
    app = QtGui.QApplication([])
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
        self.channels_line.setText(config.get('GENERAL','channels'))
        self.channels_line.setValidator(QtGui.QIntValidator())
        self.data_pack_line.setText(config.get('GENERAL','data_package'))
        self.data_pack_line.setValidator(QtGui.QIntValidator())
        
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
        
        
        
    def My_accept(self):
        if self.check():
            self.update_config()
            #config.write(open(USER_CONFIG_FILE,'w'))
            self.accept()
    
    def update_config(self):
        config.set('FILE','load_file',self.load_file)
        
        
        config.set('GENERAL','online_mode',str(not self.offline_mode_cb.isChecked()))
        #config.set('GENERAL','fs',str(freq_availables[self.cb_freq.currentIndex()]*1000))
        config.set('GENERAL','channels',str(self.channels_line.text()))
        config.set('GENERAL','data_package',str(self.data_pack_line.text()))
        
        config.set('GRAPHICS','rows_display',str(self.rows_cb.value()))
        config.set('GRAPHICS','two_windows',str(self.two_win_cb.isChecked()))
        
        config.set('DATA_FRAME','l_frame',str(self.frame_l.text()))
        config.set('DATA_FRAME','counter_pos',str(self.counter_pos.text()))
        config.set('DATA_FRAME','channels_pos',str(self.channels_pos.text()))
        config.set('DATA_FRAME','hash_pos',str(self.xor_pos.text()))
        
        
        
        
    def check(self):

        if int(self.frame_l.text()) < (int(self.channels_line.text())  + int(self.channels_pos.text())):
            self.error.setText("Error: # channels/long frame/channel pos")
            return False
        
        #config.set('DATA_FRAME','l_frame',str(self.frame_l.text()))
        #config.set('DATA_FRAME','counter_pos',str(self.counter_pos.text()))
        #config.set('DATA_FRAME','channels_pos',str(self.channels_pos.text()))
        #config.set('DATA_FRAME','hash_pos',str(self.xor_pos.text()))
        
            
        return True        
    
    def change_save_file(self):
        save_file=QtGui.QFileDialog.getSaveFileName()
        self.save_file_label.setText(save_file)
    
    def change_mode(self,offline):
        if offline:
            self.cb_freq.addItem("new FS!!!!!!!!!")
            self.cb_freq.setCurrentIndex(self.cb_freq.count()-1)
        else:
            self.cb_freq.removeItem(self.cb_freq.count()-1)
        self.channels_line.setEnabled(not offline)
        self.cb_freq.setEnabled(not offline)
        self.channels_line.setEnabled(not offline)
    def change_load_file(self):
        self.load_file=QtGui.QFileDialog.getSaveFileName()
        self.load_file_label.setText(self.load_file)
   
