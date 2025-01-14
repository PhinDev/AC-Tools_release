import bpy
import os

from .Functions import TrackFolder, get_blender_path, get_properties
from . Tools_Materials import default_mat_operators, custom_mat_operators, collision_mat_operators


class UI_Tools(bpy.types.Panel):
    """Creates a Panel in the scene context of sidebar"""
    bl_label = "Tools"
    bl_idname = "SCENE_PT_ac_tools_tools"
    bl_space_type = 'VIEW_3D'  # Correct space type for the 3D View
    bl_region_type = 'UI'  # 'UI' is the region type for the Sidebar
    bl_context = "objectmode"  # You can change this depending on the context where you want the panel to appear
    bl_category = "AC Tools"

    def draw(self, context):
        layout = self.layout


class UI_Objects(bpy.types.Panel):
    """Creates a Panel in the scene context of sidebar"""
    bl_label = "AC Objects"
    bl_idname = "SCENE_PT_ac_tools_objects"
    bl_space_type = 'VIEW_3D'  # Correct space type for the 3D View
    bl_region_type = 'UI'  # 'UI' is the region type for the Sidebar
    bl_context = "objectmode"  # You can change this depending on the context where you want the panel to appear
    bl_category = "AC Tools"
    bl_parent_id = "SCENE_PT_ac_tools_tools"

    def draw(self, context):
        layout = self.layout

        props = get_properties(context)

        layout.prop(props, "grid_align", text="Align")
        layout.prop(props, "grid_offset", text="Offset")
        #layout.prop(props, "track_align", text="Align Track") # make function for align first...
        box = layout.box()
        box.operator("object.create_start", icon='RESTRICT_SELECT_OFF')
        box.operator("object.create_hotlap_start", icon='RESTRICT_SELECT_OFF')
        box.operator("object.create_pit", icon='PMARKER_ACT')
        box.operator("object.create_timing", icon='TIME')


class UI_Materials(bpy.types.Panel):
    """Creates a Panel in the scene context of sidebar"""
    bl_label = "AC Materials"
    bl_idname = "SCENE_PT_ac_tools_materials"
    bl_space_type = 'VIEW_3D'  # Correct space type for the 3D View
    bl_region_type = 'UI'  # 'UI' is the region type for the Sidebar
    bl_context = "objectmode"  # You can change this depending on the context where you want the panel to appear
    bl_category = "AC Tools"
    bl_parent_id = "SCENE_PT_ac_tools_tools"

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        col = box.column()
        col.operator("object.remove_material", icon='TRASH')
        col.separator()

        col.label(text='Default:')
        for op in default_mat_operators:
            col.operator(op.bl_idname, icon='VIEW_PERSPECTIVE')
        if custom_mat_operators:
            col.label(text='Custom:')
        for op in custom_mat_operators:
            col.operator(op.bl_idname, icon='VIEW_PERSPECTIVE')

        if collision_mat_operators:
            col.label(text='Collision:')
        for op in collision_mat_operators:
            col.operator(op.bl_idname, icon='MESH_CUBE')

        box.separator(type='SPACE')
        box.operator("ac_tools.add_material", icon='ADD', text='Add new material')
        box.operator("ac_tools.load_materials", icon='FILE_REFRESH', text='Reload materials')

        row = layout.row()
        row.label(text="""\nTo modify or create materials check your './ac_track/data/surfaces.ini' and adjust it.\
                  \nThe names of the materials have to math the object prefixes! \
                  """, icon='INFO')
    

class UI_ProjectSetup(bpy.types.Panel):
    """Creates a Panel in the scene context of sidebar"""
    bl_label = "Project Setup"
    bl_idname = "SCENE_PT_acetrack_project_setup"
    bl_space_type = 'VIEW_3D'  # Correct space type for the 3D View
    bl_region_type = 'UI'  # 'UI' is the region type for the Sidebar
    bl_context = "objectmode"  # You can change this depending on the context where you want the panel to appear
    bl_category = "AC Tools"

    def draw(self, context):
        props = get_properties(context)
        layout = self.layout

        scene = context.scene

        if not bpy.data.filepath:
            layout.label(text='Save .blend first')
            return

        # TRACK FOLDER
        tf = TrackFolder(props.track_folder)
        if not tf.exists():
            box = layout.box()
            box.operator("project.init", text="Create Default Track Folder")
            layout.label(text="...or choose folder...")
            layout.prop(props, "track_folder", text="")
        else:
            box = layout.box()
            box.operator("project.edit_track_ui", icon='CURRENT_FILE')
            box.operator("project.edit_surface_ini", icon='CURRENT_FILE')
            box.label(text="Track Folder:")
            box.prop(props, "track_folder", text="")
            box.operator("project.open_track_folder", icon='FILEBROWSER')
            box.operator("project.rename_track", text="Rename Track", icon='GREASEPENCIL')
            #box.operator("project.edit_surface_ini")


class UI_ProjectExport(bpy.types.Panel):
    """Creates a Panel in the scene context of sidebar"""
    bl_label = "Project Export"
    bl_idname = "SCENE_PT_acetrack_project_export"
    bl_space_type = 'VIEW_3D'  # Correct space type for the 3D View
    bl_region_type = 'UI'  # 'UI' is the region type for the Sidebar
    bl_context = "objectmode"  # You can change this depending on the context where you want the panel to appear
    bl_category = "AC Tools"

    def draw(self, context):
        props = get_properties(context)
        layout = self.layout

        if not bpy.data.filepath:
            layout.label(text='Save .blend first')
            return

        # EXPORT FBX
        box = layout.box()
        box.label(text="Scene to FBX")
        box.prop(props, "disable_export_checks", text="Disable Export Checks")
        box.operator("project.export_fbx_for_ac", text="Export FBX for KsEditor", icon='EXPORT')
