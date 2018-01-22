bci
===

This GUI was designed to provide a fast and flexible interface for processing, acquiring and visualizing data from extracellular electrodes.

Everything is written in Ptyhon, using PyQt and PyQtGraph for the ui.

**Dependencies**

  * Python 2.7 
  * PyQt 4.8+
  * numpy 
  * scipy >= 0.10
  * pyqtgraph >= 0.9.8
  * Beep (linux)

**Example**
 
Run Example/data_maker.sh for build the example data.


**Instalation**

with virtualenv

apt install virtualenv python-dev

virtualenv --always-copy bmi-venv
source bmi-venv/bin/activate

pip install numpy pyqtgraph scipy

numpy=1.12.1 
pyqtgraph=0.10.0
scipy=0.19.0

download from riverbankcomputing.com, pyqt4 y sip
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.2/sip-4.19.2.tar.gz

SIP:
extract
python configure.py
make
make install (whitout the '--always-copy' modifier requires sudo)

PyQt:
python configure-ng.py
make
make install


**Use**
source bmi-venv/bin/activate
python main.py
