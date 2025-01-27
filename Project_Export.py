import bpy
import os
import subprocess as sp

from .Functions import TrackFolder, get_properties, read_json


from pathlib import Path
class PROJECT_OT_export_fbx_for_ac(bpy.types.Operator):
    bl_idname = "project.export_fbx_for_ac"
    bl_label = "Export FBX for AC"
    bl_description = """Export scene to FBX with Assetto-Corsa-Standards. You still can export manually if problems occur.
Parameters:
            filepath=fbx_path, 
            check_existing=False, 
            global_scale=0.01,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            object_types={'EMPTY', 'MESH', 'OTHER'},
            axis_forward='-Z', 
            axis_up='Y',
            use_tspace=True,
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            use_triangles=True,
            mesh_smooth_type='OFF',
            colors_type='SRGB'
            """

    def execute(self, context):
        props = get_properties(context)
        name = Path(bpy.data.filepath).stem
        if props.exp_use_sel:
            if len(context.selected_objects) == 0:
                self.report({'INFO'}, "No object selected!")
                return {'FINISHED'}
            if len(context.selected_objects) > 1:
                name = name + '_objects'
            else:
                name = context.active_object.name

        fbx_path = os.path.join(os.path.dirname(bpy.data.filepath), name + ".fbx")

        if not props.disable_export_checks and not ready_for_export(self, context):
            return {'FINISHED'}

        # EXPORT SCENE as FBX
        bpy.ops.export_scene.fbx(
            filepath=fbx_path, 
            check_existing=False, 
            global_scale=0.01, # if problems -> set to 1
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            object_types={'EMPTY', 'MESH', 'OTHER'},
            axis_forward='-Z', 
            axis_up='Y',
            use_tspace=True,
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            use_triangles=True,
            mesh_smooth_type='OFF',
            colors_type='SRGB',
            use_selection=props.exp_use_sel
            )
        
        self.report({'INFO'}, f"Exported to {fbx_path}")
        return {'FINISHED'}


# Additional/Functional Export Checks (can be disabled through property 'disable_export_checks')
from .Properties import AC_OBJ_PREFIX, AC_COLLECTION_NAME, FILE_UI_TRACK
def ready_for_export(self, context: bpy.types.Context):
    if not ac_objects_valid(self, context):
        return False
    
    return True


# sub method of ready_for_export
def ac_objects_valid(self, context):
    if AC_COLLECTION_NAME not in context.view_layer.layer_collection.children:
        self.report({'INFO'}, f"Collection '{AC_COLLECTION_NAME}' doesn't exist. Please add AC-Objects before export!")
        return False
    
    objects = context.view_layer.layer_collection.children[AC_COLLECTION_NAME].collection.objects
    
    # check if AC objects exist and match track_ui pits etc
    for prefix in AC_OBJ_PREFIX.values():
        # check if existing at all
        if not any(obj.name.startswith(prefix) for obj in objects):
            self.report({'INFO'}, f"AC-Object missing! '{prefix}_<n>'")
            return False
        
        # check timing
        if prefix == AC_OBJ_PREFIX['TIME']:
            count = sum(1 for obj in objects if obj.name.startswith(prefix))
            if count % 2 > 0:
                self.report({'INFO'}, f"One timing object is missing!")
                return False
            continue

        # check pits
        if prefix == AC_OBJ_PREFIX['PIT']:
            try:
                props = get_properties(context)
                data = read_json(TrackFolder(props.track_folder).get_ac_file_path(FILE_UI_TRACK))
                required_pit_count = int(data['pitboxes'])
            except:
                self.report({'INFO'}, f"Could not extract pit count from {FILE_UI_TRACK}. Please check manually!")
                return False
            
            scene_pit_count = sum(1 for obj in objects if obj.name.startswith(prefix))
            if scene_pit_count != required_pit_count:
                self.report({'INFO'}, f"Required pit count: '{required_pit_count}' - pits in scene: '{scene_pit_count}'. Setup pits or adjust pit setting in track ui file!")
                return False
            continue
        
    return True
