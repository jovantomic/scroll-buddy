import {mountBuddy} from './character.js?v=4';
import {motionNames,poseAt} from './motions.js?v=4';
try{
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const buddy=await mountBuddy(document.querySelector('#puppet'));
 let motion='idle',paused=reduced,elapsed=0,speed=1,last=performance.now();
 const controls=document.querySelector('#motions');
 for(const name of motionNames){const b=document.createElement('button');b.textContent=name;b.dataset.motion=name;b.classList.toggle('active',name===motion);b.setAttribute('aria-pressed',String(name===motion));b.onclick=()=>{
  motion=name;elapsed=0;paused=false;sync();};controls.append(b);}
 function sync(){controls.querySelectorAll('button').forEach(b=>{const active=b.dataset.motion===motion;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});document.querySelector('#mode').textContent=motion.toUpperCase()+' / LIVE RIG';document.querySelector('#pause').textContent=paused?'Play ▷':'Pause Ⅱ';}
 document.querySelector('#pause').onclick=()=>{paused=!paused;sync()};
 document.querySelector('#speed').oninput=e=>{speed=Number(e.target.value);document.querySelector('#speed-value').textContent=speed.toFixed(1)+'×'};
 document.querySelector('#frame').oninput=e=>{elapsed=Number(e.target.value);paused=true;buddy.poseAt(motion,elapsed);document.querySelector('#frame-value').textContent=elapsed.toFixed(2)+'s';sync()};
 document.querySelector('#joints').onchange=e=>buddy.showJoints(e.target.checked);
 document.querySelector('#explode').onchange=e=>{buddy.showParts(e.target.checked);document.querySelector('#puppet').classList.toggle('exploded',e.target.checked)};
 function tick(now){const dt=Math.min(.05,(now-last)/1000);last=now;if(!paused)elapsed+=dt*speed;
  buddy.poseAt(buddy.exploded?'idle':motion,elapsed);const phase=motion==='jump'?Math.min(1,elapsed):elapsed%1;document.querySelector('#frame').value=phase;document.querySelector('#frame-value').textContent=phase.toFixed(2)+'s';if(motion==='jump'&&elapsed>=1&&!paused){paused=true;sync()};requestAnimationFrame(tick);}
 requestAnimationFrame(tick);sync();
 const manifest=await fetch('manifest.json').then(r=>r.json());const gallery=document.querySelector('#gallery');
 for(const name of manifest.parts){const a=document.createElement('a');a.className='part';a.href=`${manifest.partsDirectory||'parts'}/${name}.svg`;a.download=`${name}.svg`;const region=manifest.regions[name];const img=document.createElementNS('http://www.w3.org/2000/svg','svg');img.setAttribute('viewBox',region.bounds.join(' '));img.setAttribute('role','img');img.setAttribute('aria-label',name.replaceAll('-',' '));const bitmap=document.createElementNS('http://www.w3.org/2000/svg','image');bitmap.setAttribute('href',new URL(region.file,import.meta.url).href);bitmap.setAttribute('width','1254');bitmap.setAttribute('height','1254');img.append(bitmap);const text=document.createElement('span');text.textContent=name; a.append(img,text);gallery.append(a);}
 const scrollBuddy=await mountBuddy(document.querySelector('#scroll-puppet'));
 gsap.registerPlugin(ScrollTrigger);const lenis=new Lenis({lerp:.09,smoothWheel:!reduced});lenis.on('scroll',ScrollTrigger.update);gsap.ticker.add(t=>lenis.raf(t*1000));gsap.ticker.lagSmoothing(0);
 const clock={p:0};const title=document.querySelector('.scroll-title');
 const timeline=gsap.timeline({scrollTrigger:{trigger:'#scroll-demo',start:'top top',end:()=>'+='+innerHeight*2.7,pin:'.scroll-stage',scrub:reduced?true:.5,invalidateOnRefresh:true},onUpdate(){
  const p=clock.p;const pose=reduced?{}:p<.52?poseAt('run',p*9):p<.72?poseAt('jump',(p-.52)/.2):poseAt('wave',(p-.72)*4);
  scrollBuddy.setPose(pose);gsap.set('#scroll-puppet',{left:(15+p*65)+'%'});gsap.set('.scroll-progress i',{scaleX:p});title.textContent=p<.52?'Your scroll. His next move.':p<.72?'A little leap of imagination.':'Hello from the other side.';
 }});timeline.to(clock,{p:1,duration:1,ease:'none'});
 addEventListener('pagehide',()=>{timeline.scrollTrigger.kill();timeline.kill();lenis.destroy();},{once:true});
}catch(error){const el=document.querySelector('#error');el.style.display='block';el.textContent='Could not load the kit. Please serve this folder using a local HTTP server. '+error.message;console.error(error);}
