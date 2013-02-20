# -*- coding: utf-8 -*-
#
# Moonstone is platform for processing of medical images (DICOM).
# Copyright (C) 2009-2011 by Neppo Tecnologia da Informação LTDA
# and Aevum Softwares LTDA
#
# This file is part of Moonstone.
#
# Moonstone is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys
import logging
import unittest

# Add bloodstone in Python path
sys.path.append(os.path.abspath(os.path.join(os.pardir, os.pardir, 
                                             os.pardir, os.pardir, os.pardir)))

import vtk
from PySide import QtCore, QtGui

from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget


class QVtkWidgetTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In SimpleTest::setUp()")
        self.cone = vtk.vtkConeSource()
        self.cone.SetResolution(8)
        self.coneMapper = vtk.vtkPolyDataMapper()
        self.coneMapper.SetInput(self.cone.GetOutput())
        self.coneActor = vtk.vtkActor()
        self.coneActor.SetMapper(self.coneMapper)
    
    def test_qvtkwidget(self):
        logging.debug("In SimpleTest::test_qvtkwidget()")
        app = QtGui.QApplication(sys.argv)
        
        ren = vtk.vtkRenderer()
        ren.AddActor(self.coneActor)
        
        win = QVtkWidget()
        win.setWindowTitle("Test QVtkWidget")
        win.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        win.GetRenderWindow().AddRenderer(ren)
        win.Initialize()
        win.Start()
        win.show()
        
        app.exec_()
        
    def test_qvtkwidget_mainwindow(self):
        logging.debug("In SimpleTest::test_qvtkwidget_mainwindow()")
        
        
        class _QVtkWidgetCone(QtGui.QMainWindow):

            def __init__(self, parent=None):
                logging.debug("In SimpleTest::_QVtkWidgetCone::__init__()")
                super(_QVtkWidgetCone, self).__init__(parent)
                
                self.setWindowTitle("Test QVtkWidget with QMainWindow")
                self.setGeometry(QtCore.QRect(500, 500, 200, 200))
        
                centralwidget = QtGui.QWidget(self)
                centralwidget.setObjectName("centralwidget")
                gridLayout = QtGui.QGridLayout(centralwidget)
                gridLayout.setObjectName("gridLayout")
                self.setCentralWidget(centralwidget)
                
                ren = vtk.vtkRenderer()
        
                widget = QVtkWidget(centralwidget)
                widget.setWindowTitle("Test QVtkWidget with QMainWindow")
                widget.setGeometry(QtCore.QRect(1, 30, 200, 200))
                widget.GetRenderWindow().AddRenderer(ren)
                widget.GetRenderWindow().SetSize(200, 200)
                
                cone = vtk.vtkConeSource()
                cone.SetResolution(8)
                
                coneMapper = vtk.vtkPolyDataMapper()
                coneMapper.SetInput(cone.GetOutput())
                
                coneActor = vtk.vtkActor()
                coneActor.SetMapper(coneMapper)
                
                ren.AddActor(coneActor)
            

        app = QtGui.QApplication(sys.argv)
        widget = _QVtkWidgetCone()
        widget.show()
        app.exec_()
        
    def test_qvtkwidget_mainwindow_with_mdi(self):
        logging.debug("In SimpleTest::test_qvtkwidget_mainwindow_with_mdi()")
        
        
        class _QVtkWidgetCone(QtGui.QMainWindow):

            def __init__(self, parent=None):
                logging.debug("In SimpleTest::_QVtkWidgetCone::__init__()")
                super(_QVtkWidgetCone, self).__init__(parent)
                
                self.setWindowTitle("Test QVtkWidget with QMainWindow")
                self.setGeometry(QtCore.QRect(500, 500, 250, 250))
        
                centralwidget = QtGui.QWidget(self)
                centralwidget.setObjectName("centralwidget")
                gridLayout = QtGui.QGridLayout(centralwidget)
                gridLayout.setObjectName("gridLayout")
                windowArea = QtGui.QMdiArea(centralwidget)
                windowArea.setObjectName("windowArea")
                gridLayout.addWidget(windowArea, 0, 0, 1, 1)
                self.setCentralWidget(centralwidget)
        
                subwindow = QtGui.QMdiSubWindow()
                subwindow.setGeometry(QtCore.QRect(0, 0, 200, 200))
                windowArea.addSubWindow(subwindow)
                
                ren = vtk.vtkRenderer()
        
                widget = QVtkWidget(subwindow)
                widget.setWindowTitle("Test QVtkWidget with QMainWindow")
                widget.setGeometry(QtCore.QRect(1, 30, 200, 200))
                widget.GetRenderWindow().AddRenderer(ren)
                widget.GetRenderWindow().SetSize(200, 200)
                
                cone = vtk.vtkConeSource()
                cone.SetResolution(8)
                
                coneMapper = vtk.vtkPolyDataMapper()
                coneMapper.SetInput(cone.GetOutput())
                
                coneActor = vtk.vtkActor()
                coneActor.SetMapper(coneMapper)
                
                ren.AddActor(coneActor)
            

        app = QtGui.QApplication(sys.argv)
        widget = _QVtkWidgetCone()
        widget.show()
        app.exec_()


if __name__ == "__main__":
    unittest.main()