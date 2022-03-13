bl_info = {
    "name": "Beamng Easy Export",
    "author": "Damian Paterson / Wireframe Art",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Scene > Beamng Easy Export",
    "description": "A tool to simplify the process of exporting Collada files for BeamngNG",
    "category": "Export",
}

import bpy
from bpy.props import PointerProperty, IntProperty, BoolProperty, StringProperty

class LodProperties(bpy.types.PropertyGroup):
    lod_object : PointerProperty(type=bpy.types.Object)
    lod_pixel_size : IntProperty()
    
class BngexportProperties(bpy.types.PropertyGroup):
    export_file_path : bpy.props.StringProperty(name="export path",description="Directory Collada File will be exported to",subtype='DIR_PATH')
    collision_object_prop : PointerProperty(type=bpy.types.Object, name="Collision Mesh")
    object_name_prop : StringProperty(name="Object Name", description="Name used for LODs and the exported file")
    lod1_object_prop : PointerProperty(type=bpy.types.Object, name="LOD 1", description="LOD Object")
    lod1_pixel_size : IntProperty(name="", description="Pixel Size for LOD")
    lod2_object_prop : PointerProperty(type=bpy.types.Object, name="LOD 2", description="LOD Object")
    lod2_pixel_size : IntProperty(name="", description="Pixel Size for LOD")
    lod3_object_prop : PointerProperty(type=bpy.types.Object, name="LOD 3", description="LOD Object")
    lod3_pixel_size : IntProperty(name="", description="Pixel Size for LOD")
    lod4_object_prop : PointerProperty(type=bpy.types.Object, name="LOD 4", description="LOD Object")
    lod4_pixel_size : IntProperty(name="", description="Pixel Size for LOD")
    lod5_object_prop : PointerProperty(type=bpy.types.Object, name="LOD 5", description="LOD Object")
    lod5_pixel_size : IntProperty(name="", description="Pixel Size for LOD")
    auto_billboard_prop : BoolProperty(name="Generate Autobillboard", description="Adds an empty object that BeamNG will use to create a billboard object")
    apply_modifiers : BoolProperty(name="Apply Modifiers", description="Applies modifiers on export")
    auto_billboard_pixel_size : IntProperty(name="billboard pixel size", description="Pixel Size for Billboard")
    origin_object_prop : PointerProperty(type=bpy.types.Object, name="Center", description="Will set the center of the Exported Object to this Object, if blank the center will be at 0,0,0" )
    
              
class BNGEXPORT_PT_main_panel(bpy.types.Panel):
    bl_label = "Beamng Easy Export"
    bl_idname = "BNGEXPORT_PT_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_category = "Beamng Easy Export"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bngexporttools = scene.bngexport_tools
        layout.operator("bngexport.export_operator")
        layout.prop(bngexporttools, "export_file_path")
        layout.prop(bngexporttools, "object_name_prop")
        row = layout.row()
        row.prop(bngexporttools, "lod1_object_prop")
        row.prop(bngexporttools, "lod1_pixel_size")
        row = layout.row()
        row.prop(bngexporttools, "lod2_object_prop")
        row.prop(bngexporttools, "lod2_pixel_size")
        row = layout.row()
        row.prop(bngexporttools, "lod3_object_prop")
        row.prop(bngexporttools, "lod3_pixel_size")
        row = layout.row()
        row.prop(bngexporttools, "lod4_object_prop")
        row.prop(bngexporttools, "lod4_pixel_size")
        row = layout.row()
        row.prop(bngexporttools, "lod5_object_prop")
        row.prop(bngexporttools, "lod5_pixel_size")
        row = layout.row()
        row.prop(bngexporttools, "auto_billboard_prop")
        row.prop(bngexporttools, "auto_billboard_pixel_size")
        layout.prop(bngexporttools, "apply_modifiers")
        layout.prop(bngexporttools, "collision_object_prop")
        layout.prop(bngexporttools, "origin_object_prop")


        
class BNGEXPORT_OT_export_op(bpy.types.Operator):
    """ Exports the object with the correct naming conventions and hierarchy
    """
    bl_label = "Export Objects"
    bl_idname = "bngexport.export_operator"
    def execute(self, context): 
        scene = context.scene
        bngexporttools = scene.bngexport_tools    
        testlist = []
        originalcontext = bpy.context.area.type
        bpy.context.area.type = 'VIEW_3D'
        bpy.ops.object.select_all(action='DESELECT')
        
        originlocation = (0,0,0)
        
        if bngexporttools.origin_object_prop:
            originlocation = bngexporttools.origin_object_prop.location
            
        bpy.ops.collection.create(name="TmpExportCollection")
        exportcol = bpy.data.collections["TmpExportCollection"]
        bpy.context.collection.children.link(exportcol)
            
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(originlocation), scale=(1, 1, 1))
        base = bpy.context.selected_objects[0]
            
        self.duplicatecheck(dupliname="base00")    
        base.name = "base00"
        self.setcollection(targetcol=exportcol, targetobj=base)
            
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(originlocation), scale=(1, 1, 1))
        start = bpy.context.selected_objects[0]
            
        self.duplicatecheck(dupliname="start01") 
        start.name = "start01"
        self.setcollection(targetcol=exportcol, targetobj=start)
        
        start.parent = base
        start.matrix_parent_inverse = base.matrix_world.inverted()
        
            
        if bngexporttools.lod1_object_prop: 
            lod1 = bngexporttools.lod1_object_prop
            lod1size = bngexporttools.lod1_pixel_size
            self.configurelod(currentlod=lod1, pixelsize=lod1size, tmpcol=exportcol, parentstart=start)
            
        if bngexporttools.lod2_object_prop:
            lod2 = bngexporttools.lod2_object_prop
            lod2size = bngexporttools.lod2_pixel_size
            self.configurelod(currentlod=lod2, pixelsize=lod2size, tmpcol=exportcol, parentstart=start)
            
        if bngexporttools.lod3_object_prop:
            lod3 = bngexporttools.lod3_object_prop
            lod3size = bngexporttools.lod3_pixel_size
            self.configurelod(currentlod=lod3, pixelsize=lod3size, tmpcol=exportcol, parentstart=start)
            
        if bngexporttools.lod4_object_prop:
            lod4 = bngexporttools.lod4_object_prop
            lod4size = bngexporttools.lod4_pixel_size
            self.configurelod(currentlod=lod4, pixelsize=lod4size, tmpcol=exportcol, parentstart=start)
            
        if bngexporttools.lod5_object_prop:
            lod5 = bngexporttools.lod5_object_prop
            lod5size = bngexporttools.lod5_pixel_size
            self.configurelod(currentlod=lod5, pixelsize=lod5size, tmpcol=exportcol, parentstart=start)
        
        if bngexporttools.auto_billboard_prop:
            billboardsize = bngexporttools.auto_billboard_pixel_size
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            billboard = bpy.context.selected_objects[0]
            
            billboardname = ("bb_autobillboard" + str(billboardsize))
            self.duplicatecheck(dupliname=billboardname)    
            billboard.name = billboardname
            self.setcollection(targetcol=exportcol, targetobj=billboard)
            billboard.parent = base
            billboard.matrix_parent_inverse = base.matrix_world.inverted()
                
        if bngexporttools.collision_object_prop:
            colmesh = bngexporttools.collision_object_prop
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.duplicate({"object" : colmesh,"selected_objects" : [colmesh]}, linked=False)
            loddup = bpy.context.selected_objects[0]
            
            dupname = ("Colmesh-1")
            self.duplicatecheck(dupliname=dupname)
            loddup.name = dupname
            self.setcollection(targetcol=exportcol, targetobj=loddup)
            loddup.parent = start
            loddup.matrix_parent_inverse = start.matrix_world.inverted()
              
        #Export
        bpy.ops.object.select_all(action='DESELECT')
        base.select_set(True)
        bpy.context.view_layer.objects.active = base
        
        exportpathabs = bpy.path.abspath(bngexporttools.export_file_path)
        exportpathfull = exportpathabs + bngexporttools.object_name_prop        
        bpy.ops.wm.collada_export(filepath=exportpathfull, check_existing=False, filter_blender=False, 
        apply_modifiers=bngexporttools.apply_modifiers,
        selected=True, 
        include_children=True, 
        triangulate=True)
        
        #Deletes Temporary Collection
        for obj in exportcol.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(exportcol, do_unlink=True)
        
        bpy.context.area.type = originalcontext
        return {'FINISHED'}
    
    def duplicatecheck(self, dupliname):
        print("it worked and dupliname is " + dupliname)
        for o in bpy.data.objects:
            if o.name == dupliname:
                o.name = (o.name + "_BexportRename.001")
                print("Renamed Duplicate")
        return {'FINISHED'}
    
    def setcollection(self, targetcol, targetobj):
        for coll in targetobj.users_collection:
            coll.objects.unlink(targetobj)
        targetcol.objects.link(targetobj)
        return {'FINISHED'}
    
    def configurelod(self, currentlod, pixelsize, tmpcol, parentstart):
        scene = bpy.context.scene
        bngexporttools = scene.bngexport_tools
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.duplicate({"object" : currentlod,"selected_objects" : [currentlod]}, linked=False)
        loddup = bpy.context.selected_objects[0]
        
        dupname = (bngexporttools.object_name_prop + str(pixelsize))
        self.duplicatecheck(dupliname=dupname)
        loddup.name = dupname
        self.setcollection(targetcol=tmpcol, targetobj=loddup)
        loddup.parent = parentstart
        loddup.matrix_parent_inverse = parentstart.matrix_world.inverted()
        
        
        return {'FINISHED'}
                      
classes = [BngexportProperties,BNGEXPORT_PT_main_panel,BNGEXPORT_OT_export_op] 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.bngexport_tools = bpy.props.PointerProperty(type= BngexportProperties)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.bngexport_tools
 
 
 
if __name__ == "__main__":
    register()