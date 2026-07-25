/* ================= GAME 3: Find the Dog ================= */
const dogGame = {
  title:'Find the Dog', round:0, light:{x:0,y:0}, found:false, foundT:0, target:null, btn:null,
  intro:'The dogs snuck out to play hide and seek in the dark — and dragged a friend along.\nSweep the flashlight (drag or tap) and shine it on whoever is hiding. Three rounds.',
  introBtn:'lights on',
  rounds:[
    {img:'dogWs', h:96, r:170, bark:'WOOF!', bg:'dogBgYard', where:'the yard'},
    {img:'dogBs', h:96, r:120, bark:'woof woof!', bg:'dogBgRoom', where:'the house'},
    {img:'platypus', h:66, r:95, bark:'...krrrr? that is not a dog!', bg:'dogBgPond', where:'the pond'},
  ],
  init(){
    this.round=0; this.light={x:GW/2,y:GH/2};
    this.place();
  },
  place(){
    const cfg=this.rounds[this.round];
    const im=imgs[cfg.img], s=cfg.h/im.height;
    // keep hiding spots in the lower part of the scene (grass / floor / water),
    // not up in the sky or on the walls
    const yMin = GH*0.34, yMax = GH-90;
    this.target={img:cfg.img, w:im.width*s, h:cfg.h,
      x: 60+Math.random()*(GW-120), y: yMin+Math.random()*(yMax-yMin), r:cfg.r, bark:cfg.bark};
    this.found=false; this.foundT=0; this.btn=null;
  },
  down(x,y){
    if(this.found){
      const b=this.btn;
      if(b && this.foundT>0.6 && x>=b.x && x<=b.x+b.w && y>=b.y && y<=b.y+b.h) this.next();
      return;
    }
    this.light.x=x; this.light.y=y;
    const tg=this.target;
    if(Math.abs(x-tg.x)<tg.w/2+20 && Math.abs(y-tg.y)<tg.h/2+20){
      this.found=true; this.foundT=0;
    }
  },
  move(x,y){ if(!this.found){ this.light.x=x; this.light.y=y; } },
  next(){
    this.round++;
    if(this.round>=this.rounds.length){
      this.round=this.rounds.length-1;
      this.found=false; this.btn=null;
      progress.dogs=true; refreshHud();
      showGmsg('<h3>found everyone</h3><p>The dogs (and one confused platypus) are safe. They knew you would find them.</p><button onclick="closeGame()">good dogs</button>');
    } else this.place();
  },
  update(dt){
    if(this.found) this.foundT+=dt;
  },
  draw(){
    const cfg=this.rounds[Math.min(this.round, this.rounds.length-1)];
    // night scene for this round, cover-fit
    const bg=imgs[cfg.bg];
    const s=Math.max(GW/bg.width, GH/bg.height);
    gctx.drawImage(bg, (GW-bg.width*s)/2, (GH-bg.height*s)/2, bg.width*s, bg.height*s);
    const tg=this.target;
    gctx.drawImage(imgs[tg.img], tg.x-tg.w/2, tg.y-tg.h/2, tg.w, tg.h);
    // darkness with flashlight hole
    const R = this.found ? tg.r + Math.min(this.foundT,1.6)*900 : tg.r;
    const lx = this.found ? tg.x : this.light.x, ly = this.found ? tg.y : this.light.y;
    const grad = gctx.createRadialGradient(lx,ly, R*0.25, lx,ly, R);
    grad.addColorStop(0,'rgba(6,8,10,0)');
    grad.addColorStop(0.75,'rgba(6,8,10,.55)');
    grad.addColorStop(1,'rgba(6,8,10,.985)');
    gctx.fillStyle=grad; gctx.fillRect(0,0,GW,GH);
    gctx.fillStyle='#f3e6c8'; gctx.font='15px Courier New'; gctx.textAlign='center';
    gctx.fillText('round '+Math.min(this.round+1,3)+' of 3 — '+cfg.where+' is dark. find who is hiding.', GW/2, 26);
    if(this.found){
      gctx.font='bold 22px Courier New';
      gctx.fillStyle='rgba(247,236,215,'+Math.min(1,this.foundT*2)+')';
      gctx.fillText(tg.bark, GW/2, tg.y - tg.h/2 - 18);
      // next button once the scene is revealed
      if(this.foundT>0.6){
        const last = this.round===this.rounds.length-1;
        const bw=170, bh=44;
        this.btn={x:GW/2-bw/2, y:GH-72, w:bw, h:bh};
        const b=this.btn, a=Math.min(1,(this.foundT-0.6)*3);
        gctx.save(); gctx.globalAlpha=a;
        gctx.fillStyle='rgba(20,16,14,.85)';
        gctx.beginPath(); gctx.roundRect(b.x, b.y, b.w, b.h, 8); gctx.fill();
        gctx.strokeStyle='#c9a15a'; gctx.lineWidth=2; gctx.stroke();
        gctx.fillStyle='#f3e6c8'; gctx.font='bold 16px Courier New';
        gctx.fillText(last ? 'finish ♥' : 'next →', GW/2, b.y+28);
        gctx.restore();
      }
    }
  }
};
