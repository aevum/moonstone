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
sys.path.append(os.path.abspath(os.path.join(os.pardir, os.pardir, os.pardir)))

import vtk

from bloodstone.scenes.core.scene import VtkScene
from bloodstone.scenes.core.interactor import VtkInteractor 


class VtkInteractorTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In VtkInteractorTest::setUp()")
        self.cone = vtk.vtkConeSource()
        self.cone.SetResolution(8)
        self.coneMapper = vtk.vtkPolyDataMapper()
        self.coneMapper.SetInput(self.cone.GetOutput())
        self.coneActor = vtk.vtkActor()
        self.coneActor.SetMapper(self.coneMapper)
    
    def test_interactor(self):
        logging.debug("In VtkInteractorTest::test_interactor()")
        from PySide import QtCore, QtGui
        
        from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
        
        app = QtGui.QApplication(sys.argv)
        widget = QVtkWidget()
        widget.setWindowTitle("Test VtkInteractor")
        widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        
        interactor = VtkInteractor(widget)
        interactor.actor = self.coneActor
        interactor.renderer.ResetCamera()
        
        widget.Initialize()
        widget.Start()
        
        widget.show()
        app.exec_()
        
        
class VtkSceneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In VtkSceneTest::setUp()")
        self.cone = vtk.vtkConeSource()
        self.cone.SetResolution(8)
        self.coneMapper = vtk.vtkPolyDataMapper()
        self.coneMapper.SetInput(self.cone.GetOutput())
        self.coneActor = vtk.vtkActor()
        self.coneActor.SetMapper(self.coneMapper)
        
    def test_scene(self):
        logging.debug("In VtkSceneTest::test_scene()")
        from PySide import QtCore, QtGui
        
        from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
        
        app = QtGui.QApplication(sys.argv)
    
        widget = QVtkWidget()
        widget.setWindowTitle("Test VtkScene")
        widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        
        scene = VtkScene(widget)
        scene.actor = self.coneActor
        scene.renderer.ResetCamera()
        scene.initialize()
        
        widget.show()
        
        app.exec_()


if __name__ == "__main__":
    unittest.main()