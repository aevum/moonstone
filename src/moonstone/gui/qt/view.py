import logging

from PySide import QtCore
from PySide import QtGui

from widget.viewplane_ui import Ui_ViewPlane

class View( QtGui.QDockWidget, Ui_ViewPlane ):

    def __init__( self, title, mscreenParent, planeNumber = 1 ):

        logging.debug("In View::__init__()")
        super( View, self ).__init__()
        self.planeNumber = planeNumber
        if planeNumber > 1:
            title = "{0} {1}".format(title, planeNumber)
        self.title = title 
        self._mscreenParent = mscreenParent
        self._id = "{0}".format( self._mscreenParent.getNewChildId() )
        self.setAcceptDrops(True)
        self.setupUi(self)
        self.setWidget(self.widget)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum))
        QtGui.QSizePolicy.Slider
        self.createWidgets()
        self.createScene()
        self.createActions()
        self.updateWidgets()

    def createWidgets( self ):

        logging.debug("In View::createWidgets()")
        self.connect(self.splitter, QtCore.SIGNAL("splitterMoved(int, int)"), self.splitterMoved)
        self.splitter.setSizes([1,0])

    def createScene( self ):

        logging.debug("In View::createScene()")

    def createActions( self ):

        logging.debug("In View::createActions()")

    def updateWidgets( self ):

        logging.debug("In View::UpdateWidgets()")

    def resizeEvent(self, event):
        logging.debug("In View::resizeEvent()")
        self.resizeAction()