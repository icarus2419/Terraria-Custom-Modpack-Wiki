import logo as _logo

CSS = r"""
<meta name="viewport" content="width=device-width, initial-scale=1">
@@ICONS@@<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Pixelify+Sans:wght@400;500;600;700&family=Asap:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700&display=swap">
<title>Joseph's Modpack Wiki</title>
<style>
:root{
  --bg:#efe9df; --surface:#fbf8f3; --surface-2:#f2ece2; --surface-3:#e6ded1;
  --line:#d9cfc0; --line-strong:#bfb2a0;
  --ink:#221b15; --ink-2:#5b4f44; --ink-3:#736556;
  --brass:#a8560b; --brass-bright:#8f4708; --brass-soft:#f7e4cd; --brass-line:#d8b98a;
  --flag:#b23a1c; --flag-soft:#f9e0d6;
  --tip-bg:#221b15; --tip-ink:#f4efe8;
  --shadow:0 1px 2px rgba(25,29,48,.07), 0 8px 24px -12px rgba(25,29,48,.18);
  --radius:7px;
  --slot-bg:#e4dccf; --slot-line:#c8bcaa; --slot-in:rgba(255,255,255,.85);
  --pre:#0d6b5e; --pre-soft:#d7efe9; --pre-line:#7fc4b6;
  --hard:#b23a1c; --hard-soft:#f9e0d6; --hard-line:#dda893;
  --rar-blend:#14100e; --rar-amt:48%;
  --ui-shadow:none; --wordshadow:rgba(34,27,21,.16); --grid:rgba(34,27,21,.075);
  color-scheme:light;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --bg:#14100e; --surface:#1c1714; --surface-2:#241d19; --surface-3:#2e2621;
    --line:#3a302a; --line-strong:#4e4139;
    --ink:#f4efe8; --ink-2:#c2b5a6; --ink-3:#8e8175;
    --brass:#ff9d3d; --brass-bright:#ffb968; --brass-soft:#3a2410; --brass-line:#7a4f1e;
    --flag:#ff7a5c; --flag-soft:#3d1c14;
    --tip-bg:#0c0908; --tip-ink:#f4efe8;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 28px -14px rgba(0,0,0,.7);
    --slot-bg:#2a221d; --slot-line:#40352d; --slot-in:rgba(255,255,255,.07);
    --pre:#5fd3bd; --pre-soft:#0f3a34; --pre-line:#2a6b60;
    --hard:#ff7a5c; --hard-soft:#3d1c14; --hard-line:#7a3626;
    --rar-blend:#14100e; --rar-amt:0%;
    --ui-shadow:0 1px 0 rgba(0,0,0,.6); --wordshadow:rgba(0,0,0,.7); --grid:rgba(255,190,120,.055);
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#14100e; --surface:#1c1714; --surface-2:#241d19; --surface-3:#2e2621;
  --line:#3a302a; --line-strong:#4e4139;
  --ink:#f4efe8; --ink-2:#c2b5a6; --ink-3:#8e8175;
  --brass:#ff9d3d; --brass-bright:#ffb968; --brass-soft:#3a2410; --brass-line:#7a4f1e;
  --flag:#ff7a5c; --flag-soft:#3d1c14;
  --tip-bg:#0c0908; --tip-ink:#f4efe8;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 28px -14px rgba(0,0,0,.7);
  --slot-bg:#2a221d; --slot-line:#40352d; --slot-in:rgba(255,255,255,.07);
  --pre:#5fd3bd; --pre-soft:#0f3a34; --pre-line:#2a6b60;
  --hard:#ff7a5c; --hard-soft:#3d1c14; --hard-line:#7a3626;
  --rar-blend:#14100e; --rar-amt:0%;
  --ui-shadow:0 1px 0 rgba(0,0,0,.6); --wordshadow:rgba(0,0,0,.7); --grid:rgba(255,190,120,.055);
  color-scheme:dark;
}

*{box-sizing:border-box}
body{
  background:var(--bg); color:var(--ink);
  font-family:"Asap","Segoe UI",system-ui,-apple-system,sans-serif;
  font-size:15px; line-height:1.5;
  -webkit-font-smoothing:antialiased;
}
img{display:block}
.px{image-rendering:pixelated; image-rendering:crisp-edges}
a{color:var(--brass); text-decoration-thickness:1px; text-underline-offset:2px}
a:hover{color:var(--brass-bright)}
:focus-visible{outline:2px solid var(--brass-bright); outline-offset:2px; border-radius:3px}

.wrap{max-width:1420px; margin:0 auto; padding:0 20px}

/* ---------- masthead ---------- */
.masthead{
  position:relative; overflow:hidden;
  border-bottom:2px solid var(--brass-line);
  background:
    linear-gradient(180deg, color-mix(in srgb,var(--brass-soft) 55%, var(--surface)) 0%, var(--surface) 100%);
}
.masthead::after{
  content:""; position:absolute; inset:0; pointer-events:none; z-index:0;
  background-image:
    repeating-linear-gradient(0deg, transparent 0 3px, var(--grid) 3px 4px),
    repeating-linear-gradient(90deg, transparent 0 3px, var(--grid) 3px 4px);
}
.mast-in{position:relative; z-index:1; display:flex; flex-wrap:wrap; gap:22px 34px; align-items:flex-end; padding:26px 0 20px}
.brandline{display:flex; align-items:center; gap:14px; min-width:0}
.station{
  width:52px; height:52px; flex:none; padding:7px;
  background:var(--surface); border:1px solid var(--brass-line); border-radius:var(--radius);
  box-shadow:var(--shadow);
}
.station img{width:100%; height:100%; object-fit:contain}
h1{
  font-family:"Pixelify Sans","Asap",sans-serif; font-weight:600;
  font-size:clamp(26px,3.6vw,40px); line-height:1; margin:0 0 5px;
  letter-spacing:.01em; text-wrap:balance;
  text-shadow:2px 2px 0 var(--wordshadow);
}
/* wordmark: the owner's name recedes so the thing itself carries the ember */
h1 .wm-a{color:var(--ink-2)}
h1 .wm-b{color:var(--brass)}
h1 .wm-rule{display:block; width:2.2em; height:3px; margin-top:10px;
  background:linear-gradient(90deg, var(--brass), transparent)}
.tagline{margin:0; color:var(--ink-2); font-size:14.5px; max-width:62ch}
/* the compact masthead every page uses: a name and one line, not a title card */
.masthead.slim .mast-in{padding:14px 0 12px}
.masthead.slim h1{font-size:clamp(22px,2.4vw,30px); margin:0 0 3px}
.masthead.slim .tagline{font-size:13.5px; max-width:none}
.masthead.slim .tagline .dim{color:var(--ink-3)}
.masthead.slim .brandline{flex:1 1 100%}
.tagline b{color:var(--ink); font-weight:600}
.eyebrow{
  font-family:"Pixelify Sans",sans-serif; font-size:10.5px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--brass); margin:0 0 5px;
}
.sectionbar{
  display:flex; align-items:center; gap:12px; padding:14px 16px;
  border-bottom:1px solid var(--line); position:relative; overflow:hidden;
  background:
    radial-gradient(120% 180% at 0% 0%, color-mix(in srgb,var(--brass) 13%, transparent), transparent 62%),
    linear-gradient(180deg,var(--surface-2),var(--surface));
}
.sectionbar::after{
  content:""; position:absolute; left:0; right:0; bottom:0; height:1px;
  background:linear-gradient(90deg, var(--brass), transparent 70%);
}
.sectionbar .sbsp{
  width:40px; height:40px; flex:none; display:grid; place-items:center;
  background:linear-gradient(180deg, color-mix(in srgb,var(--brass) 20%, var(--slot-bg)), var(--slot-bg));
  border:1px solid var(--brass-line); border-radius:5px;
  box-shadow:inset 0 1px 0 var(--slot-in), 0 0 14px -6px var(--brass);
}
.sectionbar .sbsp img{max-width:28px; max-height:28px; width:auto; height:auto}
.sectionbar h2{margin:0; font-family:"Pixelify Sans",sans-serif; font-weight:600; font-size:19px; line-height:1.1; text-shadow:1px 1px 0 var(--wordshadow)}
.sectionbar .sbnote{
  margin-left:auto; font-family:"JetBrains Mono",monospace; font-size:11.5px;
  color:var(--ink-3); text-align:right;
}
@media (max-width:560px){ .sectionbar .sbnote{display:none} }
.meta{display:flex; gap:26px; margin:0 0 3px; flex-wrap:wrap}
.meta div{display:flex; flex-direction:column; gap:1px}
.meta dt{
  font-family:"Pixelify Sans",sans-serif; font-size:10.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3);
}
.meta dd{
  margin:0; font-family:"JetBrains Mono",ui-monospace,monospace; font-weight:700;
  font-size:19px; font-variant-numeric:tabular-nums; color:var(--ink);
}

/* ---------- controls ---------- */
.controls{
  position:sticky; top:0; z-index:30; background:var(--bg);
  border-bottom:1px solid var(--line); padding:11px 0;
}
.ctl-in{display:flex; gap:12px; align-items:center; flex-wrap:wrap}
/* on a phone the chips wrap to 300px of filters; pinning that to the top leaves no room
   for results, so let the whole bar scroll away */
@media (max-width:760px){
  .controls{position:static; padding:9px 0}
  .ctl-in{gap:8px}
  .chip{padding:3px 9px; font-size:11.5px}
}
.search{position:relative; flex:1 1 250px; min-width:200px; max-width:360px}
.search input{
  width:100%; font:inherit; font-size:14.5px; color:var(--ink);
  background:var(--surface); border:1px solid var(--line-strong); border-radius:var(--radius);
  padding:8px 30px 8px 11px;
}
.search input::placeholder{color:var(--ink-3)}
.search input:focus{border-color:var(--brass); outline:none; box-shadow:0 0 0 3px color-mix(in srgb,var(--brass) 20%, transparent)}
.clearx{
  position:absolute; right:5px; top:50%; transform:translateY(-50%);
  border:0; background:none; color:var(--ink-3); cursor:pointer; font-size:17px;
  line-height:1; padding:4px 6px; border-radius:4px;
}
.clearx:hover{color:var(--ink)}
.chips{display:flex; gap:6px; flex-wrap:wrap}
.chip{
  font:inherit; font-size:12.5px; font-weight:600; cursor:pointer;
  padding:6px 11px; border-radius:100px; border:1px solid var(--line-strong);
  background:var(--surface); color:var(--ink-2); display:inline-flex; gap:6px; align-items:center;
}
.chip .n{font-family:"JetBrains Mono",monospace; font-size:11px; color:var(--ink-3); font-variant-numeric:tabular-nums}
.chip:hover{border-color:var(--brass-line); color:var(--ink)}
.chip[aria-pressed="true"]{
  background:var(--brass-soft); border-color:var(--brass-line); color:var(--brass);
}
.chip[aria-pressed="true"] .n{color:var(--brass)}
.chip.flagchip[aria-pressed="true"]{background:var(--flag-soft); border-color:var(--flag); color:var(--flag)}
.chip.flagchip[aria-pressed="true"] .n{color:var(--flag)}
.chipsep{width:1px; align-self:stretch; background:var(--line-strong); margin:0 2px}
.chip.phmchip[aria-pressed="true"]{background:var(--pre-soft); border-color:var(--pre-line); color:var(--pre)}
.chip.phmchip[aria-pressed="true"] .n{color:var(--pre)}
.chip.hmchip[aria-pressed="true"]{background:var(--hard-soft); border-color:var(--hard-line); color:var(--hard)}
.chip.hmchip[aria-pressed="true"] .n{color:var(--hard)}
.spacer{flex:1}
.count{font-family:"JetBrains Mono",monospace; font-size:12px; color:var(--ink-3); font-variant-numeric:tabular-nums}

/* ---------- layout ---------- */
.layout{display:grid; grid-template-columns:minmax(0,1fr) 396px; gap:26px; align-items:start; padding:22px 0 60px}
@media (max-width:1080px){ .layout{grid-template-columns:minmax(0,1fr)} }

/* ---------- crafting table ---------- */
.tablecard{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); overflow:hidden; box-shadow:var(--shadow)}
.tscroll{overflow-x:auto}
table.crafts{width:100%; border-collapse:collapse; font-size:14px}
table.crafts th{
  text-align:left; font-family:"Pixelify Sans",sans-serif; font-weight:500;
  font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3);
  padding:9px 14px; background:var(--surface-2); border-bottom:1px solid var(--line);
  position:sticky; top:0; z-index:2;
}
table.crafts th.c-res{width:34%}
tr.modrow th{
  background:var(--surface-3); color:var(--ink); font-size:11.5px; letter-spacing:.08em;
  border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:7px 14px;
  position:static; box-shadow:inset 4px 0 0 var(--modcol,var(--line-strong));
}
tr.modrow .mr{display:flex; align-items:center; gap:9px; flex-wrap:wrap}
tr.modrow .swatch{width:9px; height:9px; border-radius:2px; flex:none}
tr.modrow .mn{font-family:"Pixelify Sans",sans-serif}
tr.modrow .mc{font-family:"JetBrains Mono",monospace; font-size:10.5px; color:var(--ink-3); letter-spacing:0; text-transform:none}
tbody tr.rec{border-bottom:1px solid var(--line)}
tbody tr.rec:last-child{border-bottom:0}
tbody tr.rec:hover{background:var(--surface-2)}
tbody tr.rec.sel{background:color-mix(in srgb, var(--brass) 11%, transparent)}
tbody tr.rec.sel td.res{box-shadow:inset 4px 0 0 var(--brass)}
td{padding:10px 14px; vertical-align:middle}
td.res{border-right:1px solid var(--line); position:relative}
td.ing{position:relative}
td.ing::before{
  content:"="; position:absolute; left:-9px; top:12px;
  font-family:"JetBrains Mono",monospace; font-size:13px; font-weight:700; color:var(--brass);
  opacity:.55;
}
tbody tr.rec:hover td.ing::before{opacity:1}

.it{
  display:inline-flex; align-items:center; gap:7px; cursor:pointer;
  background:none; border:0; padding:2px 4px 2px 2px; margin:-2px 0; border-radius:5px;
  font:inherit; color:var(--ink); text-align:left; line-height:1.3;
}
.it:hover{background:color-mix(in srgb,var(--brass) 15%, transparent)}
.it .sp{
  width:34px; height:34px; flex:none; display:grid; place-items:center;
  background:
    linear-gradient(180deg, color-mix(in srgb,var(--slot-in) 55%, transparent), transparent 62%),
    var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:4px;
  box-shadow:inset 0 1px 0 var(--slot-in), 0 1px 1px rgba(0,0,0,.10);
}
.it .sp img{max-width:26px; max-height:26px; width:auto; height:auto}
.it:hover .sp{border-color:var(--brass); box-shadow:inset 0 1px 0 var(--slot-in), 0 0 0 2px color-mix(in srgb,var(--brass) 30%, transparent)}
.it .nm{min-width:0}
.it .q{
  font-family:"JetBrains Mono",monospace; font-size:12px; font-weight:600;
  color:var(--ink-3); font-variant-numeric:tabular-nums;
}
.it.res-it{font-weight:600}
.it.res-it .sp{
  border-color:color-mix(in srgb, var(--rar,var(--slot-line)) 60%, var(--slot-line));
  box-shadow:inset 0 1px 0 var(--slot-in), 0 0 0 1px color-mix(in srgb,var(--rar,transparent) 22%, transparent),
             0 0 10px -2px color-mix(in srgb,var(--rar,transparent) 45%, transparent);
}
.it .vrt{font-size:9.5px; letter-spacing:.04em; text-transform:uppercase; color:var(--brass);
  border:1px solid var(--brass-line); border-radius:100px; padding:0 5px; white-space:nowrap;
  font-family:"Pixelify Sans",sans-serif}
.rar{color:var(--rar); color:color-mix(in srgb, var(--rar) calc(100% - var(--rar-amt)), var(--rar-blend)); text-shadow:var(--ui-shadow)}
.modtick{width:5px; height:5px; border-radius:50%; flex:none; margin-left:1px}

ul.ing{list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; align-items:center; gap:3px 4px}
ul.ing li{display:flex; align-items:center; gap:4px; flex-wrap:wrap}
ul.ing li + li::before{
  content:"+"; font-family:"JetBrains Mono",monospace; font-size:13px; font-weight:700;
  color:var(--ink-3); flex:none; margin-right:4px; line-height:1;
}
ul.ing li:first-child::before{
  content:""; width:0; flex:none; margin:0;
}
.orsep{font-size:11.5px; font-style:italic; color:var(--ink-3); padding:0 1px}

.badge-chg{
  display:inline-flex; align-items:center; gap:4px; margin-left:7px; vertical-align:middle;
  font-family:"Pixelify Sans",sans-serif; font-size:10px; letter-spacing:.05em; text-transform:uppercase;
  color:var(--flag); background:var(--flag-soft); border:1px solid color-mix(in srgb,var(--flag) 40%, transparent);
  padding:1px 6px; border-radius:100px; white-space:nowrap;
}
.era{
  display:inline-flex; align-items:center; gap:3px; margin-left:7px; vertical-align:middle;
  font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.06em; text-transform:uppercase;
  padding:1px 6px; border-radius:100px; white-space:nowrap; border:1px solid;
}
.era.pre{color:var(--pre); background:var(--pre-soft); border-color:var(--pre-line)}
.era.hard{color:var(--hard); background:var(--hard-soft); border-color:var(--hard-line)}
.verdict{
  display:flex; gap:10px; align-items:flex-start; padding:10px 11px; border-radius:5px;
  border:1px solid; font-size:13px; line-height:1.45;
}
.verdict.pre{background:var(--pre-soft); border-color:var(--pre-line); color:var(--ink)}
.verdict.hard{background:var(--hard-soft); border-color:var(--hard-line); color:var(--ink)}
.verdict .mark{font-size:16px; line-height:1.2; flex:none; font-weight:700}
.verdict.pre .mark{color:var(--pre)}
.verdict.hard .mark{color:var(--hard)}
.verdict b{display:block; margin-bottom:1px}
.verdict .reason{color:var(--ink-2); font-size:12.5px}
.blockers{margin-top:6px; font-size:12px; color:var(--ink-2)}
.blockers b{display:inline; font-weight:600; color:var(--hard)}
.badge-dup{
  display:inline-block; margin-left:7px; font-size:10.5px; color:var(--ink-3);
  font-style:italic; white-space:nowrap;
}
.empty{padding:44px 18px; text-align:center; color:var(--ink-3)}
.empty b{display:block; color:var(--ink); font-size:16px; margin-bottom:5px; font-family:"Pixelify Sans",sans-serif}

/* ---------- detail panel ---------- */
.detail{position:sticky; top:64px; max-height:calc(100vh - 84px); overflow-y:auto;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  box-shadow:var(--shadow);}
@media (max-width:1080px){ .detail{position:static; max-height:none} }
.d-head{display:flex; gap:14px; padding:16px 16px 13px; border-bottom:1px solid var(--line);
  background:linear-gradient(180deg, var(--surface-2), var(--surface))}
.d-sp{
  width:64px; height:64px; flex:none; display:grid; place-items:center;
  background:var(--slot-bg); border:1px solid var(--brass-line); border-radius:4px;
  box-shadow:inset 0 1px 0 var(--slot-in);
}
.d-ttl h2.rar{text-shadow:var(--ui-shadow)}
.grouplist{display:flex; flex-wrap:wrap; gap:5px}
.gitem{
  display:inline-flex; align-items:center; gap:6px; font-size:12.5px;
  background:var(--surface-2); border:1px solid var(--line); border-radius:100px;
  padding:3px 10px 3px 4px; color:var(--ink);
}
button.gitem{cursor:pointer; font-family:inherit}
button.gitem:hover{border-color:var(--brass); color:var(--brass)}
.gitem .gsp{width:22px;height:22px;display:grid;place-items:center;background:var(--slot-bg);
  border:1px solid var(--slot-line); border-radius:3px; flex:none}
.gitem .gsp img{max-width:17px;max-height:17px;width:auto;height:auto}
.groupnote{font-size:12px; color:var(--ink-3); margin:0 0 8px; font-style:italic}
.d-sp img{max-width:46px; max-height:46px; width:auto; height:auto}
.d-ttl{min-width:0; flex:1}
.d-ttl h2{margin:0 0 6px; font-size:19px; line-height:1.2; font-weight:700; text-wrap:balance}
.pills{display:flex; gap:5px; flex-wrap:wrap}
.pill{
  font-size:10.5px; font-weight:600; letter-spacing:.04em; text-transform:uppercase;
  padding:2px 7px; border-radius:100px; border:1px solid var(--line-strong); color:var(--ink-2);
  font-family:"Pixelify Sans",sans-serif; white-space:nowrap;
}
.pill.rare{border-color:transparent}
.pill.hm{background:var(--flag-soft); color:var(--flag); border-color:color-mix(in srgb,var(--flag) 35%, transparent)}
.pill.mod{border-color:transparent; color:#fff}

.d-sec{padding:14px 16px; border-bottom:1px solid var(--line)}
.d-sec:last-child{border-bottom:0}
.d-sec h3{
  margin:0 0 8px; font-family:"Pixelify Sans",sans-serif; font-weight:500;
  font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3);
}
.tip{
  background:var(--tip-bg); color:var(--tip-ink); border-radius:5px; padding:9px 11px;
  font-size:13px; line-height:1.45; border:1px solid color-mix(in srgb,var(--brass) 30%, transparent);
}
.tip span{display:block}
.lead{margin:0; font-size:13.5px; line-height:1.55; color:var(--ink-2)}
.lead em{color:var(--ink); font-style:normal; font-weight:600}

table.drops{width:100%; border-collapse:collapse; font-size:12.5px}
table.drops th{
  text-align:left; font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3); font-weight:500; padding:0 8px 5px 0; position:static; background:none; border:0;
}
table.drops td{padding:4px 8px 4px 0; border-top:1px solid var(--line); vertical-align:top}
table.drops td.rate,table.drops td.qty{font-family:"JetBrains Mono",monospace; font-variant-numeric:tabular-nums; white-space:nowrap; color:var(--ink-2)}
table.drops th.rate,table.drops th.qty{text-align:right}
table.drops td.rate,table.drops td.qty{text-align:right; padding-right:0}

.kv{display:flex; gap:20px; flex-wrap:wrap; font-size:13px}
.kv div{display:flex; flex-direction:column; gap:1px}
.kv dt{font-family:"Pixelify Sans",sans-serif; font-size:9.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-3)}
.kv dd{margin:0; font-family:"JetBrains Mono",monospace; font-size:12.5px; color:var(--ink)}

/* recipe tree */
.tree{list-style:none; margin:0; padding:0; font-size:13px}
.tree ul{list-style:none; margin:3px 0 3px 12px; padding:0 0 0 13px; border-left:1px solid var(--line-strong)}
.tree li{position:relative; padding:1.5px 0}
.tree ul>li::before{
  content:""; position:absolute; left:-13px; top:15px; width:9px; height:1px; background:var(--line-strong);
}
.tree .leafnote{font-size:11.5px; color:var(--ink-3); margin-left:5px; font-style:italic}
.altline{font-size:11.5px; color:var(--ink-3); margin:5px 0 2px; font-style:italic}
.recgroup + .recgroup{margin-top:11px; padding-top:11px; border-top:1px dashed var(--line-strong)}
.recmeta{font-size:11px; color:var(--ink-3); margin-bottom:5px; display:flex; align-items:center; gap:6px}
.usedin{display:flex; flex-direction:column; gap:2px}
.wikilink{font-size:12.5px}
.hint{padding:34px 18px; text-align:center; color:var(--ink-3); font-size:13.5px}
.hint b{display:block; font-family:"Pixelify Sans",sans-serif; color:var(--ink); font-size:15px; margin-bottom:6px}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--line); background:var(--surface); padding:22px 0 34px; font-size:12.5px; color:var(--ink-2)}
footer .fgrid{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:20px 34px}
footer h2.fh{margin:0 0 6px; font-family:"Pixelify Sans",sans-serif; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3); font-weight:500}
footer p{margin:0 0 7px; line-height:1.55; max-width:60ch}
footer ul{margin:0; padding-left:16px; line-height:1.6}
.note-warn{border-left:2px solid var(--flag); padding-left:10px}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
</style>
"""

CSS = CSS.replace("@@ICONS@@", _logo.head_links())
