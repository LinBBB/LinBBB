# encoding:utf-8
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QDialog
from gui_ui.register import Ui_Register_Form
from gui_ui.Login import *

# 注册页面
class Register_Page(Ui_Register_Form,QWidget):
    def __init__(self):
        super(Register_Page, self).__init__()
        self.setupUi(self)
        self.show()




app = QApplication(sys.argv)
register_page = Register_Page()

sys.exit(app.exec_())