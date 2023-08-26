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

import bpy
from bpy.types import UIList
from bpy.props import IntProperty, PointerProperty, BoolProperty, EnumProperty

class LodProperties(bpy.types.PropertyGroup):
    lod_object : PointerProperty(type=bpy.types.Object, name="LOD Object")
    lod_collection : PointerProperty(type=bpy.types.Collection, name="LOD Collection")
    lod_pixel_size : IntProperty(default = 0)
    lod_modifiers_bool : BoolProperty(name="Apply Modifiers", default = False)
    lod_object_type_enum : EnumProperty(
    name = "LOD Object Type",
    default = 'OBJECT',
    items = [('OBJECT','Object','Object LOD Type','OBJECT_DATA',0), 
             ('COLLECTION','Collection','Collection LOD Type','OUTLINER_COLLECTION',1)],
    )
    lod_type_enum : EnumProperty(
    name = "LOD Type",
    default = 'SHAPE',
    items = [('SHAPE','Shape','Visual Shape Level of Detail','OBJECT_DATA',0), 
             ('COLLISION','Collision','Collision Level of Detail','OBJECT_DATA',1),
             ('BILLBOARD','Billboard','Billboard Level of Detail','OBJECT_DATA',2),
             ('AUTOBILLBOARD','Auto Billboard','Auto Billboard Level of Detail','EMPTY_DATA',3),
             ('NULLDETAIL','Null Detail','Null Level of Detail','EMPTY_DATA',4),
             ('CENTER','Center','Non Export object used to specifiy the center of the exported object','EMPTY_DATA',5)],
    )

class LOD_UL_List(UIList):
    """LOD UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        scene = context.scene
        bngexporttools = scene.bngexport_tools
        custom_icon = 'ERROR'
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            
            #---Sets Naming for UI List Objects---#
            
            customname = "INVALID"
            if item.lod_pixel_size or item.lod_pixel_size == 0:
                customname = bngexporttools.object_name_prop + "_d"+str(item.lod_pixel_size)
                
            lodtype = item.lod_type_enum
            
            if lodtype == "CENTER":
                customname = "Center"
            if lodtype == "NULLDETAIL":
                customname = "nulldetail"+str(item.lod_pixel_size)
            if lodtype == "COLLISION":
                customname = "Colmesh-1"
            if lodtype == "BILLBOARD":
                customname = "bb_"+bngexporttools.object_name_prop+str(item.lod_pixel_size)
            if lodtype == "AUTOBILLBOARD":
                customname = "bb_autobillboard"+str(item.lod_pixel_size)

            #---Sets Icon---#
            
            if lodtype == "BILLBOARD" or lodtype == "SHAPE" or lodtype == "COLLISION":
                custom_icon = 'OBJECT_DATA'
            if lodtype == "CENTER" or lodtype == "NULLDETAIL" or lodtype == "AUTOBILLBOARD":
                custom_icon = 'EMPTY_DATA'
                
            layout.label(text=customname, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class LIST_OT_NewItem(bpy.types.Operator):
    """Add a new item to the list."""
    bl_idname = "lod_list.new_item"
    bl_label = "Add a new item"
    def execute(self, context):
        context.scene.lod_list.add()
        return{'FINISHED'}
    
class LIST_OT_DeleteItem(bpy.types.Operator):
    """Delete the selected lod from the list."""
    bl_idname = "lod_list.delete_item"
    bl_label = "Deletes an lod"
    @classmethod
    def poll(cls, context):
        return context.scene.lod_list

    def execute(self, context):
        lod_list = context.scene.lod_list
        index = context.scene.list_index
        lod_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(lod_list) - 1)
        return{'FINISHED'}
    
class LIST_OT_MoveItem(bpy.types.Operator):
    """Move an lod in the list."""
    bl_idname = "lod_list.move_item"
    bl_label = "Move an lod in the list"
    direction : bpy.props.EnumProperty(items=(
        ('UP', 'Up', ""),
        ('DOWN', 'Down', ""),
        ))

    @classmethod
    def poll(cls, context):
        return context.scene.lod_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """
        index = bpy.context.scene.list_index
        list_length = len(bpy.context.scene.lod_list) - 1
        new_index = index + (-1 if self.direction == 'UP' else 1)
        bpy.context.scene.list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        lod_list = context.scene.lod_list
        index = context.scene.list_index
        neighbor = index + (-1 if self.direction == 'UP' else 1)
        lod_list.move(neighbor, index)
        self.move_index()
        return{'FINISHED'}
