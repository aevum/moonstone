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

# Add Moonstone in Python path
sys.path.append(os.path.abspath(os.path.join(os.pardir, os.pardir, os.pardir)))

import vtk

from moonstone.gui.qt.axialplane import AxialPlane
from moonstone.gui.qt.mainwindow import MainWindow
from moonstone.gui.qt.volumeplane import VolumePlane
from moonstone.gui.qt.coronalplane import CoronalPlane
from moonstone.gui.qt.sagittalplane import SagittalPlane
from moonstone.bloodstone.scenes.axial import VtkAxialScene
from moonstone.bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget


class AxialPlaneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In VtkAxialSceneTest::setUp()")
        self.dicomdir = os.path.abspath("/home/moonstone/dicomdir")
        
    def test_axial_plane_with_actor(self):
        logging.debug("In VtkAxialSceneTest::test_axial_scene_with_actor()")
        from PySide import QtCore, QtGui
        
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
    
        widget = AxialPlane()
        widget.setWindowTitle("Test AxialPlane with actor")
        widget.scene.actor = coneActor
        widget.scene.renderer.ResetCamera()
        widget.show()
        
        app.exec_()
        

class CoronalPlaneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In CoronalPlaneTest::setUp()")
        self.dicomdir = os.path.abspath("/home/moonstone/dicomdir")
        
    def test_coronal_plane_with_actor(self):
        logging.debug("In CoronalPlaneTest::test_coronal_plane_with_actor()")
        from PySide import QtCore, QtGui
        
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
    
        widget = CoronalPlane()
        widget.setWindowTitle("Test CoronalPlane with actor")
        widget.scene.actor = coneActor
        widget.scene.renderer.ResetCamera()
        widget.show()
        
        app.exec_()
        
        
class SagittalPlaneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In SagittalPlaneTest::setUp()")
        self.dicomdir = os.path.abspath("/home/moonstone/dicomdir")
        
    def test_sagittal_plane_with_actor(self):
        logging.debug("In SagittalPlaneTest::test_sagittal_plane_with_actor()")
        from PySide import QtCore, QtGui
        
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
    
        widget = SagittalPlane()
        widget.setWindowTitle("Test SagittalPlane with actor")
        widget.scene.actor = coneActor
        widget.scene.renderer.ResetCamera()
        widget.show()
        
        app.exec_()

        
class VolumePlaneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In VolumePlaneTest::setUp()")
        self.dicomdir = os.path.abspath("/home/moonstone/dicomdir")
        
    def test_volume_plane_with_actor(self):
        logging.debug("In VolumePlaneTest::test_volume_plane_with_actor()")
        from PySide import QtCore, QtGui
        
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
    
        widget = VolumePlane()
        widget.setWindowTitle("Test VolumePlane with actor")
        widget.scene.actor = coneActor
        widget.scene.renderer.ResetCamera()
        widget.show()
        
        app.exec_()


class MainWindowTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In MainWindowTest::setUp()")
        self.dicomdir = os.path.abspath("/home/moonstone/dicomdir")
        
    def test_mainwindow(self):
        logging.debug("In MainWindowTest::test_mainwindow()")
        from PySide import QtCore, QtGui
        
        app = QtGui.QApplication(sys.argv)
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
    
        widget = MainWindow()
        widget.setWindowTitle("Test MainWindow")
        widget.show()
        
        app.exec_()


if __name__ == "__main__":
    unittest.main()