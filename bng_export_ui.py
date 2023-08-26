#    <Beamng Easy Export, Blender addon for exporting objects to BeamNG.>
#    Copyright (C) <2022> <Damian Paterson>
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
from bpy.props import StringProperty
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel 
from bpy.types import Panel, Menu

class BngexportProperties(bpy.types.PropertyGroup):
    export_file_path : bpy.props.StringProperty(name="export path",description="Directory Collada File will be exported to",subtype='DIR_PATH')
    object_name_prop : StringProperty(name="Object Name", description="Name used for LODs and the exported file")
    
class BNGEXPORT_PT_main_panel(bpy.types.Panel):
    bl_label = "BeamNG Easy Export"
    bl_idname = "BNGEXPORT_PT_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_category = "Beamng Easy Export"
    
    def draw_header_preset(self, _context): 
        MY_PT_presets.draw_panel_header(self.layout)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bngexporttools = scene.bngexport_tools
        layout.operator("bngexport.export_operator")
        layout.prop(bngexporttools, "export_file_path")
        layout.prop(bngexporttools, "object_name_prop")
        row = layout.row()
        row.template_list("LOD_UL_List", "LOD_List", scene,"lod_list", scene, "list_index")
        column = row.column()
        column.operator("lod_list.new_item", icon= 'ADD', text= "")
        column.operator("lod_list.delete_item", icon= 'REMOVE', text= "")
        column.operator('lod_list.move_item', icon='TRIA_UP',text= "").direction = 'UP' 
        column.operator('lod_list.move_item', icon='TRIA_DOWN',text= "").direction = 'DOWN'

        if scene.list_index >= 0 and scene.lod_list:
            item = scene.lod_list[scene.list_index]
            row = layout.row()
            column = row.column()
            
            if item.lod_type_enum == "SHAPE" or item.lod_type_enum == "COLLISION" or item.lod_type_enum == "BILLBOARD" or item.lod_type_enum == "CENTER":
                if item.lod_object_type_enum == "OBJECT":
                    column.prop(item, "lod_object")
                else:
                    column.prop(item, "lod_collection")
                if item.lod_type_enum != "CENTER":
                    column.prop(item, "lod_object_type_enum")
                    
            column.prop(item, "lod_type_enum")
            
            if item.lod_type_enum != "CENTER" and item.lod_type_enum != "COLLISION":        
                split = column.split(factor= 0.23)
                split.label(text="LOD Pixel Size:")
                split.prop(item, "lod_pixel_size", text="")
                
            if item.lod_type_enum == "SHAPE" or item.lod_type_enum == "COLLISION" or item.lod_type_enum == "BILLBOARD":
                column.prop(item, "lod_modifiers_bool")
                
#---Creates Presets---#

class MT_ExportPresets(Menu): 
    bl_label = 'My Presets' 
    preset_subdir = 'object/my_presets' 
    preset_operator = 'script.execute_preset' 
    draw = Menu.draw_preset

class OT_AddExportPreset(AddPresetBase, bpy.types.Operator):
    bl_idname = 'my.add_preset'
    bl_label = 'Add A preset'
    preset_menu = 'MT_MyPresets'
        
    # Common variable used for all preset values
    preset_defines = [
                        'obj = bpy.context.object',
                        'scene = bpy.context.scene',
                        'bngexporttools = scene.bngexport_tools',    
                     ]

    # Properties to store in the preset
    preset_values = [
                        'bngexporttools.export_file_path ',
                        'bngexporttools.object_name_prop',
                        'scene.lod_list',
                    ]
                    
    # Directory to store the presets
    preset_subdir = 'object/my_presets'
    
class MY_PT_presets(PresetPanel, Panel): 
    bl_label = 'My Presets' 
    preset_subdir = 'object/my_presets' 
    preset_operator = 'script.execute_preset' 
    preset_add_operator = 'my.add_preset'
                      
