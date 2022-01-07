# Freestyle to Grease Pencil Convertor
Converting freestyle strokes to grease pencil object in blender 2.8x.\
This is not a complete version and it is still under development.\
The convertor use the lineset you set in freestyle settings. The thickness,color and the modifiers of the freestyle stroke will not be rendered.
## usage
1.Open the edit > preferences > add-ons and install this python script("freestyle_gpencil_convertor.py").\
2.Set the output grease pencil object name and stroke layer name in the scene > render panel. (The "use_freestyle" property should be activated).\
3.Render the scene(with F12) and this add-on will convert the freestyle strokes into grease pencil strokes output into the grease pencil object you set in the panel.
