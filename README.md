# Freestyle to Grease Pencil Convertor
Converting freestyle strokes to grease pencil object in blender 2.8x.\
It supports the lineset,color,alpha of the freestyle strokes.While modifiers on the freestyle stroke's shape is not supported.\
It's a rebuild version for the freestyle grease pencil exporter on this page https://github.com/folkertdev/freestyle-gpencil-exporter. \
Some bugs were fixed and it uses a more effcient script with less memory cost.
## usage
1.Open the edit > preferences > add-ons and install this python script(named "fs2gp.py").\
2.Set the output grease pencil object name and stroke layer name in the scene > render panel. (The freestyle should be enabled).\
![settings.png](https://github.com/legend-of-wind/Freestyle-to-GreasePencil-blender/blob/main/images/settings%20panel.png)\
3.Render the scene and this add-on will convert the freestyle strokes into gpencil strokes at the end of the rendering process.(Render animation is also supported.)\
4.An grease pencil object and layer named as you set in the step 2 will be added to the selected collection.\
5.You can set the "viewport shading" as "material preview" to display the color and alpha of the grease pencil.\
![output.png](https://github.com/legend-of-wind/Freestyle-to-GreasePencil-blender/blob/main/images/output.png)
