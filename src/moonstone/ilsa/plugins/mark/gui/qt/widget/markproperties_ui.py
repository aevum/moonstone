# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/moonstone/src/moonstone/ilsa/plugins/mark/resources/ui/qt/markproperties.ui'
#
# Created: Fri Feb 21 10:21:51 2014
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MarkProperties(object):
    def setupUi(self, MarkProperties):
        MarkProperties.setObjectName("MarkProperties")
        MarkProperties.resize(212, 282)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-select.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MarkProperties.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(MarkProperties)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(MarkProperties)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName("widget")
        self.gridLayout_4 = QtGui.QGridLayout(self.widget)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_4.addWidget(self.label_3, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget_2 = QtGui.QWidget(self.widget)
        self.widget_2.setMinimumSize(QtCore.QSize(70, 28))
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 28))
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.widget_2)
        self.gridLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lineColorFrame = QtGui.QFrame(self.widget_2)
        self.lineColorFrame.setMinimumSize(QtCore.QSize(60, 0))
        self.lineColorFrame.setMaximumSize(QtCore.QSize(16777215, 14))
        self.lineColorFrame.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.lineColorFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lineColorFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.lineColorFrame.setObjectName("lineColorFrame")
        self.gridLayout_2.addWidget(self.lineColorFrame, 0, 0, 1, 1)
        self.horizontalLayout_4.addWidget(self.widget_2)
        self.gridLayout_4.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.newMarkButton = QtGui.QPushButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newMarkButton.setIcon(icon1)
        self.newMarkButton.setObjectName("newMarkButton")
        self.gridLayout_4.addWidget(self.newMarkButton, 3, 1, 1, 1)
        self.deleteMarkButton = QtGui.QPushButton(self.widget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/edit-delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteMarkButton.setIcon(icon2)
        self.deleteMarkButton.setObjectName("deleteMarkButton")
        self.gridLayout_4.addWidget(self.deleteMarkButton, 3, 0, 1, 1)
        self.thicknessBox = QtGui.QDoubleSpinBox(self.widget)
        self.thicknessBox.setObjectName("thicknessBox")
        self.gridLayout_4.addWidget(self.thicknessBox, 0, 1, 1, 1)
        self.lock = QtGui.QCheckBox(self.widget)
        self.lock.setObjectName("lock")
        self.gridLayout_4.addWidget(self.lock, 2, 0, 1, 1)
        self.visible = QtGui.QCheckBox(self.widget)
        self.visible.setObjectName("visible")
        self.gridLayout_4.addWidget(self.visible, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.markGroup = QtGui.QGroupBox(MarkProperties)
        self.markGroup.setMinimumSize(QtCore.QSize(0, 50))
        self.markGroup.setObjectName("markGroup")
        self.verticalLayout.addWidget(self.markGroup)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(MarkProperties)
        QtCore.QMetaObject.connectSlotsByName(MarkProperties)

    def retranslateUi(self, MarkProperties):
        MarkProperties.setWindowTitle(QtGui.QApplication.translate("MarkProperties", "Mark Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MarkProperties", "Radius", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MarkProperties", "Line color:", None, QtGui.QApplication.UnicodeUTF8))
        self.newMarkButton.setText(QtGui.QApplication.translate("MarkProperties", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteMarkButton.setText(QtGui.QApplication.translate("MarkProperties", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.lock.setText(QtGui.QApplication.translate("MarkProperties", "Lock", None, QtGui.QApplication.UnicodeUTF8))
        self.visible.setText(QtGui.QApplication.translate("MarkProperties", "Visible", None, QtGui.QApplication.UnicodeUTF8))
        self.markGroup.setTitle(QtGui.QApplication.translate("MarkProperties", "Marks", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MarkProperties = QtGui.QWidget()
    ui = Ui_MarkProperties()
    ui.setupUi(MarkProperties)
    MarkProperties.show()
    sys.exit(app.exec_())

