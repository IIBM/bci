bci
===

**Archivos:**

  main: codigo general
  
  capture: funciones relacionadas a la captura y parseo de los datos
  
  libgraph: clases graficas modificadas.

  bci_config_editor: editor de configuracion grafico.
  
  configuration: carga las configuraciones utilizando 
  
  data_processing: manejo de datos y funciones accesorias. signal_config es su archivo de configuracion
  
  multiprocess: crea y configura las colas, tuberias y procesos que se utilizaran. multiprocess_config es su archivo de configuracion
  
  user_config_DEFAULT: Caracteristicas generales que un usuario tipo querria modificar. Si se encuentra el archivo user_config.py se utiliza este en su lugar
  
  *.ui: diseño de menus, ventanas, etc

    
**Dependencias:**

  * Python 2.7 
  * PyQt 4.8+
  * numpy 
  * scipy 
  * pyqtgraph-0.9.8
  * Beep (linux)




