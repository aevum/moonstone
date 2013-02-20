# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/igor/Desenvolvimento/neppo/Moonstone/src/resources/ui/qt/importsearch.ui'
#
# Created: Tue Mar  6 18:01:46 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ImportSearch(object):
    def setupUi(self, ImportSearch):
        ImportSearch.setObjectName("ImportSearch")
        ImportSearch.resize(356, 248)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/moonstone.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ImportSearch.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ImportSearch)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(ImportSearch)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.patientName = QtGui.QLineEdit(self.groupBox)
        self.patientName.setObjectName("patientName")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.patientName)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_4)
        self.studyDescription = QtGui.QLineEdit(self.groupBox)
        self.studyDescription.setObjectName("studyDescription")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.studyDescription)
        self.serieDescription = QtGui.QLineEdit(self.groupBox)
        self.serieDescription.setObjectName("serieDescription")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.serieDescription)
        self.modality = QtGui.QLineEdit(self.groupBox)
        self.modality.setObjectName("modality")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.modality)
        self.institution = QtGui.QLineEdit(self.groupBox)
        self.institution.setObjectName("institution")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.institution)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancelButton = QtGui.QPushButton(ImportSearch)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/dialog-close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.searchButton = QtGui.QPushButton(ImportSearch)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/default/icon/22x22/page-region.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.searchButton.setIcon(icon2)
        self.searchButton.setObjectName("searchButton")
        self.horizontalLayout.addWidget(self.searchButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ImportSearch)
        QtCore.QMetaObject.connectSlotsByName(ImportSearch)

    def retranslateUi(self, ImportSearch):
        ImportSearch.setWindowTitle(QtGui.QApplication.translate("ImportSearch", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImportSearch", "Advanced Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportSearch", "Patient name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ImportSearch", "Study description:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ImportSearch", "Serie description:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ImportSearch", "Modality:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ImportSearch", "Institution:", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("ImportSearch", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setText(QtGui.QApplication.translate("ImportSearch", "Search", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportSearch = QtGui.QWidget()
    ui = Ui_ImportSearch()
    ui.setupUi(ImportSearch)
    ImportSearch.show()
    sys.exit(app.exec_())

