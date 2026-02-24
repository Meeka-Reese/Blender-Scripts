import bpy
class GenerateWeightText(bpy.types.Operator):
    bl_idname = "object.generate_weight_textures"
    bl_label = "Generate Textures From Weights"
    
    filepath: bpy.props.StringProperty(
        name="Save Path",
        description="Path to save the texture",
        default="//",
        subtype='FILE_PATH'
    )
    
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    
    def execute(self, context):
        #Select Object
        bpy.context.scene.render.engine = 'CYCLES'
        obj =  bpy.context.active_object
        mesh = obj.data
        
        #Add Material to Object with Image and Color Attribute
        mat = bpy.data.materials.new(name="MyMaterial")
        mat.use_nodes = True
        
        #Set up node variables
        nodes = mat.node_tree.nodes
        vc_node = nodes.new(type="ShaderNodeVertexColor")
        TextNode = nodes.new(type="ShaderNodeTexImage") 
        output = mat.node_tree.nodes.get("Material Output")
        links = mat.node_tree.links 
        
        if obj.data.materials:
            obj.data.materials[0] = mat  # Replace existing material in slot 0
        else:
            obj.data.materials.append(mat)  # Add new material slot
            
        links.new(vc_node.outputs["Color"], output.inputs["Surface"]) 
        #Link Attrib to surf
        
        #Iterate through Vertex Groups
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        for vg in obj.vertex_groups:
            
            obj.vertex_groups.active_index = vg.index
            bpy.ops.paint.vertex_color_from_weight()
            
            #Set active Attribute in VC
            active_color = mesh.color_attributes.active_color
            vc_node.layer_name = active_color.name
    
            TextName = vg.name
            
            if TextName in bpy.data.images:                                                         bpy.data.images.remove(bpy.data.images[TextName])

            # Create image and hold reference directly
            Image = bpy.data.images.new(name=TextName, width=1024, height=1024)

            # Make sure the image node is active so the baker targets it
            nodes.active = TextNode
            TextNode.image = Image
            
            bpy.ops.object.mode_set(mode='OBJECT') #set to obj mode for bake
            bpy.ops.object.bake(type='COMBINED')
            bpy.ops.object.mode_set(mode='VERTEX_PAINT') #set back to vpaint for rest of iter
            
            #save file with proper file name
            Image.filepath_raw = self.filepath + TextName + ".png"
            Image.file_format = "PNG"
            Image.save()

        return {'FINISHED'}
bpy.utils.register_class(GenerateWeightText)
bpy.ops.object.generate_weight_textures('INVOKE_DEFAULT')