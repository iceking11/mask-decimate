bl_info = {
    "name": "Mask Decimate",
    "author": "Ian Lloyd Dela Cruz",
    "version": (1, 0),
    "blender": (2, 7, 5),
    "location": "3d View > Tool shelf",
    "description": "Dyntopo Mask Decimation",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mask Tools"}

import bpy
import math
import bmesh
from bpy.props import *

def mask_to_vertex_group(obj, name):
    vgroup = obj.vertex_groups.new(name)
    bpy.ops.object.vertex_group_set_active(group=vgroup.name)
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    deform_layer = bm.verts.layers.deform.active
    if deform_layer is None: deform_layer = bm.verts.layers.deform.new()
    mask = bm.verts.layers.paint_mask.active
    if mask is not None:
        for v in bm.verts:
            if v[mask] == 1:
                v.select = True
                v[deform_layer][vgroup.index] = 1.0
            else:
                v.select = False                   
    else:
        for v in bm.verts:
            v[deform_layer][vgroup.index] = 1.0
  
    bm.to_mesh(obj.data)
    bm.free()
    pass
    return vgroup

class MaskDecimate(bpy.types.Operator):
    '''Decimate Masked Areas'''
    bl_idname = "mask.decimate"
    bl_label = "Decimate masked areas"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def execute(self, context):
        wm = context.window_manager 
        activeObj = context.active_object
        modnam = "Mask Decimate"
        vname = "mask decimation vgroup"
        
        if context.sculpt_object.use_dynamic_topology_sculpting:
            dynatopoEnabled = True
        else:
            dynatopoEnabled = False
        
        #convert mask to vgroup
        mask_to_vertex_group(activeObj, vname)
        
        #place decimate modifier
        md = bpy.context.active_object.modifiers.new(modnam, 'DECIMATE')
        md.vertex_group = vname
        md.ratio = wm.maskdecimate_str

        #apply modifier and remove vgroup
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modnam)
        
        if vname in bpy.context.active_object.vertex_groups:
            bpy.ops.object.vertex_group_set_active(group=vname)            
            bpy.ops.object.vertex_group_remove(all=False)   
        
        bpy.ops.object.mode_set(mode='SCULPT')
        if dynatopoEnabled:
            bpy.ops.sculpt.dynamic_topology_toggle()                
        return {'FINISHED'}         
        
class MaskDecimationPanel(bpy.types.Panel):
    """Mask Decimation Function"""
    bl_label = "Mask Decimate"
    bl_idname = "OBJECT_PT_maskdecimate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Mask Tools'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        row_sw = layout.row(align=True)
        row_sw.alignment = 'EXPAND'
        row_sw.operator("mask.decimate", "Mask Decimate")
        row_sw = layout.row(align=False)
        row_sw.prop(wm, "maskdecimate_str", "Decimation Strength")
       
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.WindowManager.maskdecimate_str = FloatProperty(min = 0, max = 1, step = 0.1, precision = 3, default = 1)
  
def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()















