JS = r"""
<script>
(function(){
"use strict";
var D = JSON.parse(document.getElementById("dataset").textContent);
var I = D.items, R = D.recipes, MODS = D.mods, ORDER = D.order;

var BYNAME={}; Object.keys(I).forEach(function(k){ var n=I[k].n; if(!(n in BYNAME)) BYNAME[n]=+k; });
var MODCOL = {vanilla:"#6f7794", thorium:"#3f9e8c", fargo:"#c9552f",
              spirit_reforged:"#7a5cc4", spirit:"#5a80c9", fables:"#c98a24"};
var RARECOL = {"-13":"#e02020","-12":"#8f6fd8","-11":"#e8c33a","-1":"#8b8b8b","0":"#f0f0f0",
  "1":"#9696ff","2":"#96ff96","3":"#ffc896","4":"#ff9696","5":"#ff96ff","6":"#d2a0ff",
  "7":"#96ff0a","8":"#ffff0a","9":"#05c8ff","10":"#ff2864","11":"#b428ff"};

function lum(hex){
  var r=parseInt(hex.substr(1,2),16)/255,g=parseInt(hex.substr(3,2),16)/255,b=parseInt(hex.substr(5,2),16)/255;
  function f(c){return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4);}
  return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b);
}
function el(t,c,txt){var e=document.createElement(t); if(c)e.className=c; if(txt!=null)e.textContent=txt; return e;}

function sprite(it,max){
  var box=el("span","sp");
  if(it.sp){var im=new Image(); im.src=it.sp; im.alt=""; im.className="px"; im.loading="lazy";
    if(max){im.style.maxWidth=max+"px"; im.style.maxHeight=max+"px";}
    box.appendChild(im);}
  return box;
}

function itemBtn(id, qty, isRes){
  var it=I[id];
  var b=el("button","it"+(isRes?" res-it":""));
  b.type="button"; b.dataset.id=id;
  b.title=it.n+(it.tt?" — "+it.tt:"");
  b.appendChild(sprite(it));
  var nm=el("span","nm",it.n);
  if(isRes && RARECOL[String(it.r)]){
    nm.className="nm rar";
    nm.style.setProperty("--rar",RARECOL[String(it.r)]);
    b.style.setProperty("--rar",RARECOL[String(it.r)]);
  }
  b.appendChild(nm);
  if(qty&&qty>1) b.appendChild(el("span","q","×"+qty));
  if(it.own!=="vanilla"){
    var d=el("span","modtick"); d.style.background=MODCOL[it.own]||"#888";
    d.title=MODS[it.own].name; b.appendChild(d);
  }
  return b;
}

/* ---------------- state ---------------- */
var active=new Set(ORDER), q="", onlyChg=false, sel=null;
var eras={pre:true, hard:true};

function recipeMatches(r){
  if(!active.has(r.src)) return false;
  if(onlyChg && !r.chg) return false;
  if(r.phm===true && !eras.pre) return false;
  if(r.phm===false && !eras.hard) return false;
  if(!q) return true;
  var t=I[r.res].n.toLowerCase();
  if(t.indexOf(q)>=0) return true;
  for(var i=0;i<r.ing.length;i++) for(var j=0;j<r.ing[i].length;j++)
    if(I[r.ing[i][j].i].n.toLowerCase().indexOf(q)>=0) return true;
  return false;
}

/* ---------------- table ---------------- */
var tbody=document.getElementById("tbody"), countEl=document.getElementById("count");
function renderTable(){
  tbody.textContent="";
  var shown=0, bySrc={};
  R.forEach(function(r,i){ if(recipeMatches(r)){ (bySrc[r.src]=bySrc[r.src]||[]).push(i); shown++; } });
  ORDER.forEach(function(src){
    var list=bySrc[src]; if(!list||!list.length) return;
    var tr=el("tr","modrow"), th=el("th"); th.colSpan=2;
    th.style.setProperty("--modcol", MODCOL[src]);
    var mr=el("div","mr");
    var sw=el("span","swatch"); sw.style.background=MODCOL[src]; mr.appendChild(sw);
    mr.appendChild(el("span","mn",MODS[src].name));
    mr.appendChild(el("span","mc",list.length+(list.length===1?" combination":" combinations")+" · "+MODS[src].wiki));
    th.appendChild(mr); tr.appendChild(th); tbody.appendChild(tr);

    list.forEach(function(ri){
      var r=R[ri];
      var row=el("tr","rec"); row.dataset.ri=ri;
      var td1=el("td","res");
      td1.appendChild(itemBtn(r.res, r.rq>1?r.rq:0, true));
      if(r.chg){
        var bd=el("span","badge-chg","changed by "+MODS[r.src].short);
        bd.title="This recipe differs from the vanilla one. The mod's version is what the game will use.";
        td1.appendChild(bd);
      }
      if(r.phm!==null && r.phm!==undefined){
        var eb=el("span","era "+(r.phm?"pre":"hard"), r.phm?"pre-hardmode":"hardmode");
        eb.title = r.phm ? "Every ingredient is obtainable before Hardmode."
                         : "Needs " + (r.blk && r.blk.length ? r.blk.join(", ") : "Hardmode content") + ".";
        td1.appendChild(eb);
      }
      if(r.dup!=null){
        var du=el("span","badge-dup","also listed by "+MODS[R[r.dup].src].short);
        td1.appendChild(du);
      }
      row.appendChild(td1);
      var td2=el("td","ing"), ul=el("ul","ing");
      r.ing.forEach(function(g){
        var li=el("li");
        g.forEach(function(e,k){
          if(k) li.appendChild(el("span","orsep","or"));
          li.appendChild(itemBtn(e.i, e.q, false));
        });
        ul.appendChild(li);
      });
      td2.appendChild(ul); row.appendChild(td2); tbody.appendChild(row);
    });
  });
  if(!shown){
    var tr=el("tr"), td=el("td"); td.colSpan=2; td.className="empty";
    var d=el("div","");
    d.appendChild(el("b","Nothing matches"));
    d.appendChild(document.createTextNode("Try a different item name, or turn a source back on."));
    td.appendChild(d); tr.appendChild(td); tbody.appendChild(tr);
  }
  countEl.textContent=shown+" of "+R.length+" combinations";
  markSel();
}

function markSel(){
  var rows=tbody.querySelectorAll("tr.rec");
  for(var i=0;i<rows.length;i++){
    var r=R[+rows[i].dataset.ri];
    var hit=(sel!=null)&&(r.res===sel||r.ing.some(function(g){return g.some(function(e){return e.i===sel;});}));
    rows[i].classList.toggle("sel",!!hit);
  }
}

/* ---------------- detail ---------------- */
var panel=document.getElementById("detail");

function madeBy(id){ return I[id].mk||[]; }

function treeFor(recIdx, depth, seen){
  var r=R[recIdx], ul=el("ul","");
  r.ing.forEach(function(g){
    var li=el("li");
    g.forEach(function(e,k){
      if(k) li.appendChild(el("span","orsep","or"));
      li.appendChild(itemBtn(e.i,e.q,false));
    });
    var first=g[0].i;
    var sub=madeBy(first);
    if(sub.length && depth<5 && seen.indexOf(first)<0){
      var s2=seen.concat([first]);
      li.appendChild(treeFor(sub[0], depth+1, s2));
      if(sub.length>1) li.appendChild(el("div","altline",(sub.length-1)+" other way"+(sub.length>2?"s":"")+" to make this — open it to see them"));
    } else if(!sub.length){
      var it=I[first], hint=acquireHint(it);
      if(hint) li.appendChild(el("span","leafnote",hint));
    }
    ul.appendChild(li);
  });
  return ul;
}

function acquireHint(it){
  if(it.d && it.d.length) return "drop · "+it.d[0].source;
  var tg=(it.tg||[]).join(" ").toLowerCase();
  if(tg.indexOf("vendor")>=0 || it.b) return "bought";
  if(tg.indexOf("fish")>=0) return "fished";
  var l=(it.l||"").toLowerCase();
  if(l.indexOf("dropped by")>=0||l.indexOf("drops from")>=0) return "drop";
  if(l.indexOf("chest")>=0) return "chest";
  if(l.indexOf("purchased")>=0||l.indexOf("sold by")>=0||l.indexOf("bought")>=0) return "bought";
  if(l.indexOf("fish")>=0) return "fished";
  if(l.indexOf("craft")>=0) return "crafted elsewhere";
  return "";
}

function pill(text,cls,style){var p=el("span","pill"+(cls?" "+cls:""),text); if(style)for(var k in style)p.style[k]=style[k]; return p;}

function renderDetail(id, fromUser){
  sel=id; panel.textContent="";
  var it=I[id];

  var head=el("div","d-head");
  var sp=el("div","d-sp"); if(it.sp){var im=new Image(); im.src=it.sp; im.alt=""; im.className="px"; sp.appendChild(im);}
  head.appendChild(sp);
  var t=el("div","d-ttl");
  var h2=el("h2",null,it.n);
  if(RARECOL[String(it.r)]){ h2.className="rar"; h2.style.setProperty("--rar",RARECOL[String(it.r)]); }
  t.appendChild(h2);
  var pl=el("div","pills");
  pl.appendChild(pill(MODS[it.own].name,"mod",{background:MODCOL[it.own]}));
  if(it.rn && RARECOL[String(it.r)]){
    var c=RARECOL[String(it.r)];
    pl.appendChild(pill(it.rn,"rare",{background:c,color:lum(c)>0.5?"#14172b":"#fff"}));
  }
  if(it.hm) pl.appendChild(pill("Hardmode","hm"));
  (it.ty||[]).slice(0,3).forEach(function(x){ pl.appendChild(pill(x)); });
  t.appendChild(pl); head.appendChild(t); panel.appendChild(head);

  if(it.tt){
    var s=el("div","d-sec"); s.appendChild(el("h3",null,"In-game tooltip"));
    var tip=el("div","tip");
    it.tt.split(/\s*·\s*/).forEach(function(line){ if(line.trim()) tip.appendChild(el("span",null,line.trim())); });
    s.appendChild(tip); panel.appendChild(s);
  }

  if(it.grp && it.grp.length){
    var sg=el("div","d-sec");
    sg.appendChild(el("h3",null,"Recipe group — any one of these"));
    sg.appendChild(el("p","groupnote","Not an item. The recipe accepts whichever of these you have, and they can be mixed."));
    var gl=el("div","grouplist");
    it.grp.forEach(function(nme){
      var gid=BYNAME[nme];
      var node;
      if(gid!=null && gid!==+id){ node=el("button","gitem"); node.type="button"; node.dataset.gid=gid; }
      else node=el("span","gitem");
      var g2=I[gid];
      if(g2 && g2.sp){ var box=el("span","gsp"); var im=new Image(); im.src=g2.sp; im.alt=""; im.className="px"; box.appendChild(im); node.appendChild(box); }
      node.appendChild(document.createTextNode(nme));
      gl.appendChild(node);
    });
    sg.appendChild(gl); panel.appendChild(sg);
  }
  if(it.phm===true || it.phm===false){
    var sv2=el("div","d-sec");
    sv2.appendChild(el("h3",null,"Before Hardmode?"));
    var vb=el("div","verdict "+(it.phm?"pre":"hard"));
    vb.appendChild(el("span","mark", it.phm?"\u2713":"\u2717"));
    var vt=el("div","");
    vt.appendChild(el("b",null, it.phm ? "Yes \u2014 obtainable pre-Hardmode"
                                       : "No \u2014 Hardmode only"));
    if(it.pw) vt.appendChild(el("div","reason", it.pw.charAt(0).toUpperCase()+it.pw.slice(1)+"."));
    var mk0=madeBy(id), blk=[];
    mk0.forEach(function(ri){ (R[ri].blk||[]).forEach(function(b){ if(blk.indexOf(b)<0) blk.push(b); }); });
    if(!it.phm && blk.length){
      var bd=el("div","blockers");
      bd.appendChild(document.createTextNode("Blocked by "));
      bd.appendChild(el("b",null,blk.join(", ")));
      sv2.appendChild(vb);
      vt.appendChild(bd);
    }
    vb.appendChild(vt);
    if(!sv2.firstChild || sv2.lastChild!==vb) sv2.appendChild(vb);
    panel.appendChild(sv2);
  }
  var sHow=el("div","d-sec"); sHow.appendChild(el("h3",null,"How to get it"));
  if(it.l) sHow.appendChild(el("p","lead",it.l));
  else sHow.appendChild(el("p","lead","No description on the source wiki. Follow the link below."));
  panel.appendChild(sHow);

  if(it.d && it.d.length){
    var sd=el("div","d-sec"); sd.appendChild(el("h3",null,"Dropped by"));
    var tb=el("table","drops"), hr=el("tr");
    ["Source","Qty","Rate"].forEach(function(h,i){ var th=el("th",i?(i===1?"qty":"rate"):null,h); hr.appendChild(th); });
    var thead=el("thead"); thead.appendChild(hr); tb.appendChild(thead);
    var tb2=el("tbody");
    it.d.forEach(function(dr){
      var tr=el("tr");
      tr.appendChild(el("td",null,dr.source));
      tr.appendChild(el("td","qty",dr.qty||"—"));
      tr.appendChild(el("td","rate",dr.rate||"—"));
      tb2.appendChild(tr);
    });
    tb.appendChild(tb2); sd.appendChild(tb); panel.appendChild(sd);
  }

  var mk=madeBy(id);
  if(mk.length){
    var sc=el("div","d-sec");
    sc.appendChild(el("h3",null,mk.length===1?"Combines from":"Combines from ("+mk.length+" ways)"));
    mk.forEach(function(ri){
      var r=R[ri], g=el("div","recgroup");
      var meta=el("div","recmeta");
      var sw=el("span","swatch"); sw.style.cssText="width:8px;height:8px;border-radius:2px;display:inline-block;background:"+MODCOL[r.src];
      meta.appendChild(sw);
      meta.appendChild(document.createTextNode(MODS[r.src].name+(r.chg?" — changed from vanilla":"")));
      g.appendChild(meta);
      var root=el("ul","tree"); root.appendChild(treeFor(ri,0,[id]));
      g.appendChild(root.firstChild ? root : root);
      sc.appendChild(g);
    });
    panel.appendChild(sc);
  }

  var ui=(it.ui||[]);
  if(ui.length){
    var su=el("div","d-sec"); su.appendChild(el("h3",null,"Used to make"));
    var box=el("div","usedin");
    ui.forEach(function(ri){
      var r=R[ri], line=el("div","");
      line.appendChild(itemBtn(r.res,0,false));
      if(r.src!=="vanilla"){ var sm=el("span","leafnote",MODS[r.src].short); line.appendChild(sm); }
      box.appendChild(line);
    });
    su.appendChild(box); panel.appendChild(su);
  }

  var kv=[];
  if(it.b) kv.push(["Buy",it.b]);
  if(it.s) kv.push(["Sell",it.s]);
  if(it.df) kv.push(["Defense",it.df]);
  if(kv.length){
    var sv=el("div","d-sec"); sv.appendChild(el("h3",null,"Value"));
    var dl=el("dl","kv");
    kv.forEach(function(p){ var d=el("div"); d.appendChild(el("dt",null,p[0])); d.appendChild(el("dd",null,p[1])); dl.appendChild(d); });
    sv.appendChild(dl); panel.appendChild(sv);
  }

  var sl=el("div","d-sec");
  var a=el("a","wikilink",it.n+" on "+it.h+" ↗");
  a.href=it.u; a.target="_blank"; a.rel="noopener noreferrer";
  sl.appendChild(a); panel.appendChild(sl);

  markSel();
  if(!fromUser) return;                                   /* never move the page on first paint */
  if(window.matchMedia("(max-width:1080px)").matches) panel.scrollIntoView({behavior:"smooth",block:"start"});
  else panel.scrollTop=0;
}

/* ---------------- events ---------------- */
document.addEventListener("click",function(ev){
  var gb=ev.target.closest("button.gitem");
  if(gb){ renderDetail(+gb.dataset.gid, true); return; }
  var b=ev.target.closest(".it");
  if(b){ renderDetail(+b.dataset.id, true); }
});

var searchEl=document.getElementById("q");
searchEl.addEventListener("input",function(){ q=searchEl.value.trim().toLowerCase(); renderTable(); });
document.getElementById("clearq").addEventListener("click",function(){ searchEl.value=""; q=""; renderTable(); searchEl.focus(); });

document.querySelectorAll(".chip[data-src]").forEach(function(c){
  c.addEventListener("click",function(){
    var s=c.dataset.src;
    if(active.has(s)) active.delete(s); else active.add(s);
    if(!active.size){ ORDER.forEach(function(x){active.add(x);}); }
    document.querySelectorAll(".chip[data-src]").forEach(function(x){
      x.setAttribute("aria-pressed", active.has(x.dataset.src)?"true":"false");
    });
    renderTable();
  });
});
document.querySelectorAll(".chip[data-era]").forEach(function(c){
  c.addEventListener("click",function(){
    var e=c.dataset.era;
    eras[e]=!eras[e];
    if(!eras.pre && !eras.hard){ eras.pre=true; eras.hard=true; }
    document.querySelectorAll(".chip[data-era]").forEach(function(x){
      x.setAttribute("aria-pressed", eras[x.dataset.era]?"true":"false");
    });
    renderTable();
  });
});
var chgBtn=document.getElementById("chgtoggle");
chgBtn.addEventListener("click",function(){
  onlyChg=!onlyChg; chgBtn.setAttribute("aria-pressed",onlyChg?"true":"false"); renderTable();
});

renderTable();
renderDetail(window.__INITIAL__);
})();
</script>
"""
