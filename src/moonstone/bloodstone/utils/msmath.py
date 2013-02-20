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

ORIENTATION_RIGHT = 1
ORIENTATION_LEFT = -1
ORIENTATION_CENTER = 0
POSITION_HIGHER = 1
POSITION_LOWER = -1
POSITION_SAME = 0

def intersect_line_with_plane(p1, p2, n, p0):
        logging.debug("In math::intersectLineWithPlane()")
        p21 = [0.0 ,0.0 ,0.0]
    
        p21[0] = p2[0] - p1[0]
        p21[1] = p2[1] - p1[1]
        p21[2] = p2[2] - p1[2]
            
        num = vtk.vtkMath.Dot(n,p0) - ( n[0]*p1[0] + n[1]*p1[1] + n[2]*p1[2] ) 
        den = n[0]*p21[0] + n[1]*p21[1] + n[2]*p21[2]
        
        if den == 0:
            return None
                
        t = num / den  
        
        x = [0.0 , 0.0 , 0.0]       
        
        x[0] = p1[0] + t*p21[0]
        x[1] = p1[1] + t*p21[1]
        x[2] = p1[2] + t*p21[2]        
        return x

def subtract_vector(v1, v2):
        return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]

def sum_vector(v1, v2):
    return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]


def multiply_vector_by_scalar(v, a):
        logging.debug("In math::multiply_vector_by_scalar()")
        return [a*v[0], a*v[1], a*v[2]]

def trasnlate_vector(v1 , p):
        logging.debug("In math::trasnlate_vector()")
        v1List = list(v1)
        transform = vtk.vtkTransform()
        transform.Translate(p)
        v1List.append(1)
        transform.MultiplyPoint(v1List,v1List)
        v1List.pop()
        return v1List

def distance_from_plane(point, plane):
    return plane.DistanceToPlane(
                                    plane.GetOrigin(),
                                    plane.GetNormal(), point)


def compare_point_height(p1, p2, scene):
        """return 1 i p1 i closest from p2 to camera, return -1 if p2 is closest
        and 0 i they are in the same height
        """
        logging.debug("In Implant::comparePointHeight()")
        
        cameraPlane = vtk.vtkPlane()
        cameraPlane.SetNormal(scene.camera.GetViewPlaneNormal())
        cameraPlane.SetOrigin(scene.camera.GetPosition())
        p1Distance = cameraPlane.DistanceToPlane(cameraPlane.GetOrigin(), 
                                                 cameraPlane.GetNormal(), p1)
        p2Distance = cameraPlane.DistanceToPlane(cameraPlane.GetOrigin(), 
                                                 cameraPlane.GetNormal(), p2)
        if p1Distance == p2Distance:
            return POSITION_SAME  #Same Height
        elif p1Distance < p2Distance:
            return POSITION_HIGHER  #p1 higher then p2
        else:
            return POSITION_LOWER #p2 higher then p1
    
def point_orientation(point, l1, l2):
        """ Returns 1 if the point is in right from 
        l1 to  l2 in view side. return -1 if it is left and 
        return 0 is is in the line
        """
        logging.debug("In Implant::pointOrientation()")
        m=(l2[0]-l1[0])*(l2[1]-l1[1])

        p1=(point[0]-l1[0])*(point[1]-l1[1]) 
        
        p2=(l2[0]-point[0])*(l2[1]-point[1]) 
        
        p3=(l2[0]-point[0])*(point[1]-l1[1])*2
        
        
        if m == p1 + p2 + p3 : 
            return ORIENTATION_CENTER        
        elif m < p1 + p2 + p3 :
            return ORIENTATION_LEFT
        else:
            return ORIENTATION_RIGHT  
        
def calculate_distance(head, tail):
    return vtk.vtkMath.Norm([head[0]-tail[0],head[1]-tail[1],head[2]-tail[2]] )     

def calculateAngle( point1, center, point2):
        """ Calculate angle between three points"""
        try:
            v1 = [point1[0]-center[0], point1[1]-center[1], point1[2]-center[2]]
            v2 = [point2[0]-center[0], point2[1]-center[1], point2[2]-center[2]]
            tetha = math.acos(
                        vtk.vtkMath.Dot(v1, v2) / (
                                vtk.vtkMath.Norm(v1) * vtk.vtkMath.Norm(v2)))
            return math.degrees(tetha)
        except:
            return 0.0

def calculate_plane_2_plane_transform(planeOrigin, planeDest):
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    #TODO scale transform
    #ODOT
    
    poo = planeOrigin.GetOrigin()
    pop1 = planeOrigin.GetPoint1()
    pop2 = planeOrigin.GetPoint2()
    
    pdo = planeDest.GetOrigin()
    pdp1 = planeDest.GetPoint1()
    pdp2 = planeDest.GetPoint2()
    
    transform.Translate(pdo[0] - poo[0], pdo[1] - poo[1], pdo[2] - poo[2])
    transform.Update()
    poo = list(transform.TransformPoint(poo))
    pop1 = list(transform.TransformPoint(pop1))
    pop2 = list(transform.TransformPoint(pop2))
    
    transform.Translate(-poo[0], -poo[1], -poo[2])
    

    #calculating p1 x Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop1, 
                              poo, 
                              [1,0,0],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp1, 
                              poo, 
                              [1,0,0],
                              point2)
    xRotate = calculateAngle(point1, poo, point2)
    transform.RotateX(xRotate)
    
    #calculating p1 y Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop1, 
                              poo, 
                              [0,1,0],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp1, 
                              poo, 
                              [0,1,0],
                              point2)
    yRotate = calculateAngle(point1, poo, point2)
    transform.RotateY(yRotate)

    #calculating p1 z Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop1, 
                              poo, 
                              [0,0,1],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp1, 
                              poo, 
                              [0,0,1],
                              point2)
    zRotate = calculateAngle(point1, poo, point2)
    transform.RotateZ(zRotate)
        
    transform.Translate(poo[0], poo[1], poo[2])
    
    transform.Update()
    poo = list(transform.TransformPoint(planeOrigin.GetOrigin()))
    pop1 = list(transform.TransformPoint(planeOrigin.GetPoint1()))
    pop2 = list(transform.TransformPoint(planeOrigin.GetPoint2()))
    
    transform.Translate(-poo[0], -poo[1], -poo[2])
    
    #calculating p1 x Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop2, 
                              poo, 
                              [1,0,0],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp2, 
                              poo, 
                              [1,0,0],
                              point2)
    xRotate = calculateAngle(point1, poo, point2)
    transform.RotateX(xRotate)
    
    #calculating p1 y Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop2, 
                              poo, 
                              [0,1,0],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp2, 
                              poo, 
                              [0,1,0],
                              point2)
    yRotate = calculateAngle(point1, poo, point2)
    transform.RotateY(yRotate)

    #calculating p1 z Rotation
    point1 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pop2, 
                              poo, 
                              [0,0,1],
                              point1)
    
    point2 = [0, 0, 0]
    vtk.vtkPlane.ProjectPoint(pdp2, 
                              poo, 
                              [0,0,1],
                              point2)
    zRotate = calculateAngle(point1, poo, point2)
    transform.RotateZ(zRotate)
   
   
    transform.Translate(poo[0], poo[1], poo[2])
    transform.Update()
    
    return transform



 
