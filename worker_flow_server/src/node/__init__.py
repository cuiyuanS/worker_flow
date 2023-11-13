from src.node.constant import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


def get_node_info(node_class):
    obj_class = NODE_CLASS_MAPPINGS[node_class]
    info = {}
    info['input'] = obj_class.INPUT_TYPES()
    info['output'] = obj_class.RETURN_TYPES
    info['output_name'] = obj_class.RETURN_NAMES if hasattr(obj_class, 'RETURN_NAMES') else info['output']
    info['name'] = node_class
    info['display_name'] = NODE_DISPLAY_NAME_MAPPINGS[
        node_class] if node_class in NODE_DISPLAY_NAME_MAPPINGS.keys() else node_class
    info['description'] = obj_class.DESCRIPTION if hasattr(obj_class, 'DESCRIPTION') else ''
    info['category'] = 'sd'
    if hasattr(obj_class, 'OUTPUT_NODE') and obj_class.OUTPUT_NODE == True:
        info['output_node'] = True
    else:
        info['output_node'] = False

    if hasattr(obj_class, 'CATEGORY'):
        info['category'] = obj_class.CATEGORY
    return info
