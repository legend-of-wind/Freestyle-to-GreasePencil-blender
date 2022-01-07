import bpy

bl_info = {  #注册插件信息
    "name": "Freestyle to Grease Pencil",
    "author": "yang shuaiyi",
    "version": (0, 8),
    "blender": (2, 83, 0),
    "location": "Properties > Render > Freestyle GPencil Convertor",
    "description": "Exports Freestyle strokes to Grease Pencil Strokes",
    "category": "Render",
    }

from freestyle.types import Operators, StrokeShader
import parameter_editor 
'''
from freestyle.shaders import *
from freestyle.predicates import *
from freestyle.chainingiterators import ChainSilhouetteIterator, ChainPredicateIterator
'''


def create_gpencil_frame(scene,frame_cur,layer_name="FSstroke",obj_name="GPencil"):
    if obj_name not in scene.objects.keys():
        if obj_name in bpy.data.grease_pencils.keys():
            #if layer_name in bpy.data.grease_pencils[obj_name].layers.keys():
             #   bpy.data.grease_pencils[obj_name].layers[]
            bpy.data.grease_pencils.remove(bpy.data.grease_pencils[obj_name])
        bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
        scene.objects[-1].name = obj_name
    gpencil = scene.objects[obj_name]
    scene.grease_pencil=scene.objects[obj_name].data

    if layer_name in gpencil.data.layers.keys():
        gp_layer = gpencil.data.layers[layer_name]
    else:
        gp_layer = gpencil.data.layers.new(layer_name, set_active=True)
    gp_layer.clear() 
    
    try:
        gp_frame=gp_layer.frames.new(frame_cur)
    except:
        for frame in gp_layer.frames:
            if frame.frame_number==frame_cur:
                self.gpencil_layer.frames.remove(frame)
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
        bpy.types.Scene.use_extract_linestyle = bpy.props.BoolProperty(
                name="Extract Stroke Linestyle",
                description="Convert Freestyle linestyle into Grease Pencil",
                default=True)
        bpy.types.Scene.simple_convert = bpy.props.BoolProperty(
                name="Simple Convertion",
                description="Only Convert Visible Strokes",
                default=True)
        bpy.types.Scene.fs_gp_object_name = bpy.props.StringProperty(
                name = "Layer",  #通过StringProperty定义有GUI的字符串
                description = "Name of the output Grease Pencil Object",
                default = "GPencil",) 
        bpy.types.Scene.fs_gp_layer_name = bpy.props.StringProperty(
                name = "Object",  #通过StringProperty定义有GUI的字符串
                description = "Name of the output Grease Pencil Layer",
                default = "FSstroke",) 
                
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.use_freestyle_gpencil_convert
        del bpy.types.Scene.use_extract_linestyle
        del bpy.types.Scene.fs_gp_object_name
        del bpy.types.Scene.fs_gp_layer_name
        
    @classmethod
    def poll(self,context):
        return context.scene.view_layers["View Layer"].use_freestyle and context.scene.view_layers["View Layer"].freestyle_settings.mode=="EDITOR"

    def draw(self, context):
        self.layout.prop(context.scene, 'fs_gp_object_name')
        self.layout.prop(context.scene, 'fs_gp_layer_name')
        self.layout.prop(context.scene, 'use_freestyle_gpencil_convert')
        #self.layout.prop(context.scene, 'simple_convert')
        #self.layout.prop(context.scene, 'use_extract_linestyle')
'''  
op=Operators()
def get_strokes():  
    return tuple(map(op.get_stroke_from_index, range(op.get_strokes_size())))

def render_visible_strokes():  
    upred = QuantitativeInvisibilityUP1D(0) #谓词:可见线条
    #从viewedge中选出边
    op.select(upred)
    #为stroke创建双向链
    op.bidirectional_chain(ChainSilhouetteIterator(), NotUP1D(upred))
    #创建stroke 从当前所有选中viewedge
    op.create(TrueUP1D(), [])
    return get_strokes()
'''

def draw_from_freestyle(fs_stroke_tab):
    """从freestyle创建gp笔画"""    
    scene=bpy.context.scene    
    gp_frame=create_gpencil_frame(scene,scene.frame_current,
                obj_name=scene.fs_gp_object_name,layer_name=scene.fs_gp_layer_name)
                
    camera_mat = scene.camera.matrix_local.copy()  #获取相机局部坐标(复制)
    
#    if scene.simple_convert==True:
#    fs_stroke_tab=render_visible_strokes()
        
    for fs_stroke in fs_stroke_tab:
        gp_stroke = gp_frame.strokes.new()
        gp_stroke.display_mode = '3DSPACE'
        gp_stroke.points.add(count=fs_stroke.stroke_vertices_size()) #创建gp笔画
        fs_vert_iter=fs_stroke.vertices_begin() #获取迭代器 从第一个顶点开始
    
        if scene.use_extract_linestyle==True:
            for fs_vert,gp_point in zip(fs_vert_iter,gp_stroke.points):
                fs_point=fs_vert.point_3d 
                gp_point.co=camera_mat@fs_point
    return
'''
                gp_point.pressure=fs_vert.attribute.thickness[0]
        else:
            for fs_vert,gp_point in zip(fs_vert_iter,gp_stroke.points):
                fs_point=fs_vert.point_3d 
                gp_point.co=camera_mat@fs_point'''
     


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

    