# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "ACeTrack",
    "author": "Phineas Engl",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

import bpy

from .Functions import get_properties
from .Tools_Materials import load_materials
from . import auto_load

auto_load.init()


def init():
    context = bpy.context

    if not context.scene: # check if context is loaded
        return
    
    # init custom materials
    load_materials(context) # FIXME init hier bringt nur bedingt was, wenn man dann erst projekt öffnet -> auch woanders init für track_folder
    
    return None


def register():
    auto_load.register()

    bpy.app.timers.register(init, first_interval=0.1) # delay so context is loaded already
    


def unregister():
    auto_load.unregister()
