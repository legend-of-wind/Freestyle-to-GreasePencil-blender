import bpy

bl_info = {  #注册插件信息
    "name": "Freestyle to Grease Pencil",
    "author": "Yang Shuaiyi",
    "version": (1,0),
    "blender": (2, 83, 0),
    "location": "Properties > Render > Freestyle GPencil Convertor",
    "description": "Converts Freestyle strokes to Grease Pencil Strokes",
    "category": "Render",
    }

from freestyle.types import Operators, StrokeShader
from mathutils import Vector, Matrix, Color
import parameter_editor 

def create_gpencil_frame(scene,frame_cur,layer_name="FSstroke",obj_name="GPencil"):
    if obj_name not in scene.objects.keys():
        if obj_name in bpy.data.grease_pencils.keys():
            bpy.data.grease_pencils.remove(bpy.data.grease_pencils[obj_name])  #已经删除物体的gp数据清除 
        bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
        bpy.context.collection.objects[-1].name = obj_name  #加入在集合的最后一个
        bpy.context.collection.objects[-1].data.name=obj_name

    gpencil=scene.objects[obj_name].data

    if layer_name in gpencil.layers.keys():
        gp_layer = gpencil.layers[layer_name]
    else:
        gp_layer = gpencil.layers.new(layer_name, set_active=True)
    gp_layer.use_lights=False #disable light to obtain the same color
    
    try:
        gp_frame=gp_layer.frames.new(frame_cur)  #数据中已经有当前帧
    except:
        for frame in gp_layer.frames:
            if frame.frame_number==frame_cur:
                gp_layer.frames.remove(frame)
                gp_frame=gp_layer.frames.new(frame_cur)
    return gp_frame
        

class FsGpConvertorPanel(bpy.types.Panel): #面板对象
    """Creates a Panel in the render context of the properties editor"""
    bl_idname = "RENDER_PT_FsGpConvertorPanel"
    bl_space_type = 'PROPERTIES'
    bl_label = "Freestyle GPencil Convertor"
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def register(cls):
        bpy.types.Scene.use_freestyle_gpencil_convert = bpy.props.BoolProperty(
                name="Use GPencil Convert",
                description="Convert Freestyle edges to Grease Pencil",
                default=True)
        bpy.types.Scene.fs_gp_object_name = bpy.props.StringProperty(
                name = "Object",  #通过StringProperty定义有GUI的字符串
                description = "Name of the output Grease Pencil object",
                default = "GPencil",) 
        bpy.types.Scene.fs_gp_layer_name = bpy.props.StringProperty(
                name = "Layer", 
                description = "Name of the output Grease Pencil layer",
                default = "FSstroke",) 
        bpy.types.Scene.basic_line_width = bpy.props.FloatProperty(
                name = "Basic Line Width", 
                description = "Basic width of the Grease Pencil strokes",
                default = 10,)
                
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.use_freestyle_gpencil_convert
        del bpy.types.Scene.fs_gp_object_name
        del bpy.types.Scene.fs_gp_layer_name
        
    @classmethod
    def poll(self,context):
        return context.scene.view_layers["View Layer"].use_freestyle and context.scene.view_layers["View Layer"].freestyle_settings.mode=="EDITOR"

    def draw(self, context):
        self.layout.prop(context.scene, 'fs_gp_object_name')
        self.layout.prop(context.scene, 'fs_gp_layer_name')
        self.layout.prop(context.scene, 'use_freestyle_gpencil_convert')
        self.layout.prop(context.scene, 'basic_line_width')

def draw_from_freestyle(fs_stroke_tab):
    """从freestyle创建gp笔画"""    
    scene=bpy.context.scene    
    gp_frame=create_gpencil_frame(scene,scene.frame_current,
    obj_name=scene.fs_gp_object_name,layer_name=scene.fs_gp_layer_name)
                
    camera_mat = scene.camera.matrix_local.copy()  #获取相机局部坐标(复制)
        
    for fs_stroke in fs_stroke_tab:
        gp_stroke = gp_frame.strokes.new()

        gp_stroke.display_mode = '3DSPACE'
        gp_stroke.line_width=scene.basic_line_width  #basic thickness
        gp_stroke.vertex_color_fill=[1,1,1,1]  #base color
        
        gp_stroke.points.add(count=fs_stroke.stroke_vertices_size()) #创建gp笔画
        fs_vert_iter=fs_stroke.vertices_begin() #获取迭代器 从第一个顶点开始

        for fs_vert,gp_point in zip(fs_vert_iter,gp_stroke.points):
            fs_point=fs_vert.point_3d
            gp_point.co=camera_mat@fs_point

            gp_point.pressure = sum(fs_vert.attribute.thickness)/2
            gp_point.vertex_color=list(fs_vert.attribute.color)+[1]
            gp_point.strength=fs_vert.attribute.alpha
    return


class StrokeCollector(StrokeShader):  #利用shade收集笔画
    def __init__(self):
        StrokeShader.__init__(self)
        self.viewmap = []

    def shade(self, stroke):
        self.viewmap.append(stroke)
        
        
class FSCallbacks:
    @classmethod
    def poll(cls, scene, linestyle):
        return scene.render.use_freestyle and scene.use_freestyle_gpencil_convert
        
    @classmethod
    def modifier_post(cls, scene, layer, lineset):
        cls.shader = StrokeCollector()  #渲染对象创建 注册为绘制程序获取viewmap渲染缓存
        return [cls.shader]
    
    @classmethod
    def lineset_post(cls, scene, layer, lineset):  
        if cls.poll==False: 
            return []
        fs_stroke_tab = cls.shader.viewmap 
        draw_from_freestyle(fs_stroke_tab)
        
        
classes = (
    FsGpConvertorPanel,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    del parameter_editor.callbacks_modifiers_post[:]
    del parameter_editor.callbacks_lineset_post[:]
    parameter_editor.callbacks_modifiers_post.append(FSCallbacks.modifier_post)  #注册渲染时回调函数
    parameter_editor.callbacks_lineset_post.append(FSCallbacks.lineset_post)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del parameter_editor.callbacks_modifiers_post[:]
    del parameter_editor.callbacks_lineset_post[:]

if __name__=="__main__":
    register()

    
