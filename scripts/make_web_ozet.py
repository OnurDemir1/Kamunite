#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.json + ozet.json -> tek dosyalik, telefon uyumlu ozet.html uretir."""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

index = json.load(open(os.path.join(DATA, "index.json"), encoding="utf-8"))
ozet = json.load(open(os.path.join(DATA, "ozet.json"), encoding="utf-8"))

payload = json.dumps({"index": index, "ozet": ozet}, ensure_ascii=False)

HTML = """<title>KPSS Kadro Veri Seti — Özet</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --bg:#F5F7FA; --surface:#FFFFFF; --surface2:#FBFCFE;
  --ink:#151A21; --muted:#5A6472; --line:#E2E7EF;
  --accent:#1E4FD6; --accent-soft:#EAF0FE;
  --ok:#158A55; --ok-soft:#E6F5EE; --warn:#B4700A; --warn-soft:#FBF1DE;
  --shadow:0 1px 2px rgba(20,30,50,.06),0 8px 24px rgba(20,30,50,.06);
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0D1015; --surface:#151A22; --surface2:#12161D;
  --ink:#E7ECF3; --muted:#94A1B4; --line:#242D3A;
  --accent:#6C97FF; --accent-soft:#172542;
  --ok:#35B57C; --ok-soft:#122A20; --warn:#E0A32E; --warn-soft:#2A2110;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.35);
}}
:root[data-theme="light"]{
  --bg:#F5F7FA; --surface:#FFFFFF; --surface2:#FBFCFE; --ink:#151A21; --muted:#5A6472;
  --line:#E2E7EF; --accent:#1E4FD6; --accent-soft:#EAF0FE; --ok:#158A55; --ok-soft:#E6F5EE;
  --warn:#B4700A; --warn-soft:#FBF1DE; --shadow:0 1px 2px rgba(20,30,50,.06),0 8px 24px rgba(20,30,50,.06);
}
:root[data-theme="dark"]{
  --bg:#0D1015; --surface:#151A22; --surface2:#12161D; --ink:#E7ECF3; --muted:#94A1B4;
  --line:#242D3A; --accent:#6C97FF; --accent-soft:#172542; --ok:#35B57C; --ok-soft:#122A20;
  --warn:#E0A32E; --warn-soft:#2A2110; --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  line-height:1.5;-webkit-text-size-adjust:100%}
.wrap{max-width:980px;margin:0 auto;padding:28px 18px 64px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-size:clamp(26px,6vw,40px);line-height:1.1;margin:.28em 0 .1em;text-wrap:balance;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:15px;margin:0 0 22px;max-width:60ch}
.mono{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
/* KPI */
.kpis{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:22px 0}
@media(min-width:680px){.kpis{grid-template-columns:repeat(4,1fr)}}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 16px 14px;box-shadow:var(--shadow)}
.kpi .n{font-family:ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums;
  font-size:clamp(22px,5.4vw,30px);font-weight:700;letter-spacing:-.02em}
.kpi .l{font-size:12.5px;color:var(--muted);margin-top:3px}
.kpi.good .n{color:var(--ok)}
/* card */
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:var(--shadow);margin:20px 0}
.card h2{font-size:16px;margin:0 0 4px;letter-spacing:-.01em}
.card .k{font-size:13px;color:var(--muted);margin:0 0 12px}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;
  padding:3px 9px;border-radius:999px;border:1px solid transparent;white-space:nowrap}
.badge.ok{color:var(--ok);background:var(--ok-soft);border-color:color-mix(in srgb,var(--ok) 25%,transparent)}
.badge.warn{color:var(--warn);background:var(--warn-soft);border-color:color-mix(in srgb,var(--warn) 30%,transparent)}
.checktable{width:100%;border-collapse:collapse;font-size:13.5px}
.checktable th,.checktable td{padding:7px 8px;text-align:right;border-bottom:1px solid var(--line)}
.checktable th:first-child,.checktable td:first-child{text-align:left}
.checktable td.n,.checktable th.n{font-family:ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
.checktable tr:last-child td{border-bottom:none;font-weight:700}
/* controls */
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:26px 0 10px}
.controls h2{font-size:17px;margin:0;margin-right:auto;letter-spacing:-.01em}
input[type=search]{font:inherit;font-size:14px;padding:8px 12px;border-radius:10px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);min-width:150px}
input[type=search]:focus{outline:2px solid var(--accent);outline-offset:1px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:var(--surface);box-shadow:var(--shadow)}
table.grid{border-collapse:collapse;width:100%;font-size:13.5px;min-width:640px}
table.grid th,table.grid td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
table.grid th:first-child,table.grid td:first-child{text-align:left;position:sticky;left:0;background:var(--surface)}
table.grid thead th{position:sticky;top:0;background:var(--surface2);color:var(--muted);font-size:11.5px;
  letter-spacing:.06em;text-transform:uppercase;cursor:pointer;user-select:none;z-index:2}
table.grid thead th:first-child{z-index:3}
table.grid td.n{font-family:ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
table.grid tbody tr:hover td{background:var(--accent-soft)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;vertical-align:middle;margin-right:6px}
.dot.ok{background:var(--ok)} .dot.warn{background:var(--warn)}
.note{font-size:13.5px;color:var(--muted);margin:14px 2px 0}
footer{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}
a{color:var(--accent)}
</style>

<div class="wrap">
  <div class="eyebrow">KPSS Merkezi Yerleştirme · 2012 – 2026</div>
  <h1>Kadro Veri Seti — Özet</h1>
  <p class="sub">Tüm KPSS dönemlerinin açılan kadroları ve detayları (EKPSS hariç),
     ÖSYM resmî rakamlarıyla doğrulanmış olarak derli toplu indirildi.</p>

  <div class="kpis" id="kpis"></div>

  <div class="card">
    <h2>Resmî ÖSYM çapraz kontrolü — KPSS-2024/1 <span class="badge ok">BİREBİR</span></h2>
    <p class="k">Kaynak: ÖSYM “Yerleştirme Sonuçlarına İlişkin Sayısal Bilgiler” PDF ↔ bu veri seti</p>
    <table class="checktable">
      <thead><tr><th>Öğrenim</th><th class="n">ÖSYM kont.</th><th class="n">Bizim kont.</th><th class="n">Yerleşen</th></tr></thead>
      <tbody>
        <tr><td>Lisans</td><td class="n">1.046</td><td class="n">1.046</td><td class="n">1.046</td></tr>
        <tr><td>Önlisans</td><td class="n">615</td><td class="n">615</td><td class="n">615</td></tr>
        <tr><td>Ortaöğretim</td><td class="n">155</td><td class="n">155</td><td class="n">155</td></tr>
        <tr><td>TOPLAM</td><td class="n">1.816</td><td class="n">1.816</td><td class="n">1.816</td></tr>
      </tbody>
    </table>
  </div>

  <div class="controls">
    <h2>Dönem bazlı</h2>
    <input type="search" id="q" placeholder="Dönem ara… (ör. 2025, 2019-2)" aria-label="Dönem ara">
  </div>
  <div class="tablewrap">
    <table class="grid" id="tbl">
      <thead><tr>
        <th data-k="id">Dönem</th>
        <th data-k="scraped_kadro" class="n">Kadro</th>
        <th data-k="scraped_kontenjan" class="n">Kontenjan</th>
        <th data-k="stated_basvuran" class="n">Başvuran</th>
        <th data-k="stated_yerlesen" class="n">Yerleşen</th>
        <th data-k="durum">Durum</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <p class="note" id="note"></p>

  <footer>
    Kaynak: ÖSYM tercih kılavuzları (memurlar.net KPSS Robotu üzerinden yapılandırılmış) ·
    Doğrulama: her dönem için çekilen ↔ ÖSYM beyanı; ayrıca KPSS-2024/1 resmî PDF çapraz kontrolü. ·
    Bir sonraki adım: bu veri üzerine kişiye özel “bana uygun kadrolar” tercih robotu.
  </footer>
</div>

<script>
const DATA = __PAYLOAD__;
const fmt = n => (n==null||n==='') ? '—' : Number(n).toLocaleString('tr-TR');
const ozet = DATA.ozet, rows = DATA.index.slice();

document.getElementById('kpis').innerHTML = [
  ['n', ozet.donem_sayisi, 'Dönem'],
  ['n', fmt(ozet.toplam_kadro), 'Toplam kadro'],
  ['n', fmt(ozet.toplam_kontenjan), 'Toplam kontenjan'],
  ['good', (ozet.donem_sayisi - ozet.uyusmayan_donemler.length)+' / '+ozet.donem_sayisi, 'ÖSYM ile birebir']
].map(([cls,n,l])=>`<div class="kpi ${cls==='good'?'good':''}"><div class="n">${n}</div><div class="l">${l}</div></div>`).join('');

document.getElementById('note').innerHTML =
  ozet.uyusmayan_donemler.length
   ? `<strong>Not:</strong> ${ozet.uyusmayan_donemler.join(', ')} döneminde kaynak (memurlar.net) kendi verisinde başlıktaki toplamdan az kadro gösteriyor (scraper hatası değil). Eksik kadrolar yalnızca ÖSYM resmî PDF’inden tamamlanabilir.`
   : '';

let sortKey='id', sortDir=-1;
const tbody = document.querySelector('#tbl tbody');
function yearNum(id){const [y,d]=id.split('-');return parseInt(y)*100+parseInt(d);}
function render(){
  const q = document.getElementById('q').value.trim().toLowerCase();
  let r = rows.filter(x => !q || x.id.toLowerCase().includes(q) || (x.baslik||'').toLowerCase().includes(q));
  r.sort((a,b)=>{
    let va = sortKey==='id'? yearNum(a.id) : (a[sortKey]??-1);
    let vb = sortKey==='id'? yearNum(b.id) : (b[sortKey]??-1);
    return (va<vb?-1:va>vb?1:0)*sortDir;
  });
  tbody.innerHTML = r.map(x=>{
    const ok = x.kadro_match && x.kontenjan_match;
    const durum = ok ? '<span class="dot ok"></span>Eşleşti'
                     : `<span class="dot warn"></span>${fmt(x.scraped_kadro)}/${fmt(x.stated_kadro)}`;
    return `<tr>
      <td class="mono">${x.id}</td>
      <td class="n">${fmt(x.scraped_kadro)}</td>
      <td class="n">${fmt(x.scraped_kontenjan)}</td>
      <td class="n">${fmt(x.stated_basvuran)}</td>
      <td class="n">${fmt(x.stated_yerlesen)}</td>
      <td>${durum}</td></tr>`;
  }).join('');
}
document.querySelectorAll('#tbl thead th').forEach(th=>{
  th.addEventListener('click',()=>{
    const k=th.dataset.k; if(k==='durum')return;
    if(sortKey===k) sortDir*=-1; else {sortKey=k; sortDir=(k==='id')?-1:-1;}
    render();
  });
});
document.getElementById('q').addEventListener('input', render);
render();
</script>
"""

out = HTML.replace("__PAYLOAD__", payload)
fp = os.path.join(ROOT, "ozet_web.html")
with open(fp, "w", encoding="utf-8") as f:
    f.write(out)
print("yazildi:", fp, "(%d bytes)" % len(out))
