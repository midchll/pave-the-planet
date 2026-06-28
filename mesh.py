'''
pave-the-planet
Mitchell Deevers ~ midchll
2026

mesh.py
generate path mesh
'''

import numpy as np


def obj_polyline(verts:list[list[float]]|list[tuple[float]]) -> list[str]:
    '''Return polyline obj verts and line as list of strings'''
    if not verts:
        return []
    
    vs = []
    n = len(verts)
    mg = max([len(str(n)) for v in verts for n in v])
    
    for v in verts:
        ps = [str(i) for i in v]
        l = 'v    '
        
        for p in ps:
            l += p + ' ' * ((mg - len(p)) + 4)
        
        vs.append(l)
    
    pl = '\nl ' + ' '.join([str(i) for i in range(1, n + 1)])
    vs.append(pl)

    return vs


def obj_face():
    '''Return obj face geometry as list of strings'''
    pass


def mesh(path:np.ndarray, width:int|float) -> tuple[np.ndarray,np.ndarray]:
    '''Return vertices and faces defining path mesh'''
    ordered = path.reshape(-1, 3)
    faces = []
    
    for i in range(len(path) - 1):
        l0 = 2 * i
        r0 = l0 + 1
        l1 = l0 + 2
        r1 = l0 + 3
        
        faces.append([l0, r0, l1])
        faces.append([r0, r1, l1])
    
    faces = np.array(faces)
    
    return (ordered, faces)


def make_path(verts:list[list[float]]|list[tuple[float]], width:int|float) -> np.ndarray:
    centerline = np.array(verts)
    tangents = np.zeros_like(centerline)
    
    tangents[1:-1] = centerline[2:] - centerline[:-2]
    
    tangents[0] = centerline[1] - centerline[0]
    tangents[-1] = centerline[-1] - centerline[-2]
    
    lengths = np.linalg.norm(tangents, axis=1)
    tangents /= lengths[:, None]
    
    up = np.array([0.0, 0.0, 1.0])
    rights = np.cross(tangents, up)
    rights /= np.linalg.norm(rights, axis=1)[:, None]
    
    left = centerline - width / 2 * rights
    right = centerline + width / 2 * rights
    
    return np.stack((left, right), axis = 1)
    
     
    