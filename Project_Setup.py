from fileinput import filename
import shutil
import stat
import bpy
import os
import subprocess as sp

from .Properties import FILE_UI_TRACK, FILE_SURFACES, FILE_EXT_CFG, AC_FOLDER_NAME
from .Functions import TrackFolder, get_template, open_file_in_scripting, read_config, read_json, write_config, write_json, get_properties

# TODO adjust KsEditor.ini so its day always
# TODO init blender file (insert track template w/ path + curb w/ path)

class PROJECT_OT_init(bpy.types.Operator):
    bl_idname = "project.init"
    bl_label = "Init Project"
    bl_description = "Create default project folders and files"
    
    # Definiere Properties (Eingabefelder)
    track_name: bpy.props.StringProperty(name="Track Name", default=AC_FOLDER_NAME) # type: ignore

    def execute(self, context):
        props = get_properties(context)

        track_folder = os.path.join(os.path.dirname(bpy.data.filepath), self.track_name)
        tf = TrackFolder(track_folder) # normalerweise mit props.track_folder setzen, gibts hier aber noch nicht
        tf.set_path(track_folder, props)

        if not tf.exists():
            os.mkdir(tf._path)

        make_ui_folder(tf._path)
        make_ai_folder(tf._path)
        make_data_folder(tf._path)
        make_extension_folder(tf._path)

        self.report({'INFO'}, f"Sub-Folder {tf._path} created")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Öffnet eine Popup-Form
        return context.window_manager.invoke_props_dialog(self)



class PROJECT_OT_open_track_folder(bpy.types.Operator):
    bl_idname = "project.open_track_folder"
    bl_label = "Open Track Folder"
    bl_description = "Open Folder of AC Track"
    
    def execute(self, context):
        props = get_properties(context)
        tf = TrackFolder(props.track_folder)
        abs_track_folder = tf._path
        
        if not os.path.exists(abs_track_folder):
            self.report({'INFO'}, f"Something went wrong! Cannot locate '{abs_track_folder}'")
            return {'FINISHED'}

        os.startfile(abs_track_folder)

        return {'FINISHED'}


class PROJECT_OT_edit_track_ui(bpy.types.Operator):
    bl_idname = "project.edit_track_ui"
    bl_label = "Edit Track UI"
    bl_description = "Edit Track Properties/Info"
    
    def execute(self, context):
        path = TrackFolder(get_properties(context).track_folder).get_ac_file_path(FILE_UI_TRACK)
        if not path or not os.path.exists(path):
            self.report({'INFO'}, f"Cannot locate '{FILE_UI_TRACK}'")
            return {'FINISHED'}

        open_file_in_scripting(self, context, path)

        return {'FINISHED'}


# Definiere den Popup-Operator
class PROJECT_OT_create_file(bpy.types.Operator):
    bl_idname = "project.create_file"
    bl_label = "Create File"

    filename: bpy.props.StringProperty() # type: ignore
    path: bpy.props.StringProperty(default="//" + AC_FOLDER_NAME, description='In which subfolder the file is going to be created.', subtype='FILE_PATH') # type: ignore
    
    def __init__(self):
        props = get_properties(bpy.context)
        if props.track_folder:
            self.path = TrackFolder(props.track_folder)._path
        self.path = os.path.join(self.path, self.filename) # combine path and given filename

    # Invoke wird überschrieben, um ein Popup zu erzeugen
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # Dialog-Inhalt
    def draw(self, context):
        layout = self.layout

        layout.label(text=f"Create {self.filename}?")
        layout.prop(self.properties, "path", text="Path")

    def execute(self, context):
        file = self.path
        if os.path.exists(os.path.dirname(file)):
            open(file, 'x') # create file
            self.report({'INFO'}, f"File {file} Created!")
        else:
            self.report({'INFO'}, f"Cannot create file {file}")
        return {'FINISHED'}


from pathlib import Path
class PROJECT_OT_rename_track(bpy.types.Operator):
    bl_idname = "project.rename_track"
    bl_label = "Rename track"
    bl_description = "Rename track file and folder"
    
    new_name: bpy.props.StringProperty(name="new_name", default="") # type: ignore

    def execute(self, context):
        props = get_properties(context)
        tf = TrackFolder(props.track_folder)
        old_name = tf._track_name

        rc = tf.rename(new_name=self.properties.new_name)
        if rc == 0:
            self.report({'INFO'}, f"Successfully renamed {old_name} to {tf._track_name}")
        elif rc == 1:
            self.report({'INFO'}, "Error! Cannot rename track folder.")
        elif rc == 2:
            self.report({'INFO'}, "Error! Cannot rename track folder in ac-installation.")

        return {'FINISHED'}
    
    # Invoke wird überschrieben, um ein Popup zu erzeugen
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    # Dialog-Inhalt
    def draw(self, context):
        layout = self.layout
        tf = TrackFolder(get_properties(context).track_folder)

        layout.label(text=f"Rename {tf._track_name}")
        layout.prop(self.properties, "new_name", text="New Name")



def make_ui_folder(path):
    ui_folder = os.path.join(path, 'ui')
    if not os.path.exists(ui_folder):
        os.mkdir(ui_folder)
    
    ui_track_file = os.path.join(ui_folder, FILE_UI_TRACK)
    print(get_template(FILE_UI_TRACK))# DEBUG
    data = read_json(get_template(FILE_UI_TRACK))
    write_json(data, ui_track_file)


def make_ai_folder(path):
    ai_folder = os.path.join(path, 'ai')
    if not os.path.exists(ai_folder):
        os.mkdir(ai_folder)


def make_data_folder(path):
    data_folder = os.path.join(path, 'data')
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)

    # write config file
    surfaces_file = os.path.join(data_folder, FILE_SURFACES)
    cfg = read_config(get_template(FILE_SURFACES))
    write_config(cfg, surfaces_file)

def make_extension_folder(path):
    extension_folder = os.path.join(path, 'extension')
    if not os.path.exists(extension_folder):
        os.mkdir(extension_folder)

    # write config file
    ext_cfg_file = os.path.join(extension_folder, FILE_EXT_CFG)
    cfg = read_config(get_template(FILE_EXT_CFG))
    write_config(cfg, ext_cfg_file)
    