import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, Quaternion
random.seed(17)
OUT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials):bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.fps=30
scene.world.color=(.22,.22,.22)
scene.view_settings.view_transform='AgX'
def rgb(h):
 h=h.lstrip('#');v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in v)+(1,)
def mat(name,h,rough=.5,metal=0,knit=False,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=rgb(h);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(h);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=rgb(h);p.inputs['Emission Strength'].default_value=emit
 if knit:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=190;n.inputs['Detail'].default_value=2
  b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=.009
  m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m
skin=mat('Skin / warm peach','F3B58D',.48);skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.07
purple=mat('Hoodie / violet knit','745ACB',.76,knit=True);dark=mat('Trousers / deep lavender','6354A5',.78,knit=True)
cuff=mat('Ribbed knit','917BDC',.79,knit=True);hat=mat('Beanie / periwinkle','8872DA',.8,knit=True)
hair=mat('Hair / chocolate','643C29',.52);hairlight=mat('Hair / warm highlight','825335',.53)
eye=mat('Eyes / glossy espresso','291B23',.18);white=mat('Catchlights','FFFFFF',.18)
blush=mat('Cheeks / peach','EEA08B',.75);mouth=mat('Smile / cocoa','9B523D',.65)
cyan=mat('Cyan LEDs','6DF7ED',.25,emit=1.6);pink=mat('Pink pixels','E98DDD',.5,emit=.15)
navy=mat('Headphones / graphite violet','393452',.4,.20);pads=mat('Headphones / padded purple','655C94',.6)
sole=mat('Sneaker soles','B7ADDB',.56);shoe=mat('Sneakers / violet','6F5AA7',.54);lace=mat('Laces','C9BCEB',.7)
zipper=mat('Zipper / brushed nickel','C8CDD9',.35,.55);seam=mat('Stitch seams','6653AA',.8)
black=mat('Mouth cavity','49242E',.6)
objects=[];weights={}
def finish(o,name,material,bone=None):
 o.name=name
 if material:o.data.materials.append(material)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 objects.append(o)
 if bone:weights[o.name]=bone
 return o
def uv(name,loc,scale,material,bone=None,segments=40,rings=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc);o=bpy.context.object;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,name,material,bone)
def box(name,loc,dims,r,material,bone=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 b=o.modifiers.new('Soft rounded edges','BEVEL');b.width=r;b.segments=4
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return finish(o,name,material,bone)
def curve(name,points,radius,material,bone=None):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=12;d.bevel_depth=radius;d.bevel_resolution=3
 s=d.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
 bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
 return finish(o,name,material,bone)
def loft(name,points,radii,material,bones=None,sides=32,flatten=1):
 pts=[Vector(p) for p in points];verts=[];faces=[]
 for i,(p,r) in enumerate(zip(pts,radii)):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
  u=tangent.cross(Vector((0,1,0))).normalized()
  if u.length<.1:u=tangent.cross(Vector((1,0,0))).normalized()
  v=tangent.cross(u).normalized()
  for k in range(sides):
   a=k*2*math.pi/sides;co=p+r*(math.cos(a)*u+math.sin(a)*flatten*v);verts.append(co)
 for i in range(len(pts)-1):
  for k in range(sides):faces.append((i*sides+k,i*sides+(k+1)%sides,(i+1)*sides+(k+1)%sides,(i+1)*sides+k))
 faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(pts)-1)*sides+k for k in range(sides)))
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);finish(o,name,material)
 sub=o.modifiers.new('Continuous cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 if bones:
  # Smooth blend at elbow/knee. Vertices stay in one continuous mesh.
  a,b,joint,width=bones;ga=o.vertex_groups.new(name=a);gb=o.vertex_groups.new(name=b)
  axis=(pts[-1]-pts[0]).normalized();j=Vector(joint)
  for vert in o.data.vertices:
   t=max(0,min(1,.5+(vert.co-j).dot(axis)/width));t=t*t*(3-2*t)
   ga.add([vert.index],1-t,'REPLACE');gb.add([vert.index],t,'REPLACE')
 return o
# Armature, Z up and face toward -Y.
bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0));rig=bpy.context.object;rig.name='Timothy_Rig';rig.data.name='Timothy_Skeleton'
for b in list(rig.data.edit_bones):rig.data.edit_bones.remove(b)
def bone(n,h,t,parent=None):
 b=rig.data.edit_bones.new(n);b.head=h;b.tail=t
 if parent:b.parent=rig.data.edit_bones[parent]
 return b
bone('Root',(0,0,0),(0,0,.25));bone('Hips',(0,0,1.02),(0,0,1.3),'Root');bone('Chest',(0,0,1.3),(0,0,2.03),'Hips');bone('Neck',(0,0,2.03),(0,0,2.30),'Chest');bone('Head',(0,0,2.30),(0,0,3.35),'Neck')
for sign,label in [(-1,'L'),(1,'R')]:
 bone('UpperArm.'+label,(sign*.43,0,2.00),(sign*.69,0,1.65),'Chest')
 bone('Forearm.'+label,(sign*.69,0,1.65),(sign*.80,-.015,1.31),'UpperArm.'+label)
 bone('Hand.'+label,(sign*.80,-.015,1.31),(sign*.82,-.04,1.09),'Forearm.'+label)
 bone('Thigh.'+label,(sign*.22,0,1.15),(sign*.23,0,.69),'Hips')
 bone('Shin.'+label,(sign*.23,0,.69),(sign*.24,0,.29),'Thigh.'+label)
 bone('Foot.'+label,(sign*.24,0,.29),(sign*.24,-.30,.13),'Shin.'+label)
bone('Companion',(-1.15,0,2.5),(-1.15,0,2.8),'Root')
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
# Torso: one closed surface.
body=loft('Hoodie / continuous torso',[(0,0,1.10),(0,0,1.15),(0,.015,1.28),(0,.025,1.72),(0,.025,1.96),(0,.025,2.06),(0,.025,2.13)],[.40,.47,.49,.47,.44,.32,.21],purple,flatten=.69);weights[body.name]='Chest'
uv('Neck',(0,0,2.20),(.17,.16,.22),skin,'Neck')
# Hips under hem, so legs remain attached in every pose.
box('Trouser waist',(0,.02,1.105),(.79,.52,.23),.10,dark,'Hips')
hood=[]
for i in range(24):
 a=2*math.pi*i/23;hood.append((.33*math.cos(a),.22*math.sin(a)+.025,2.085+.11*math.sin(a)))
curve('Padded hoodie collar',hood,.095,purple,'Chest')
# Hem, zipper, pockets, embroidered pixels.
curve('Hem ribbing',[(.43*math.cos(i*2*math.pi/32),.30*math.sin(i*2*math.pi/32),1.17) for i in range(33)],.047,cuff,'Chest')
curve('Zipper tape',[(0,-.333,1.20),(0,-.324,1.65),(0,-.300,1.97)],.019,seam,'Chest')
for i in range(29):
 z=1.22+i*.025;y=-.336+(z-1.22)*.04
 for s in [-1,1]:box('Zip tooth',(.010*s,y-.010,z),(.017,.015,.012),.003,zipper,'Chest')
box('Zipper pull',(0,-.350,1.94),(.064,.034,.11),.018,zipper,'Chest')
box('Pull slot',(0,-.371,1.96),(.022,.008,.035),.006,navy,'Chest')
for s in [-1,1]:
 box('Kangaroo pocket '+str(s),(s*.24,-.307,1.40),(.32,.06,.29),.065,purple,'Chest')
 curve('Pocket stitch '+str(s),[(s*.11,-.342,1.52),(s*.23,-.354,1.47),(s*.38,-.330,1.48)],.007,seam,'Chest')
 for x,z in [(.18,1.81),(.27,1.86),(.33,1.77),(.22,1.69),(.15,1.74),(.29,1.67)]:
  box('Embroidered pixel',(s*x,-.329,z),(.047,.014,.047),.007,cyan if z!=1.86 else pink,'Chest')
# Continuous sleeves and trousers, no open sockets or separate joint caps.
for s,label in [(-1,'L'),(1,'R')]:
 pts=[(s*.40,0,2.02),(s*.45,0,2.00),(s*.53,0,1.88),(s*.64,0,1.72),(s*.69,0,1.65),(s*.735,-.008,1.51),(s*.79,-.015,1.35),(s*.81,-.015,1.29)]
 loft('Sleeve.'+label,pts,[.045,.185,.19,.16,.15,.15,.135,.095],purple,('UpperArm.'+label,'Forearm.'+label,(s*.69,0,1.65),.30))
 c=loft('Wrist rib.'+label,[(s*.785,-.015,1.38),(s*.81,-.015,1.29)],[.137,.119],cuff);weights[c.name]='Forearm.'+label
 pts=[(s*.22,0,1.18),(s*.22,0,1.11),(s*.23,0,.90),(s*.23,0,.71),(s*.235,0,.65),(s*.24,0,.45),(s*.24,-.005,.30)]
 loft('Trouser leg.'+label,pts,[.14,.207,.21,.19,.185,.18,.135],dark,('Thigh.'+label,'Shin.'+label,(s*.23,0,.69),.30),flatten=.92)
 c=loft('Ankle rib.'+label,[(s*.24,-.005,.37),(s*.24,-.005,.28)],[.16,.145],cuff);weights[c.name]='Shin.'+label
 # Rounded hand and individual fingers share the hand bone.
 uv('Palm.'+label,(s*.825,-.025,1.19),(.12,.095,.14),skin,'Hand.'+label)
 for i in range(4):
  x=s*(.75+i*.047);z=1.09+(abs(i-1.5)*.015)
  o=uv('Finger.'+label+str(i),(x,-.055,z),(.031,.043,.080),skin,'Hand.'+label,24,16);o.rotation_euler[1]=s*(i-1.5)*.09
 uv('Thumb.'+label,(s*.714,-.060,1.23),(.050,.054,.090),skin,'Hand.'+label,24,16)
 # Sneakers with cyan sole strips and three laces.
 box('Sneaker sole.'+label,(s*.245,-.12,.105),(.39,.66,.15),.070,sole,'Foot.'+label)
 box('Sneaker upper.'+label,(s*.245,-.08,.22),(.35,.56,.25),.11,shoe,'Foot.'+label)
 uv('Shoe toe.'+label,(s*.245,-.32,.17),(.18,.21,.11),shoe,'Foot.'+label)
 box('Shoe tongue.'+label,(s*.245,-.14,.33),(.21,.20,.12),.04,cuff,'Foot.'+label)
 for j in range(3):curve('Lace.'+label+str(j),[(s*.245-.105,-.32+j*.075,.25+j*.027),(s*.245,-.34+j*.075,.285+j*.027),(s*.245+.105,-.32+j*.075,.25+j*.027)],.018,lace,'Foot.'+label)
 curve('Cyan sole rail.'+label,[(s*.245-.17,-.30,.10),(s*.245-.17,-.02,.10),(s*.245-.13,.15,.10)],.018,cyan,'Foot.'+label)
 box('Shoe LED.'+label,(s*.245,-.24,.364),(.09,.016,.045),.01,cyan,'Foot.'+label)
# Soft superellipsoid head, fully modeled from all angles.
a,b,c,zc=.66,.49,.59,2.77;n=2.8;p=2/n
verts=[];faces=[];U=64;V=36
sg=lambda x:math.copysign(abs(x)**p,x)
for j in range(V+1):
 phi=-math.pi/2+j*math.pi/V
 for i in range(U):
  t=i*2*math.pi/U;verts.append((a*sg(math.cos(phi)*math.cos(t)),b*sg(math.cos(phi)*math.sin(t)),zc+c*sg(math.sin(phi))))
for j in range(V):
 for i in range(U):faces.append((j*U+i,j*U+(i+1)%U,(j+1)*U+(i+1)%U,(j+1)*U+i))
d=bpy.data.meshes.new('Head surface');d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new('Head / soft rounded cheeks',d);bpy.context.collection.objects.link(o);finish(o,o.name,skin,'Head')
def fy(x,z):return -b*max(.01,1-(abs(x)/a)**n-(abs((z-zc)/c))**n)**(1/n)
for s in [-1,1]:
 uv('Ear',(s*.65,.015,2.69),(.14,.11,.20),skin,'Head')
 uv('Inner ear',(s*.698,-.076,2.69),(.067,.030,.11),blush,'Head')
 x=s*.235;z=2.79;y=fy(x,z)-.025
 uv('Eye',(x,y,z),(.076,.031,.117),eye,'Head')
 uv('Eye catchlight',(x-.019,y-.029,z+.043),(.016,.009,.024),white,'Head',24,16)
 curve('Eyebrow',[(s*.34,fy(s*.34,2.98)-.012,2.98),(s*.25,fy(s*.25,3.015)-.015,3.015),(s*.14,fy(s*.14,2.985)-.012,2.985)],.026,hair,'Head')
 # Subtle flattened cheek pads follow the face surface.
 # Blush is blended into head vertex colors below, without raised cheek discs.
 pass
uv('Button nose',(0,-.508,2.65),(.075,.055,.054),skin,'Head')
smile=[]
for i in range(11):
 x=-.15+i*.03;z=2.48+.043*(x/.15)**2;smile.append((x,fy(x,z)-.013,z))
curve('Smile',smile,.015,mouth,'Head')
head_obj=bpy.data.objects['Head / soft rounded cheeks']
face_skin=skin.copy();face_skin.name='Face skin / blended blush'
head_obj.data.materials.clear();head_obj.data.materials.append(face_skin)
colors=head_obj.data.color_attributes.new(name='SkinTint',type='FLOAT_COLOR',domain='POINT')
base=rgb('F3B58D');rosy=rgb('EE9F96')
for v in head_obj.data.vertices:
 x,y,z=v.co;amount=sum(math.exp(-((x-s*.36)/.13)**2-((z-2.59)/.085)**2) for s in [-1,1])*.35*max(0,min(1,(-y-.25)*5))
 colors.data[v.index].color=tuple(base[k]*(1-amount)+rosy[k]*amount for k in range(3))+(1,)
color_node=face_skin.node_tree.nodes.new('ShaderNodeVertexColor');color_node.layer_name='SkinTint'
face_skin.node_tree.links.new(color_node.outputs['Color'],face_skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
# Hair fringe peeks from beneath the cuff, with tapered sculptural locks.
for k,(x0,x1,x2,x3) in enumerate([(-.48,-.39,-.28,-.18),(-.25,-.16,-.02,.08),(.00,.13,.24,.32)]):
 pts=[]
 for x,z in [(x0,3.23),(x1,3.15),(x2,3.065),(x3,3.07)]:pts.append((x,fy(x,z)-.025,z))
 o=loft('Sculpted swept fringe '+str(k),pts,[.07,.115,.085,.003],hair,flatten=.48);weights[o.name]='Head'
# Knitted beanie dome and folded cuff.
def cap(name,rings,material):
 vs=[];fs=[];N=64
 for z,r in rings:
  for i in range(N):t=i*2*math.pi/N;vs.append((r*math.cos(t),r*.79*math.sin(t)+.025,z))
 for j in range(len(rings)-1):
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 fs.append(tuple(reversed(range(N))));fs.append(tuple((len(rings)-1)*N+i for i in range(N)))
 d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);finish(o,name,material,'Head');sub=o.modifiers.new('Soft knit silhouette','SUBSURF');sub.levels=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
cap('Beanie dome',[(3.15,.64),(3.23,.66),(3.40,.62),(3.55,.49),(3.64,.26),(3.66,.035)],hat)
cap('Folded beanie cuff',[(3.09,.642),(3.10,.68),(3.17,.689),(3.25,.676),(3.26,.64)],cuff)
# Rib channels along the folded brim, subtle and geometric for glTF.
for i in range(64):
 t=i*2*math.pi/64;x=.683*math.cos(t);y=.683*.79*math.sin(t)+.025
 curve('Knit rib',[(x,y,3.115),(x*1.004,y,3.20),(x*.99,y,3.245)],.0035,hat,'Head')
box('Beanie badge',(.40,-.45,3.18),(.18,.035,.10),.018,navy,'Head')
for i in range(3):box('Badge light',(.35+i*.045,-.473,3.18),(.028,.010,.026),.004,cyan,'Head')
# Headphone headband and earcups.
arch=[(-.73,.065,2.99),(-.72,.065,3.35),(-.45,.065,3.66),(0,.065,3.745),(.45,.065,3.66),(.72,.065,3.35),(.73,.065,2.99)]
curve('Headphone headband',arch,.049,navy,'Head');curve('Headband accent',[(x,y-.033,z+.012) for x,y,z in arch],.012,pads,'Head')
for s in [-1,1]:
 uv('Headphone cushion',(s*.70,.015,2.96),(.090,.17,.22),pads,'Head')
 uv('Ear cup shell',(s*.78,.015,2.96),(.065,.15,.19),navy,'Head')
 ring=[(s*.839,.015+.115*math.cos(i*2*math.pi/40),2.96+.15*math.sin(i*2*math.pi/40)) for i in range(41)]
 curve('Ear cup LED ring',ring,.015,cyan if s<0 else pink,'Head')
# Companion: actual low-poly fur geometry, not an image billboard.
orbmat=[mat('Fur '+str(i),h,.65) for i,h in enumerate(['6C2CAF','9242D1','B763E8','4C2480','D16DDB'])]
center=Vector((-1.13,-.02,2.62));uv('Companion core',center,(.235,.235,.235),orbmat[0],'Companion')
vs=[];fs=[];mi=[];N=1350
for i in range(N):
 z=1-2*(i+.5)/N;theta=i*2.39996323;v=Vector((math.sqrt(1-z*z)*math.cos(theta),math.sqrt(1-z*z)*math.sin(theta),z));base=center+v*.225
 u=v.cross(Vector((0,0,1))).normalized();w=v.cross(u).normalized();r=.004+random.random()*.002;length=.025+random.random()*.045
 start=len(vs)
 for j in range(3):vs.append(base+(math.cos(j*2*math.pi/3)*u+math.sin(j*2*math.pi/3)*w)*r)
 vs.append(base+v*length)
 for j in range(3):fs.append((start+j,start+(j+1)%3,start+3));mi.append(random.randrange(len(orbmat)))
d=bpy.data.meshes.new('Fur strands');d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new('Companion / geometric fur',d);bpy.context.collection.objects.link(o);finish(o,o.name,None,'Companion')
for m in orbmat:o.data.materials.append(m)
for poly,index in zip(o.data.polygons,mi):poly.material_index=index
for s in [-1,1]:
 pts=[]
 for i in range(9):t=i*math.pi/8;pts.append((center.x+s*.083+.043*math.cos(t),center.y-.238,center.z+.04+.045*math.sin(t)))
 curve('Companion happy eye',pts,.012,cyan,'Companion')
curve('Companion waveform',[(center.x+x,center.y-.241,center.z-.065+z) for x,z in [(-.10,0),(-.06,0),(-.035,.025),(-.012,-.025),(.008,.035),(.033,-.025),(.052,.015),(.075,0),(.10,0)]],.008,cyan,'Companion')
# Add armature modifiers; rigid accessories also follow their named bone.
for o in objects:
 if o.type!='MESH':continue
 if o.name in weights:
  vg=o.vertex_groups.new(name=weights[o.name]);vg.add(list(range(len(o.data.vertices))),1,'REPLACE')
 mod=o.modifiers.new('Timothy skin','ARMATURE');mod.object=rig;o.parent=rig
rig['asset_note']='Procedurally modeled 3D interpretation of the supplied Timothy reference. Continuous weighted sleeve/leg meshes.'
rig['front_axis']='-Y';rig['up_axis']='Z';rig['units']='meters / stylized display scale'
# Actions: one common skeleton. No disconnected cutout parts.
for pb in rig.pose.bones:pb.rotation_mode='XYZ'
def reset():
 for pb in rig.pose.bones:pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
def rotate_world(name,axis,angle):
 pb=rig.pose.bones[name];local_axis=pb.bone.matrix_local.to_3x3().inverted()@Vector(axis)
 pb.rotation_euler=Quaternion(local_axis.normalized(),angle).to_euler('XYZ')
def keys(frame):
 for pb in rig.pose.bones:
  pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name);pb.keyframe_insert(data_path='location',frame=frame,group=pb.name)
def action(name):
 rig.animation_data_create();rig.animation_data.action=None
 a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a
 return a
for name in ['Idle','Run','Wave','Jump','Celebrate']:
 act=action(name);reset();end=60 if name=='Idle' else 30 if name=='Run' else 60
 for frame in range(1,end+2,2):
  t=(frame-1)/end;phase=t*2*math.pi;reset()
  if name=='Idle':rig.pose.bones['Chest'].rotation_euler[0]=.014*math.sin(phase);rig.pose.bones['Companion'].location.y=.045*math.sin(phase)
  elif name=='Run':
   q=math.sin(phase);rig.pose.bones['Root'].location.z=.04*abs(math.cos(phase))
   for s,label in [(-1,'L'),(1,'R')]:
    p=q*s;rotate_world('Thigh.'+label,(1,0,0),p*.60);rotate_world('Shin.'+label,(1,0,0),.12+max(0,p)*.8)
    rotate_world('UpperArm.'+label,(1,0,0),-p*.45);rotate_world('Forearm.'+label,(1,0,0),-.55)
  elif name=='Wave':
   w=min(1,t*5);rotate_world('UpperArm.L',(0,1,0),1.6*w);rotate_world('Forearm.L',(0,1,0),.25*w);rotate_world('Hand.L',(0,0,1),.25*math.sin(phase*3)*w)
  elif name=='Jump':
   j=math.sin(math.pi*t);rig.pose.bones['Root'].location.z=.52*j
   for s,label in [(-1,'L'),(1,'R')]:rotate_world('UpperArm.'+label,(0,1,0),-s*1.2*j);rotate_world('Thigh.'+label,(1,0,0),-.3*j);rotate_world('Shin.'+label,(1,0,0),.7*j)
  else:
   for s,label in [(-1,'L'),(1,'R')]:rotate_world('UpperArm.'+label,(0,1,0),-s*1.5);rotate_world('Forearm.'+label,(1,0,0),-.4+.1*math.sin(phase*2))
   rig.pose.bones['Root'].location.z=.07*abs(math.sin(phase*2))
  keys(frame)
 # Hold exact loop/landing endpoints.
 scene.frame_set(1);keys(end+1)
 rig.animation_data.action=None
 track=rig.animation_data.nla_tracks.new();track.name=name;strip=track.strips.new(name,1,act);strip.action_frame_end=end+1;track.mute=True
reset();rig.animation_data.action=None;scene.frame_set(0);reset();bpy.context.view_layer.update()
# Studio setup kept outside GLB export.
world=bpy.data.worlds.new('Lavender studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.65,.78,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
floor=mat('Studio floor','EAE7F2',.85)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));ground=bpy.context.object;ground.name='STUDIO / ground';ground.data.materials.append(floor)
def light(name,pos,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
light('Large softbox',(-3,-4,6),600,4,(1,.88,.78));light('Cool fill',(4,-2,4),350,3,(.72,.80,1));light('Violet rim',(2,3,5),650,3,(.80,.71,1))
bpy.ops.object.camera_add(location=(4,-7,3.65));cam=bpy.context.object;cam.name='STUDIO / camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=4.95
look=Vector((-.12,0,1.84));cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler()
# Export only real character geometry and skeleton, excluding the studio.
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'timothy.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_materials='EXPORT',export_extras=True)
rig.animation_data.action=None
for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(0);reset();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'timothy.blend'))
info={'mesh_objects':len(objects),'vertices':sum(len(o.data.vertices) for o in objects if o.type=='MESH'),'bones':len(rig.data.bones),'actions':[a.name for a in bpy.data.actions], 'glb_bytes':(OUT/'timothy.glb').stat().st_size}
(OUT/'model-info.json').write_text(json.dumps(info,indent=2));print('MODEL_INFO',json.dumps(info),flush=True)
for name,pos in [('front',(0,-8,3.3)),('three-quarter',(4,-7,3.65)),('back',(-4,7,3.65))]:
 cam.location=pos;cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)
cam.location=(4,-7,3.65);cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'timothy.blend'))
