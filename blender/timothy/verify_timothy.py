import bpy, json, math, struct
from pathlib import Path
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'timothy.blend'))
r=bpy.data.objects['Timothy_Rig']
for p in r.pose.bones:
 assert sum(abs(a) for a in p.rotation_euler)<1e-4,('Non-neutral saved pose',p.name,list(p.rotation_euler))
for label in ['L','R']:
 for name in ['Sleeve.'+label,'Trouser leg.'+label]:
  o=bpy.data.objects[name]
  edges={}
  for poly in o.data.polygons:
   vs=list(poly.vertices)
   for a,b in zip(vs,vs[1:]+vs[:1]):key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
  assert all(n==2 for n in edges.values()),('Non-manifold sleeve/leg',name)
  assert len(o.vertex_groups)==2
for track in r.animation_data.nla_tracks:track.mute=True
for name in ['Idle','Run','Wave','Jump','Celebrate']:
 act=bpy.data.actions[name];r.animation_data.action=act
 # Blender 5 layered actions require selecting the matching armature slot.
 if act.slots:r.animation_data.action_slot=act.slots[0]
 for f in [1,8,16,23,31]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
  for o in [bpy.data.objects['Sleeve.L'],bpy.data.objects['Sleeve.R'],bpy.data.objects['Trouser leg.L'],bpy.data.objects['Trouser leg.R']]:
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
   assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
   assert max(v.co.length for v in mesh.vertices)<6,('Exploded mesh',name,f,o.name)
   ev.to_mesh_clear()
r.animation_data.action=None
b=(out/'timothy.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);names=[a['name'] for a in d.get('animations',[])]
assert set(names)=={'Idle','Run','Wave','Jump','Celebrate'}
assert len(d.get('skins',[]))==1
result={'saved_pose':'neutral','continuous_limb_meshes':'closed/manifold','deformation_samples':25,'animations':names,'glb_skin_count':1,'bytes':len(b)}
(out/'verification.json').write_text(json.dumps(result,indent=2));print('VERIFICATION',json.dumps(result))
