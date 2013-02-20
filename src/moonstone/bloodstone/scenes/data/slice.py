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
import logging
import vtk
import math

#                
#                 up
#  (point2) *
#           |
#           |
#   left    |                 right
#           |
#           |
#  (origin) *-------------*(point1)
#                down
class Slice():
    def __init__(self, origin, p1, p2, width, height):
        logging.debug("In Slice::__init__()")
        self._p1 = p1
        self._p2 = p2    
        self._width = width
        self._origin = origin
        self._height = height
        self._plane  = vtk.vtkPlaneSource()
        self._plane.SetOrigin(self._origin)
        self._plane.SetPoint1(self._p1)
        self._plane.SetPoint2(self._p2)
        self._plane.Update()
        self.normalizePlaneSize()
        self.createBoundsPlanes()
        self._resliceTransform = None
        
    def normalizePlaneSize(self):
#        print "----------------------------------------------------------------"
#        print "BEFORE:", self._plane
        distance = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(self._plane.GetOrigin(), self._plane.GetPoint1()))
        scale = self._width/distance
        self._plane.SetPoint1([(p1 - o) * scale + o for p1, o in zip(self._plane.GetPoint1(), self._plane.GetOrigin())])
        
        distance = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(self._plane.GetOrigin(), self._plane.GetPoint2()))
        scale = self._height/distance
        self._plane.SetPoint2([(p2 - o) * scale + o for p2, o in zip(self._plane.GetPoint2(), self._plane.GetOrigin())])
        
        self._plane.SetOrigin(self._plane.GetOrigin())
        
        self._plane.Update()
#        print "AFTER:", self._plane
    
    def createBoundsPlanes(self):
        self._leftPlane = vtk.vtkPlaneSource()
        self._rightPlane = vtk.vtkPlaneSource()
        self._upPlane = vtk.vtkPlaneSource()
        self._downPlane = vtk.vtkPlaneSource()
        self.updateBoundsPlanes()
        
    def updateBoundsPlanes(self):
        point3 = [p1+p2 for p1, p2 in zip(self._plane.GetOrigin(), self._plane.GetNormal())]
        
        self._leftPlane.SetOrigin(self._plane.GetOrigin())
        self._leftPlane.SetPoint1(self._plane.GetPoint2())
        self._leftPlane.SetPoint2(point3)
        
        self._leftPlane.Push(self._width)
        self._rightPlane.SetOrigin(self._leftPlane.GetOrigin())
        self._rightPlane.SetPoint1(self._leftPlane.GetPoint1())
        self._rightPlane.SetPoint2(self._leftPlane.GetPoint2())
        self._leftPlane.Push(-self._width)
    
        self._downPlane.SetOrigin(self._plane.GetOrigin())
        self._downPlane.SetPoint1(point3)
        self._downPlane.SetPoint2(self._plane.GetPoint1())
        
        self._downPlane.Push(self._height)
        self._upPlane.SetOrigin(self._downPlane.GetOrigin())
        self._upPlane.SetPoint1(self._downPlane.GetPoint1())
        self._upPlane.SetPoint2(self._downPlane.GetPoint2())
        self._downPlane.Push(-self._height)
        
    def isPointInProjection(self, point):
        sideDistance = vtk.vtkPlane.DistanceToPlane(point, self._leftPlane.GetNormal(), self._leftPlane.GetOrigin()) +\
                       vtk.vtkPlane.DistanceToPlane(point, self._rightPlane.GetNormal(), self._rightPlane.GetOrigin())
        if sideDistance - self._width > 0.01:
            return False
        return True
    #comparing only side planes
#        upDistance = vtk.vtkPlane.DistanceToPlane(point, self._upPlane.GetNormal(), self._upPlane.GetOrigin()) +\
#                       vtk.vtkPlane.DistanceToPlane(point, self._downPlane.GetNormal(), self._downPlane.GetOrigin())
#                       
#        return upDistance <= self._height
    
    def getPointDistance(self, point):
        return vtk.vtkPlane.DistanceToPlane(point, self._plane.GetNormal(), self._plane.GetOrigin())
    
    def getCenterDistance(self, point):
        return math.sqrt(vtk.vtkMath.Distance2BetweenPoints(point, self._plane.GetCenter()))
    
    def getBaseCenterDistance(self, point):
        return math.sqrt(vtk.vtkMath.Distance2BetweenPoints(point, self.getBaseCenter())) 
    
    def getOriginDistance(self, point):
        return math.sqrt(vtk.vtkMath.Distance2BetweenPoints(point, self._plane.GetOrigin())) 
    
    def getBaseCenter(self):
        result = [(p1+p2)/2.0 for p1, p2 in zip(self._plane.GetOrigin(), self._plane.GetPoint1())]
        return result
    
    @property
    def plane(self):
        return self._plane
        
    @property
    def width(self):
        return self._width
        
    def setWidth(self, width):
        self._width = width
        self.normalizePlaneSize()
        
    @property
    def height(self):
        return self._height
        
    def setHeight(self, height):
        self._height = height
        self.normalizePlaneSize()
        
    @property
    def origin(self):
        return self._origin
        
    def setOrigin(self, origin):
        self._origin = origin
        self._plane.SetCenter([c + (no - oo) for c, oo, no in zip(self._plane.GetCenter(), self._plane.GetOrigin(), self._origin)])
        self._plane.Update()
        self.updateBoundsPlanes()
    
    @property
    def normal(self):
        return self._normal
        
    def setNormal(self, normal):
        self._normal = normal
        self._plane.SetNormal(self._normal)
        self._plane.Update()
        self.updateBoundsPlanes()
    
    @property
    def center(self):
        return self._plane.GetCenter()
        
    def setCenter(self, center):
        self._plane.SetCenter(center)
        self._plane.Update()
        self.updateBoundsPlanes()
        
    def push(self, value):
        self._plane.Push(value)
        self._plane.Update()
    
    @property
    def resliceTransform(self):
        return self._resliceTransform
        
    def setResliceTransform(self, resliceTransform):
        self._resliceTransform = resliceTransform 
        
    def getBounds(self):
        origin = self._plane.GetOrigin()
        point1 = self._plane.GetPoint1()
        point2 = self._plane.GetPoint2()
        minx = min(origin[0], point1[0], point2[0]) - 0.000001
        maxx = max(origin[0], point1[0], point2[0]) + 0.000001
        miny = min(origin[1], point1[1], point2[1]) - 0.000001
        maxy = max(origin[1], point1[1], point2[1]) + 0.000001
        minz = min(origin[2], point1[2], point2[2]) - 0.000001
        maxz = max(origin[2], point1[2], point2[2]) + 0.000001
        return [minx, maxx, miny, maxy, minz, maxz] 
        
    def save(self):
        result = {
                  "origin" : self._plane.GetOrigin(),
                  "point1" : self._plane.GetPoint1(),
                  "point2" : self._plane.GetPoint2(),
                  "width" : self._width,
                  "height" : self._height
                  }
        
        return result
        
        
        
        
        
        