import json
import os
import configparser
from pathlib import Path
import shutil
import bpy

from .Properties import AC_FOLDER_NAME


def write_json(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(file):
    try:
        with open(file) as f:
            data = json.load(f)
            return data
    except:
        print(f"Error reading {file}")
        return None
    

def read_config(file):
    config = configparser.ConfigParser()
    try:
        config.read(file)
    except:
        print(f"Error reading {file}")
    return config

def write_config(config, file):
    with open(file, 'w') as configfile:
        config.write(configfile)


def get_addon_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_template(filename):
    return os.path.join(get_addon_dir(), 'templates', filename)


# default
def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def open_folder(path):
    dir = path
    if os.path.isfile(path):
        dir = os.path.dirname(path)

    os.startfile(dir) # open folder


def get_properties(context):
    return context.scene.ac_tools_properties


def get_blender_path(path):
    abs_path = bpy.path.abspath(path)
    if not os.path.exists(abs_path):
        return None
    return abs_path


""" 
CLASS TrackFolder()
Interface for Track Folder and property 'track_folder' 
"""
class TrackFolder():
    _path = None
    _track_name = None

    def __init__(self, path):
        self._path = bpy.path.abspath(path)
        self._track_name = Path(self._path).stem


    def set_path(self, path, props):
        self._path = path
        self._track_name = Path(self._path).stem
        relpath = bpy.path.relpath(path) + "\\" # add '\' or not??
        props.track_folder = relpath

    def exists(self):
        return os.path.exists(self._path)


    def get_ac_file_path(self, filename: str):
        track_path = get_blender_path(self._path)
        if not track_path:
            print(f"Cannot locate '{self._path}'")
            return None
        
        # file: collection of: (<path>, <subfolders>, <files>)
        for file in os.walk(track_path):
            for name in file[2]:
                #print(os.path.join(file[0], name))
                if name == filename:
                    return os.path.join(file[0], name)
        return None


    def get_track_file(self):
        return os.path.join(self._path, self._track_name + ".kn5")


    def rename(self, new_name: str):
        if not self.exists():
            return 1

        rc = 0
        props = get_properties(bpy.context)

        # folder
        track_folder = self._path
        new_track_folder = os.path.join(Path(track_folder).parent, new_name + "\\")
        
        # file
        track_file = self.get_track_file()
        if os.path.exists(track_file):
            new_track_file = os.path.join(os.path.dirname(track_file), new_name + ".kn5")
            # rename track file
            print(f"Renaming File {track_file} to {new_track_file}")
            shutil.move(track_file, new_track_file)

        # rename folder
        print(f"Renaming Folder {track_folder} to {new_track_folder}")
        shutil.move(track_folder, new_track_folder)

        # set track property
        print(f"Setting property 'track_folder' to {new_track_folder}")
        self.set_path(new_track_folder, props)

        return rc
"""
END CLASS
"""



def create_triangle_mesh(name):
    # Definition der Dreieck-Geometrie (Vertices und Faces)
    vertices = [
        (-0.5, 0, 0),  # Ecke 1
        (0.5, 0, 0),  # Ecke 2
        (0, 0, -2)  # Ecke 3
    ]
    faces = [(0, 1, 2)]

    # Neues Mesh und neues Objekt erstellen
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    return mesh


import math
from mathutils import Vector
def get_distance(p1: Vector, p2: Vector):
    #return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)
    return (p2 - p1).length