def read_puzzles(game):
    puzzles = dict()
    j = 0
    for node in game.roots:
        conds = dict()
        i = 0
        for cond in node.conds:
            conds[f'{i}'] = {'title' : f'condition {i}',
                             'description' : 'no description',
                             'state' : 'active'}
            i += 1
        puzzles[f'{j}'] = {'i' : 0, 'j' : 0,
                           'title' : 'node', 'state' : 'active',
                           'description' : 'no description',
                           'color_index' : 0, 'djs' : [],
                           'conditions' : conds}
        
        j += 1
    return puzzles

def read_devices(network):
    devices = dict()
    for device in network.devices.values():
        name = f'device{device.device_id}' if device.name is None else device.name
        devices[name] = {'comps' : read_comps(device)} 
    return devices

def read_comps(device):
    comps = dict()
    if device.comps is None:
        return None
    for comp in device.comps.values():
        name = f'comp{comp.comp_id}' if comp.name is None else comp.name 
        comps[name] = {'attrs' : read_attrs(comp)}
    return comps

def read_attrs(comp):
    attrs = dict()
    if comp.attrs is None:
        return None
    for attr in comp.attrs.values():
        name = f'attr{attr.attr_id}' if attr.name is None else attr.name 
        attrs[name] = {'type' : attr.type, 'value' : attr.value}
    return attrs

