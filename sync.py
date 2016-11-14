
bl_info = {
    "name": "Sync tools",
    "category": "Animation",
    "author": "pauhull + ranfdev"
}

import random
import bpy
import math
import mathutils



class ShakePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Sync"
    bl_label = "Sync"

    def draw(self, context):

        # Define the scene
        scene = context.scene

        layout = self.layout

        row = layout.row()
        row.prop(scene, "fov")

        row = layout.row()
        row.prop(scene, "fov_start")
        row.prop(scene, "fov_end")

        row = layout.row()
        row.prop(scene, "shake")

        row = layout.row()
        row.prop(scene, "shake_strength")
        row.prop(scene, "shake_scale")

        row = layout.row()
        row.prop(scene, "light")

        row = layout.row()
        row.prop(scene, "light_strength")

        row = layout.row()
        row.prop(scene, "color")

        row = layout.row()
        row.prop(scene, "color_strength")

        row = layout.row()
        row.prop(scene, "fade")

        row = layout.row()
        row.prop(scene, "fadeInEnd")
        row.prop(scene, "fadeOutStart")

        row = layout.row()
        row.operator("animation.addsync", text="Add All")


class AddSync(bpy.types.Operator):

    bl_idname = "animation.addsync"
    bl_label = "Add Sync"
    bl_options = {"UNDO"}

    def invoke(self, context, event):

        def addNode(node, newname):
            # Activate nodes
            scene.use_nodes = True
            # Create a new hue saturation value node
            node_new = scene.node_tree.nodes.new(node)
            node_new.name = newname
            node_name = scene.node_tree.nodes[newname]
        def connectNode(nodeInput, nodeOutput):
            # Define the name
            nodeIn = scene.node_tree.nodes[nodeInput]
            nodeOut = scene.node_tree.nodes[nodeOutput]
            # Define the previous node connected to the compositor
            previous = nodeOut.inputs['Image'].links[0].from_node
            # Connect the node to the compositor
            scene.node_tree.links.new(nodeIn.outputs['Image'], nodeOut.inputs[0])
            # Connect the node to the previous node
            scene.node_tree.links.new(previous.outputs['Image'], nodeIn.inputs['Image'])

        def selectNode(name):
            return scene.node_tree.nodes[name]

        # Define the scene
        scene = bpy.context.scene

        # Add the cube
        bpy.ops.mesh.primitive_cube_add()
        ob = scene.objects.active
        ob.hide_render = True
        ob.show_wire = True
        ob.draw_type = "WIRE"
        ob.name = "Shake Controller"

        # Define the fps
        fps = scene.render.fps
        fps_base = scene.render.fps_base
        # Add noise
        ob.keyframe_insert("rotation_euler")
        action = ob.animation_data.action
        for fcu in action.fcurves:
            if fcu.data_path == "rotation_euler":
                mod = fcu.modifiers.new("NOISE")
                mod.scale = scene.shake_scale
                mod.strength = scene.shake_strength
                mod.phase = random.randrange(-500, 500)

        # Define the camera
        camera = scene.camera

        if scene.shake == True:
            con = camera.constraints.new(type='COPY_ROTATION')
            con.target = bpy.data.objects["Shake Controller"]
            con.owner_space = 'LOCAL'

        run = 0
        # Check if color cahnging is enabled
        if scene.color == True:
            addNode('CompositorNodeHueSat', 'colorChanger')
            connectNode('colorChanger', 'Composite')

        # Check if fade is enabled
        if scene.fade == True:
            addNode('CompositorNodeHueSat', 'fade')
            connectNode('fade', 'Composite')
            selectNode('fade').color_value = 0
            selectNode('fade').keyframe_insert(data_path="color_value", frame = scene.frame_start)
            selectNode('fade').color_value = 1
            selectNode('fade').keyframe_insert(data_path="color_value", frame = scene.fadeInEnd)
            selectNode('fade').keyframe_insert(data_path="color_value", frame = scene.fadeOutStart)
            selectNode('fade').color_value = 0
            selectNode('fade').keyframe_insert(data_path="color_value", frame = scene.frame_end)
        for k, v in scene.timeline_markers.items():
            run = run + 1
            frame = v.frame

            if scene.shake == True:
                con.influence = 0
                con.keyframe_insert(data_path="influence", frame=frame - 1)
                con.influence = 1
                con.keyframe_insert(data_path="influence", frame=frame)

            if scene.fov == True:

                data = camera.data
                data.lens = scene.fov_end
                data.keyframe_insert(data_path="lens", frame=frame - 1)
                data.lens = scene.fov_start
                data.keyframe_insert(data_path="lens", frame=frame)

            if scene.light == True:

                data = scene.view_settings
                data.keyframe_insert(data_path="exposure", frame=frame - 1)
                data.exposure += scene.light_strength
                data.keyframe_insert(data_path="exposure", frame=frame)
                data.exposure -= scene.light_strength

            if scene.color == True:
                selectNode('colorChanger').keyframe_insert(data_path="color_hue", frame=frame - 1)
                selectNode('colorChanger').color_hue = random.random()
                selectNode('colorChanger').keyframe_insert(data_path="color_hue", frame=frame)

        if run == 0:
            print("There are no markers")

        return {"FINISHED"}

def register() :
    bpy.utils.register_class(AddSync)
    bpy.utils.register_class(ShakePanel)
    bpy.types.Scene.shake = bpy.props.BoolProperty(name = "Shake", description = "Add shake to the intro", default = True)
    bpy.types.Scene.shake_strength = bpy.props.FloatProperty(name = "Shake Strength", description = "Strength of the shake", default = 0.05)
    bpy.types.Scene.shake_scale = bpy.props.FloatProperty(name = "Shake Scale", description = "Scale of the shake", default = 20.0)
    bpy.types.Scene.fov_start = bpy.props.FloatProperty(name = "FOV Start", description = "FOV Start", default = 50.0)
    bpy.types.Scene.fov_end = bpy.props.FloatProperty(name = "FOV End", description = "FOV End", default = 35.0)
    bpy.types.Scene.fov = bpy.props.BoolProperty(name = "Animate FOV", description = "Animate FOV", default = True)
    bpy.types.Scene.light = bpy.props.BoolProperty(name = "Light", description = "Animate FOV", default = True)
    bpy.types.Scene.color = bpy.props.BoolProperty(name = "Color", description = "Animate FOV", default = True)
    bpy.types.Scene.light_strength = bpy.props.FloatProperty(name = "Light Strength", description = "FOV End", default = 0.25)
    bpy.types.Scene.color_strength = bpy.props.FloatProperty(name = "Color Strength", description = "FOV End", default = 0.25)
    bpy.types.Scene.fade = bpy.props.BoolProperty(name = "FadeIn&Out", description = "Add fade in and fade out to the intro", default = True)
    bpy.types.Scene.fadeInEnd = bpy.props.FloatProperty(name = "FadeIn end", description = "Add fade in and fade out to the intro", default = 60)
    bpy.types.Scene.fadeOutStart = bpy.props.FloatProperty(name = "FadeOut start", description = "Add fade in and fade out to the intro", default = 250)
def unregister() :
    bpy.utils.unregister_class(AddSync)
    bpy.utils.unregister_class(ShakePanel)
    del bpy.types.Scene.shake_strength
    del bpy.types.Scene.shake_scale
    del bpy.types.Scene.color_strength
    del bpy.types.Scene.light_strength

if __name__ == "__main__" :
    register()
