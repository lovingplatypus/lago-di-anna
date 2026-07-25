import base64, json, pathlib

def b64(p, mime='png'):
    return f'data:image/{mime};base64,' + base64.b64encode(pathlib.Path('assets/'+p).read_bytes()).decode()

assets = {
    'map': b64('map.png'),
    'anna': b64('anna.png'),
    'dogW': b64('dog_white_run.png'),
    'dogB': b64('dog_black_run.png'),
    'dogWs': b64('dog_white_sit.png'),
    'dogBs': b64('dog_black_sit.png'),
    'platypus': b64('platypus.png'),
    'boat': b64('boat.png'),
    'cat': b64('cat.png'),
    'plushy': b64('plushy.png'),
    'fluffBg': b64('fluff_bg.webp', 'webp'),
    'famBg': b64('famtree_bg.webp', 'webp'),
    'dogBgYard': b64('dog_bg_yard.webp', 'webp'),
    'dogBgRoom': b64('dog_bg_room.webp', 'webp'),
    'dogBgPond': b64('dog_bg_pond.webp', 'webp'),
    'sqLove': b64('squirrels_love.png'),
    'fruitLetter': b64('fruitstand_letter.png'),
    'splashBg': b64('splash_bg.png'),
}

# Family-tree cat photos: drop assets/cat_<name>.png (or .jpg/.jpeg/.webp)
# and rebuild — the game uses the photo automatically instead of the
# placeholder card.
for name in ['malva', 'lola', 'sergei', 'naomi', 'funtik']:
    for ext, mime in (('png','png'), ('jpg','jpeg'), ('jpeg','jpeg'), ('webp','webp')):
        p = pathlib.Path(f'assets/cat_{name}.{ext}')
        if p.exists():
            assets['cat_'+name] = b64(p.name, mime)
            break

js_assets = ',\n'.join(f'  {k}: "{v}"' for k, v in assets.items())

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Lago di Anna</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body { width:100%; height:100%; overflow:hidden; background:#2a2320; font-family:'Courier New',monospace; }
  #game { position:fixed; inset:0; image-rendering:pixelated; image-rendering:crisp-edges; touch-action:none; }

  #splash { position:fixed; inset:0; background:#0b1022 center/cover no-repeat; display:flex; flex-direction:column;
    align-items:center; justify-content:center; z-index:50; transition:opacity .8s; color:#f3e6c8; text-align:center; padding:20px; }
  #splash .splashcard { background:rgba(14,12,26,.6); border:2px solid rgba(201,161,90,.5); border-radius:14px;
    padding:26px 24px 30px; max-width:452px; width:100%; backdrop-filter:blur(2px); -webkit-backdrop-filter:blur(2px);
    box-shadow:0 16px 44px rgba(0,0,0,.55); }
  #splash h1 { font-size:clamp(32px,7.5vw,58px); letter-spacing:3px; text-shadow:3px 3px 0 #7a4a2e; }
  #splash .sub { margin-top:12px; font-size:clamp(13px,3.4vw,17px); opacity:.9; }
  #splash .howto { list-style:none; text-align:left; margin:22px auto 0; max-width:352px;
    font-size:clamp(13px,3.3vw,15px); line-height:1.5; }
  #splash .howto li { margin:9px 0; }
  #splash .howto b { color:#f3d79a; }
  #splash .ctrl { margin-top:16px; font-size:clamp(11px,2.8vw,13px); opacity:.7; }
  #splash .go { display:inline-block; margin-top:24px; font-size:clamp(14px,3.5vw,17px); border:2px solid #f3e6c8; padding:11px 26px;
    border-radius:4px; animation:pulse 1.6s infinite; }
  @keyframes pulse { 50% { opacity:.45; } }
  #splash.hidden { opacity:0; pointer-events:none; }

  #prompt { position:fixed; left:50%; bottom:110px; transform:translateX(-50%); background:rgba(42,35,32,.92);
    color:#f3e6c8; border:2px solid #c9a15a; border-radius:6px; padding:9px 16px; font-size:15px;
    z-index:20; display:none; white-space:nowrap; max-width:92vw; overflow:hidden; text-overflow:ellipsis; }

  #hud { position:fixed; top:12px; left:12px; z-index:20; background:rgba(42,35,32,.75); border:2px solid #c9a15a;
    border-radius:8px; padding:6px 10px; font-size:18px; letter-spacing:6px; color:#f3e6c8; display:none; }
  #hud span { opacity:.3; } #hud span.done { opacity:1; }

  #modal { position:fixed; inset:0; background:rgba(20,16,14,.72); z-index:40; display:none;
    align-items:center; justify-content:center; padding:20px; }
  #modal .card { background:#f7ecd7; border:4px solid #7a4a2e; border-radius:10px; max-width:420px; width:100%;
    padding:26px 24px; text-align:center; color:#3d2f23; box-shadow:0 10px 0 rgba(0,0,0,.35); }
  #modal .card .em { font-size:44px; }
  #modal .card img { width:110px; image-rendering:pixelated; margin-bottom:6px; }
  #modal .card h2 { margin:8px 0 10px; font-size:22px; }
  #modal .card p { font-size:15px; line-height:1.5; white-space:pre-line; }
  #modal .card button { margin-top:18px; font-family:inherit; font-size:15px; background:#c96f5a; color:#fff;
    border:none; border-radius:6px; padding:10px 22px; cursor:pointer; box-shadow:0 3px 0 #8a4436; margin-inline:5px; }
  #modal .card button.alt { background:#8a9a5b; box-shadow:0 3px 0 #5c6b3a; }
  #modal .card button:active { transform:translateY(2px); box-shadow:none; }

  /* game overlay */
  #gover { position:fixed; inset:0; z-index:45; display:none; background:#241d18; flex-direction:column; }
  #gbar, #ebar { display:flex; align-items:center; justify-content:space-between; padding:10px 14px;
    color:#f3e6c8; background:rgba(0,0,0,.25); }
  #gtitle { font-size:17px; letter-spacing:1px; }
  #gquit, #equit { font-family:inherit; font-size:15px; background:#5a4736; color:#f3e6c8; border:2px solid #c9a15a;
    border-radius:6px; padding:6px 14px; cursor:pointer; }

  /* standalone games embedded whole in an iframe (creek, ranunculus) */
  #embed { position:fixed; inset:0; z-index:46; display:none; flex-direction:column; background:#0d3b3e; }
  #ebar { background:rgba(0,0,0,.4); font-size:17px; letter-spacing:1px; }
  #embedFrame { flex:1; width:100%; border:0; }
  #gcvs { flex:1; width:100%; touch-action:none; image-rendering:pixelated; }
  #gmsg { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); background:#f7ecd7;
    border:4px solid #7a4a2e; border-radius:10px; max-width:430px; width:88%; padding:24px 22px; text-align:center;
    color:#3d2f23; display:none; z-index:5; }
  #gmsg h3 { margin-bottom:10px; font-size:20px; }
  #gmsg p { font-size:15px; line-height:1.55; white-space:pre-line; }
  #gmsg button { margin-top:16px; font-family:inherit; font-size:15px; background:#c96f5a; color:#fff; border:none;
    border-radius:6px; padding:10px 22px; cursor:pointer; box-shadow:0 3px 0 #8a4436; }

  /* fruit-stall letter (unlocked once every game is done) */
  #fletter { position:fixed; inset:0; z-index:49; display:none; align-items:center; justify-content:center;
    background:rgba(20,16,14,.88); padding:18px; }
  #fletter .fpaper { background:#f2e5c6; border:4px solid #6e4326; border-radius:8px; max-width:560px; width:100%;
    max-height:90vh; overflow-y:auto; color:#3d2f23; box-shadow:0 12px 0 rgba(0,0,0,.45); }
  #fletter .fbanner { display:block; width:100%; image-rendering:pixelated; border-bottom:3px solid #6e4326; }
  #fletter .ftext { padding:26px 26px 8px; }
  #fletter .ftext p { font-size:15px; line-height:1.72; margin-bottom:14px; }
  #fletter .ftext .greet { font-size:19px; font-weight:bold; margin-bottom:16px; }
  #fletter .ftext .sig { margin-top:22px; font-style:italic; line-height:1.5; }
  #fletter .ftext .sig-name { font-style:italic; font-size:19px; margin-top:2px; margin-bottom:4px; }
  #fletter button { display:block; margin:6px auto 22px; font-family:inherit; font-size:15px; background:#c96f5a;
    color:#fff; border:none; border-radius:6px; padding:10px 24px; cursor:pointer; box-shadow:0 3px 0 #8a4436; }
  #fletter button:active { transform:translateY(2px); box-shadow:none; }

  #stick { position:fixed; left:22px; bottom:22px; width:118px; height:118px; border-radius:50%;
    background:rgba(243,230,200,.14); border:2px solid rgba(243,230,200,.35); z-index:30; display:none; }
  #knob { position:absolute; left:50%; top:50%; width:52px; height:52px; border-radius:50%;
    background:rgba(243,230,200,.55); transform:translate(-50%,-50%); }
  #actbtn { position:fixed; right:26px; bottom:34px; width:86px; height:86px; border-radius:50%;
    background:rgba(201,111,90,.85); border:3px solid rgba(243,230,200,.6); color:#fff; font-size:30px;
    z-index:30; display:none; align-items:center; justify-content:center; user-select:none; }
  .touch #stick, .touch #actbtn { display:flex; }
  @media (hover:hover) and (pointer:fine) { .touch #stick, .touch #actbtn { display:none; } }
</style>
</head>
<body>
<canvas id="game"></canvas>

<div id="splash">
  <div class="splashcard">
  <h1>Lago di Anna</h1>
  <p class="sub">un piccolo mondo sul Lago di Como</p>
  <ul class="howto">
    <li>Explore the lake — a little sign marks each game.</li>
    <li>Play <b>every game at least once</b> (the icons up top fill in as you go).</li>
    <li>Then visit the <b>fruit stall</b> — a letter is waiting there for you.</li>
  </ul>
  <div class="ctrl">move with the arrow keys / WASD — or the on-screen stick on mobile</div>
  <div class="go">tap to begin</div>
  </div>
</div>

<div id="prompt"></div>
<div id="hud"><span id="h-fam">🐈</span><span id="h-gar">🌸</span><span id="h-dog">🐾</span><span id="h-squ">🐿️</span></div>

<div id="modal"><div class="card">
  <div class="em" id="m-em"></div>
  <img id="m-img" style="display:none">
  <h2 id="m-title"></h2>
  <p id="m-text"></p>
  <div>
    <button id="m-alt" class="alt" style="display:none"></button>
    <button id="m-close">back to the lake</button>
  </div>
</div></div>

<div id="gover">
  <div id="gbar"><span id="gtitle"></span><button id="gquit">leave</button></div>
  <canvas id="gcvs"></canvas>
  <div id="gmsg"></div>
</div>

<div id="embed">
  <div id="ebar"><span id="etitle"></span><button id="equit">back to the lake</button></div>
  <iframe id="embedFrame" title="mini game"></iframe>
</div>

<div id="fletter"><div class="fpaper">
  <img id="fletter-img" class="fbanner" alt="A letter waiting at the fruit stall, on aged paper among lychee and mangosteen">
  <div class="ftext">
    <p class="greet">Анна,</p>
    <p>Thank you for taking the time to play through these little games I made just for you. I know they may not be the most polished games in the world, and I’m sorry I couldn’t make them much nicer. I’m not exactly a game developer after all, but I hope the thought and effort behind them still came through.</p>
    <p>This all started as just the little platypus game. At first, I thought it would simply be something lighthearted and cute for you to play. But as I kept getting to know you better, and as our conversations continued, it no longer felt right to leave it at only that. Every new thing you told me about yourself gave me another idea, another detail I wanted to include.</p>
    <p>I wanted it to feel like more than a collection of random games or pages. I wanted it to feel personal. Something that could only have been made for you. Even the smallest details were included because they reminded me of something you said, something you liked, or a conversation we shared.</p>
    <p>Я знаю, що ми знайомі не так уже й довго, але мені все одно здається, що ти вже дала мені так багато причин цінувати тебе. Що більше я про тебе дізнаюся, то цікавіше мені стає. Я хочу знати, що робить тебе щасливою, що тебе дратує, про що ти мрієш, які в тебе є звички, яких ти можливо сама навіть не помічаєш. Мені хочеться поступово відкривати всі ті дрібниці, з яких складаєшся саме ти.</p>
    <p>As time goes by, I plan to keep learning more about you, both the strengths and the flaws (which I doubt you have), so I can understand you better and like you that much more. I do not expect you to be perfect, and I would never want you to feel as though you have to be. I simply want to know the real you, and to keep discovering all the things that make you special to me.</p>
    <p>Even with all the distance between us, making this website made me feel a little closer to you. It gave me a place to put all the thoughts and affection that I could not hand to you in person. I wish I could be there to see your reaction while you go through everything, but for now, I hope this can serve as a small reminder that someone far away was thinking about you, listening to you, and putting care into making something that would make you smile.</p>
    <p>And who knows, maybe someday down the line I will come back to this website and add even more: new memories, new jokes, new games, and new parts of your life that I have yet to learn about.</p>
    <p>For now, I hope you enjoyed what I’ve made for you. It may not be perfect, but it was made with more excitement than I would probably like to admit.</p>
    <p class="sig">З ніжністю,<br>З теплом,<br>Looking ahead at our future with anticipation,</p>
    <p class="sig-name">Дмитро</p>
  </div>
  <button id="fl-close">close</button>
</div></div>

<div id="stick"><div id="knob"></div></div>
<div id="actbtn">&#9733;</div>

<script>
const ASSETS = {
__ASSETS__
};
const CREEK_HTML = __CREEK__;
const RANUNCULUS_HTML = __RANUNCULUS__;

const MAPW = 1369, MAPH = 1149;

/* ---------- geometry ---------- */
const lakePoly = [[470,800],[700,785],[880,830],[1000,880],[1120,940],[1185,1010],
  [1205,1149],[150,1149],[105,1040],[140,975],[205,915],[300,860],[385,822]];
const dockRect = [215,895,390,1035];
const solids = [
  [0,0,865,318],[975,120,1210,300],[885,70,995,235],[1205,95,1340,265],
  [15,370,400,705],[1005,395,1360,845],
];
function inRect(x,y,r){ return x>=r[0]&&x<=r[2]&&y>=r[1]&&y<=r[3]; }
function inPoly(x,y,p){
  let inside=false;
  for(let i=0,j=p.length-1;i<p.length;j=i++){
    const xi=p[i][0],yi=p[i][1],xj=p[j][0],yj=p[j][1];
    if(((yi>y)!==(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi)+xi)) inside=!inside;
  }
  return inside;
}
function walkable(x,y){
  if(x<15||x>MAPW-15||y<40||y>MAPH-12) return false;
  if(inRect(x,y,dockRect)) return true;
  if(inPoly(x,y,lakePoly)) return false;
  for(const s of solids) if(inRect(x,y,s)) return false;
  return true;
}
function waterOK(x,y){ return inPoly(x,y,lakePoly) && !inRect(x,y,dockRect); }

/* ---------- progress ---------- */
const progress = { family:false, garden:false, dogs:false, squirrel:false };
function allDone(){ return progress.family && progress.garden && progress.dogs && progress.squirrel; }
function refreshHud(){
  document.getElementById('hud').style.display = 'block';
  document.getElementById('h-fam').className = progress.family ? 'done':'';
  document.getElementById('h-gar').className = progress.garden ? 'done':'';
  document.getElementById('h-dog').className = progress.dogs ? 'done':'';
  document.getElementById('h-squ').className = progress.squirrel ? 'done':'';
}

/* ---------- zones ---------- */
const zones = [
  {id:'house', r:[40,300,215,385],  name:"Anna's House"},
  {id:'garden',r:[55,690,400,790],  name:"Ranunculus Garden"},
  {id:'stall', r:[975,295,1215,395],name:"Fruit Stall"},
  {id:'oak',   r:[1090,835,1330,935],name:"The Old Oak"},
  {id:'dock',  r:[225,930,405,1050],name:"Platypus Creek"},
];
const catZone = [320,300,500,395];

/* waypoint signs drawn on the map so the games are findable from afar;
   x,y is the tip of the sign's pointer (map pixels) */
const waypoints = [
  {x:410,  y:158, label:'family tree',    done:()=>progress.family},
  {x:228,  y:682, label:'ranunculus',     done:()=>progress.garden},
  {x:1210, y:827, label:'squirrel fluff', done:()=>progress.squirrel},
  {x:315,  y:922, label:'platypus creek', done:()=>false},
  {x:1095, y:287, label:'fruit stall',    done:()=>false, stall:true},
];

/* ---------- setup ---------- */
const cvs = document.getElementById('game');
const ctx = cvs.getContext('2d');
const imgs = {};
let loaded = 0; const keys = Object.keys(ASSETS);
keys.forEach(k => { imgs[k]=new Image(); imgs[k].onload=()=>loaded++; imgs[k].src=ASSETS[k]; });

let vw, vh;
function resize(){
  vw = innerWidth; vh = innerHeight;
  cvs.width = vw * devicePixelRatio; cvs.height = vh * devicePixelRatio;
  cvs.style.width = vw+'px'; cvs.style.height = vh+'px';
}
addEventListener('resize', resize); resize();

/* ---------- input ---------- */
const input = {x:0, y:0, act:false};
const kd = {};
addEventListener('keydown', e=>{ kd[e.key.toLowerCase()]=true;
  if([' ','enter','e'].includes(e.key.toLowerCase())) { input.act=true; e.preventDefault(); }
  if(e.key.startsWith('Arrow')) e.preventDefault(); });
addEventListener('keyup',   e=>{ kd[e.key.toLowerCase()]=false; });

const stick=document.getElementById('stick'), knob=document.getElementById('knob');
let stickId=null, stickCx=0, stickCy=0;
function setKnob(dx,dy){ knob.style.transform=`translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`; }
addEventListener('touchstart', e=>{
  document.body.classList.add('touch');
  if(activeGame || modalOpen) return;
  for(const t of e.changedTouches){
    if(t.clientX < innerWidth*0.5 && t.clientY > innerHeight*0.45 && stickId===null){
      stickId=t.identifier;
      const r=stick.getBoundingClientRect(); stickCx=r.left+r.width/2; stickCy=r.top+r.height/2;
    }
  }
},{passive:true});
addEventListener('touchmove', e=>{
  for(const t of e.changedTouches){
    if(t.identifier===stickId){
      let dx=t.clientX-stickCx, dy=t.clientY-stickCy;
      const d=Math.hypot(dx,dy), m=44;
      if(d>m){ dx=dx/d*m; dy=dy/d*m; }
      setKnob(dx,dy);
      input.x = Math.abs(dx)>7 ? dx/m : 0;
      input.y = Math.abs(dy)>7 ? dy/m : 0;
    }
  }
},{passive:true});
addEventListener('touchend', e=>{
  for(const t of e.changedTouches){
    if(t.identifier===stickId){ stickId=null; setKnob(0,0); input.x=0; input.y=0; }
  }
});
document.getElementById('actbtn').addEventListener('touchstart', e=>{ e.stopPropagation(); input.act=true; });

/* ---------- world state ---------- */
const anna = {x:650, y:520, vx:0, vy:0, flip:false, moving:false};
const SPEED = 185;

function critter(o){ return Object.assign({x:0,y:0,tx:0,ty:0,state:'pause',t:1+Math.random()*2,flip:false,angle:0}, o); }
const dogs = [
  critter({x:560,y:470, sprite:'dogW', sit:'dogWs', heading:-3*Math.PI/4, speed:95,  name:'white'}),
  critter({x:740,y:560, sprite:'dogB', sit:'dogBs', heading:-Math.PI/4,  speed:105, name:'black'}),
];
const platy = critter({x:620,y:1050, speed:38, dive:0, alpha:1});
const boat  = {x:470,y:905, moored:true, t:4, dir:1};
const cat   = {x:410, y:206, blink:0, meow:0};
const parts = [];
function heartBurst(x,y){
  for(let i=0;i<6;i++) parts.push({x:x+Math.random()*20-10, y:y-Math.random()*12,
    vx:Math.random()*44-22, vy:-28-Math.random()*36, t:1+Math.random()*0.5, txt:'♥'});
}
const ripples = [];
const mapFlowers = []; // persistent blooms added after garden completion

function pickLand(c, cx, cy, rad){
  for(let i=0;i<24;i++){
    const a=Math.random()*Math.PI*2, d=30+Math.random()*rad;
    const x=cx+Math.cos(a)*d, y=cy+Math.sin(a)*d;
    if(walkable(x,y)) { c.tx=x; c.ty=y; return true; }
  }
  return false;
}
function pickWater(c){
  for(let i=0;i<30;i++){
    const x=250+Math.random()*800, y=990+Math.random()*130;
    if(waterOK(x,y)) { c.tx=x; c.ty=y; return true; }
  }
  return false;
}

/* ---------- UI ---------- */
const promptEl = document.getElementById('prompt');
const modal = document.getElementById('modal');
let modalOpen = false, started = false, activeGame = null;

function openModal(o){
  modalOpen = true;
  document.getElementById('m-em').textContent = o.em || '';
  document.getElementById('m-em').style.display = o.em ? '' : 'none';
  const im = document.getElementById('m-img');
  im.style.display = o.img ? '' : 'none';
  if(o.img) im.src = ASSETS[o.img];
  document.getElementById('m-title').textContent = o.title;
  document.getElementById('m-text').textContent = o.text;
  const alt = document.getElementById('m-alt');
  if(o.alt){ alt.style.display=''; alt.textContent=o.alt; alt.onclick=()=>{ closeModal(); o.onAlt(); }; }
  else alt.style.display='none';
  document.getElementById('m-close').textContent = o.closeLabel || 'back to the lake';
  document.getElementById('m-close').onclick = ()=>{ closeModal(); o.onClose && o.onClose(); };
  modal.style.display = 'flex';
}
function closeModal(){ modal.style.display='none'; modalOpen=false; }
document.getElementById('m-close').onclick = closeModal;

/* ---------- standalone games embedded in an iframe ---------- */
const embedEl = document.getElementById('embed');
const embedFrame = document.getElementById('embedFrame');
let embedKey = null, onEmbedClose = null;
function openEmbed(key, title, html, bg, onClose){
  modalOpen = true;
  embedEl.style.display = 'flex';
  embedEl.style.background = bg || '#141414';
  document.getElementById('etitle').textContent = title;
  if(embedKey !== key){ embedFrame.srcdoc = html; embedKey = key; } // same key keeps its state
  onEmbedClose = onClose || null;
  setTimeout(()=>embedFrame.focus(), 60);
}
document.getElementById('equit').onclick = ()=>{
  embedEl.style.display='none'; modalOpen=false;
  const cb = onEmbedClose; onEmbedClose = null;
  cb && cb();
};
function openCreek(){ openEmbed('creek', 'Platypus Creek', CREEK_HTML, '#0d3b3e'); }

/* the ranunculus puzzle reports solved blooms via postMessage; the first
   solve completes the garden and plants the map flowers */
let gardenMsgShown = false;
function openRanunculus(){
  openEmbed('ranunculus', 'Ranunculus', RANUNCULUS_HTML, '#0e150f', ()=>{
    if(progress.garden && !gardenMsgShown){
      gardenMsgShown = true;
      openModal({title:'they bloomed',
        text:"I'm sorry I couldn't get you ranunculus flowers for your birthday.\n\nSo I made sure to have them here for you instead — a whole patch, blooming on the lake whenever you want, and they'll never wilt."});
    }
  });
}
addEventListener('message', e=>{
  if(e.data === 'ranunculus-solved' && !progress.garden){
    progress.garden = true; refreshHud();
    const cols = ['#f2a3b3','#f7c873','#f7f3f0','#f0937a'];
    if(!mapFlowers.length)
      for(let i=0;i<8;i++) mapFlowers.push({x:230+Math.random()*140, y:400+Math.random()*270, c:cols[i%4]});
  }
});
document.getElementById('splash').style.backgroundImage = 'url("'+ASSETS.splashBg+'")';
document.getElementById('splash').addEventListener('pointerdown', ()=>{
  document.getElementById('splash').classList.add('hidden'); started=true; refreshHud();
});
/* fruit-stall letter: the full note, revealed once every game is done */
document.getElementById('fletter-img').src = ASSETS.fruitLetter;
function openFruitLetter(){
  modalOpen = true;
  const fl = document.getElementById('fletter');
  fl.style.display = 'flex';
  fl.scrollTop = 0;
  const p = fl.querySelector('.fpaper'); if(p) p.scrollTop = 0;
}
document.getElementById('fl-close').onclick = ()=>{
  document.getElementById('fletter').style.display='none'; modalOpen=false;
};

/* ================= GAME OVERLAY ENGINE ================= */
const gover = document.getElementById('gover');
const gcvs = document.getElementById('gcvs');
const gctx = gcvs.getContext('2d');
const gmsg = document.getElementById('gmsg');
let GW=0, GH=0;

function sizeGame(){
  const r = gcvs.getBoundingClientRect();
  GW = r.width; GH = r.height;
  gcvs.width = GW*devicePixelRatio; gcvs.height = GH*devicePixelRatio;
  gctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  gctx.imageSmoothingEnabled = false;
}
addEventListener('resize', ()=>{ if(activeGame){ sizeGame(); activeGame.layout && activeGame.layout(); } });

let gPaused = false; // true while a game's intro screen is up
function openGame(g){
  activeGame = g;
  gover.style.display = 'flex';
  gmsg.style.display = 'none';
  document.getElementById('gtitle').textContent = g.title;
  sizeGame();
  g.init();
  if(g.intro){
    gPaused = true;
    showGmsg('<h3>'+g.title+'</h3><p>'+g.intro+'</p><button onclick="startGame()">'+(g.introBtn||'start')+'</button>');
  } else gPaused = false;
}
function startGame(){ gPaused = false; gmsg.style.display='none'; }
function closeGame(){ activeGame = null; gPaused = false; gover.style.display='none'; gmsg.style.display='none'; }
document.getElementById('gquit').onclick = closeGame;

function gPointer(e){
  const r = gcvs.getBoundingClientRect();
  const t = e.touches ? e.touches[0] : e;
  return { x:(t.clientX-r.left), y:(t.clientY-r.top) };
}
gcvs.addEventListener('pointerdown', e=>{ if(activeGame&&!gPaused&&activeGame.down){ const p=gPointer(e); activeGame.down(p.x,p.y);} });
gcvs.addEventListener('pointermove', e=>{ if(activeGame&&!gPaused&&activeGame.move){ const p=gPointer(e); activeGame.move(p.x,p.y);} });
gcvs.addEventListener('pointerup',   e=>{ if(activeGame&&!gPaused&&activeGame.up){ const p=gPointer(e); activeGame.up(p.x,p.y);} });

function showGmsg(html){ gmsg.innerHTML = html; gmsg.style.display='block'; }
function hideGmsg(){ gmsg.style.display='none'; }

__GAMES__

/* ---------- zone actions ---------- */
function zoneAction(z){
  if(z.id==='garden'){ openRanunculus(); return; }
  if(z.id==='dock'){ openCreek(); return; }
  if(z.id==='house') return openModal({img:'plushy', title:"Anna's House",
    text:'Inside, the squishiest platypus plushy on the lake is napping on the pillow. Best not to wake him.'});
  if(z.id==='stall'){
    if(allDone()){
      openModal({title:'The Fruit Stall',
        text:'Among the lychee and mangosteen, a letter is waiting here for you.',
        alt:'read the letter', onAlt:openFruitLetter, closeLabel:'not yet'});
    } else {
      openModal({title:'The Fruit Stall',
        text:'Lychee and mangosteen, picked this morning. Come back once you have played every game — something will be waiting.'});
    }
    return;
  }
  if(z.id==='oak'){
    if(!progress.squirrel) openGame(squirrelGame);
    else openModal({title:'The Old Oak',
      text:'Two squirrels are curled up together in the coziest nest on the lake.',
      alt:'gather fluff again', onAlt:()=>openGame(squirrelGame)});
    return;
  }
}

/* ---------- update ---------- */
let last = performance.now();
function update(dt, t){
  let mx = (kd['arrowright']||kd['d']?1:0) - (kd['arrowleft']||kd['a']?1:0) + input.x;
  let my = (kd['arrowdown']||kd['s']?1:0)  - (kd['arrowup']||kd['w']?1:0)  + input.y;
  const mag = Math.hypot(mx,my);
  anna.moving = mag > 0.01 && started && !modalOpen && !activeGame;
  if(anna.moving){
    mx/=Math.max(1,mag); my/=Math.max(1,mag);
    const nx = anna.x + mx*SPEED*dt, ny = anna.y + my*SPEED*dt;
    if(walkable(nx, anna.y)) anna.x = nx;
    if(walkable(anna.x, ny)) anna.y = ny;
    if(mx < -0.05) anna.flip = true; else if(mx > 0.05) anna.flip = false;
  }

  let zone = null;
  for(const z of zones) if(inRect(anna.x, anna.y, z.r)) zone = z;
  const nearCat = inRect(anna.x, anna.y, catZone);
  let nearDog = null;
  for(const d of dogs) if(Math.hypot(d.x-anna.x, d.y-anna.y) < 70) nearDog = d;

  if(!modalOpen && !activeGame && started && (zone || nearCat || nearDog)){
    promptEl.style.display = 'block';
    const key = document.body.classList.contains('touch') ? 'tap &#9733;' : 'press SPACE';
    let label;
    if(zone) label = '&#11088; '+zone.name;
    else if(nearCat) label = '&#128008; the sphynx is watching';
    else label = '&#128062; a very good dog';
    promptEl.innerHTML = label + ' &mdash; <b>' + key + '</b>';
  } else promptEl.style.display = 'none';

  if(input.act && started && !modalOpen && !activeGame){
    if(zone) zoneAction(zone);
    else if(nearCat){
      cat.meow = 2;
      heartBurst(cat.x, cat.y-28);
      openModal({title:'brrp ♥',
        text: progress.family
          ? 'She is loafing proudly beside the finished family tree.'
          : 'The Sphynx family tree got scrambled. Help her put everyone back in their place?',
        alt: progress.family ? 'rearrange the photos' : 'fix the family tree',
        onAlt: ()=>openGame(famGame),
        closeLabel:'just say hi'});
    }
    else if(nearDog){
      const d = nearDog;
      openModal({title:'Woof!',
        text: progress.dogs
          ? 'Tail wags. Wanna play hide and seek again?'
          : 'Wanna play hide and seek in the dark?',
        alt: progress.dogs ? 'play again' : "let's play",
        onAlt: ()=>openGame(dogGame),
        closeLabel:'just pet'});
      d.state='hop'; d.t=0.55;
      heartBurst(d.x, d.y-34);
    }
  }
  input.act = false;

  /* dogs */
  for(const d of dogs){
    const distA = Math.hypot(anna.x-d.x, anna.y-d.y);
    if(d.state==='hop'){ d.t-=dt; if(d.t<=0){ d.state='pause'; d.t=1; } continue; }
    if(distA < 150 && distA > 60 && anna.moving){ d.state='follow'; }
    if(d.state==='follow'){
      if(distA <= 58 || distA > 260){ d.state='pause'; d.t=0.8+Math.random(); }
      else {
        const a=Math.atan2(anna.y-d.y, anna.x-d.x);
        const nx=d.x+Math.cos(a)*d.speed*1.35*dt, ny=d.y+Math.sin(a)*d.speed*1.35*dt;
        if(walkable(nx,ny)){ d.x=nx; d.y=ny; d.angle=a; }
      }
    } else if(d.state==='pause'){
      d.t-=dt;
      if(d.t<=0 && pickLand(d, d.x, d.y, 170)) d.state='walk';
      else if(d.t<=0) d.t=1;
    } else if(d.state==='walk'){
      const dx=d.tx-d.x, dy=d.ty-d.y, dist=Math.hypot(dx,dy);
      if(dist<6){ d.state='pause'; d.t=1.5+Math.random()*3; }
      else {
        const a=Math.atan2(dy,dx);
        const nx=d.x+Math.cos(a)*d.speed*dt, ny=d.y+Math.sin(a)*d.speed*dt;
        if(walkable(nx,ny)){ d.x=nx; d.y=ny; d.angle=a; }
        else { d.state='pause'; d.t=1; }
      }
    }
  }

  /* platypus */
  if(platy.dive > 0){
    platy.dive -= dt;
    platy.alpha = Math.max(0, Math.min(1, Math.abs(platy.dive-1.2)/1.2));
    if(platy.dive <= 1.2 && platy.dive+dt > 1.2){
      pickWater(platy); platy.x=platy.tx; platy.y=platy.ty;
      ripples.push({x:platy.x, y:platy.y, r:6, t:1});
    }
  } else {
    platy.alpha = 1;
    if(platy.state==='pause'){
      platy.t-=dt;
      if(platy.t<=0){
        if(Math.random()<0.22){ platy.dive=2.4; ripples.push({x:platy.x,y:platy.y,r:6,t:1}); }
        else if(pickWater(platy)) platy.state='walk';
        else platy.t=1;
      }
    } else {
      const dx=platy.tx-platy.x, dy=platy.ty-platy.y, dist=Math.hypot(dx,dy);
      if(dist<5){ platy.state='pause'; platy.t=1+Math.random()*2.5; }
      else {
        const a=Math.atan2(dy,dx);
        platy.x+=Math.cos(a)*platy.speed*dt; platy.y+=Math.sin(a)*platy.speed*dt;
        platy.flip = dx>0;
        if(Math.random()<dt*2.2) ripples.push({x:platy.x-(platy.flip?-26:26), y:platy.y+6, r:3, t:0.9});
      }
    }
  }

  /* boat */
  if(boat.moored){ boat.t-=dt; if(boat.t<=0){ boat.moored=false; boat.dir = boat.x<700?1:-1; } }
  else {
    boat.x += boat.dir*26*dt;
    if(Math.random()<dt*1.5) ripples.push({x:boat.x-boat.dir*52, y:boat.y+18, r:4, t:1.1});
    if(boat.dir>0 && boat.x>=940){ boat.moored=true; boat.t=5+Math.random()*4; }
    if(boat.dir<0 && boat.x<=470){ boat.moored=true; boat.t=6+Math.random()*5; }
  }

  cat.blink -= dt; if(cat.blink<=0) cat.blink = 2.5+Math.random()*3;
  cat.meow = Math.max(0, cat.meow-dt);

  for(let i=parts.length-1;i>=0;i--){ const p=parts[i]; p.t-=dt; p.x+=(p.vx||0)*dt; p.y+=p.vy*dt; if(p.t<=0) parts.splice(i,1); }
  for(let i=ripples.length-1;i>=0;i--){ const r=ripples[i]; r.t-=dt; r.r+=22*dt; if(r.t<=0) ripples.splice(i,1); }
}

/* ---------- draw ---------- */
/* a floating sign with a pointer tip at (x,y), in map space */
function drawMarker(x, y, txt, faded, t, i){
  const bob = Math.sin(t*0.0028 + i*1.7)*3.5;
  ctx.save();
  ctx.globalAlpha = faded ? 0.45 : 0.95;
  ctx.font = 'bold 19px Courier New';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const w = ctx.measureText(txt).width + 20, h = 32, r = 6;
  const bx = Math.max(6, Math.min(MAPW-6-w, x - w/2));
  const by = y - h - 8 + bob;
  ctx.beginPath();
  ctx.moveTo(bx+r, by);
  ctx.lineTo(bx+w-r, by); ctx.quadraticCurveTo(bx+w, by, bx+w, by+r);
  ctx.lineTo(bx+w, by+h-r); ctx.quadraticCurveTo(bx+w, by+h, bx+w-r, by+h);
  ctx.lineTo(x+7, by+h); ctx.lineTo(x, by+h+8); ctx.lineTo(x-7, by+h);
  ctx.lineTo(bx+r, by+h); ctx.quadraticCurveTo(bx, by+h, bx, by+h-r);
  ctx.lineTo(bx, by+r); ctx.quadraticCurveTo(bx, by, bx+r, by);
  ctx.closePath();
  ctx.fillStyle = 'rgba(42,35,32,.88)';
  ctx.fill();
  ctx.lineWidth = 2; ctx.strokeStyle = '#c9a15a'; ctx.stroke();
  ctx.fillStyle = '#f3e6c8';
  ctx.fillText(txt, bx + w/2, by + h/2 + 1);
  ctx.restore();
}

function draw(t){
  const scale = Math.max(vw/MAPW, vh/MAPH);
  let camX = anna.x - vw/scale/2, camY = anna.y - vh/scale/2;
  camX = Math.max(0, Math.min(MAPW - vw/scale, camX));
  camY = Math.max(0, Math.min(MAPH - vh/scale, camY));

  ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0,0,vw,vh);
  ctx.setTransform(scale*devicePixelRatio,0,0,scale*devicePixelRatio,
                   -camX*scale*devicePixelRatio, -camY*scale*devicePixelRatio);

  ctx.drawImage(imgs.map, 0, 0);

  /* persistent garden blooms */
  for(const f of mapFlowers){
    ctx.fillStyle = '#3d2f23';
    ctx.beginPath(); ctx.arc(f.x, f.y, 8, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = f.c;
    ctx.beginPath(); ctx.arc(f.x, f.y, 6, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#f5e06e';
    ctx.beginPath(); ctx.arc(f.x, f.y, 2, 0, Math.PI*2); ctx.fill();
  }

  ctx.lineWidth = 2;
  for(const r of ripples){
    ctx.strokeStyle = 'rgba(230,245,252,'+(0.55*r.t)+')';
    ctx.beginPath(); ctx.ellipse(r.x, r.y, r.r, r.r*0.45, 0, 0, Math.PI*2); ctx.stroke();
  }

  const bob = Math.sin(t*0.0021)*2.4;
  ctx.drawImage(imgs.boat, boat.x-55, boat.y-30+bob);

  if(platy.alpha > 0.02){
    ctx.save();
    ctx.globalAlpha = platy.alpha;
    const pb = Math.sin(t*0.0035)*2;
    ctx.translate(platy.x, platy.y+pb);
    if(platy.flip) ctx.scale(-1,1);
    ctx.drawImage(imgs.platypus, -32, -15);
    ctx.restore();
  }

  const order = [];
  order.push({y:anna.y, f:()=>{
    const ab = anna.moving ? Math.abs(Math.sin(t*0.012))*3 : 0;
    ctx.save(); ctx.translate(anna.x, anna.y - ab);
    if(anna.flip) ctx.scale(-1,1);
    ctx.drawImage(imgs.anna, -13, -88);
    ctx.restore();
  }});
  for(const d of dogs){
    order.push({y:d.y, f:()=>{
      ctx.save();
      if(d.state==='walk'||d.state==='follow'){
        ctx.translate(d.x, d.y);
        ctx.rotate(d.angle - d.heading);
        ctx.drawImage(imgs[d.sprite], -26, -26);
      } else {
        const hop = d.state==='hop' ? -Math.abs(Math.sin((0.55-d.t)*11))*10 : 0;
        ctx.translate(d.x, d.y + hop);
        ctx.drawImage(imgs[d.sit], -13, -40);
      }
      ctx.restore();
    }});
  }
  order.sort((a,b)=>a.y-b.y);
  for(const o of order) o.f();

  const breathe = 1 + Math.sin(t*0.0016)*0.02;
  ctx.save();
  ctx.translate(cat.x, cat.y);
  ctx.scale(breathe, breathe);
  ctx.drawImage(imgs.cat, -11, -32);
  ctx.restore();
  if(progress.family){
    ctx.drawImage(imgs.plushy, cat.x+16, cat.y-24, 34, 23);
  }
  if(cat.meow > 0){
    ctx.font = 'bold 15px Courier New';
    ctx.fillStyle = 'rgba(61,47,35,.9)'; ctx.textAlign='center';
    ctx.fillText('~', cat.x+16, cat.y-36);
  }

  ctx.font = 'bold 17px Courier New'; ctx.textAlign = 'center';
  for(const p of parts){
    ctx.fillStyle = 'rgba(201,70,90,'+Math.min(1,p.t)+')';
    ctx.fillText(p.txt, p.x, p.y);
  }

  /* waypoint signs, on top of everything */
  let wi = 0;
  for(const w of waypoints){
    let txt = w.label, faded = false;
    if(w.stall && allDone()) txt = 'a letter for you';
    else if(w.done()){ txt += ' ✓'; faded = true; }
    drawMarker(w.x, w.y, txt, faded, t, wi++);
  }
  for(const d of dogs)
    drawMarker(d.x, d.y-52, progress.dogs ? 'hide & seek ✓' : 'hide & seek', progress.dogs, t, wi++);
}

function loop(now){
  const dt = Math.min(0.05, (now-last)/1000); last = now;
  if(loaded === keys.length){
    if(activeGame){
      if(!gPaused) activeGame.update && activeGame.update(dt, now);
      activeGame.draw && activeGame.draw(now);
    } else {
      update(dt, now); draw(now);
    }
  }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
</script>
</body>
</html>
'''

# Mini-games live in games/*.js so each can be edited on its own; they are
# concatenated into the template here, so index.html stays self-contained.
GAME_FILES = ['family_tree.js', 'find_the_dog.js', 'squirrel_nest.js']
games_js = '\n\n'.join(pathlib.Path('games/'+f).read_text().rstrip() for f in GAME_FILES)

# Standalone games (Platypus Creek, the Ranunculus puzzle) are embedded whole
# as iframe srcdoc strings. The '</' escape keeps their closing tags from
# terminating the outer <script> block.
def embed_html(path):
    return json.dumps(pathlib.Path(path).read_text()).replace('</', '<\\/')

html = html.replace('__ASSETS__', js_assets)
html = html.replace('__GAMES__', games_js)
html = html.replace('__CREEK__', embed_html('games/platypus-creek.html'))
html = html.replace('__RANUNCULUS__', embed_html('games/ranunculus.html'))
out = pathlib.Path('game/index.html')
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print('built', out, len(html)//1024, 'KB')
