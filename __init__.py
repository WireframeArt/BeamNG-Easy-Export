#    <Beamng Easy Export, Blender addon for exporting objects to BeamNG.>
#    Copyright (C) <2023> <Damian Paterson>
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Beamng Easy Export",
    "author": "Damian Paterson / Wireframe Art",
    "version": (2, 0),
    "blender": (3, 6, 1),
    "location": "Properties > Scene > Beamng Easy Export",
    "description": "A tool to simplify the process of exporting Collada files for BeamngNG",
    "category": "Export",
}

from .LODUIList import *
from .export_bng_object import *
from .bng_export_ui import *
from bpy.props import CollectionProperty


classes = [BngexportProperties, BNGEXPORT_PT_main_panel, BNGEXPORT_OT_export_op, MT_ExportPresets, OT_AddExportPreset,MY_PT_presets, LOD_UL_List, LodProperties, LIST_OT_NewItem, LIST_OT_DeleteItem, LIST_OT_MoveItem] 

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bngexport_tools = bpy.props.PointerProperty(type=BngexportProperties)
    bpy.types.Scene.lod_list = CollectionProperty(type=LodProperties)
    bpy.types.Scene.list_index = IntProperty(name="Index for lod_list", default = 0)
 
def unregister():
    del bpy.types.Scene.bngexport_tools
    del bpy.types.Scene.lod_list
    del bpy.types.Scene.list_index
    for cls in classes:
        bpy.utils.unregister_class(cls)
 
if __name__ == "__main__":
    register()
