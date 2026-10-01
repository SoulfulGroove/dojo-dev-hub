(() => {
  const data = window.RESALE_DATA || [];
  const svg = document.getElementById("chart");
  const search = document.getElementById("search");
  const sample = document.getElementById("sample");
  const sampleValue = document.getElementById("sampleValue");
  const labels = document.getElementById("labels");
  const reset = document.getElementById("reset");
  const categoryName = document.getElementById("categoryName");
  const categorySummary = document.getElementById("categorySummary");
  const metrics = document.getElementById("metrics");

  const NS = "http://www.w3.org/2000/svg";
  const W=940,H=610,m={l:72,r:28,t:32,b:68};
  const xMin=0,xMax=100,yMin=20,yMax=105;
  let selected=null;

  const sx=v=>m.l+(v-xMin)/(xMax-xMin)*(W-m.l-m.r);
  const sy=v=>H-m.b-(v-yMin)/(yMax-yMin)*(H-m.t-m.b);
  const radius=n=>7+Math.sqrt(n)*2.15;
  const ring=b=>1+Math.min(5,b/7);

  function el(tag,attrs={}){
    const node=document.createElementNS(NS,tag);
    Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,String(v)));
    return node;
  }
  function txt(parent,x,y,value,attrs={}){
    const t=el("text",{x,y,...attrs}); t.textContent=value; parent.appendChild(t); return t;
  }
  function clear(){
    while(svg.firstChild) svg.removeChild(svg.firstChild);
  }
  function metric(label,value){
    return '<div class="metric"><span>'+label+'</span><strong>'+value+'</strong></div>';
  }
  function profile(d){
    selected=d.name;
    categoryName.textContent=d.name;
    const spread=d.average-d.median;
    const reliability=d.pct10>=80?"Strong reliability":d.pct10>=60?"Moderate reliability":"Higher processing risk";
    categorySummary.textContent =
      d.pct10.toFixed(1)+"% of sampled lots clear $10, with a median hammer price of $"+d.median.toFixed(2)+".";
    metrics.innerHTML=
      metric("Median","$"+d.median.toFixed(2))+
      metric("$10+ rate",d.pct10.toFixed(1)+"%")+
      metric("Average","$"+d.average.toFixed(2))+
      metric("Average bids",d.bids.toFixed(1))+
      metric("Sample size",String(d.sample))+
      metric("Average − median","$"+spread.toFixed(2))+
      '<div class="badge">'+reliability+'</div>';
    render();
  }

  function render(){
    clear();
    const q=search.value.trim().toLowerCase();
    const minN=Number(sample.value)||1;
    sampleValue.textContent=String(minN);
    const filtered=data.filter(d=>d.sample>=minN && (!q || d.name.toLowerCase().includes(q)));

    const zones=[
      [0,20,70,105,"rgba(243,185,95,.07)"],
      [20,100,70,105,"rgba(66,211,146,.09)"],
      [0,20,20,70,"rgba(239,109,120,.06)"],
      [20,100,20,70,"rgba(155,140,255,.05)"]
    ];
    zones.forEach(([x1,x2,y1,y2,fill])=>{
      svg.appendChild(el("rect",{x:sx(x1),y:sy(y2),width:sx(x2)-sx(x1),height:sy(y1)-sy(y2),fill}));
    });

    [0,20,40,60,80,100].forEach(v=>{
      const x=sx(v);
      svg.appendChild(el("line",{x1:x,y1:m.t,x2:x,y2:H-m.b,stroke:"rgba(143,163,187,.18)","stroke-width":1}));
      txt(svg,x,H-31,"$"+v,{"text-anchor":"middle",fill:"#8fa3bb","font-size":11});
    });
    [20,40,60,80,100].forEach(v=>{
      const y=sy(v);
      svg.appendChild(el("line",{x1:m.l,y1:y,x2:W-m.r,y2:y,stroke:"rgba(143,163,187,.18)","stroke-width":1}));
      txt(svg,57,y+4,v+"%",{"text-anchor":"end",fill:"#8fa3bb","font-size":11});
    });

    svg.appendChild(el("line",{x1:sx(20),y1:m.t,x2:sx(20),y2:H-m.b,stroke:"#55c7ff","stroke-width":1.3,"stroke-dasharray":"6 6"}));
    svg.appendChild(el("line",{x1:m.l,y1:sy(70),x2:W-m.r,y2:sy(70),stroke:"#55c7ff","stroke-width":1.3,"stroke-dasharray":"6 6"}));

    txt(svg,sx(67),sy(99),"HIGH OPPORTUNITY",{fill:"#8fa3bb","font-size":11,"font-weight":800});
    txt(svg,sx(2),sy(99),"RELIABLE / LOWER VALUE",{fill:"#8fa3bb","font-size":11,"font-weight":800});
    txt(svg,sx(2),sy(24),"LOW VALUE / LOWER RELIABILITY",{fill:"#8fa3bb","font-size":11,"font-weight":800});

    filtered.forEach(d=>{
      const g=el("g",{tabindex:0,role:"button","aria-label":d.name});
      const active=selected===d.name;
      const r=radius(d.sample);
      const c=el("circle",{
        cx:sx(d.median),cy:sy(d.pct10),r,
        fill:active?"rgba(85,199,255,.8)":"rgba(104,170,255,.54)",
        stroke:active?"#55c7ff":"rgba(232,238,247,.78)",
        "stroke-width":active?4:ring(d.bids),
        style:"cursor:pointer"
      });
      const activate=()=>profile(d);
      c.addEventListener("click",activate);
      g.addEventListener("keydown",e=>{
        if(e.key==="Enter"||e.key===" "){e.preventDefault();activate();}
      });
      g.appendChild(c);

      const mode=labels.value;
      if(mode==="all" || (mode==="selected" && active)){
        txt(g,sx(d.median)+r+5,sy(d.pct10)+4,d.name,{
          fill:"#e8eef7","font-size":11,"font-weight":active?750:520
        });
      }
      svg.appendChild(g);
    });

    txt(svg,(m.l+W-m.r)/2,H-10,"Median hammer price",{
      "text-anchor":"middle",fill:"#e8eef7","font-size":13,"font-weight":700
    });
    const y=txt(svg,18,H/2,"Lots clearing $10+",{
      "text-anchor":"middle",fill:"#e8eef7","font-size":13,"font-weight":700
    });
    y.setAttribute("transform","rotate(-90 18 "+H/2+")");
  }

  search.addEventListener("input",render);
  sample.addEventListener("input",render);
  labels.addEventListener("change",render);
  reset.addEventListener("click",()=>{
    selected=null; search.value=""; sample.value="5"; labels.value="all";
    categoryName.textContent="Choose a bubble";
    categorySummary.textContent="Tap or click a category to inspect its resale profile.";
    metrics.innerHTML="";
    render();
  });
  render();
})();