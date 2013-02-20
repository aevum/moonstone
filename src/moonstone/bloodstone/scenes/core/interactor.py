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
import types
import logging

import vtk


class VtkInteractor(object):

    def __init__(self, interactor):
        logging.debug("In VtkInteractor::__init__()")
        self._interactor = interactor
        self._interactorStyle = self._interactor.GetInteractorStyle()
        self._window = self._interactor.GetRenderWindow()
        if self._window.GetRenderers().GetFirstRenderer() is None:
            self._window.AddRenderer(vtk.vtkRenderer())
        self._renderer = self._window.GetRenderers().GetFirstRenderer()
        self._camera = self._renderer.GetActiveCamera()
        self._actor = None
        self._actors = []
        self._culler = None
        self._cullers = []
        self._light = None
        self._lights = []
        self._volume = None
        self._volumes = []

    @property
    def interactor(self):
        return self._interactor

    @property
    def interactorStyle(self):
        logging.debug("In VtkInteractor::interactorStyle.getter()")
        return self._interactorStyle

    @interactorStyle.setter
    def interactorStyle(self, interactorStyle):
        logging.debug("In VtkInteractor::interactorStyle.setter()")
        self._interactorStyle = interactorStyle
        self.updateInteractorStyle()
        self._interactor.SetInteractorStyle(interactorStyle)
        
    def updateInteractorStyle(self):
        logging.debug("In VtkInteractor::updateInteractorStyle()")
        pass

    @interactorStyle.deleter
    def interactorStyle(self):
        logging.debug("In VtkInteractor::interactorStyle.deleter()")
        self._interactor.SetInteractorStyle(None)
        self._interactorStyle = None

    @property
    def window(self):
        logging.debug("In VtkInteractor::window.getter()")
        return self._window

    @window.setter
    def window(self, window):
        logging.debug("In VtkInteractor::window.setter()")
        self._interactor.SetRenderWindow(window)
        self._window = window

    @window.deleter
    def window(self):
        logging.debug("In VtkInteractor::window.deleter()")
        self._interactor.SetRenderWindow(None)
        self._window = None

    @property
    def renderer(self):
        logging.debug("In VtkInteractor::renderer.getter()")
        return self._renderer

    @renderer.setter
    def renderer(self, renderer):
        logging.debug("In VtkInteractor::renderer.setter()")
        renderers = self._window.GetRenderers()
        nRenderers = renderers.GetNumberOfItems()
        for x in range(nRenderers):
            self._window.RemoveRenderer(renderers.GetNextItem())
        self._window.AddRenderer(renderer)
        self._renderer = renderer

    @renderer.deleter
    def renderer(self):
        logging.debug("In VtkInteractor::renderer.deleter()")
        self._window.RemoveRenderer(self._renderer)
        self._renderer = None

    @property
    def camera(self):
        logging.debug("In VtkInteractor::camera.getter()")
        return self._renderer.GetActiveCamera()

    @camera.setter
    def camera(self, camera):
        logging.debug("In VtkInteractor::camera.setter()")
        self._renderer.SetActiveCamera(camera)
        self._camera = camera

    @camera.deleter
    def camera(self):
        logging.debug("In VtkInteractor::camera.deleter()")
        self._renderer.ResetCamera()
        self._camera = None

    @property
    def actor(self):
        logging.debug("In VtkInteractor::actor.getter()")
        return self._actor

    @actor.setter
    def actor(self, actor):
        logging.debug("In VtkInteractor::actor.setter()")
        actors = self._renderer.GetActors()
        nActors = actors.GetNumberOfItems()
        for x in range(nActors):
            self._renderer.RemoveActor(actors.GetNextItem())
        self._renderer.AddActor(actor)
        self._renderer.Render()
        self._actor = actor

    @actor.deleter
    def actor(self):
        logging.debug("In VtkInteractor::actor.deleter()")
        self._renderer.RemoveActor(self._actor)
        self._renderer.Render()
        self._actor = None

    def addActor(self, actor):
        logging.debug("In VtkInteractor::addActor()")
        self._renderer.AddActor(actor)
        self._renderer.Render()
        self._actors.append(actor)

    def removeActor(self, actor):
        logging.debug("In VtkInteractor::removeActor()")
        if not actor in self._actors:
            return
        self._renderer.RemoveActor(actor)
        self._renderer.Render()
        self._actors.remove(actor)

    @property
    def actors(self):
        logging.debug("In VtkInteractor::actors.getter()")
        return self._actors

    @actors.setter
    def actors(self, actors):
        logging.debug("In VtkInteractor::actors.setter()")
        if isinstance(actors, types.ListType) or \
           isinstance(actors, types.TupleType):
            for actor in actors:
                self._renderer.AddActor(actor)
            self._actors.extend(list(actors))
        elif isinstance(actors, types.DictionaryType):
            for actor in actors.itervalues():
                self._renderer.AddActor(actor)
            self._actors.extend(actors.values())
        else:
            self._renderer.AddActor(actors)
            self._actors.append(actors)
        self._renderer.Render()

    @actors.deleter
    def actors(self):
        logging.debug("In VtkInteractor::actors.deleter()")
        for actor in self._actors:
            self._renderer.RemoveActor(actor)
        self._renderer.Render()
        self._actors = []

    def addCuller(self, culler):
        logging.debug("In VtkInteractor::addCuller()")
        self._renderer.AddCuller(culler)
        self._renderer.Render()
        self._cullers.append(culler)

    def removeCuller(self, culler):
        logging.debug("In VtkInteractor::removeCuller()")
        if not culler in self._cullers:
            return
        self._renderer.RemoveCuller(culler)
        self._renderer.Render()
        self._cullers.vtkRemove(culler)

    @property
    def culler(self):
        logging.debug("In VtkInteractor::culler.getter()")
        return self._culler

    @culler.setter
    def culler(self, culler):
        logging.debug("In VtkInteractor::culler.setter()")
        cullers = self._renderer.GetCullers()
        nCullers = cullers.GetNumberOfItems()
        for x in range(nCullers):
            self._renderer.RemoveCuller(cullers.GetNextItem())
        self._renderer.AddCuller(culler)
        self._renderer.Render()
        self._culler = culler

    @culler.deleter
    def culler(self):
        logging.debug("In VtkInteractor::culler.deleter()")
        self._renderer.RemoveCuller(self._culler)
        self._renderer.Render()
        self._culler = None

    @property
    def cullers(self):
        logging.debug("In VtkInteractor::cullers.getter()")
        return self._cullers

    @cullers.setter
    def cullers(self, cullers):
        logging.debug("In VtkInteractor::cullers.setter()")
        if isinstance(cullers, types.ListType) or \
           isinstance(cullers, types.TupleType):
            for culler in cullers:
                self._renderer.AddCuller(culler)
            self._cullers.extend(list(cullers))
        elif isinstance(cullers, types.DictionaryType):
            for culler in cullers.itervalues():
                self._renderer.AddCuller(culler)
            self._cullers.extend(cullers.values())
        else:
            self._renderer.AddCuller(cullers)
            self._cullers.append(cullers)
        self._renderer.Render()

    @cullers.deleter
    def cullers(self):
        logging.debug("In VtkInteractor::cullers.deleter()")
        for culler in self._cullers:
            self._renderer.RemoveCuller(culler)
        self._renderer.Render()
        self._cullers = []

    def addLight(self, light):
        logging.debug("In VtkInteractor::addLight()")
        self._renderer.AddLight(light)
        self._renderer.Render()
        self._lights.append(light)

    def removeLight(self, light):
        logging.debug("In VtkInteractor::removeLight()")
        if not light in self._lights:
            return
        self._renderer.RemoveLight(light)
        self._renderer.Render()
        self._lights.vtkRemove(light)

    @property
    def light(self):
        logging.debug("In VtkInteractor::light.getter()")
        return self._light

    @light.setter
    def light(self, light):
        logging.debug("In VtkInteractor::light.setter()")
        lights = self._renderer.GetLights()
        nLights = lights.GetNumberOfItems()
        for x in range(nLights):
            self._renderer.RemoveLight(lights.GetNextItem())
        self._renderer.AddLight(light)
        self._renderer.Render()
        self._light = light

    @light.deleter
    def light(self):
        logging.debug("In VtkInteractor::light.deleter()")
        self._renderer.RemoveLight(self._light)
        self._renderer.Render()
        self._light = None

    @property
    def lights(self):
        logging.debug("In VtkInteractor::lights.getter()")
        return self._lights

    @lights.setter
    def lights(self, lights):
        logging.debug("In VtkInteractor::lights.setter()")
        if isinstance(lights, types.ListType) or \
           isinstance(lights, types.TupleType):
            for light in lights:
                self._renderer.AddLight(light)
            self._lights.extend(list(lights))
        elif isinstance(lights, types.DictionaryType):
            for light in lights.itervalues():
                self._renderer.AddLight(light)
            self._lights.extend(lights.values())
        else:
            self._renderer.AddLight(lights)
            self._lights.append(lights)
        self._renderer.Render()

    @lights.deleter
    def lights(self):
        logging.debug("In VtkInteractor::lights.deleter()")
        for light in self._lights:
            self._renderer.RemoveLight(light)
        self._renderer.Render()
        self._lights = []

    def addVolume(self, volume):
        logging.debug("In VtkInteractor::addVolume()")
        self._renderer.AddVolume(volume)
        self._renderer.Render()
        self._volumes.append(volume)

    def removeVolume(self, volume):
        logging.debug("In VtkInteractor::removeVolume()")
        if not volume in self._volumes:
            return
        self._renderer.RemoveVolume(volume)
        self._renderer.Render()
        self._volumes.remove(volume)

    @property
    def volume(self):
        logging.debug("In VtkInteractor::volume.getter()")
        return self._volume

    @volume.setter
    def volume(self, volume):
        logging.debug("In VtkInteractor::volume.setter()")
        volumes = self._renderer.GetVolumes()
        nVolumes = volumes.GetNumberOfItems()
        for x in range(nVolumes):
            self._renderer.RemoveVolume(volumes.GetNextItem())
        self._renderer.AddVolume(volume)
        self._renderer.Render()
        self._volume = volume

    @volume.deleter
    def volume(self):
        logging.debug("In VtkInteractor::volume.deleter()")
        self._renderer.RemoveVolume(self._volume)
        self._renderer.Render()
        self._volume = None

    @property
    def volumes(self):
        logging.debug("In VtkInteractor::volumes.getter()")
        return self._volumes

    @volumes.setter
    def volumes(self, volumes):
        logging.debug("In VtkInteractor::volumes.setter()")
        if isinstance(volumes, types.ListType) or \
           isinstance(volumes, types.TupleType):
            for volume in volumes:
                self._renderer.AddVolume(volume)
            self._volumes.extend(list(volumes))
        elif isinstance(volumes, types.DictionaryType):
            for volume in volumes.itervalues():
                self._renderer.AddVolume(volume)
            self._volumes.extend(volumes.values())
        else:
            self._renderer.AddVolume(volumes)
            self._volumes.append(volumes)
        self._renderer.Render()

    @volumes.deleter
    def volumes(self):
        logging.debug("In VtkInteractor::volumes.deleter()")
        for volume in self._volumes:
            self._renderer.RemoveVolume(volume)
        self._renderer.Render()
        self._volumes = []
    
    def destroy(self):
        del self.actor
        del self.actors
        del self.camera
        del self.culler
        del self.cullers
        del self.light
        del self.lights
        del self.volume
        del self.volumes
        del self.interactorStyle
        del self.renderer
        del self._renderer
        self._interactor.destroy()
        
#        import objgraph
#        objgraph.show_refs(self._interactor)
        del self._interactor

