bl_info = {
    "name": "Export Pose JSON",
    "author": "Zhewen Zheng",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Export Pose",
    "description": "Export selected object pose at each frame to JSON file",
    "category": "Object"
}

import bpy
import os
import json


def listify_matrix(matrix):
    return [list(row) for row in matrix]


class OBJECT_OT_export_pose_json(bpy.types.Operator):
    bl_idname = "object.export_pose_json"
    bl_label = "Export Pose JSON"
    bl_description = "Export selected object's pose at each frame to a JSON file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}

        out_data = {
            'object_name': obj.name,
            'frames': [],
            'camera_angle_x': obj.data.angle_x
        }

        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        for i, frame in enumerate(range(scene.frame_start, scene.frame_end + 1)):
            scene.frame_set(frame)
            frame_data = {
                'frame': frame,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'transform_matrix': [list(row) for row in obj.matrix_world]
            }
            out_data['frames'].append(frame_data)

        try:
            with open(self.filepath, 'w') as f:
                json.dump(out_data, f, indent=4)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write file: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported pose data to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        blend_filepath = bpy.data.filepath
        if blend_filepath:
            default_name = os.path.splitext(os.path.basename(blend_filepath))[0] + "_pose.json"
            self.filepath = os.path.join(os.path.dirname(blend_filepath), default_name)
        else:
            self.filepath = "pose.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OBJECT_PT_export_pose_panel(bpy.types.Panel):
    bl_label = "Export Pose JSON"
    bl_idname = "OBJECT_PT_export_pose_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Export Pose'

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_export_pose_json.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_export_pose_json)
    bpy.utils.register_class(OBJECT_PT_export_pose_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_export_pose_panel)
    bpy.utils.unregister_class(OBJECT_OT_export_pose_json)


if __name__ == "__main__":
    register()
