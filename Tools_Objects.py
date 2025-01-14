import bpy
from math import radians
from mathutils import Vector

from .Properties import ALIGN_LEFT, ALIGN_RIGHT, AC_OBJ_PREFIX, AC_COLLECTION_NAME
from .Functions import create_triangle_mesh, get_distance, get_properties


# TODO create objets referring to road (if road selected automatically place it on road / timing besides road)
# FIXME timing doesnt seem to work...
# TODO create simple collider objects 1WALL_<object> (cube with outer borders/convex hull?) with NULL material, visibility off
#   advanced: make little mesh (like curvature for obj)
# TODO make custom materials (+ material guide)


class OBJECT_OT_create_start(bpy.types.Operator):
    bl_idname = "object.create_start"
    bl_label = "Create Start Position"
    bl_description = "Create an AC object for ingame-logic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_ac_object(AC_OBJ_PREFIX['START'])
        return {'FINISHED'}
   

class OBJECT_OT_create_hotlap_start(bpy.types.Operator):
    bl_idname = "object.create_hotlap_start"
    bl_label = "Create Hotlap Start Position"
    bl_description = "Create an AC object for ingame-logic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_ac_object(AC_OBJ_PREFIX['HOTLAP'])
        return {'FINISHED'}


class OBJECT_OT_create_pit(bpy.types.Operator):
    bl_idname = "object.create_pit"
    bl_label = "Create Pit Position"
    bl_description = "Create an AC object for ingame-logic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_ac_object(AC_OBJ_PREFIX['PIT'])
        return {'FINISHED'}


class OBJECT_OT_create_time(bpy.types.Operator):
    bl_idname = "object.create_timing"
    bl_label = "Create Timing Position"
    bl_description = "Create an AC object for ingame-logic"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        create_timing_objects(AC_OBJ_PREFIX['TIME'])
        return {'FINISHED'}



# TODO offset to left or right and recalc when selected -> change orientation (UNDO step!!)
def create_ac_object(prefix: str):
    props = get_properties(bpy.context)
    align = props.grid_align
    offset = props.grid_offset

    if align == ALIGN_RIGHT:
        offset = offset * -1

    location = get_track_middle_point(prefix)
    max_number = 0
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(prefix):
            try:
                pos = -1
                number = int(obj.name.rsplit('_')[pos])
                if number >= max_number:
                    max_number = number + 1
                    location = Vector((obj.location.x, obj.location.y - 3, obj.location.z)) # offset y for grid layour  
            except:
                continue

    name = f"{prefix}_{max_number}"

    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name])

    obj = bpy.data.objects.new(name, create_triangle_mesh(name))
    if max_number == 0:
        obj.location = location
    else:
        obj.location = (
            location.x - offset if max_number % 2 != 0 else location.x + offset, # grid layout left/right
            location.y,
            location.z
        )

    set_default_material(obj)
    setup_ac_object(obj)


def create_timing_objects(prefix: str):
    props = get_properties(bpy.context)
    offset = props.grid_offset

    location = get_track_middle_point(prefix)
    max_number = 0
    for obj in bpy.context.scene.objects:
        if obj.name.startswith(prefix):
            try:
                pos = -2
                number = int(obj.name.rsplit('_')[pos])
                if number >= max_number:
                    max_number = number + 1
            except:
                continue

    # create for both sides
    name_l = f"{prefix}_{max_number}_L"
    name_r = f"{prefix}_{max_number}_R"

    if name_l in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name_l])
    if name_r in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name_r])

    obj_l = bpy.data.objects.new(name_l, create_triangle_mesh(name_l))
    obj_r = bpy.data.objects.new(name_r, create_triangle_mesh(name_r))

    obj_l.location = Vector((location.x - (offset / 2), location.y, location.z))
    obj_r.location = Vector((location.x + (offset / 2), location.y, location.z))

    set_default_material(obj_l)
    set_default_material(obj_r)

    setup_ac_object(obj_l)
    setup_ac_object(obj_r)


def set_default_material(obj: bpy.types.Object):
    name = "AC_OBJECT"
    mat = (bpy.data.materials.get(name) or bpy.data.materials.new(name))
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    node = nodes.get('Principled BSDF')
    if node:
        inp: bpy.types.Node = node.inputs.get('Base Color')
        if inp:
            inp.default_value = (0.8, 0, 0, 1)
            print("Input adjusted")
        else:
            print(f"Input not found {node.inputs}")
            for i in node.inputs:
                print(f"Input {i}")
    else:
        print(f"Node principled not found")

    obj.data.materials.append(mat)


def setup_ac_object(obj: bpy.types.Object):
    from mathutils import Matrix

    # make z front and y up
    obj.rotation_euler = (radians(90), 0,0)
    obj.data.update()

    # Objekt zur Szene hinzufügen
    if AC_COLLECTION_NAME not in bpy.data.collections:
        c = bpy.data.collections.new(AC_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(c)
    bpy.data.collections[AC_COLLECTION_NAME].objects.link(obj)

    obj.select_set(True)

# TODO make it location, roatation and track_width - not only location!
def get_track_middle_point(prefix: str):
    context = bpy.context
    props = get_properties(context)
    obj = context.active_object
    cursor = context.scene.cursor.location

    if not props.track_align or not obj:
        print("Track Align deactivated or no active object - Using Cursor location")
        return cursor
    
    # find closest x/y to the "left" and then also to the "right" of cursor (depending on direction...)
    # draw line in 90 degree to track direction
    # don't forget rotation (keep in mind local z=forward, y=up!)

    vertices = [v.co for v in obj.data.vertices]
    world_vertices = [obj.matrix_world @ v for v in vertices]
    for v in world_vertices:
        print(f"Track: {v}")
    print(f"Cursor: {cursor}")

    distances = [get_distance(cursor, v) for v in world_vertices]
    for d in distances:
        print(f"Distance {d}")





    if prefix == AC_OBJ_PREFIX['TIME']:
        pass # place to left and right of track
    if prefix == AC_OBJ_PREFIX['PIT']:
        pass # try to find pit direction and rotate location
    if prefix == AC_OBJ_PREFIX['HOTLAP']:
        pass # place in middle of track
    if prefix == AC_OBJ_PREFIX['START']:
        pass # place in left/right half of the track
    
    location = None

    return location