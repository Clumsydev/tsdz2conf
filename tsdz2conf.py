import sys, os, json, string
from pathlib import Path
from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QVBoxLayout,  QHBoxLayout, \
                            QStyleOptionTab, QStyleOptionFocusRect, QStylePainter, QTabBar, QTabWidget, QStyle, \
                            QLineEdit, QLabel, QFormLayout, QRadioButton, QGroupBox, QPushButton

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            # we are running in a pyinstaller made bundle
            bundle_dir = Path(sys._MEIPASS)
        else:
            # we are running in a normal Python environment
            bundle_dir = Path(__file__).parent
        
        self.display_ver = "VLCD5" # not sure yet, if there are display specific things

        self.setupGui(self.display_ver)
        self.dataDir = Path(bundle_dir / 'config')
        self.mappingFilename = 'mapping.json'
        self.mappedData = self.getDataFromJSON(self.dataDir / self.mappingFilename)

        # the following code fills in the descriptions and edit fields we defined in the mapping file
        for row_dict in self.mappedData:
            if row_dict['Category'] == 'Battery':
                self.bat_form_lay.addRow(InfoLabel(row_dict['Description']), LineEdit(str(row_dict['Default_Value'])))
            elif row_dict['Category'] == 'Motor':
                self.motor_form_lay.addRow(InfoLabel(row_dict['Description']), LineEdit(str(row_dict['Default_Value'])))

        self.bat_w.update()
        self.motor_w.update()

    def setupGui(self, display_v = "VLCD5"):
        self.title = 'TSDZ2 Configurator'
        self.display_v = display_v
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.centralWidget = QWidget(self)
        self.layout = QVBoxLayout(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        self.w = TabWidget(self.centralWidget)
        self.w.setFixedHeight(self.height-100)

        self.bat_w, self.motor_w, self.pwm_w, self.wheel_w, self.assist_w, self.console_w = QWidget(), QWidget(), QWidget(), QWidget(), QWidget(), QWidget()
        self.categories = [ ["Battery", self.bat_w], 
                            ["Motor", self.motor_w],
                            ["PWM Duty Cycle", self.pwm_w],
                            ["Wheel and PAS", self.wheel_w],
                            ["Assist Levels", self.assist_w],
        ]
        
        for cat in self.categories:
            self.w.addTab(cat[1], cat[0]) # String, Widget-obj
        
        self.w.setStyleSheet('''
            QTabBar::tab {height: 140px; width: 60px; font-weight: bold; font-size: 14px;}
            ''')

        #self.bat_lay = QVBoxLayout(self.bat_w)

        self.bat_form_lay = QFormLayout(self.bat_w)
        #self.bat_form_lay.addRow(InfoLabel("Max. battery power [W]"), LineEdit('510'))
        #self.bat_form_lay.addRow(InfoLabel("Max. battery current [A]"), LineEdit('13'))
        self.bat_w.setLayout(self.bat_form_lay)

        self.motor_lay = QVBoxLayout(self.motor_w)

        self.motor_rbutton_lay = QHBoxLayout()
        self.rbutton1 = QRadioButton("36 V")
        self.rbutton2 = QRadioButton("48 V")
        self.rbutton3 = QRadioButton("36 V - High Cadence")
        self.rbutton4 = QRadioButton("48 V - High Cadence")
        self.motor_rbutton_lay.addWidget(self.rbutton1)
        self.motor_rbutton_lay.addWidget(self.rbutton2)
        self.motor_rbutton_lay.addWidget(self.rbutton3)
        self.motor_rbutton_lay.addWidget(self.rbutton4)

        self.motor_rbutton_groupbox = QGroupBox("Motor selection: ")
        self.motor_rbutton_groupbox.setLayout(self.motor_rbutton_lay)
        self.motor_rbutton_groupbox.setFixedSize(500,60)

        self.motor_form_lay = QFormLayout()
        #self.motor_form_lay.addRow(InfoLabel("Bla"), LineEdit('13'))

        self.motor_lay.addWidget(self.motor_rbutton_groupbox)
        self.motor_lay.addLayout(self.motor_form_lay)
        self.motor_w.setLayout(self.motor_lay)

        self.cmdButW = QWidget()
        self.cmdBut_lay = QHBoxLayout(self.cmdButW)
        self.cmdBut_lay.setAlignment(QtCore.Qt.AlignRight)
        self.cmdButW.setLayout(self.cmdBut_lay)

        self.cmdBut_compileBut, self.cmdBut_flashBut, self.cmdBut_compileandflashBut = QPushButton(), QPushButton(), QPushButton()
        bObjs = [self.cmdBut_compileBut, self.cmdBut_flashBut, self.cmdBut_compileandflashBut]
        bTexts = ["Compile", "Flash", "Compile and Flash"]

        for i,button in enumerate(bObjs):
            button.setText(bTexts[i])
            bWidth = button.fontMetrics().boundingRect(str(button.text)).width() + 15 # limits button size
            button.setMaximumWidth(bWidth)
            self.cmdBut_lay.addWidget(button)

        self.layout.addWidget(self.w)
        self.layout.addWidget(self.cmdButW)
        self.show()

    def getDataFromJSON(self, file):
        with open(file, 'r') as json_file:
            rowdata_json = json.load(json_file)
        return rowdata_json

class LineEdit(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.setFixedWidth(100)
        self.setFixedHeight(24)
        self.setContentsMargins(5,0,5,0)
        self.setStyleSheet('''
        LineEdit { background-color : white;}
        ''')

class InfoLabel(QLabel):
    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.setFixedWidth(500)
        self.setFixedHeight(24)
        self.setContentsMargins(5,0,5,0)
        self.setStyleSheet('''
        InfoLabel { background-color : lightGrey;}
        ''')

class TabBar(QTabBar):
    def __init__(self):
        QTabBar.__init__(self)
        #self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        #self.setStyleSheet("QTabBar::tab {height: 115px; width: 30px; color: font-weight: bold; font-size: 10px;}")

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self,index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt,i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel,opt)
            painter.restore()

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        self.widget=QTabWidget.__init__(self, parent)
        self.tb=TabBar()
        self.setTabBar(self.tb)
        self.setTabPosition(QTabWidget.West)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('TSDZ2 Configurator')
    appw = App()
    app.setStyle('Fusion') # we need this to get a uniform look and feel on all platforms

    sys.exit(app.exec_())