from PySide import QtCore, QtGui

class ImportItemDelegate(QtGui.QItemDelegate):
    def __init__(self):
        super(ImportItemDelegate, self).__init__()
    
    def paint(self, *args, **kwargs):
        column = args[2].column()
        value = args[2].data()
        if column == 2:
            progressBarOption = QtGui.QStyleOptionProgressBar()
            progressBarOption.rect = args[1].rect
            progressBarOption.minimum = 0
            progressBarOption.maximum = 100
            if isinstance(value, int) : 
                progressBarOption.progress = int(value)
                progressBarOption.text =  "{0}%".format(int(value))
            progressBarOption.textVisible = True
            QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_ProgressBar, progressBarOption, args[0], None)
            return
        return QtGui.QItemDelegate.paint(self, *args, **kwargs)
    
#    def createEditor(self, *args, **kwargs):
#        editor = None
#        column = args[2].column()
#        value = args[2].data()
#        if column == 0:
#            editor = QtGui.QCheckBox(args[0]) 
#        if editor:
#            return editor
#        return QtGui.QItemDelegate.createEditor(self, *args, **kwargs)