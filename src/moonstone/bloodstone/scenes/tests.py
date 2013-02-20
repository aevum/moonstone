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
sys.path.insert(0, os.path.abspath(os.path.join(os.pardir, os.pardir)))

import vtk

#from bloodstone.scenes.axial import VtkAxialScene
from bloodstone.scenes.imageplane import VtkImagePlane
from bloodstone.utils.data import reader_vti, reader_to_imagedata


class VtkImagePlaneTest(unittest.TestCase):
    
    def setUp(self):
        logging.debug("In VtkImagePlaneTest::setUp()")
        self.dicomdir1 = os.path.abspath("/home/igor/Desenvolvimento/neppo/Dicons/teste dicom 08/")
        self.dicomdir2 = os.path.abspath("/home/igor/Desenvolvimento/neppo/Dicons/Regina Dicom 04/")
        #self.dicomdir = os.path.abspath("/home/igor/Desenvolvimento/neppo/Dicons/dicomwrong")
        #self.dicomdir2 = os.path.abspath("/home/igor/Desenvolvimento/neppo/Dicons/dicomwrong")
        self.dicomdir3 = os.path.abspath("/home/igor/Desenvolvimento/neppo/Dicons/dicon 04 janaian impl. instalado/")
        
        self.vtidir1 = os.path.abspath("/home/igor/.moonstone/data/Juliana Felice^ /1.76.380.18.2.3308.2131.vti")
        self.vtidir2 = os.path.abspath("/home/igor/.moonstone/data/Juliana Felice^ /1.76.380.18.2.3308.2140.vti")
        
    """def test_image_plane(self):
        logging.debug("In VtkImagePlaneTest::test_image_plane()")
        
        from PySide import QtCore, QtGui
        
        from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget
        
        app = QtGui.QApplication(sys.argv)
    
        widget = QVtkWidget()
        widget.setWindowTitle("Test VtkAxial with actor")
        widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        
        cone = vtk.vtkConeSource()
        cone.SetResolution(8)
        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInput(cone.GetOutput())
        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)
        
        scene = VtkImagePlane(widget)
        scene.actor = coneActor
        scene.renderer.ResetCamera()
        scene.initialize()
        
        widget.show()
        
        app.exec_()
    """
        
    """def test_image_plane_image_actor(self):
        logging.debug("In VtkAxialSceneTest::test_image_plane_image_actor()")
        from PySide import QtCore, QtGui
        
        from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget

        # vtkGDCMImageReader is a source object that reads some DICOM files
        # this reader is single threaded.
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(self.dicomdir)
        reader.Update()
        
        app = QtGui.QApplication(sys.argv)
        
        actions = {}
        actions["Slice"] = 0
        
        widget = QVtkWidget()
        widget.setWindowTitle("Test VtkAxial with image actor")
        widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
    
        scene = VtkImagePlane(widget)
        scene.input = reader
        scene.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        scene.planeOrientation = VtkImagePlane.PLANE_ORIENTATION_AXIAL
        scene.enabled()
            
        def slotMouseWheelForwardEvent(obj, event, scene):
            scene.pushByScalar += scene._imageData.GetSpacing()[2]*1
            scene.updatePlane()
            scene.highlightPlane(True)
            scene.activateMargins(True)
            scene.updateMargins()
            scene.buildRepresentation()
            scene.window.Render()
            
        def slotMouseWheelBackwardEvent(obj, event, scene):
            scene.pushByScalar -= scene._imageData.GetSpacing()[2]*1
            scene.updatePlane()
            scene.highlightPlane(True)
            scene.activateMargins(True)
            scene.updateMargins()
            scene.buildRepresentation()
            scene.window.Render()
            
        #scene.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        scene.interactorStyle.AddObserver('MouseWheelForwardEvent', 
            lambda o, e, i=scene: slotMouseWheelForwardEvent(o, e, i))
        scene.interactorStyle.AddObserver('MouseWheelBackwardEvent', 
            lambda o, e, i=scene: slotMouseWheelBackwardEvent(o, e, i))
        
        widget.show()
        
        app.exec_()
    """
        
    def test_image_plane_image_actor_with_vti(self):
        logging.debug("In VtkAxialSceneTest::test_image_plane_image_actor_with_vti()")
        from PySide import QtCore, QtGui
        
        from bloodstone.scenes.gui.qt.component.qvtkwidget import QVtkWidget

        reader = reader_vti(self.vtidir2)
        imagedata = reader_to_imagedata(reader)
        
        app = QtGui.QApplication(sys.argv)
        
        actions = {}
        actions["Slice"] = 0
        
        widget = QVtkWidget()
        widget.setWindowTitle("Test VtkAxial with image actor")
        widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
    
        scene = VtkImagePlane(widget)
        scene.input = reader
        scene.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        scene.planeOrientation = VtkImagePlane.PLANE_ORIENTATION_AXIAL
        scene.enabled()
            
        def slotMouseWheelForwardEvent(obj, event, scene):
            #scene.pushByScalar += scene._imageData.GetSpacing()[2]*1
            #transform = vtk.vtkTransform()
            #transform.RotateWXYZ(356.084381104, -0.0432691946626, -0.052828669548, 0.0)
            #scene.transform = transform
            scene.updatePlane()
            scene.highlightPlane(True)
            scene.activateMargins(True)
            scene.updateMargins()
            scene.buildRepresentation()
            scene.window.Render()
            
        def slotMouseWheelBackwardEvent(obj, event, scene):
            scene.pushByScalar -= scene._imageData.GetSpacing()[2]*1
            scene.updatePlane()
            scene.highlightPlane(True)
            scene.activateMargins(True)
            scene.updateMargins()
            scene.buildRepresentation()
            scene.window.Render()
            
        #scene.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        scene.interactorStyle.AddObserver('MouseWheelForwardEvent', 
            lambda o, e, i=scene: slotMouseWheelForwardEvent(o, e, i))
        scene.interactorStyle.AddObserver('MouseWheelBackwardEvent', 
            lambda o, e, i=scene: slotMouseWheelBackwardEvent(o, e, i))
        
        widget.show()
        
        app.exec_()
        

if __name__ == "__main__":
    unittest.main()