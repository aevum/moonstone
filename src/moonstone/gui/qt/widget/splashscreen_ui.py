# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/splashscreen.ui'
#
# Created: Tue Mar 13 14:51:20 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        SplashScreen.setObjectName("SplashScreen")
        SplashScreen.resize(600, 450)
        SplashScreen.setMinimumSize(QtCore.QSize(600, 450))
        SplashScreen.setMaximumSize(QtCore.QSize(600, 450))
        SplashScreen.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SplashScreen.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(SplashScreen)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbSplashScreen = QtGui.QLabel(SplashScreen)
        self.lbSplashScreen.setMinimumSize(QtCore.QSize(600, 430))
        self.lbSplashScreen.setMaximumSize(QtCore.QSize(600, 430))
        self.lbSplashScreen.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lbSplashScreen.setLineWidth(0)
        self.lbSplashScreen.setText("")
        self.lbSplashScreen.setPixmap(QtGui.QPixmap(":/static/default/splashscreen/splashscreen.png"))
        self.lbSplashScreen.setObjectName("lbSplashScreen")
        self.verticalLayout.addWidget(self.lbSplashScreen)
        self.lbDescription = QtGui.QLabel(SplashScreen)
        self.lbDescription.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lbDescription.setStyleSheet("color: rgb(0, 85, 255);\n"
"background-color: rgb(255, 255, 255);")
        self.lbDescription.setLineWidth(0)
        self.lbDescription.setMargin(5)
        self.lbDescription.setObjectName("lbDescription")
        self.verticalLayout.addWidget(self.lbDescription)

        self.retranslateUi(SplashScreen)
        QtCore.QMetaObject.connectSlotsByName(SplashScreen)

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QtGui.QApplication.translate("SplashScreen", "Moonstone", None, QtGui.QApplication.UnicodeUTF8))
        self.lbDescription.setText(QtGui.QApplication.translate("SplashScreen", "...Moonstone Medical", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SplashScreen = QtGui.QWidget()
    ui = Ui_SplashScreen()
    ui.setupUi(SplashScreen)
    SplashScreen.show()
    sys.exit(app.exec_())

