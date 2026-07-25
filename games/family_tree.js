/* ================= GAME 1: The Sphynx Family Tree ================= */
const famGame = {
  title:'🐈 The Sphynx Family Tree',
  intro:'The family photos fell off the tree and got shuffled!\nDrag each cat onto their spot — parents on top, kitten at the bottom. If a photo bounces back, it belongs somewhere else.',
  introBtn:"fix the tree",
  // bg = pixel position of the painted frame in famtree_bg (1536x1024).
  // slot = [column, row] for the portrait fallback layout: Malva→Sergei on
  // the left, Lola→Naomi on the right, Funtik (their kitten) at the bottom.
  // fact: fun fact shown after the game is solved
  defs:[
    {id:'malva',  name:'Malva',  slot:[0,   0], bg:[248,248], tint:'#d9a8c4', fact:'Malva is a cuddler — but only with me. She follows me around everywhere I go.'},
    {id:'lola',   name:'Lola',   slot:[1,   0], bg:[533,248], tint:'#c9a15a', fact:'Lola is pretty much the owner of the house. She loves being on my shoulders, and shows it by lifting her arm up and meowing at me to get up there. I\'ve given her shoulder rides since she was a kitten.'},
    {id:'sergei', name:'Sergei', slot:[0,   1], bg:[248,513], tint:'#9db3c9', fact:'Sergei talks too much. He yells 24/7 — especially when mom isn\'t home.'},
    {id:'naomi',  name:'Naomi',  slot:[1,   1], bg:[533,514], tint:'#a8c9a2', fact:'Naomi bites your nose when she\'s hungry and swats at your hands when she wants pets. She also loves belly rubs.'},
    {id:'funtik', name:'Funtik', slot:[0.5, 2], bg:[402,793], tint:'#e0b9a2', fact:'Funtik chews on the paper towel roll to show that he\'s hungry — or when he doesn\'t get something he wants.'},
  ],
  tray:[[940,330],[1140,330],[1340,330],[1040,600],[1240,600]],
  links:[['malva','sergei'],['lola','naomi'],['sergei','funtik'],['naomi','funtik']],
  pieces:[], drag:null, done:false, hearts:[], wrong:null, wrongT:0,
  cw:90, ch:100, useBg:true, bs:1, bx:0, by:0,
  layout(){
    // the painted board is landscape; portrait screens fall back to the drawn tree
    this.useBg = GW > GH*1.05;
    if(this.useBg){
      const im = imgs.famBg;
      this.bs = Math.min(GW/im.width, GH/im.height);
      this.bx = (GW - im.width*this.bs)/2;
      this.by = (GH - im.height*this.bs)/2;
      this.cw = this.ch = 150*this.bs;
    } else {
      this.cw = Math.min(GW*0.17, GH*0.15, 108);
      this.ch = this.cw*1.12;
    }
    const rowY = [GH*0.17, GH*0.41, GH*0.65];
    const n = this.pieces.length, gap = Math.min(this.cw*1.3, GW*0.94/n);
    for(const p of this.pieces){
      if(this.useBg){
        p.sx = this.bx + p.bg[0]*this.bs;
        p.sy = this.by + p.bg[1]*this.bs;
        const tr = this.tray[p.tray];
        p.hx = this.bx + tr[0]*this.bs;
        p.hy = this.by + tr[1]*this.bs;
      } else {
        p.sx = GW*(0.29 + p.slot[0]*0.42);
        p.sy = rowY[p.slot[1]];
        p.hx = GW/2 + (p.tray-(n-1)/2)*gap;
        p.hy = GH*0.885;
      }
      if(p.locked){ p.x=p.sx; p.y=p.sy; }
      else if(this.drag!==p){ p.x=p.hx; p.y=p.hy; }
    }
  },
  init(){
    this.done=false; this.hearts=[]; this.drag=null; this.wrong=null; this.wrongT=0; this.extraShown=false;
    const order=[...this.defs.keys()].sort(()=>Math.random()-0.5);
    this.pieces=this.defs.map((d,i)=>({...d, locked:false, factRead:false, tray:order[i], x:0,y:0,sx:0,sy:0,hx:0,hy:0}));
    this.layout();
  },
  down(x,y){
    if(this.done){
      // fun-fact mode: tap a photo to read about that cat
      for(const p of this.pieces){
        if(p.locked && Math.abs(x-p.sx)<this.cw/2+8 && Math.abs(y-p.sy)<this.ch/2+8){
          p.factRead=true;
          showGmsg('<h3>'+p.name+' 🐈</h3><p>'+p.fact+'</p><br><button onclick="famGame.factClosed()">aww</button>');
          return;
        }
      }
      return;
    }
    for(let i=this.pieces.length-1;i>=0;i--){
      const p=this.pieces[i];
      if(!p.locked && Math.abs(x-p.x)<this.cw/2+12 && Math.abs(y-p.y)<this.ch/2+12){
        this.drag=p; this.pieces.splice(i,1); this.pieces.push(p); return;
      }
    }
  },
  factClosed(){
    hideGmsg();
    if(!this.extraShown && this.pieces.every(q=>q.factRead)){
      this.extraShown=true;
      setTimeout(()=>showGmsg('<h3>one extra fun fact ♥</h3><p>The person who made this game likes you more than Funtik likes shopping bags, more than the squirrels like fluff, more than every ranunculus on this lake put together.\n\nEvery game here exists because thinking of you makes even ordinary days feel like something worth building.</p><br><button onclick="closeGame()">♥</button>'), 400);
    }
  },
  move(x,y){ if(this.drag){ this.drag.x=x; this.drag.y=y; } },
  up(){
    const p=this.drag; this.drag=null;
    if(!p) return;
    let best=null, bd=1e9;
    for(const q of this.pieces){
      const d=Math.hypot(p.x-q.sx, p.y-q.sy);
      if(d<bd){ bd=d; best=q; }
    }
    if(best===p && bd < this.cw*0.8){
      p.locked=true; p.x=p.sx; p.y=p.sy;
      for(let i=0;i<6;i++) this.hearts.push({x:p.sx, y:p.sy-this.ch/2, vx:Math.random()*60-30, vy:-40-Math.random()*50, t:1.2});
      if(this.pieces.every(q=>q.locked) && !this.done){
        this.done=true; progress.family=true; refreshHud();
        setTimeout(()=>showGmsg('<h3>La Famiglia 🐈♥</h3><p>You got them all right!\nNow tap each photo to read a fun fact about that cat.</p><button onclick="hideGmsg()">ooh!</button>'), 700);
      }
    } else {
      if(best && !best.locked && bd < this.cw*0.8){ this.wrong=best; this.wrongT=0.7; }
      p.x=p.hx; p.y=p.hy;
    }
  },
  update(dt){
    this.wrongT = Math.max(0, this.wrongT-dt);
    for(let i=this.hearts.length-1;i>=0;i--){ const h=this.hearts[i]; h.t-=dt; h.x+=h.vx*dt; h.y+=h.vy*dt; if(h.t<=0)this.hearts.splice(i,1); }
  },
  card(p, x, y){
    const w=this.cw, h=this.ch;
    gctx.save();
    gctx.beginPath(); gctx.roundRect(x-w/2, y-h/2, w, h, 8);
    gctx.fillStyle='#f7ecd7'; gctx.fill();
    gctx.clip();
    const im = imgs['cat_'+p.id];
    if(im && im.complete && im.naturalWidth){
      const s = Math.max(w/im.naturalWidth, h/im.naturalHeight);
      const oldSmooth = gctx.imageSmoothingEnabled;
      gctx.imageSmoothingEnabled = true;
      gctx.drawImage(im, x-im.naturalWidth*s/2, y-im.naturalHeight*s/2, im.naturalWidth*s, im.naturalHeight*s);
      gctx.imageSmoothingEnabled = oldSmooth;
    } else {
      gctx.fillStyle=p.tint; gctx.fillRect(x-w/2, y-h/2, w, h);
      gctx.font=(w*0.42)+'px serif'; gctx.textAlign='center';
      gctx.fillText('🐈', x, y+w*0.08);
    }
    gctx.restore();
    gctx.beginPath(); gctx.roundRect(x-w/2, y-h/2, w, h, 8);
    gctx.strokeStyle='#7a4a2e'; gctx.lineWidth=3; gctx.stroke();
  },
  arrow(x1,y1,x2,y2){
    gctx.beginPath(); gctx.moveTo(x1,y1); gctx.lineTo(x2,y2); gctx.stroke();
    const a=Math.atan2(y2-y1,x2-x1);
    gctx.beginPath(); gctx.moveTo(x2,y2);
    gctx.lineTo(x2-9*Math.cos(a-0.45), y2-9*Math.sin(a-0.45));
    gctx.lineTo(x2-9*Math.cos(a+0.45), y2-9*Math.sin(a+0.45));
    gctx.closePath(); gctx.fill();
  },
  draw(t){
    const byId={}; for(const p of this.pieces) byId[p.id]=p;
    if(this.useBg){
      // painted board: frames, arrows and panel headers are part of the art
      gctx.fillStyle='#3a2413'; gctx.fillRect(0,0,GW,GH);
      const im=imgs.famBg;
      gctx.drawImage(im, this.bx, this.by, im.width*this.bs, im.height*this.bs);
    } else {
      gctx.fillStyle='#3a2e25'; gctx.fillRect(0,0,GW,GH);
      gctx.fillStyle='#f3e6c8'; gctx.font='15px Courier New'; gctx.textAlign='center';
      gctx.fillText('drag each cat photo to their spot on the tree', GW/2, GH*0.06);
      gctx.strokeStyle='rgba(201,161,90,.8)'; gctx.fillStyle='rgba(201,161,90,.8)'; gctx.lineWidth=2.5;
      for(const [a,b] of this.links){
        const pa=byId[a], pb=byId[b];
        this.arrow(pa.sx, pa.sy+this.ch/2+6, pb.sx, pb.sy-this.ch/2-8);
      }
    }
    // slots
    for(const p of this.pieces){
      const flash = this.wrong===p && this.wrongT>0;
      if(p.locked){
        gctx.fillStyle = this.useBg ? '#5b3a1e' : '#f3e6c8';
        gctx.font='bold '+Math.max(13,this.cw*0.14)+'px Courier New'; gctx.textAlign='center';
        gctx.fillText(p.name, p.sx, p.sy+this.ch/2+(this.useBg ? Math.max(20,this.ch*0.25) : 17));
        continue;
      }
      if(!this.useBg || flash){
        gctx.save();
        gctx.setLineDash([7,5]);
        gctx.strokeStyle = flash ? 'rgba(217,90,80,.95)' : 'rgba(243,230,200,.55)';
        gctx.lineWidth = flash ? 3 : 2;
        gctx.beginPath(); gctx.roundRect(p.sx-this.cw/2, p.sy-this.ch/2, this.cw, this.ch, 8);
        gctx.stroke();
        gctx.restore();
      }
    }
    // photo cards (locked cards sit in their slots, the rest wait in the tray)
    for(const p of this.pieces) this.card(p, p.locked?p.sx:p.x, p.locked?p.sy:p.y);
    // names under the tray photos (locked ones are labeled in the slots loop)
    gctx.textAlign='center';
    for(const p of this.pieces){
      if(p.locked) continue;
      gctx.fillStyle = this.useBg ? '#5b3a1e' : '#f3e6c8';
      gctx.font='bold '+Math.max(13,this.cw*0.14)+'px Courier New';
      gctx.fillText(p.name, p.x, p.y+this.ch/2+(this.useBg ? Math.max(20,this.ch*0.2) : 17));
    }
    // fun-fact mode: mark photos that still have an unread fact
    if(this.done){
      for(const p of this.pieces){
        if(p.factRead) continue;
        const bx=p.sx+this.cw/2-6, by=p.sy-this.ch/2+6;
        const r=9+Math.sin((t||0)*0.005)*1.5;
        gctx.fillStyle='#c9a15a';
        gctx.beginPath(); gctx.arc(bx, by, r, 0, Math.PI*2); gctx.fill();
        gctx.strokeStyle='#7a4a2e'; gctx.lineWidth=2; gctx.stroke();
        gctx.fillStyle='#3d2f23'; gctx.font='bold 13px Courier New';
        gctx.fillText('?', bx, by+4);
      }
    }
    gctx.font='bold 18px Courier New'; gctx.textAlign='center';
    for(const h of this.hearts){ gctx.fillStyle='rgba(201,70,90,'+Math.min(1,h.t)+')'; gctx.fillText('♥',h.x,h.y); }
  }
};
