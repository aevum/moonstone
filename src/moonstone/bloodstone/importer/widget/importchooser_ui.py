# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../src/moonstone/bloodstone/importer/resources/ui/qt/importchooser.ui'
#
# Created: Thu May  3 17:14:10 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ImportChooser(object):
    def setupUi(self, ImportChooser):
        ImportChooser.setObjectName("ImportChooser")
        ImportChooser.resize(653, 288)
        ImportChooser.setMinimumSize(QtCore.QSize(0, 210))
        self.verticalLayout = QtGui.QVBoxLayout(ImportChooser)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_3 = QtGui.QWidget(ImportChooser)
        self.widget_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.recursiveCheck = QtGui.QCheckBox(self.widget_3)
        self.recursiveCheck.setObjectName("recursiveCheck")
        self.horizontalLayout_4.addWidget(self.recursiveCheck)
        self.addButton = QtGui.QPushButton(self.widget_3)
        self.addButton.setMaximumSize(QtCore.QSize(150, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/document-new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_4.addWidget(self.addButton)
        spacerItem = QtGui.QSpacerItem(361, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.availableStudiesLabel = QtGui.QLabel(self.widget_3)
        self.availableStudiesLabel.setObjectName("availableStudiesLabel")
        self.horizontalLayout_4.addWidget(self.availableStudiesLabel)
        self.verticalLayout.addWidget(self.widget_3)
        self.label = QtGui.QLabel(ImportChooser)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.widget_2 = QtGui.QWidget(ImportChooser)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 210))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tableView = QtGui.QTableView(self.widget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSortingEnabled(False)
        self.tableView.setWordWrap(True)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_3.addWidget(self.tableView)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget = QtGui.QWidget(ImportChooser)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 30))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.progressLabel = QtGui.QLabel(self.widget)
        self.progressLabel.setText("")
        self.progressLabel.setObjectName("progressLabel")
        self.horizontalLayout.addWidget(self.progressLabel)
        self.statusLabel = QtGui.QLabel(self.widget)
        self.statusLabel.setText("")
        self.statusLabel.setObjectName("statusLabel")
        self.horizontalLayout.addWidget(self.statusLabel)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.stopButton = QtGui.QPushButton(self.widget)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        self.cancelButton = QtGui.QPushButton(self.widget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.importButton = QtGui.QPushButton(self.widget)
        self.importButton.setObjectName("importButton")
        self.horizontalLayout.addWidget(self.importButton)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(ImportChooser)
        QtCore.QMetaObject.connectSlotsByName(ImportChooser)

    def retranslateUi(self, ImportChooser):
        ImportChooser.setWindowTitle(QtGui.QApplication.translate("ImportChooser", "Importer", None, QtGui.QApplication.UnicodeUTF8))
        self.recursiveCheck.setText(QtGui.QApplication.translate("ImportChooser", "Recursively", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("ImportChooser", "Add Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.availableStudiesLabel.setText(QtGui.QApplication.translate("ImportChooser", "Available Series: {0}", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportChooser", "Select the series you want to import:", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("ImportChooser", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("ImportChooser", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.importButton.setText(QtGui.QApplication.translate("ImportChooser", "Import", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportChooser = QtGui.QWidget()
    ui = Ui_ImportChooser()
    ui.setupUi(ImportChooser)
    ImportChooser.show()
    sys.exit(app.exec_())

