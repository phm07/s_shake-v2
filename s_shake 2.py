##################################
#                                #
#   WRITTEN BY PAUHULL, 2016     #
#        PAUHULL-SHOP.TK         #
#      YOUTUBE.COM/PAUHULL       #
#                                #    
#     PLEASE DON'T EARN MONEY    #                
#         WITH MY WORK.          #            
#            THANKS              #         
#                                #            
##################################

bl_info = {
    "name": "S_Shake V2",
    "category": "Animation",
    "author": "pauhull"
}

import random
import bpy

class ShakePanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Shake"
    bl_label = "Shake"

    def draw(self, context):
        col1 = self.layout.column(align=True)
        col1.prop(context.scene, "fov")
        
        col2 = self.layout.column(align=True)
        col2.prop(context.scene, "fov_start")
        col2.prop(context.scene, "fov_end")
        
        col3 = self.layout.column(align=True)
        col3.prop(context.scene, "shake_strength")
        col3.prop(context.scene, "shake_scale")
        
        col4 = self.layout.column(align=True)
        col4.operator("animation.addshake", text="Add Shake")

class AddShake(bpy.types.Operator):
	
    bl_idname = "animation.addshake"
    bl_label = "Add Shake"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        scene = bpy.context.scene
		
        bpy.ops.mesh.primitive_cube_add()
        ob = scene.objects.active
        ob.hide_render = True
        ob.show_wire = True
        ob.draw_type = "WIRE"
        ob.name = "Shake Controller"
	
        fps = scene.render.fps
        fps_base = scene.render.fps_base
		
        strength = context.scene.shake_strength
        scale = context.scene.shake_scale
        fov_start = context.scene.fov_start
        fov_end = context.scene.fov_end
        fov = context.scene.fov
        
        ob.keyframe_insert("rotation_euler")
        action = ob.animation_data.action
        for fcu in action.fcurves:
            if fcu.data_path == "rotation_euler":
                mod = fcu.modifiers.new("NOISE")
                mod.scale = scale
                mod.strength = strength
                mod.phase = random.randrange(-500, 500)

        camera = bpy.context.scene.camera
        con = camera.constraints.new(type='COPY_ROTATION')
        con.target = bpy.data.objects["Shake Controller"]
        con.owner_space = 'LOCAL'
        
        run = 0
        
        for k, v in scene.timeline_markers.items():
            run = run + 1
            frame = v.frame
            con.influence = 0
            con.keyframe_insert(data_path="influence", frame=frame - 1)
            con.influence = 1
            con.keyframe_insert(data_path="influence", frame=frame)
            
            if fov == True:
            
                data = camera.data
                data.lens = fov_end
                data.keyframe_insert(data_path="lens", frame=frame - 1)
                data.lens = fov_start
                data.keyframe_insert(data_path="lens", frame=frame)
                
            
        if run == 0:
            print("There are no markers")
        
        return {"FINISHED"}

def register() :
    bpy.utils.register_class(AddShake)
    bpy.utils.register_class(ShakePanel)
    bpy.types.Scene.shake_strength = bpy.props.FloatProperty(name = "Shake Strength", description = "Strength of the shake", default = 0.05)
    bpy.types.Scene.shake_scale = bpy.props.FloatProperty(name = "Shake Scale", description = "Scale of the shake", default = 20.0)
    bpy.types.Scene.fov_start = bpy.props.FloatProperty(name = "FOV Start", description = "FOV Start", default = 50.0)
    bpy.types.Scene.fov_end = bpy.props.FloatProperty(name = "FOV End", description = "FOV End", default = 35.0)
    bpy.types.Scene.fov = bpy.props.BoolProperty(name = "Animate FOV", description = "Animate FOV", default = True)
def unregister() :
    bpy.utils.unregister_class(AddShake)
    bpy.utils.unregister_class(ShakePanel)
    del bpy.types.Scene.shake_strength
    del bpy.types.Scene.shake_scale
    
if __name__ == "__main__" :
    register()