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

from PySide import QtGui
from PySide import QtCore

from moonstone.bloodstone.scenes.sliceimageplane import VtkSliceImagePlane
from moonstone.bloodstone.scenes.imagevolume import VtkImageVolume


class CameraController2D(object):
    BUTTON_LEFT = 0
    BUTTON_RIGHT = 1
    BUTTON_MIDDLE = 2
    BUTTON_SCROLL = 3
    ACTION_NONE = 0
    ACTION_CHANGE_SLICE = 1
    ACTION_ZOOM = 2
    ACTION_TRANSLATE = 3
    ACTION_FLIP_HORIZONTAL = 4
    ACTION_FLIP_VERTICAL = 5
    ACTION_POINTER = 6
    ACTION_ROTATE = 7

    def __init__(self, mWindow):
        logging.debug("In CameraController2D::__init__()")
        self._mWindow = mWindow
        self._mainWindow = self._mWindow.parent().parent()
        self._actions = {self.BUTTON_LEFT: [], self.BUTTON_RIGHT: [], self.BUTTON_MIDDLE: [], self.BUTTON_SCROLL: []}
        self._activeEvents = {self.BUTTON_LEFT: {}, self.BUTTON_RIGHT: {}, self.BUTTON_MIDDLE: {}, self.BUTTON_SCROLL: {}}
        self._activeActions = {self.BUTTON_LEFT: None, self.BUTTON_RIGHT: None, self.BUTTON_MIDDLE: None, self.BUTTON_SCROLL: None}
        self.createWidgets()
        self.createDefaultAcions()

    def createDefaultAcions(self):
        logging.debug("In CameraController2D::createDefaultAcions()")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/dialog-cancel.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addAction(self.ACTION_NONE,
                       self.BUTTON_LEFT,
                       self._slotActionNoneLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "None",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_NONE,
                       self.BUTTON_RIGHT,
                       self._slotActionNoneRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "None",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_NONE,
                       self.BUTTON_MIDDLE,
                       self._slotActionNoneMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "None",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_NONE,
                       self.BUTTON_SCROLL,
                       self._slotActionNoneScroll,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "None",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/transform-move.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_TRANSLATE,
                       self.BUTTON_LEFT,
                       self._slotActionTranslateLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Translate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        self.addAction(self.ACTION_TRANSLATE,
                       self.BUTTON_RIGHT,
                       self._slotActionTranslateRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Translate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        self.addAction(self.ACTION_TRANSLATE,
                       self.BUTTON_MIDDLE,
                       self._slotActionTranslateMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Translate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/zoom-in.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_ZOOM,
                       self.BUTTON_LEFT,
                       self._slotActionZoomLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Zoom",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_ZOOM,
                       self.BUTTON_RIGHT,
                       self._slotActionZoomRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Zoom",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_ZOOM,
                       self.BUTTON_MIDDLE,
                       self._slotActionZoomMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Zoom",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_ZOOM,
                       self.BUTTON_SCROLL,
                       self._slotActionZoomScroll,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Zoom",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/transform-rotate.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_ROTATE,
                       self.BUTTON_LEFT,
                       self.slotActionRotateLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Rotate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_ROTATE,
                       self.BUTTON_RIGHT,
                       self.slotActionRotateRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Rotate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_ROTATE,
                       self.BUTTON_MIDDLE,
                       self.slotActionRotateMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Rotate",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))


        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/object-flip-horizontal.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_FLIP_HORIZONTAL,
                       self.BUTTON_LEFT,
                       self._slotActionFlipHorizontalLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Horizontal",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        self.addAction(self.ACTION_FLIP_HORIZONTAL,
                       self.BUTTON_MIDDLE,
                       self._slotActionFlipHorizontalMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Horizontal",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        self.addAction(self.ACTION_FLIP_HORIZONTAL,
                       self.BUTTON_RIGHT,
                       self._slotActionFlipHorizontalRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Horizontal",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/object-flip-vertical.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_FLIP_VERTICAL,
                       self.BUTTON_LEFT,
                       self._slotActionFlipVerticalLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Vertical",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_FLIP_VERTICAL,
                       self.BUTTON_RIGHT,
                       self._slotActionFlipVerticalRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Vertical",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_FLIP_VERTICAL,
                       self.BUTTON_MIDDLE,
                       self._slotActionFlipVerticalMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Flip Vertical",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/snap-intersection.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_CHANGE_SLICE,
                       self.BUTTON_LEFT,
                       self._slotActionChangeSliceLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Change Slice",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_CHANGE_SLICE,
                       self.BUTTON_RIGHT,
                       self._slotActionChangeSliceRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Change Slice",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_CHANGE_SLICE,
                       self.BUTTON_MIDDLE,
                       self._slotActionChangeSliceMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Change Slice",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_CHANGE_SLICE,
                       self.BUTTON_SCROLL,
                       self._slotActionChangeSliceScroll,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Change Slice",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/static/default/icon/48x48/snap-orthogonal.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.addAction(self.ACTION_POINTER,
                       self.BUTTON_LEFT,
                       self._slotActionPointerLeft,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Pointer",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))
        self.addAction(self.ACTION_POINTER,
                       self.BUTTON_RIGHT,
                       self._slotActionPointerRight,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Pointer",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

        self.addAction(self.ACTION_POINTER,
                       self.BUTTON_MIDDLE,
                       self._slotActionPointerMiddle,
                       icon,
                       QtGui.QApplication.translate("CameraController2D",
                                                    "Pointer",
                                                    None,
                                                    QtGui.QApplication.UnicodeUTF8))

    def _slotActionChangeSliceScroll(self, obj, event, plane):
        if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
            self.actionsChooser(self.BUTTON_SCROLL)
            return
        if event == "MouseWheelForwardEvent":
            plane.planeSlide.setValue(plane.planeSlideValue + 1)

        else:
            plane.planeSlide.setValue(plane.planeSlideValue - 1)
        plane.planeSlide.update()
        plane.scene.window.Render()

    def _slotActionPointerLeft(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionPointerLeft()")
        scene = plane.scene
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionLeft
        except:
            obj._actionLeft = False
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                obj._actionLeft = False
                self.actionsChooser(self.BUTTON_LEFT)
                return
            obj._actionLeft = True
        elif event == "LeftButtonReleaseEvent":
            obj._actionLeft = False
        if obj._actionLeft:
            scene.picker.Pick(mouseX, mouseY, 0, scene.renderer)
            px, py, pz = scene.picker.GetPickPosition()

            Q = [px, py, pz]
            Q = scene.toOriginalView(Q)

            planes = self._mWindow.planes
            for plane in planes:
                if (not isinstance(plane.scene, VtkSliceImagePlane)) or plane.scene == scene:
                    continue
                plane.setSliceToPosition(Q)
                scene.window.Render()

    def _slotActionPointerRight(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionPointerLeft()")
        scene = plane.scene
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionRight
        except:
            obj._actionRight = False
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            obj._actionRight = True
        elif event == "RightButtonReleaseEvent":
            obj._actionRight = False
        if obj._actionRight:
            scene.picker.Pick(mouseX, mouseY, 0, scene.renderer)
            px, py, pz = scene.picker.GetPickPosition()

            Q = [px, py, pz]
            Q = scene.toOriginalView(Q)

            planes = self._mWindow.planes
            for plane in planes:
                if (not isinstance(plane.scene, VtkSliceImagePlane)) or plane.scene == scene:
                    continue
                plane.setSliceToPosition(Q)
                scene.window.Render()

    def _slotActionPointerMiddle(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionPointerLeft()")
        scene = plane.scene
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionMiddle
        except:
            obj._actionMiddle = False
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            obj._actionMiddle = True
        elif event == "MiddleButtonReleaseEvent":
            obj._actionMiddle = False
        if obj._actionMiddle:
            scene.picker.Pick(mouseX, mouseY, 0, scene.renderer)
            px, py, pz = scene.picker.GetPickPosition()

            Q = [px, py, pz]
            Q = scene.toOriginalView(Q)

            planes = self._mWindow.planes
            for plane in planes:
                if (not isinstance(plane.scene, VtkSliceImagePlane)) or plane.scene == scene:
                    continue
                plane.setSliceToPosition(Q)
                scene.window.Render()

    def _slotActionChangeSliceLeft(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionChangeSliceLeft()")
        scene = plane.scene
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionLeft
        except:
            obj._actionLeft = False
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            obj._actionLeft = True
        elif event == "LeftButtonReleaseEvent":
            obj._actionLeft = False
            obj.OnLeftButtonUp()
        else:
            if obj._actionLeft:
                deltaY = mouseY - lastY
                z = plane.planeSlideValue + deltaY
                plane.planeSlide.setValue(z)
                plane.planeSlide.update()
                scene.render()

    def _slotActionChangeSliceRight(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionChangeSliceLeft()")
        scene = plane.scene
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionRight
        except:
            obj._actionRight = False
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            obj._actionRight = True
        elif event == "RightButtonReleaseEvent":
            obj._actionRight = False
            obj.OnRightButtonUp()
        else:
            if obj._actionRight:
                deltaY = mouseY - lastY
                z = plane.planeSlideValue + deltaY
                plane.planeSlide.setValue(z)
                plane.planeSlide.update()
                scene.render()

    def _slotActionChangeSliceMiddle(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionChangeSliceLeft()")
        scene = plane.scene
        (lastX, lastY) = scene.interactor.GetLastEventPosition()
        (mouseX, mouseY) = scene.interactor.GetEventPosition()
        try:
            obj._actionMiddle
        except:
            obj._actionMiddle = False
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            obj._actionMiddle = True
        elif event == "MiddleButtonReleaseEvent":
            obj._actionMiddle = False
            obj.OnMiddleButtonUp()
        else:
            if obj._actionMiddle:
                deltaY = mouseY - lastY
                z = plane.planeSlideValue + deltaY
                plane.planeSlide.setValue(z)
                plane.planeSlide.update()
                scene.render()

    def _slotActionNoneLeft(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionNone()")
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  self.actionsChooser(self.BUTTON_LEFT)

    def _slotActionNoneRight(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionNone()")
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  self.actionsChooser(self.BUTTON_RIGHT)

    def _slotActionNoneMiddle(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionNone()")
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  self.actionsChooser(self.BUTTON_MIDDLE)

    def _slotActionNoneScroll(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionNone()")
        if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              self.actionsChooser(self.BUTTON_SCROLL)

    def _slotActionTranslateLeft(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionTranslate()")
        scene = plane.scene
        try:
            obj._actionLeft
        except:
            obj._actionLeft = False
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            else:
              obj._actionLeft = True
        elif event == "LeftButtonReleaseEvent":
            obj._actionLeft = False
            obj.OnLeftButtonUp()
        else:
            if obj._actionLeft:
                obj.Pan()
                obj.OnLeftButtonDown()
                scene.window.Render()

    def _slotActionFlipHorizontalLeft(self, obj, event, plane):
        scene = plane.scene
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            scene.flipHorizontal()

    def _slotActionFlipHorizontalRight(self, obj, event, plane):
        scene = plane.scene
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            scene.flipHorizontal()

    def _slotActionFlipHorizontalMiddle(self, obj, event, plane):
        scene = plane.scene
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            scene.flipHorizontal()

    def _slotActionFlipVerticalLeft(self, obj, event, plane):
        scene = plane.scene
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            scene.flipVertical()
        elif event == "LeftButtonReleaseEvent":
            obj.OnLeftButtonUp()

    def _slotActionFlipVerticalRight(self, obj, event, plane):
        scene = plane.scene
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            scene.flipVertical()
        elif event == "RightButtonReleaseEvent":
            obj.OnRightButtonUp()

    def _slotActionFlipVerticalMiddle(self, obj, event, plane):
        scene = plane.scene
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            scene.flipVertical()
        elif event == "MiddleButtonReleaseEvent":
            obj.OnMiddleButtonUp()

    def _slotActionZoomLeft(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionLeft
        except:
            obj._actionLeft = False
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            obj._actionLeft = True
        elif event == "LeftButtonReleaseEvent":
            obj._actionLeft = False
            obj.OnLeftButtonUp()
        else:
            if obj._actionLeft:
                scene.interactorStyle.Dolly()
                scene.interactorStyle.OnLeftButtonDown()
                scene.window.Render()
            else:
                obj.OnLeftButtonUp()

    def _slotActionZoomRight(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionRight
        except:
            obj._actionRight = False
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            obj._actionRight = True
        elif event == "RightButtonReleaseEvent":
            obj._actionRight = False
            obj.OnLeftButtonUp()
        else:
            if obj._actionRight:
                scene.interactorStyle.Dolly()
                scene.interactorStyle.OnRightButtonDown()
                scene.window.Render()
            else:
                obj.OnRightButtonUp()

    def _slotActionZoomScroll(self, obj, event, plane):
        if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  self.actionsChooser(self.BUTTON_SCROLL)
                  return
        if event == "MouseWheelForwardEvent":
            plane.scene.camera.Zoom(1.1)

        else:
            plane.scene.camera.Zoom(0.9)
        plane.planeSlide.update()
        plane.scene.window.Render()

    def _slotActionZoomMiddle(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionMiddle
        except:
            obj._actionMiddle = False
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            obj._actionMiddle = True
        elif event == "MiddleButtonReleaseEvent":
            obj._actionMiddle = False
            obj.OnMiddleButtonUp()
        else:
            if obj._actionMiddle:
                scene.interactorStyle.Dolly()
                scene.interactorStyle.OnMiddleButtonDown()
                scene.window.Render()
            else:
                obj.OnMiddleButtonUp()

    def slotActionRotateLeft(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionLeft
        except:
            obj._actionLeft = False
        if event == "LeftButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
              obj._actionLeft = False
              self.actionsChooser(self.BUTTON_LEFT)
              return
            obj._actionLeft = True
        elif event == "LeftButtonReleaseEvent":
            obj._actionLeft = False
            obj.OnLeftButtonUp()
        else:
            if obj._actionLeft:
                obj.Spin()
                obj.OnLeftButtonDown()
                scene.window.Render()
            else:
                obj.OnLeftButtonUp()

    def slotActionRotateRight(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionRight
        except:
            obj._actionRight = False
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            obj._actionRight = True
        elif event == "RightButtonReleaseEvent":
            obj._actionRight = False
            obj.OnRightButtonUp()
        else:
            if obj._actionRight:
                obj.Spin()
                obj.OnRightButtonDown()
                scene.window.Render()
            else:
                obj.OnRightButtonUp()

    def slotActionRotateMiddle(self, obj, event, plane):
        scene = plane.scene
        try:
            obj._actionMiddle
        except:
            obj._actionMiddle = False
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            obj._actionMiddle = True
        elif event == "MiddleButtonReleaseEvent":
            obj._actionMiddle = False
            obj.OnMiddleButtonUp()
        else:
            if obj._actionMiddle:
                obj.Spin()
                obj.OnMiddleButtonDown()
                scene.window.Render()
            else:
                obj.OnMiddleButtonUp()

    def _slotActionTranslateRight(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionTranslateRight()")
        scene = plane.scene
        try:
            obj._actionRight
        except:
            obj._actionRight = False
        if event == "RightButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionRight = False
                  self.actionsChooser(self.BUTTON_RIGHT)
                  return
            obj._actionRight = True
        elif event == "RightButtonReleaseEvent":
            obj._actionRight = False
            obj.OnRightButtonUp()
        else:
            if obj._actionRight:
                obj.Pan()
                obj.OnRightButtonDown()
                scene.window.Render()
            else:
                obj.OnRightButtonUp()

    def _slotActionTranslateMiddle(self, obj, event, plane):
        logging.debug("In CameraController2D::_slotActionTranslateMiddle()")
        scene = plane.scene
        try:
            obj._actionMiddle
        except:
            obj._actionMiddle = False
        if event == "MiddleButtonPressEvent":
            if plane.scene.interactor.GetRenderWindow().GetInteractor().GetControlKey():
                  obj._actionMiddle = False
                  self.actionsChooser(self.BUTTON_MIDDLE)
                  return
            obj._actionMiddle = True
        elif event == "MiddleButtonReleaseEvent":
            obj._actionMiddle = False
            obj.OnRightButtonUp()
        else:
            if obj._actionMiddle:
                obj.Pan()
                obj.OnMiddleButtonDown()
                scene.window.Render()
            else:
                obj.OnMiddleButtonUp()

    def createWidgets(self):
        logging.debug("In CameraController2D::createWidgets()")
        self._actionLeftButton = QtGui.QAction(self._mainWindow)
        self._actionLeftButton.setCheckable(False)
        self._actionLeftButton.setObjectName("actionLeftButton")
        self._actionLeftButton.setText(
            QtGui.QApplication.translate("CameraController2D", "Left",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self._mWindow.connect(self._actionLeftButton, QtCore.SIGNAL("triggered()"),
                              lambda a=self.BUTTON_LEFT: self.actionsChooser(a))

        self._mainWindow.toolBarTools_2.addAction(self._actionLeftButton)


        self._actionMiddleButton = QtGui.QAction(self._mainWindow)
        self._actionMiddleButton.setCheckable(False)
        self._actionMiddleButton.setObjectName("actionMiddleButton")
        self._actionMiddleButton.setText(
            QtGui.QApplication.translate("CameraController2D", "Middle",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self._mWindow.connect(self._actionMiddleButton, QtCore.SIGNAL("triggered()"),
                              lambda a=self.BUTTON_MIDDLE: self.actionsChooser(a))
        self._mainWindow.toolBarTools_2.addAction(self._actionMiddleButton)

        self._actionScroll = QtGui.QAction(self._mainWindow)
        self._actionScroll.setCheckable(False)
        self._actionScroll.setObjectName("actionScroll")
        self._actionScroll.setText(
            QtGui.QApplication.translate("CameraController2D", "Scroll",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self._mWindow.connect(self._actionScroll, QtCore.SIGNAL("triggered()"),
                              lambda a=self.BUTTON_SCROLL: self.actionsChooser(a))
        self._mainWindow.toolBarTools_2.addAction(self._actionScroll)

        self._actionRightButton = QtGui.QAction(self._mainWindow)
        self._actionRightButton.setCheckable(False)
        self._actionRightButton.setObjectName("actionRightButton")
        self._actionRightButton.setText(
            QtGui.QApplication.translate("CameraController2D", "Right",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self._mWindow.connect(self._actionRightButton, QtCore.SIGNAL("triggered()"),
                              lambda a=self.BUTTON_RIGHT: self.actionsChooser(a))
        self._mainWindow.toolBarTools_2.addAction(self._actionRightButton)
    
    def actionsChooser(self, actionType):
        logging.debug("In CameraController2D::leftButtonChooser()")
        menu = QtGui.QMenu(self._mWindow)
        for action in self._actions[actionType]:
            menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())

    def slotActionChoosed(self, action):
        logging.debug("In CameraController2D::slotActionChoosed()")
        actionType = action.actionType
        actionSlot = action.actionSlot
        if actionType == self.BUTTON_LEFT:
            self._actionLeftButton.setIcon(action.icon())
        elif actionType == self.BUTTON_RIGHT:
            self._actionRightButton.setIcon(action.icon())
        elif actionType == self.BUTTON_MIDDLE:
            self._actionMiddleButton.setIcon(action.icon())
        elif actionType == self.BUTTON_SCROLL:
            self._actionScroll.setIcon(action.icon())
        for key in self._activeEvents[actionType].keys():
            scene = key[0]
            scene.interactorStyle.RemoveObserver(self._activeEvents[actionType][key])
        self._activeActions[actionType] = action
        self._activeEvents[actionType] = {}
        events = self._getEventList(actionType)
        planes = self._mWindow.planes
        for event in events:
            for plane in planes:
                if not isinstance(plane.scene, VtkImageVolume):
                    eventNumber = plane.scene.interactorStyle.AddObserver(event, lambda o, e, s=plane: actionSlot(o, e, s))
                    self._activeEvents[actionType][plane.scene, event] = eventNumber

    def addAction(self, actionID, actionType, actionSlot, icon, text):
        logging.debug("In CameraController2D::addAction()")
        action = QtGui.QAction(self._mainWindow)
        action.setCheckable(False)
        action.setText(
            QtGui.QApplication.translate(text, "&{0}".format(text),
                                         None, QtGui.QApplication.UnicodeUTF8))
        action.setIcon(icon)
        action.actionID = actionID
        action.actionType = actionType
        action.actionSlot = actionSlot
        self._actions[actionType].append(action)
        self._mWindow.connect(action,
                              QtCore.SIGNAL("triggered()"),
                              lambda a=action:
                              self.slotActionChoosed(a))

    def _getEventList(self, actionType):
        logging.debug("In CameraController2D::_getEventList()")
        if actionType == self.BUTTON_LEFT:
            return ["LeftButtonPressEvent", "LeftButtonReleaseEvent", "MouseMoveEvent"]
        elif actionType == self.BUTTON_RIGHT:
            return ["RightButtonPressEvent", "RightButtonReleaseEvent", "MouseMoveEvent"]
        elif actionType == self.BUTTON_MIDDLE:
            return ["MiddleButtonPressEvent", "MiddleButtonReleaseEvent", "MouseMoveEvent"]
        elif actionType == self.BUTTON_SCROLL:
            return ["MouseWheelForwardEvent", "MouseWheelBackwardEvent"]

    def selectAction(self, actionID, actionType):
        logging.debug("In CameraController2D::selectAction()")
        for action in self._actions[actionType]:
            if action.actionID == actionID:
                self.slotActionChoosed(action)

    def lockAction(self, actionType, actionID, lock):
        for action in self._actions[actionType]:
            if action.actionID == actionID:
                action.setDisabled(lock)
                return

    def lockButton(self, actionType, lock):
        actionList = self._actions[actionType]
        for action in actionList:
            action.setDisabled(lock)

    def lockButtons(self, lock):
        for actionList in self._actions.values():
            for action in actionList:
                action.setDisabled(lock)

    def updatePlanes(self):
        for action in self._activeActions.values():
            if action:
                self.slotActionChoosed(action)

    def setDefaults(self, actionLeft=None, actionRight=None, actionMiddle=None, actionScroll=None):
        if actionLeft:
            self.selectAction(actionLeft, self.BUTTON_LEFT)
        else:
            self.selectAction(self.ACTION_TRANSLATE, self.BUTTON_LEFT)
        if actionRight:
            self.selectAction(actionRight, self.BUTTON_RIGHT)
        else:
            self.selectAction(self.ACTION_ZOOM, self.BUTTON_RIGHT)
        if actionMiddle:
            self.selectAction(actionMiddle, self.BUTTON_MIDDLE)
        else:
            self.selectAction(self.ACTION_POINTER, self.BUTTON_MIDDLE)
        if actionScroll:
            self.selectAction(actionScroll, self.BUTTON_SCROLL)
        else:
            self.selectAction(self.ACTION_CHANGE_SLICE, self.BUTTON_SCROLL)

    def getActiveAction(self, actionType):
        return self._activeActions[actionType].actionID