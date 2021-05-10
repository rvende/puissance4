#from power import *
from fen import *
import sys
import threading

if __name__ == '__main__':
   App = QtWidgets.QApplication(sys.argv)
   window = Ui_Puissance4Plus1(1)
   #window.show()
   threading.Thread(target=window.worker.main,args=()).start()
   sys.exit(App.exec())