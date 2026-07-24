/* ================= GAME 4: The Squirrel Nest ================= */
const squirrelGame = {
  title:'🐿️ The Squirrel Nest',
  intro:'The squirrel is building the coziest nest on the lake, and fluff is tumbling down from the old oak.\nTap the fluff before the wind steals it — it falls faster and faster as the nest fills.',
  introBtn:'gather fluff',
  need:12,
  fluffs:[], flying:[], pile:[], hearts:[], nestCount:0, done:false, spawnT:0, time:0, wind:0,
  nest:{x:0,y:0,r:0},
  layout(){
    // cover-fit the background; the nest position tracks the painted nest
    const im=imgs.fluffBg;
    this.bs = Math.max(GW/im.width, GH/im.height);
    this.bx = (GW - im.width*this.bs)/2;
    this.by = (GH - im.height*this.bs)/2;
    this.nest.x = this.bx + 1150*this.bs;
    this.nest.y = this.by + 480*this.bs;
    this.nest.r = 130*this.bs;
  },
  init(){
    this.fluffs=[]; this.flying=[]; this.pile=[]; this.hearts=[];
    this.nestCount=0; this.done=false; this.spawnT=0.3; this.time=0; this.wind=0;
    this.layout();
  },
  spawn(){
    // fluff falls quicker as the nest fills up
    const pace = 1 + Math.min(0.6, this.nestCount*0.05);
    this.fluffs.push({
      x: GW*0.04 + Math.random()*GW*0.92,
      y: -20,
      r: 9 + Math.random()*7,
      vy: (55 + Math.random()*45)*pace,
      ph: Math.random()*Math.PI*2,
      sway: 24 + Math.random()*36,
    });
  },
  down(x,y){
    if(this.done) return;
    for(let i=this.fluffs.length-1;i>=0;i--){
      const f=this.fluffs[i];
      if(Math.hypot(x-f.x, y-f.y) < f.r+12){
        this.fluffs.splice(i,1); this.flying.push(f); return;
      }
    }
  },
  update(dt){
    this.time += dt;
    // a slow, shifting breeze that carries every puff sideways
    this.wind = Math.sin(this.time*0.5)*42 + Math.sin(this.time*0.17+2)*26;
    if(!this.done){
      this.spawnT-=dt;
      if(this.spawnT<=0){ this.spawn(); this.spawnT=0.45+Math.random()*0.5; }
    }
    for(let i=this.fluffs.length-1;i>=0;i--){
      const f=this.fluffs[i];
      f.ph+=dt*1.7;
      f.vy+=16*dt;
      f.y+=f.vy*dt;
      f.x+=(Math.sin(f.ph)*f.sway + this.wind)*dt;
      if(f.y>GH+30 || f.x<-40 || f.x>GW+40) this.fluffs.splice(i,1);
    }
    for(let i=this.flying.length-1;i>=0;i--){
      const f=this.flying[i];
      const dx=this.nest.x-f.x, dy=(this.nest.y-10)-f.y, d=Math.hypot(dx,dy), sp=430;
      if(d < sp*dt){
        this.flying.splice(i,1);
        this.nestCount++;
        this.pile.push({dx:(Math.random()*2-1)*this.nest.r*0.5, dy:-Math.random()*this.nest.r*0.35, r:this.nest.r*(0.11+Math.random()*0.08)});
        if(this.nestCount>=this.need && !this.done){
          this.done=true; progress.squirrel=true; refreshHud();
          for(let h=0;h<10;h++) this.hearts.push({x:this.nest.x, y:this.nest.y-40, vx:Math.random()*80-40, vy:-40-Math.random()*50, t:1.5});
          setTimeout(()=>showGmsg('<h3>love at the old oak 🐿️♥🐿️</h3><p>The nest is packed with the softest fluff on the lake —\nand someone came to share it.</p><button onclick="closeGame()">aww</button>'), 1200);
        }
      } else { f.x+=dx/d*sp*dt; f.y+=dy/d*sp*dt; }
    }
    for(let i=this.hearts.length-1;i>=0;i--){
      const h=this.hearts[i]; h.t-=dt; h.x+=h.vx*dt; h.y+=h.vy*dt;
      if(h.t<=0) this.hearts.splice(i,1);
    }
  },
  fluffBall(x,y,r){
    gctx.fillStyle='#f7f3ec';
    for(let i=0;i<5;i++){
      const an=i/5*Math.PI*2;
      gctx.beginPath(); gctx.arc(x+Math.cos(an)*r*0.4, y+Math.sin(an)*r*0.4, r*0.55, 0, Math.PI*2); gctx.fill();
    }
    gctx.beginPath(); gctx.arc(x,y,r*0.7,0,Math.PI*2); gctx.fill();
  },
  draw(t){
    const nx=this.nest.x, ny=this.nest.y;
    // painted dusk scene (squirrel waiting by the nest is part of it)
    const im=imgs.fluffBg;
    gctx.drawImage(im, this.bx, this.by, im.width*this.bs, im.height*this.bs);
    // gathered fluff piling up in the nest
    for(const p of this.pile) this.fluffBall(nx+p.dx, ny+p.dy, p.r);
    // once the nest is ready, the couple appears
    if(this.done){
      const lv=imgs.sqLove, w=this.nest.r*2.6, h=w*lv.height/lv.width;
      const bob=Math.sin(t*0.002)*3;
      gctx.drawImage(lv, nx-w/2, ny-h*0.72+bob, w, h);
    }
    // drifting fluff (caught ones fly to the nest)
    for(const f of this.fluffs) this.fluffBall(f.x, f.y, f.r);
    for(const f of this.flying) this.fluffBall(f.x, f.y, f.r);
    // ui text
    gctx.fillStyle='#f3e6c8'; gctx.font='15px Courier New'; gctx.textAlign='center';
    if(!this.done){
      gctx.fillText('tap the drifting fluff to send it to the nest', GW/2, GH*0.075);
      gctx.fillText(this.nestCount+' / '+this.need, GW/2, GH*0.12);
    }
    gctx.font='bold 18px Courier New';
    for(const h of this.hearts){ gctx.fillStyle='rgba(201,70,90,'+Math.min(1,h.t)+')'; gctx.fillText('♥',h.x,h.y); }
  }
};
