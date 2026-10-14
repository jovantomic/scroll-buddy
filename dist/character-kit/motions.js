/** Pure motion functions: seconds in, pose out. No DOM, subscription, model or network. */
const tau=Math.PI*2;
export const motionNames=['idle','run','walk','wave','jump','point','dance'];
export function poseAt(name,seconds=0){
 const p={};const phase=seconds*tau,s=Math.sin(phase),c=Math.cos(phase);
 if(name==='run'||name==='walk'){
  const run=name==='run',stride=run?24:14;
  p['leg-left']=s*stride;p['leg-right']=-s*stride;
  p['knee-left']=Math.max(0,-s)*(run?38:18);p['knee-right']=-Math.max(0,s)*(run?38:18);
  p['ankle-left']=-p['leg-left']*.35;p['ankle-right']=-p['leg-right']*.35;
  p['arm-left']=-s*(run?18:12);p['arm-right']=s*(run?18:12);
  p['elbow-left']=run?-65-s*20:-20-s*8;p['elbow-right']=run?65-s*20:20-s*8;
  p.body=run?-5:-2;p.head=run?4:2;p.y=-Math.abs(c)*(run?10:3);
 }else if(name==='wave'){
  p.handOpen=true;
  p['arm-right']=-145;p['elbow-right']=-15+s*22;p['wrist-right']=s*12;p.head=-5;p.body=-3;
 }else if(name==='jump'){
  // Single jump, duration 1 second. Clamp rather than accidentally restarting.
  const t=Math.min(1,Math.max(0,seconds));const lift=Math.sin(t*Math.PI);
  p.y=-lift*72;p['leg-left']=-lift*16;p['leg-right']=lift*16;
  p['knee-left']=lift*28;p['knee-right']=-lift*28;
  p['arm-left']=lift*110;p['arm-right']=-lift*110;p.head=-lift*6;
 }else if(name==='point'){
  p['arm-right']=-78;p['elbow-right']=-8;p['wrist-right']=6;p.head=6;p.body=-2;
 }else if(name==='dance'){
  p.body=s*10;p.head=-s*12;p['arm-left']=60+c*25;p['arm-right']=-60+c*25;
  p['elbow-left']=35;p['elbow-right']=-35;p['leg-left']=s*15;p['leg-right']=-s*15;p.y=-Math.abs(c)*8;
 }else{p.y=Math.sin(phase*.35)*2;p.head=Math.sin(phase*.2)*2;}
 p.orb=Math.sin(phase*.25)*8;p.orbY=Math.sin(phase*.5)*5;
 return p;
}
