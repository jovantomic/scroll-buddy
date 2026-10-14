from pathlib import Path
import base64,json,math
out=Path(__file__).parent/'dist/character-kit'
parts={
'head':([8,16,330,326],[77,22,170,168]),
'body':([125,140,1000,1014],[83,176,154,157]),
'upper-arm-left':([976,45,216,283],None),
'upper-arm-right':([687,45,219,281],None),
'forearm-left':([379,351,150,274],None),
'forearm-right':([101,351,150,274],None),
'hand-left':([686,454,160,156],None),
'hand-right':([1010,454,178,156],None),
'upper-leg-left':([66,631,189,294],None),
'upper-leg-right':([391,629,185,299],None),
'shin-left':([707,641,163,270],None),
'shin-right':([1010,641,163,270],None),
'shoe-left':([18,969,280,230],None),
'shoe-right':([347,969,266,230],None),
'orb':([595,900,386,354],[-22,105,138,126]),
'hand-right-open':([974,952,268,213],None),
}
joints={'root':[160,310],'body':[160,313],'head':[161,185],'arm-left':[114,215],'elbow-left':[91,269],'wrist-left':[87,307],'arm-right':[207,215],'elbow-right':[231,269],'wrist-right':[236,307],'leg-left':[141,316],'knee-left':[138,370],'ankle-left':[139,414],'leg-right':[183,316],'knee-right':[188,370],'ankle-right':[188,414],'orb':[52,155]}
# Both source anchor points map EXACTLY to the parent/child pivots.
anchors={
'upper-arm-left':((1128,108),(1042,258),'arm-left','elbow-left'),
'upper-arm-right':((750,108),(830,258),'arm-right','elbow-right'),
'forearm-left':((475,408),(452,569),'elbow-left','wrist-left'),
'forearm-right':((150,408),(163,569),'elbow-right','wrist-right'),
'upper-leg-left':((172,684),(146,848),'leg-left','knee-left'),
'upper-leg-right':((460,684),(511,850),'leg-right','knee-right'),
'shin-left':((782,700),(784,864),'knee-left','ankle-left'),
'shin-right':((1086,700),(1086,864),'knee-right','ankle-right'),
}
matrices={}
for name,(p,q,j,k) in anchors.items():
 u,v=joints[j],joints[k];dx,dy=q[0]-p[0],q[1]-p[1];vx,vy=v[0]-u[0],v[1]-u[1];den=dx*dx+dy*dy
 a=(vx*dx+vy*dy)/den;b=(vy*dx-vx*dy)/den
 matrices[name]=[a,b,-b,a,u[0]-a*p[0]+b*p[1],u[1]-b*p[0]-a*p[1]]
for n,source,target,scale in [
 ('shoe-left',(190,1008),'ankle-left',.24),('shoe-right',(455,1008),'ankle-right',.24),
 ('hand-left',(782,462),'wrist-left',.20),('hand-right',(1097,468),'wrist-right',.20),
 ('hand-right-open',(1151,1143),'wrist-right',-.18)]:
 x,y=joints[target];matrices[n]=[scale,0,0,scale,x-scale*source[0],y-scale*source[1]]
bodyclip='<defs><clipPath id="torso-core"><path d="M280 140H970L965 350L990 680L1040 975L970 1150H280L214 975L258 680L280 350Z"/></clipPath></defs>'
regions={}
for n,(bounds,target) in parts.items():
 src='torso.png' if n=='body' else 'closed-atlas.png'
 embedded='data:image/png;base64,'+base64.b64encode((out/src).read_bytes()).decode()
 clip=bodyclip if n=='body' else '';attr=' clip-path="url(#torso-core)"' if n=='body' else ''
 box=' '.join(map(str,bounds))
 (out/'raster-parts'/f'{n}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}" role="img" aria-label="{n}">{clip}<image href="{embedded}" width="1254" height="1254"{attr}/></svg>')
 regions[n]={'bounds':bounds,'placement':target,'file':src,'matrix':matrices.get(n)}
def art(n):
 b,t=parts[n];src=regions[n]['file'];clip=bodyclip if n=='body' else '';attr=' clip-path="url(#torso-core)"' if n=='body' else ''
 if t:
  x,y,w,h=t;matrix=''
 else:
  x,y,w,h=b;matrix='matrix('+ ' '.join(f'{v:.9f}' for v in matrices[n])+')'
 svg=f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="'+ ' '.join(map(str,b)) +f'" overflow="hidden">{clip}<image href="{src}" width="1254" height="1254"{attr}/></svg>'
 if matrix:svg=f'<g transform="{matrix}">{svg}</g>'
 return f'<g data-part="{n}">{svg}</g>'
def group(n,c):
 x,y=joints[n];return f'<g data-joint="{n}" data-pivot="{x},{y}">{c}</g>'
def limb(side,kind):
 if kind=='arm':
  hand=art(f'hand-{side}')
  if side=='right':hand+='<g data-open-hand="true" display="none">'+art('hand-right-open')+'</g>'
  # Child end caps overlap parent ends, both anchored to the same joint center.
  return group(f'arm-{side}',art(f'upper-arm-{side}')+group(f'elbow-{side}',art(f'forearm-{side}')+group(f'wrist-{side}',hand)))
 return group(f'leg-{side}',art(f'upper-leg-{side}')+group(f'knee-{side}',art(f'shin-{side}')+group(f'ankle-{side}',art(f'shoe-{side}'))))
inner=limb('left','leg')+limb('right','leg')+group('body',art('body')+limb('left','arm')+limb('right','arm')+group('head',art('head')))
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 480" role="img" aria-label="Rendered purple buddy character">'+group('root',inner)+group('orb',art('orb'))+'<g data-debug="joints" display="none">'+''.join(f'<circle cx="{x}" cy="{y}" r="3" fill="#ff506e"/><text x="{x+7}" y="{y}" font-size="7" fill="#342848">{n}</text>' for n,(x,y) in joints.items())+'</g></svg>'
(out/'character.svg').write_text(svg)
(out/'manifest.json').write_text(json.dumps({'format':'raster-puppet-v4','viewBox':[0,0,320,480],'parts':list(parts),'partsDirectory':'raster-parts','joints':joints,'regions':regions,'sourceAnchors':anchors,'artwork':'Closed fabric ends with calibrated source-to-joint transforms and overlapping child layers.'},indent=2))
for n,(p,q,j,k) in anchors.items():
 a,b,c,d,e,f=matrices[n]
 for s,t in [(p,joints[j]),(q,joints[k])]:assert math.dist([a*s[0]+c*s[1]+e,b*s[0]+d*s[1]+f],t)<1e-7
print('Eight limb segments calibrated: both endpoints map to joint centers.')
