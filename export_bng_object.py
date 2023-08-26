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
import time
#import bmesh

class BNGEXPORT_OT_export_op(bpy.types.Operator):
    """ Exports the object with the correct naming conventions and hierarchy
    """
    bl_label = "Export Objects"
    bl_idname = "bngexport.export_operator"
    bl_options = {'UNDO'}

    def execute(self, context):   
        starttime = time.time()
        scene = context.scene
        bngexporttools = scene.bngexport_tools    



        originlocation = None
        for lod in scene.lod_list:
            LODType = lod.lod_type_enum
            if LODType == "CENTER":
                if lod.lod_object:
                    originlocation = lod.lod_object.location
          
        bpy.ops.collection.create(name="TmpExportCollection")
        exportcol = bpy.data.collections["TmpExportCollection"]
        bpy.context.collection.children.link(exportcol)

        self.duplicatecheck(dupliname="base00")       
        base = bpy.data.objects.new("base00", None)
        bpy.context.scene.collection.objects.link(base)
        self.setcollection(targetcol=exportcol, targetobj=base)

        self.duplicatecheck(dupliname="start01") 
        start = bpy.data.objects.new("start01", None)
        bpy.context.scene.collection.objects.link(start)
        self.setcollection(targetcol=exportcol, targetobj=start)
        
        start.parent = base
        start.matrix_parent_inverse = base.matrix_world.inverted()
        
        for lod in scene.lod_list:

            LODObject = lod.lod_object
            LODCollection = lod.lod_collection
            LODObjectType = lod.lod_object_type_enum
            LODType = lod.lod_type_enum
            LODPixelSize = lod.lod_pixel_size
            lodapplymodifiers = lod.lod_modifiers_bool

            lodinfodict = {
                "LodType" : lod.lod_type_enum,
                "LodObject" : lod.lod_object,
                "LodCol" : exportcol,
                "ApplyMods" : lod.lod_modifiers_bool,
                "Psize" : lod.lod_pixel_size,
                "ParentObj" : start,
                "LodName" : None
            }

            if LODType == "SHAPE":
                if LODObjectType == "OBJECT":
                    self.bngexport_configurelod(lodinfodict)
                    
                if LODObjectType == "COLLECTION":
                    merged_obj=self.mergecollection(collection=LODCollection)
                    lodinfodict["LodObject"] = merged_obj
                    lodinfodict["LodType"] = "SHAPE"
                    self.bngexport_configurelod(lodinfodict)

            if LODType == "COLLISION":
                if LODObjectType == "OBJECT":
                    self.bngexport_configurelod(lodinfodict)
                if LODObjectType == "COLLECTION":
                    object=self.mergecollection(collection=LODCollection)
                    lodinfodict["LodObject"] = object
                    lodinfodict["LodType"] = "SHAPE"
                    self.bngexport_configurelod(lodinfodict)

            if LODType == "BILLBOARD":
                if LODObjectType == "OBJECT":
                    self.bngexport_configurelod(lodinfodict)

                if LODObjectType == "COLLECTION":
                    object=self.mergecollection(collection=LODCollection)
                    lodinfodict["LodObject"] = object
                    lodinfodict["LodType"] = "SHAPE"
                    self.bngexport_configurelod(lodinfodict)
                    
            if LODType == "AUTOBILLBOARD":
                name = "bb_autobillboard"+str(LODPixelSize)
                lodinfodict["LodType"] = "EMPTY"
                lodinfodict["LodName"] = name
                lodinfodict["ParentObj"] = base

                self.bngexport_configurelod(lodinfodict)

            if LODType == "NULLDETAIL":
                name = "nulldetail"+str(LODPixelSize)
                lodinfodict["LodType"] = "EMPTY"
                lodinfodict["LodName"] = name
                lodinfodict["ParentObj"] = base

                self.bngexport_configurelod(lodinfodict)
            
        #Export
        bpy.ops.ed.undo_push()   
        bpy.ops.object.select_all(action='DESELECT')
        base.select_set(True)
        bpy.context.view_layer.objects.active = base
        
        exportpathabs = bpy.path.abspath(bngexporttools.export_file_path)
        exportpathfull = exportpathabs + bngexporttools.object_name_prop    

        bpy.ops.wm.collada_export(
        filepath=exportpathfull, 
        check_existing=False, 
        filter_blender=False, 
        apply_modifiers=False,
        selected=True, 
        include_children=True, 
        triangulate=True
        )

        bpy.ops.ed.undo()
        endtime = time.time()
        
        self.report({'INFO'}, "BeamNG Object exported in " + str(round(endtime-starttime, 2)) + " seconds")
        return {'FINISHED'} 
    
    def duplicatecheck(self, dupliname):
        for o in bpy.data.objects:
            if o.name == dupliname:
                o.name = (o.name + "_BexportRename.001")
        return
    
    def setcollection(self, targetcol, targetobj):
        for coll in targetobj.users_collection:
            coll.objects.unlink(targetobj)
        targetcol.objects.link(targetobj)
        return
    
    def bngexport_configurelod(self, lodinfo):
        if lodinfo["LodType"] == None:
            print("Lod Type has not been set")
            return
        
        scene = bpy.context.scene
        bngexporttools = scene.bngexport_tools

        match lodinfo["LodType"]:

            #Object LOD Configuration

            case "SHAPE":
                if lodinfo["LodObject"] == None or lodinfo["LodCol"] == None or lodinfo["ApplyMods"] == None or lodinfo["Psize"] == None or lodinfo["ParentObj"] == None:
                    print("SHAPE LOD has been configured incorrectly")
                    return

                loddup=self.bngexport_duplicate(lodinfo["LodObject"], lodinfo["LodCol"])

                if lodinfo["ApplyMods"] == True:
                    self.lodapplymodifiers(object=loddup)
                
                dupname = (bngexporttools.object_name_prop + "_d" +str(lodinfo["Psize"]))
                self.duplicatecheck(dupliname=dupname)
                loddup.name = dupname

                self.bngexport_setparent(childobj=loddup, parentobj=lodinfo["ParentObj"])
                return

            #Collision LOD Configuration

            case "COLLISION":
                if lodinfo["LodObject"] == None or lodinfo["LodCol"] == None or lodinfo["ApplyMods"] == None or lodinfo["ParentObj"] == None:
                    print("COLLISION LOD has been configured incorrectly")
                    return

                colmesh = lodinfo["LodObject"]
                loddup=self.bngexport_duplicate(colmesh, lodinfo["LodCol"])

                if lodinfo["ApplyMods"] == True:
                    self.lodapplymodifiers(object=loddup)

                dupname = ("Colmesh-1")
                self.duplicatecheck(dupliname=dupname)
                loddup.name = dupname

                self.bngexport_setparent(childobj=loddup, parentobj=lodinfo["ParentObj"])
                return

            #Empty LOD Configuration

            case "EMPTY":
                if lodinfo["LodName"] == None or lodinfo["LodCol"] == None or lodinfo["ParentObj"] == None:
                    print("EMPTY LOD has been configured incorrectly")
                    return

                self.duplicatecheck(dupliname=lodinfo["LodName"]) 
                empty = bpy.data.objects.new(lodinfo["LodName"], None)
                bpy.context.scene.collection.objects.link(empty)
                self.setcollection(targetcol=lodinfo["LodCol"], targetobj=empty)
                self.bngexport_setparent(childobj=empty, parentobj=lodinfo["ParentObj"])
                return

            #Billboard LOD Configuration

            case "BILLBOARD":
                if lodinfo["Psize"] == None or lodinfo["LodCol"] == None or lodinfo["ParentObj"] == None or lodinfo["LodObject"] == None or lodinfo["ApplyMods"] == None:
                    print("BILLBOARD LOD has been configured incorrectly")
                    return

                loddup=self.bngexport_duplicate(lodinfo["LodObject"], lodinfo["LodCol"])

                if lodinfo["ApplyMods"] == True:
                    self.lodapplymodifiers(object=loddup)

                dupname = ("bb_"+bngexporttools.object_name_prop +"_d"+ str(lodinfo["Psize"]))
                self.duplicatecheck(dupliname=dupname)
                loddup.name = dupname
                self.bngexport_setparent(childobj=loddup, parentobj=lodinfo["ParentObj"])
                return

            #LOD type invalid

            case _:
                print("Invalid LOD Type")
                return

    def lodapplymodifiers(self, object):
        if object.type == 'MESH':
            if object.modifiers:
                for targetmodifier in object.modifiers:
                    bpy.ops.object.modifier_apply({"object" : object,"selected_objects" : [object]}, modifier=targetmodifier.name)
            
        
    def mergecollection(self, collection):
        scene = bpy.context.scene
        merge_list = []
        
        bpy.ops.collection.create(name="TmpDupliMergeCollection")
        duplimergecol = bpy.data.collections["TmpDupliMergeCollection"]
        bpy.context.collection.children.link(duplimergecol)

        objgroups = []
        objmaterials = []

        for i in collection.objects:

            if i.type == 'MESH':

                if i.vertex_groups:
                    for vg in i.vertex_groups:
                        objgroups.append(vg)

                if i.data.materials:
                    for m in i.data.materials:
                        objmaterials.append(m)

                dup=self.bngexport_duplicate(obj=i, col=duplimergecol)
                self.lodapplymodifiers(object=dup)
                
                mb = dup.matrix_basis
                if hasattr(dup.data, "transform"):
                    dup.data.transform(mb)
                for c in dup.children:
                    c.matrix_local = mb @ c.matrix_local
                dup.matrix_basis.identity()
                
                merge_list.append(dup)

        self.bngexport_join(activeobj=merge_list[0], selectedobjs=merge_list)

        for vg in objgroups:
            if vg.name not in merge_list[0].vertex_groups:
                merge_list[0].vertex_groups.new(name=vg.name)

        for m in objmaterials:
            if m.name not in merge_list[0].data.materials:
                merge_list[0].data.materials.append(bpy.data.materials[m.name])

        self.setcollection(targetcol=bpy.data.collections['TmpExportCollection'], targetobj=merge_list[0])
        return merge_list[0]        

    def bngexport_duplicate(self, obj, col):
        objcopy = obj.copy()
        if objcopy.data:
            objcopy.data = objcopy.data.copy()
        col.objects.link(objcopy)
        return objcopy

    def bngexport_setparent(self, childobj, parentobj):
        childobj.parent = parentobj
        childobj.matrix_parent_inverse = parentobj.matrix_world.inverted()

    def bngexport_join(self, activeobj, selectedobjs):
        with bpy.context.temp_override(active_object=activeobj, selected_editable_objects=selectedobjs):
            bpy.ops.object.join()
