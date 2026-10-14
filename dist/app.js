/* One pinned scene. All poses and scene changes are derived from scroll progress. */
gsap.registerPlugin(ScrollTrigger);
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const lenis=new Lenis({lerp:.085,smoothWheel:!reduced});
lenis.on('scroll',ScrollTrigger.update);gsap.ticker.add(t=>lenis.raf(t*1000));gsap.ticker.lagSmoothing(0);
const canvas=document.querySelector('#buddy'),ctx=canvas.getContext('2d'),sprite=new Image();
sprite.src='assets/buddy.png';let progress=0,lastProgress=0,pose=-1,direction=1,auto=false,trigger;
const chapters=[...document.querySelectorAll('.chapter')],nav=[...document.querySelectorAll('nav button')];
const wrap=document.querySelector('.buddy-wrap'),orb=document.querySelector('.orb'),panel=document.querySelector('.panel');
function draw(frame){if(!sprite.complete||!sprite.naturalWidth)return;const cw=sprite.naturalWidth/4,ch=sprite.naturalHeight/2;ctx.clearRect(0,0,384,512);ctx.save();if(direction<0){ctx.translate(384,0);ctx.scale(-1,1)}ctx.drawImage(sprite,(frame%4)*cw,Math.floor(frame/4)*ch,cw,ch,0,0,384,512);ctx.restore();pose=frame;}
sprite.onload=()=>draw(6);
const mix=(a,b,t)=>a+(b-a)*t,clamp=t=>Math.min(1,Math.max(0,t));
function update(p){progress=p;const moving=Math.abs(p-lastProgress)>.00008;direction=p<lastProgress? -1:1;
const chapter=p<.16?0:p<.48?1:p<.78?2:3;
chapters.forEach((el,i)=>gsap.set(el,{autoAlpha:i===chapter?1:0,y:0}));nav.forEach((el,i)=>{el.classList.toggle('active',i===chapter);el.setAttribute('aria-current',i===chapter?'step':'false')});
let x=69,y=0,scale=1;
if(p<.16){x=mix(69,30,clamp(p/.16));}
else if(p<.48){let t=(p-.16)/.32;x=mix(30,73,t);y=-Math.sin(Math.PI*clamp((t-.28)/.44))*(innerWidth<700?85:130);}
else if(p<.78){x=mix(73,58,clamp((p-.48)/.13));}
else{x=mix(58,82,clamp((p-.78)/.19));scale=1-.98*clamp((p-.92)/.075);}
if(reduced){x=chapter===0?69:chapter===1?65:chapter===2?55:75;y=0;scale=1;}
gsap.set(wrap,{left:x+'%',y,scale,opacity:1});
gsap.set('.shadow',{scaleX:1+Math.abs(y)/150,opacity:1-Math.abs(y)/180});
gsap.set('.obstacle',{autoAlpha:chapter===1?1:0});gsap.set(panel,{autoAlpha:chapter===2?1:0});gsap.set('.portal',{autoAlpha:chapter===3?1:0});
gsap.set('.orbit,.label',{autoAlpha:chapter===0?1:0});gsap.set('.speech',{autoAlpha:p<.055?1:0});
gsap.set(orb,{x:chapter===2?mix(0,120,clamp((p-.56)/.12)):Math.sin(p*50)*12,y:Math.sin(p*70)*9,scale:chapter===3?1-clamp((p-.92)/.075):1});
const lit=p>.64&&p<.78;panel.classList.toggle('lit',lit);panel.querySelector('strong').textContent=lit?'Ideja je živa.':'Čekam iskru.';panel.querySelector('.panel-state').textContent=lit?'CONNECTED ✦':'SLEEP MODE';
panel.querySelectorAll('.bars i').forEach((bar,i)=>gsap.set(bar,{height:lit?8+Math.abs(Math.sin(p*110+i))*24:6}));
const frame=reduced?6:chapter===2&&p>.56?7:!moving||p<.02||p>.97?6:Math.floor(p*210)%6;draw(frame);
gsap.set('.progress>div',{scaleX:p});document.querySelector('#percentage').textContent=String(Math.round(p*100)).padStart(3,'0')+'%';lastProgress=p;
}
trigger=ScrollTrigger.create({trigger:'#journey',start:'top top',end:()=>'+='+innerHeight*4.5,pin:'#stage',anticipatePin:1,invalidateOnRefresh:true,onUpdate:self=>update(self.progress)});
update(0);
function go(p,duration=1.3){lenis.scrollTo(trigger.start+(trigger.end-trigger.start)*p,{duration,force:true});}
nav.forEach(b=>b.onclick=()=>{stopDemo();go([0,.23,.69,.84][Number(b.dataset.step)])});
document.querySelector('#start').onclick=()=>go(.23);document.querySelector('#replay').onclick=()=>{stopDemo();go(0,2)};document.querySelector('#back').onclick=()=>{stopDemo();go(0,2)};
function stopDemo(){auto=false;document.querySelector('#demo').innerHTML='Pusti demo <span>↗</span>';}
document.querySelector('#demo').onclick=()=>{if(auto){lenis.scrollTo(window.scrollY,{immediate:true,force:true});stopDemo();return}auto=true;document.querySelector('#demo').innerHTML='Zaustavi <span>Ⅱ</span>';go(0,.1);setTimeout(()=>{if(auto)lenis.scrollTo(trigger.end,{duration:18,easing:t=>t,force:true,onComplete:stopDemo})},150)};
addEventListener('wheel',stopDemo,{passive:true});addEventListener('touchstart',stopDemo,{passive:true});addEventListener('keydown',e=>{if(['ArrowDown','ArrowUp','PageDown','PageUp','Home','End',' '].includes(e.key))stopDemo()});
