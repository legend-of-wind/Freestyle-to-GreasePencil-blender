from freestyle.predicates import *
from freestyle.types import Operators, StrokeShader, StrokeVertex
from freestyle.chainingiterators import ChainSilhouetteIterator, ChainPredicateIterator
import bpy
from mathutils import Vector, Matrix
import numpy as np

op=Operators()

def get_strokes():  #从当前渲染器获取所有线段 有时使用freestyle.context代替
    # a tuple containing all strokes from the current render. should get replaced by freestyle.context at some point
    return tuple(map(op.get_stroke_from_index, range(op.get_strokes_size())))

def render_visible_strokes():  
    """渲染可见线条至strokes对象"""
    upred = QuantitativeInvisibilityUP1D(0) #谓词:可见线条
    #从viewedge中选出边
    op.select(upred)
    #为stroke创建双向链
    op.bidirectional_chain(ChainSilhouetteIterator(), NotUP1D(upred))
    #创建stroke 从当前所有选中viewedge
    op.create(TrueUP1D(), [])
    return get_strokes()

def get_grease_pencil(gpencil_obj_name='GPencil'):
    """
    返回给定名称的gp对象 有则获取,无则创建
    gpencil_obj_name: gp对象名称
    """
    #创建 直接加入context.object
    if gpencil_obj_name not in bpy.context.scene.objects:
        bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
        #重命名(最后加入的物体)
        bpy.context.scene.objects["蜡笔"].name = gpencil_obj_name
    #获取gp对象
    gpencil = bpy.context.scene.objects[gpencil_obj_name]
    return gpencil

def get_grease_pencil_layer(gpencil: bpy.types.GreasePencil, gpencil_layer_name='GP_Layer',
                            clear_layer=False):
    """
    返回gp层 有则获取,无则创建
    gpencil: 层所在的gp对象
    gpencil_layer_name: 层的名字
    clear_layer: 覆写之前内容
    """
    #获取 创建gp
    if gpencil.data.layers and gpencil_layer_name in gpencil.data.layers:
        gpencil_layer = gpencil.data.layers[gpencil_layer_name]
    else:
        gpencil_layer = gpencil.data.layers.new(gpencil_layer_name, set_active=True)
    #清空
    if clear_layer:
        gpencil_layer.clear() 
    return gpencil_layer

def init_grease_pencil(gpencil_obj_name='GPencil', gpencil_layer_name='GP_Layer',
                       clear_layer=True) -> bpy.types.GPencilLayer:
    """
    创建gp对象 并为其添加层
    """
    gpencil = get_grease_pencil(gpencil_obj_name)
    gpencil_layer = get_grease_pencil_layer(gpencil, gpencil_layer_name, clear_layer=clear_layer)
    return gpencil_layer

def draw_from_freestyle(gp_frame,fs_stroke_tab):
    camera_mat = np.array(bpy.context.scene.camera.matrix_local.copy())  #获取相机局部坐标(复制)
    #对每个fs笔画
    for fs_stroke in fs_stroke_tab:
        gp_stroke = gp_frame.strokes.new()
        gp_stroke.display_mode = '3DSPACE'
        v_cnt=fs_stroke.stroke_vertices_size()
        gp_stroke.points.add(count=v_cnt) #创建gp笔画
        fs_vert_iter=fs_stroke.vertices_begin() #获取迭代器 从第一个顶点开始
        #对每个gp点
        for fs_vert,gp_point in zip(fs_vert_iter,gp_stroke.points):
            fs_point=np.array(list(fs_vert.point_3d)+[1])  #处理齐次坐标
            gp_point.co=tuple(np.dot(camera_mat,fs_point)[:3])
            #print(gp_point.co)
        #print("\n")
    return  
        
gp_layer = init_grease_pencil()
gp_frame = gp_layer.frames.new(0)
fs_stroke_tab=render_visible_strokes()
draw_from_freestyle(gp_frame,fs_stroke_tab)