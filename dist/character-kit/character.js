import {poseAt} from './motions.js?v=4';
const kitURL=new URL('./',import.meta.url);
export async function mountBuddy(container,{debug=false}={}){
 const response=await fetch(new URL('character.svg?v=4',kitURL));if(!response.ok)throw new Error('Could not load character.svg');
 const source=await response.text();const doc=new DOMParser().parseFromString(source,'image/svg+xml');
 if(doc.querySelector('parsererror'))throw new Error('Invalid character SVG');
 const svg=document.importNode(doc.documentElement,true);
 svg.querySelectorAll('image').forEach(el=>el.setAttribute('href',new URL(el.getAttribute('href'),kitURL).href));
 svg.style.cssText='width:100%;height:100%;overflow:visible;display:block';container.replaceChildren(svg);
 const joints=new Map([...svg.querySelectorAll('[data-joint]')].map(el=>[el.dataset.joint,el]));
 const images=[...svg.querySelectorAll('[data-part]')];let exploded=false,debugShown=false;
 const debugLayer=svg.querySelector('[data-debug]');
 const debugCircles=[...debugLayer.querySelectorAll('circle')],debugLabels=[...debugLayer.querySelectorAll('text')];
 function updateDebug(){
  if(!debugShown)return;const matrix=svg.getCTM();if(!matrix)return;const inverse=matrix.inverse();
  [...joints.values()].forEach((joint)=>{const i=debugLabels.findIndex(label=>label.textContent===joint.dataset.joint);if(i<0)return;const local=joint.getCTM();if(!local)return;const [x,y]=joint.dataset.pivot.split(',').map(Number);const point=new DOMPoint(x,y).matrixTransform(inverse.multiply(local));debugCircles[i].setAttribute('cx',point.x);debugCircles[i].setAttribute('cy',point.y);debugLabels[i].setAttribute('x',point.x+7);debugLabels[i].setAttribute('y',point.y);});
 }
 function setPose(pose={}){
  for(const [name,el] of joints){const [x,y]=el.dataset.pivot.split(',').map(Number);const angle=pose[name]||0;
   let translate=name==='root'?`translate(${pose.x||0} ${pose.y||0}) `:name==='orb'?`translate(${pose.orbX||0} ${pose.orbY||0}) `:'';
   el.setAttribute('transform',`${translate}rotate(${angle} ${x} ${y})`);
  }
  const open=svg.querySelector('[data-open-hand]');if(open){open.setAttribute('display',pose.handOpen?'inline':'none');svg.querySelector('[data-part="hand-right"]').setAttribute('display',pose.handOpen?'none':'inline');}
  updateDebug();
 }
 function showJoints(value){debugShown=value;debugLayer.setAttribute('display',value?'inline':'none');updateDebug();}
 function showParts(value){exploded=value;images.forEach(el=>{const n=el.dataset.part;let x=0,y=0;
  if(value){if(n.includes('left'))x=-95;if(n.includes('right'))x=95;
   if(n==='head')y=-70;if(n==='body')y=-15;
   if(n==='beanie')y=-105;if(n==='headphones'){x=100;y=-80;}
   if(n.includes('forearm'))y=35;if(n.includes('hand'))y=70;if(n.includes('shin'))y=40;if(n.includes('shoe'))y=80;
   if(n==='orb'){x=-65;y=-50;}
  }el.setAttribute('transform',`translate(${x} ${y})`);
 });}
 showJoints(debug);setPose();
 return {svg,setPose,poseAt:(name,t)=>setPose(poseAt(name,t)),showJoints,showParts,get exploded(){return exploded},destroy(){container.replaceChildren()}};
}
