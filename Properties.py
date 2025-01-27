import bpy

# CONSTANTS
ALIGN_RIGHT = 'RIGHT'
ALIGN_LEFT = 'LEFT'

AC_COLLECTION_NAME = "AC_OBJECTS"
AC_OBJ_PREFIX = {
    "START":  "AC_START",
    "HOTLAP": "AC_HOTLAP_START",
    "PIT":    "AC_PIT",
    "TIME":   "AC_TIME"
}

AC_FOLDER_NAME = "ac_track"

FILE_UI_TRACK = 'ui_track.json'
FILE_EXT_CFG = 'ext_config.ini'
FILE_SURFACES = 'surfaces.ini'

# BLENDER PROPERTIES

class MyProperties(bpy.types.PropertyGroup):

    track_folder: bpy.props.StringProperty(
        name="track_folder",
        description="Location of the project track folder",
        default="//" + AC_FOLDER_NAME,
        subtype='DIR_PATH'
    ) # type: ignore

    grid_align: bpy.props.EnumProperty(
        name = "grid_align",
        description="Alignment direction of grid (towards first position)",
        items=[
            (ALIGN_LEFT, "Left", "Align left"),
            (ALIGN_RIGHT, "Right", "Align right"),
        ],
        default=ALIGN_LEFT  # Standardwert
    ) # type: ignore

    grid_offset: bpy.props.IntProperty(
        name = "grid_offset",
        description= "Offset for grid positions and AC elements",
        default = 3
    ) # type: ignore

    track_align: bpy.props.BoolProperty(
        name="track_align",
        description="Align AC-Object to selected object and cursor position",
        default=False
    ) # type: ignore

    disable_export_checks: bpy.props.BoolProperty(
        name="disable_export_checks",
        description="Disable export checks (might improve performance)",
        default=False
    ) # type: ignore

    exp_use_sel: bpy.props.BoolProperty(
        name = "Use Selection",
        description="Use selection only on export",
        default=False
    ) # type: ignore

# Registration-Funktionen, falls nicht automatisch registriert:
def register():
    bpy.types.Scene.ac_tools_properties = bpy.props.PointerProperty(type=MyProperties)

def unregister():
    del bpy.types.Scene.ac_tools_properties