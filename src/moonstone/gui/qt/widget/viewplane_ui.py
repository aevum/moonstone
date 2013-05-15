# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/moonstone/src/resources/ui/qt/viewplane.ui'
#
# Created: Thu May  2 14:31:51 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ViewPlane(object):
    def setupUi(self, ViewPlane):
        ViewPlane.setObjectName("ViewPlane")
        ViewPlane.resize(443, 436)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ViewPlane.setWindowIcon(icon)
        self.widget = QtGui.QWidget(ViewPlane)
        self.widget.setGeometry(QtCore.QRect(0, 0, 31, 87))
        self.widget.setObjectName("widget")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setContentsMargins(0, 6, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.splitter = QtGui.QSplitter(self.widget)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setObjectName("splitter")
        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.plane = QtGui.QWidget(self.frame)
        self.plane.setObjectName("plane")
        self.horizontalLayout_4.addWidget(self.plane)
        self.planeSlide = QtGui.QScrollBar(self.frame)
        self.planeSlide.setOrientation(QtCore.Qt.Vertical)
        self.planeSlide.setObjectName("planeSlide")
        self.horizontalLayout_4.addWidget(self.planeSlide)
        self.toolbar = QtGui.QToolBar(self.splitter)
        self.toolbar.setMaximumSize(QtCore.QSize(16777215, 35))
        self.toolbar.setSizeIncrement(QtCore.QSize(0, 35))
        self.toolbar.setObjectName("toolbar")
        self.horizontalLayout_5.addWidget(self.splitter)

        self.retranslateUi(ViewPlane)
        QtCore.QMetaObject.connectSlotsByName(ViewPlane)

    def retranslateUi(self, ViewPlane):
        ViewPlane.setWindowTitle(QtGui.QApplication.translate("ViewPlane", "View Plane", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ViewPlane = QtGui.QWidget()
    ui = Ui_ViewPlane()
    ui.setupUi(ViewPlane)
    ViewPlane.show()
    sys.exit(app.exec_())

