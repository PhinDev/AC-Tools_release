import copy
import bpy
import os

from .Properties import FILE_SURFACES
from .Functions import TrackFolder, get_properties, read_config, write_config

DEFAULT_MATERIALS = {
    "road": {"prefix": "1ROAD", "type": "default"},
    "curb": {"prefix": "1KERB", "type": "default"},
    "grass": {"prefix": "1GRASS", "type": "default"},
    "sand": {"prefix": "1SAND", "type": "default"},
    "wall": {"prefix": "1WALL", "type": "collision"}
}

from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty
class AddMaterial(bpy.types.Operator):
    bl_idname = "ac_tools.add_material"
    bl_label = "Add Material"
    bl_description = "Add material to surface.ini"
    bl_options = {'REGISTER', 'UNDO'}

    # TODO Werte analysieren
    # cd 'E:\\SteamLibrary\steamapps\common\assettocorsa'
    # grep -i ff_effect ./*/data/surfaces.ini | cut -d'=' -f2 | sort -u

    key: StringProperty(
        name="Key",
        description="Unique identifier for the surface",
        default="ASPHALT"
    ) # type: ignore
    friction: FloatProperty(
        name="Friction",
        description="Coefficient of friction",
        default=0.98,
        min=0.0,
        max=1.0
    ) # type: ignore
    damping: FloatProperty(
        name="Damping",
        description="Damping factor",
        default=0.01,
        min=0.0,
        max=1.0
    ) # type: ignore
    wav: StringProperty(
        name="WAV",
        description="Sound file associated with the surface",
        subtype='DIR_PATH',
        default=""
    ) # type: ignore
    wav_pitch: FloatProperty(
        name="WAV Pitch",
        description="Pitch adjustment for the sound file",
        default=0.0
    ) # type: ignore
    ff_effect: StringProperty(
        name="Force Feedback Effect",
        description="Force feedback effect (NULL, 0 or 1)",
        default="NULL" # TODO entweder NULL, 0 oder 1 (gibt ggf. welche dazwischen)
    ) # type: ignore
    dirt_additive: FloatProperty(
        name="Dirt Additive",
        description="Amount of dirt additive",
        default=0.0,
        min=0.0,
        max=1.0
    ) # type: ignore
    black_flag_time: IntProperty(
        name="Black Flag Time",
        description="Time in seconds for black flag",
        default=0
    ) # type: ignore
    is_valid_track: BoolProperty(
        name="Is Valid Track",
        description="Indicates if the track is valid",
        default=True
    ) # type: ignore
    sin_height: FloatProperty(
        name="Sin Height",
        description="Simulates a bumpy road. This defines the height of the bumps.",
        default=0.0
    ) # type: ignore
    sin_length: FloatProperty(
        name="Sin Length",
        description="Simulates a bumpy road. This defines the length of the bumps.",
        default=0.0,
        min=0.0,
        max=1.0
    ) # type: ignore
    is_pitlane: BoolProperty(
        name="Is Pitlane",
        description="Indicates if it's a pitlane",
        default=False
    ) # type: ignore
    vibration_gain: FloatProperty(
        name="Vibration Gain",
        description="Gain for vibration effect",
        default=0.0,
        min=0.0,
        max=1.0
    ) # type: ignore
    vibration_length: FloatProperty(
        name="Vibration Length",
        description="Length of vibration effect",
        default=0.0
    ) # type: ignore


    def execute(self, context):
        props = get_properties(context)
        
        # VALIDATION
        if not self.key or self.key == "":
            self.report({'INFO'}, f"Error! Key must not be empty.")
            return {'FINISHED'}
        if self.wav and not self.wav.lower().endswith('.wav'):
            self.report({'INFO'}, f"Error! WAV file invalid.")
            return {'FINISHED'}
        
        # TODO choose sounds from enum
        # E:\SteamLibrary\steamapps\common\assettocorsa\sdk\audio\ac_fmod_sdk_1_9\Assets\surfaces\ ?

        
        tf = TrackFolder(props.track_folder)

        surfaces_file = tf.get_ac_file_path(FILE_SURFACES)
        if not surfaces_file:
            self.report({'INFO'}, f"Error. Cannot locate surface.ini.") # TODO auto create file
            return {'FINISHED'}
        
        self.key = self.key.upper()
        max_nr = 0
        cfg = read_config(surfaces_file)
        for surface_slot in cfg.sections():
            key = cfg[surface_slot].get('key')
            if key == self.key:
                self.report({'INFO'}, f"Error. Material {key} vs {self.key} already exists.")
                return {'FINISHED'}

            # find max nr and new slotname
            try:
                nr = int(surface_slot.split('_')[1])
                if nr >= max_nr:
                    max_nr = nr + 1
            except:
                continue

        slot = f"SURFACE_{max_nr}" # this will be the "name" of the new material slot [SURFACE_<n>] -> cfg[slot] = ...
        cfg[slot] = {
            "key": self.key,
            "friction": round(self.friction, 2),          # Rundung auf 2 Dezimalstellen
            "damping": round(self.damping, 2),
            "wav": self.wav,
            "wav_pitch": round(self.wav_pitch, 2),
            "ff_effect": self.ff_effect,
            "dirt_additive": round(self.dirt_additive, 2),
            "black_flag_time": self.black_flag_time,
            "is_valid_track": int(self.is_valid_track),  # Bool zu Int
            "sin_height": round(self.sin_height, 2),
            "sin_length": round(self.sin_length, 2),
            "is_pitlane": int(self.is_pitlane),         # Bool zu Int
            "vibration_gain": round(self.vibration_gain, 2),
            "vibration_length": round(self.vibration_length, 2),
        }

        write_config(cfg, surfaces_file)

        load_materials(context)

        self.report({'INFO'}, f"Successfully added material {slot}: '{self.key}'")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Öffnet eine Popup-Form
        return context.window_manager.invoke_props_dialog(self)
    
    # Dialog-Inhalt
    def draw(self, context):
        layout = self.layout
    # Section: General Surface Properties
        layout.label(text="General Surface Properties")
        layout.prop(self, "key")
        layout.prop(self, "friction")
        layout.prop(self, "damping")

        # Section: Sound Properties
        layout.label(text="Sound Properties")
        layout.prop(self, "wav")
        layout.prop(self, "wav_pitch")

        # Section: Force Feedback Properties
        layout.label(text="Force Feedback Properties")
        layout.prop(self, "ff_effect")

        # Section: Additional Properties
        layout.label(text="Additional Properties")
        layout.prop(self, "dirt_additive")
        layout.prop(self, "black_flag_time")
        layout.prop(self, "is_valid_track")
        layout.prop(self, "sin_height")
        layout.prop(self, "sin_length")
        layout.prop(self, "is_pitlane")
        layout.prop(self, "vibration_gain")
        layout.prop(self, "vibration_length")


# OPERATOR #

class RemoveMaterial(bpy.types.Operator):
    bl_idname = "object.remove_material"
    bl_label = "Remove Material"
    bl_description = "Removing AC-Material prefix from object name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        objects = context.selected_objects
        return objects is not None and len(objects) > 0

    def execute(self, context):
        remove_prefix(self, context.selected_objects)

        return {'FINISHED'}

# DYNAMIC MATERIAL SYSTEM:

class LoadMaterials(bpy.types.Operator):
    bl_idname = "ac_tools.load_materials"
    bl_label = "Load Materials"
    bl_description = "Loads custom materials from surface.ini"

    def execute(self, context):
        nr = load_materials(context)
        self.report({'INFO'}, f"Successfully loaded {nr} materials.")
        return {'FINISHED'}
    

class MaterialData:
    TYPE_DEFAULT = 'default'
    TYPE_CUSTOM = 'custom'
    TYPE_COLLISION = 'collision'

    def __init__(self):
        self.data = copy.deepcopy(DEFAULT_MATERIALS)
        self.prefix_to_key = {item['prefix']: key for key, item in self.data.items()}

    def add_material(self, key, prefix, material_type, physics: bool = True):
        self.data[key] = {'prefix': f"{int(physics)}{prefix}", 'type': material_type}
        self.prefix_to_key[prefix] = key

    def get(self, key):
        return self.data[key] if key in self.data else None

    def get_by_prefix(self, prefix):
        key = self.prefix_to_key.get(prefix)
        return self.data[key] if key else None

    def get_prefix(self, key):
        return self.data[key]['prefix']
    
    def get_all_of_type(self, type):
        return {key: item for key, item in self.data.items() if item['type'] == type}

    def get_all_prefixes(self):
        return {item['prefix'] for item in self.data.values()}



# custom material operators
materials = MaterialData()
default_mat_operators = []
custom_mat_operators = []
collision_mat_operators = []

def load_materials(context):
    # unregister old
    for op in default_mat_operators + custom_mat_operators + collision_mat_operators:
        bpy.utils.unregister_class(op)
        print(f"Removed {op}")

    # init
    default_mat_operators.clear()
    custom_mat_operators.clear()
    collision_mat_operators.clear()

    global materials
    materials.__init__()

    # add custom surfaces to materials
    custom_surfaces = get_surface_names(TrackFolder(get_properties(context).track_folder))
    for surf in custom_surfaces:
        if not materials.get(surf.lower()):
            materials.add_material(surf.lower(), surf.upper(), MaterialData.TYPE_CUSTOM)

    #for key in materials.data.keys():
    #    print(f"{key}: {materials.data[key]}")

    # create operators
    for mat, data in materials.data.items():
        op = create_material_operator(mat)
        mat_type = data['type']
        
        if mat_type == MaterialData.TYPE_DEFAULT:
            default_mat_operators.append(op)
        elif mat_type == MaterialData.TYPE_CUSTOM:
            custom_mat_operators.append(op)
        elif mat_type == MaterialData.TYPE_COLLISION:
            collision_mat_operators.append(op)

        bpy.utils.register_class(op)
        print(f"Load {mat}")

    return len(materials.data)


def get_surface_names(tf: TrackFolder):
    surface_names = []
    surfaces_file = tf.get_ac_file_path(FILE_SURFACES)
    if surfaces_file:
        cfg = read_config(surfaces_file)
        for surface_slot in cfg.sections():
            surf_name = cfg[surface_slot].get('key')
            surface_names.append(surf_name)
            print(f"Custom: {surface_slot} '{surf_name}'")

    return surface_names


# Dynamische Operator-Erstellung
def create_material_operator(material_name):
    class CustomMaterialOperator(bpy.types.Operator):
        bl_idname = f"object.make_{material_name.lower()}"
        bl_label = f"Make {material_name.capitalize()}"
        bl_description = f"Renaming object so {material_name} material will be applied"
        bl_options = {'REGISTER', 'UNDO'}
        
        @classmethod
        def poll(cls, context):
            objects = context.selected_objects
            return objects is not None and len(objects) > 0

        def __str__(self):
            return material_name.upper()

        def execute(self, context):
            rename_objects(self, context.selected_objects, material_name.lower())
            return {'FINISHED'}
    
    return CustomMaterialOperator


# FUNCTIONS

def rename_objects(self, objects: bpy.types.Object, material_name: str):
    if not materials.get(material_name):
        self.report({'ERROR'}, f"Invalid prefix {material_name}. Aborting rename.")
        return False
    
    prefix = materials.get_prefix(material_name)

    for obj in objects:
        if obj.name.startswith(tuple(materials.get_all_prefixes())):
            self.report({'ERROR'}, f"Object already is an AC material! Reset before reassigning.")
            continue
        obj.name = prefix + '.' + obj.name

    return True


def remove_prefix(self, objects):
    for obj in objects:
        for prefix in materials.get_all_prefixes():
            # replace AC-Prefix
            if obj.name.startswith(prefix):
                obj.name = obj.name.replace(prefix, '')
                # replace delimiter
                if obj.name.startswith(('.', '_', '-')):
                    obj.name = obj.name[1:]

                self.report({'INFO'}, f"Removed AC-Material from object {obj.name}")
                return True
            
    return False
