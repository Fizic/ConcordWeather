from windows import *
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
ex = HomeW()
ex.show()
sys.exit(app.exec_())