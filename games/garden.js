/* ================= GAME 2: Ranunculus Garden ================= */
const gardenGame = {
  title:'🌸 Ranunculus Garden',
  intro:'Nine beds of soil are waiting in the dark earth.\nTap each one to wake the ranunculus sleeping inside and watch it bloom.',
  introBtn:'to the garden',
  plots:[], bloomCount:0,
  colors:[['#f2a3b3','#e87a92'],['#f7c873','#eda63f'],['#f7f3f0','#e0d5cc'],['#f0937a','#d96b52']],
  layout(){
    const cols=3, rows=3;
    const cw=Math.min(GW*0.8, 420), ch=Math.min(GH*0.62, 420);
    const x0=GW/2-cw/2, y0=GH/2-ch/2+14;
    this.plots.forEach((p,i)=>{
      p.x = x0 + cw/(cols*2) + (i%cols)*(cw/cols);
      p.y = y0 + ch/(rows*2) + Math.floor(i/cols)*(ch/rows);
      p.r = Math.min(cw/cols, ch/rows)*0.42;
    });
  },
  init(){
    this.bloomCount=0;
    this.plots=[]; for(let i=0;i<9;i++) this.plots.push({t:0, c:this.colors[i%4], done:false});
    this.layout();
  },
  down(x,y){
    for(const p of this.plots){
      if(!p.done && Math.hypot(x-p.x,y-p.y)<p.r){
        p.done=true;
        this.bloomCount++;
        if(this.bloomCount===9){
          setTimeout(()=>{
            progress.garden = true; refreshHud();
            if(!mapFlowers.length)
              for(let i=0;i<8;i++) mapFlowers.push({x:230+Math.random()*140, y:400+Math.random()*270, c:this.colors[i%4][0]});
            showGmsg('<h3>they bloomed 🌸</h3><p>I owe you an apology: once, on a beautiful day, I could not get you your favorite flowers.\n\nSo I planted them here instead — now they bloom for you whenever you want.</p><span class="draft">(draft wording — the real message goes here)</span><br><button onclick="closeGame()">♥</button>');
          }, 1400);
        }
      }
    }
  },
  update(dt){ for(const p of this.plots) if(p.done && p.t<1) p.t=Math.min(1,p.t+dt*0.8); },
  draw(t){
    gctx.fillStyle='#4a3423'; gctx.fillRect(0,0,GW,GH);
    gctx.fillStyle='#f3e6c8'; gctx.font='15px Courier New'; gctx.textAlign='center';
    gctx.fillText('tap the soil to wake the ranunculus', GW/2, GH*0.09);
    for(const p of this.plots){
      // soil mound
      gctx.fillStyle='#6e5238';
      gctx.beginPath(); gctx.ellipse(p.x,p.y+p.r*0.5,p.r*0.85,p.r*0.4,0,0,Math.PI*2); gctx.fill();
      if(p.t>0){
        const g = p.t;
        // stem
        gctx.strokeStyle='#7fae5f'; gctx.lineWidth=4;
        gctx.beginPath(); gctx.moveTo(p.x,p.y+p.r*0.45);
        gctx.lineTo(p.x, p.y+p.r*0.45 - g*p.r*0.9); gctx.stroke();
        // layered petals unfold
        const cy = p.y+p.r*0.45 - g*p.r*0.9;
        const layers = 4;
        for(let l=layers; l>=1; l--){
          const lr = p.r*0.42 * (l/layers) * Math.min(1, g*1.4);
          const sway = Math.sin(t*0.002 + p.x)*1.5;
          gctx.fillStyle = l%2 ? p.c[0] : p.c[1];
          gctx.beginPath(); gctx.arc(p.x+sway*(l/layers), cy, lr, 0, Math.PI*2); gctx.fill();
        }
        gctx.fillStyle='#f5e06e';
        gctx.beginPath(); gctx.arc(p.x, cy, p.r*0.07*Math.min(1,g*1.4), 0, Math.PI*2); gctx.fill();
      } else {
        gctx.fillStyle='rgba(243,230,200,.35)'; gctx.font='13px Courier New';
        gctx.fillText('tap', p.x, p.y+4);
      }
    }
  }
};
