# Freestyle to Grease Pencil Convertor
Converting freestyle strokes to grease pencil object in blender 2.8x.\
It supports the lineset,color,alpha of the freestyle strokes.\
Modifiers on the freestyle stroke shape is not supported.
## usage
1.Open the edit > preferences > add-ons and install this python script("fs2gp.py").\
2.Set the output grease pencil object name and stroke layer name in the scene > render panel. (The "use_freestyle" property should be activated).\
3.Render the scene and this add-on will convert the freestyle strokes into gpencil strokes and the end of the rendering process.
