#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html'in <style> blogunu koyu-cam (warm tan) temayla degistirir ve
header'daki marka blogunu (logo + baslik + aciklama) kaldirir."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(ROOT, "index.html")

CSS = r"""
:root{
  --bg:#202228;
  --glass:rgba(255,255,255,.045);
  --glass-2:rgba(255,255,255,.075);
  --glass-brd:rgba(255,255,255,.09);
  --glass-brd-2:rgba(255,255,255,.20);
  --ink:#f4f4f5; --text:#cfced4; --muted:#a1a1aa; --muted2:#6c6c77;
  --accent:#ffffff; --accent-2:#f0f0f2; --accent-ink:#17191f;
  --accent-soft:rgba(255,255,255,.12); --accent-brd:rgba(255,255,255,.34);
  --grad:linear-gradient(135deg,#ffffff,#e4e4e8);
  --glow:rgba(255,255,255,.14);
  --ok:#6fd39a; --ok-soft:rgba(111,211,154,.15); --ok-brd:rgba(111,211,154,.42);
  --no:#f08a80; --no-soft:rgba(240,138,128,.15); --no-brd:rgba(240,138,128,.4);
  --fill:rgba(255,255,255,.05); --fill-hover:rgba(255,255,255,.09);
  --divider:rgba(255,255,255,.08);
  --optbg:#262a31;
  --tb:rgba(26,28,34,.6);
  --sb:rgba(255,255,255,.22); --sb-hover:rgba(255,255,255,.42);
  --shadow:0 12px 38px rgba(0,0,0,.55);
  --shadow-card:0 8px 26px rgba(0,0,0,.4);
  --inner:inset 0 1px 0 rgba(255,255,255,.07);
  --radius:14px; --radius-sm:10px; --blur:20px;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{color:var(--text);min-height:100%;-webkit-font-smoothing:antialiased;overflow-x:hidden;line-height:1.5;padding-top:56px;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  background:var(--bg)}

/* profil butonu + form */
.profile-btn{position:fixed;top:12px;right:18px;z-index:260;width:44px;height:44px;border-radius:50%;cursor:pointer;
  border:1px solid var(--glass-brd-2);background:var(--glass-2);color:var(--ink);display:grid;place-items:center;
  box-shadow:var(--shadow),var(--inner);transition:.15s}
.profile-btn:hover{border-color:#fff;transform:translateY(-1px)}
.profile-btn svg{width:21px;height:21px}
.profile-btn.set::after{content:"";position:absolute;top:1px;right:1px;width:11px;height:11px;border-radius:50%;background:var(--ok);border:2px solid var(--bg)}
.prof-form{display:flex;flex-direction:column;gap:5px}
.prof-form label{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin-top:12px}
.prof-form input,.prof-form select{width:100%}
.prof-form .hint{font-size:11.5px;color:var(--muted2);margin-top:1px}
.prof-check{display:flex;flex-direction:row;align-items:center;gap:10px;font-size:14.5px;color:var(--text);font-weight:500;cursor:pointer;text-transform:none;letter-spacing:0}
.prof-check input{width:auto;width:18px;height:18px;accent-color:var(--accent)}
/* profil ayri sayfa */
.profile-page{position:fixed;inset:0;z-index:300;background:var(--bg);overflow-y:auto;display:none}
.home-page{position:fixed;inset:0;z-index:200;background:var(--bg);overflow-y:auto;display:none;padding:44px 20px}
.home-page.show{display:flex;align-items:center;justify-content:center}
.home-inner{width:100%;max-width:660px;text-align:center;margin:auto}
.home-logo{width:74px;height:74px;object-fit:contain;margin:0 auto 12px;display:block}
.home-title{font-size:34px;font-weight:800;letter-spacing:-.02em;margin:0;color:var(--ink)}
.home-sub{color:var(--muted);margin:7px 0 34px;font-size:15px}
.home-cards{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.home-card{display:flex;flex-direction:column;align-items:flex-start;gap:15px;text-align:left;padding:24px;border-radius:18px;background:var(--glass);border:1px solid var(--glass-brd);cursor:pointer;transition:.16s;color:inherit;font:inherit}
.home-card:hover:not(:disabled){border-color:var(--glass-brd-2);background:var(--glass-2);transform:translateY(-2px)}
.home-card:disabled{opacity:.45;cursor:not-allowed}
.hc-icon{width:46px;height:46px;border-radius:12px;background:var(--grad);color:var(--accent-ink);display:flex;align-items:center;justify-content:center;flex:none}
.hc-icon svg{width:24px;height:24px}
.hc-body{display:flex;flex-direction:column;gap:5px}
.hc-h{font-size:17px;font-weight:700;color:var(--ink)}
.hc-p{color:var(--muted);font-size:13px;line-height:1.5}
.soon-tag{font-size:10px;font-weight:700;color:var(--accent-ink);background:var(--grad);border-radius:5px;padding:2px 7px;vertical-align:middle;margin-left:6px;letter-spacing:.02em}
.home-hint{color:var(--muted2);font-size:12.5px;margin:28px 0 0}
.home-btn{position:fixed;top:12px;left:18px;z-index:210;width:44px;height:44px;border-radius:50%;cursor:pointer;background:var(--glass-2);border:1px solid var(--glass-brd);color:var(--ink);display:none;align-items:center;justify-content:center}
.home-btn:hover{border-color:var(--glass-brd-2)}
body.in-app .home-btn{display:flex}
@media(max-width:560px){.home-cards{grid-template-columns:1fr}.home-title{font-size:28px}}
.ilan-page{position:fixed;inset:0;z-index:220;background:var(--bg);overflow-y:auto;display:none;padding:26px 20px 90px}
.ilan-page.show{display:block}
.ilan-inner{max-width:900px;margin:0 auto}
.ilan-controls{display:flex;align-items:center;gap:16px;margin:16px 0 18px;flex-wrap:wrap}
.ilan-card{background:var(--glass);border:1px solid var(--glass-brd);border-radius:14px;margin-bottom:12px;overflow:hidden}
.ilan-head{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:15px 18px;cursor:pointer}
.ilan-head:hover{background:var(--glass-2)}
.il-kurum{font-size:11.5px;color:var(--muted);font-weight:700;letter-spacing:.03em;text-transform:uppercase}
.il-baslik{font-size:14.5px;font-weight:700;color:var(--ink);margin-top:3px;line-height:1.35}
.il-meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;color:var(--muted);font-size:12px}
.il-badge{flex:none;font-size:11.5px;font-weight:700;padding:5px 11px;border-radius:999px;white-space:nowrap;align-self:center}
.il-badge.ok{color:var(--accent-ink);background:var(--grad)}
.il-badge.no{color:var(--muted);background:var(--fill);border:1px solid var(--glass-brd)}
.ilan-unvanlar{display:none;padding:2px 18px 14px}
.ilan-unvanlar.show{display:block}
.uv-row{padding:12px 0;border-top:1px solid var(--glass-brd)}
.uv-top{display:flex;justify-content:space-between;align-items:center;gap:10px}
.uv-ad{font-weight:700;font-size:13.5px;color:var(--ink)}
.uv-badge{flex:none;font-size:11px;font-weight:700;padding:3px 9px;border-radius:7px;white-space:nowrap}
.uv-badge.ok{color:var(--ok);background:var(--ok-soft);border:1px solid var(--ok-brd)}
.uv-badge.no{color:var(--muted2);background:var(--fill)}
.uv-meta{color:var(--muted);font-size:12.5px;margin-top:4px}
.uv-bol{font-size:12.5px;color:var(--text);margin-top:7px;line-height:1.6}
.uv-bol b{color:var(--ink)}
.uv-bol.muted{color:var(--muted2)}
.uv-genel{color:var(--ok)}
.uv-sart{margin-top:9px}
.uv-sart>summary{cursor:pointer;color:var(--muted);font-size:12px;font-weight:600;user-select:none;list-style:none}
.uv-sart>summary::-webkit-details-marker{display:none}
.uv-sart>summary::before{content:"▸ ";}
.uv-sart[open]>summary::before{content:"▾ ";}
.uv-sart>summary:hover{color:var(--ink)}
.uv-sart-metin{margin-top:8px;padding:11px 13px;background:var(--fill);border:1px solid var(--glass-brd);border-radius:9px;font-size:12px;color:var(--text);line-height:1.6;max-height:280px;overflow-y:auto;white-space:pre-wrap}
.uv-link{display:inline-block;margin-top:14px;color:var(--ink);font-size:13px;font-weight:600;text-decoration:none;border-bottom:1px solid var(--glass-brd-2);padding-bottom:1px}
.uv-row.uv-ok .uv-ad::before{content:"★ ";color:var(--accent)}
.profile-page.show{display:block}
.pp-inner{max-width:600px;margin:0 auto;padding:26px 22px 64px}
.pp-back{display:inline-flex;align-items:center;gap:7px;font:inherit;font-size:14px;font-weight:600;color:var(--muted);background:none;border:0;cursor:pointer;padding:6px 4px 6px 0;margin-bottom:22px}
.pp-back:hover{color:var(--ink)}
.pp-back svg{width:18px;height:18px}
.pp-title{font-size:26px;font-weight:750;letter-spacing:-.02em;color:var(--ink);margin:0 0 6px}
.pp-sub{font-size:14px;color:var(--muted);margin:0 0 28px;max-width:54ch;line-height:1.55}
.pp-form{display:flex;flex-direction:column;gap:22px}
.pp-field{display:flex;flex-direction:column;gap:8px}
.pp-field label{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600}
.pp-field input,.pp-field select{width:100%;font-size:15px;padding:13px 15px;border-radius:12px}
.pp-field .hint{font-size:12.5px;color:var(--muted2)}
.pp-actions{display:flex;gap:12px;margin-top:34px}
.pp-actions button{font:inherit;font-size:14px;font-weight:600;border-radius:999px;padding:13px 26px;cursor:pointer;border:1px solid var(--glass-brd);transition:.15s}
.pp-actions .primary{background:var(--grad);color:var(--accent-ink);border-color:transparent;box-shadow:0 6px 18px var(--glow)}
.pp-actions .primary:hover{filter:brightness(1.05)}
.pp-actions .ghost{background:var(--fill);color:var(--ink)}
.pp-actions .ghost:hover{background:var(--fill-hover)}
.pp-iller{display:flex;flex-wrap:wrap;gap:6px;max-height:230px;overflow-y:auto;padding:2px}
.il-chip{font:inherit;font-size:12.5px;font-weight:500;color:var(--muted);cursor:pointer;background:var(--fill);border:1px solid var(--glass-brd);border-radius:999px;padding:6px 12px;transition:.14s;user-select:none}
.il-chip:hover{color:var(--ink);border-color:var(--glass-brd-2)}
.il-chip.active{color:var(--accent-ink);background:var(--grad);border-color:transparent}
.pp-iller-count{font-size:12px;color:var(--accent-2);font-weight:600}
.pp-tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.pp-tags:empty{display:none}
.tag-item{display:inline-flex;align-items:center;gap:4px;font-size:12.5px;font-weight:500;background:var(--accent-soft);color:var(--accent-2);border:1px solid var(--accent-brd);border-radius:999px;padding:4px 6px 4px 12px}
.tag-item button{border:0;background:none;color:inherit;cursor:pointer;font-size:16px;line-height:1;padding:0 3px;opacity:.65}
.tag-item button:hover{opacity:1}
.chips.locked{opacity:.4;pointer-events:none}
.spec-badge{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;font-weight:700;letter-spacing:.02em;color:var(--accent-ink);background:var(--grad);border-radius:6px;padding:2px 8px;margin-bottom:8px}
.spec-tag{display:inline-block;font-size:9.5px;font-weight:800;color:var(--accent-ink);background:var(--grad);border-radius:5px;padding:1px 5px;margin-right:5px;vertical-align:middle}
.cert-badge{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;font-weight:700;color:#2a1e00;background:linear-gradient(135deg,#ffd97a,#efb545);border-radius:6px;padding:2px 8px;margin-bottom:8px;margin-left:6px}
.cert-tag{display:inline-block;font-size:9.5px;font-weight:800;color:#2a1e00;background:linear-gradient(135deg,#ffd97a,#efb545);border-radius:5px;padding:1px 5px;margin-right:5px;vertical-align:middle}
.spill.spec{color:var(--accent-ink);background:var(--grad);font-weight:600}
.spill.warn{color:#2a1e00;background:linear-gradient(135deg,#ffd97a,#efb545);font-weight:600}
.nit-grp{list-style:none;margin:12px 0 5px;padding:0;color:var(--muted);font-size:11.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.pp-autosave{align-self:center;color:var(--muted);font-size:12.5px}
.ac-wrap{position:relative}
.ac-menu{position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:60;background:#26282f;border:1px solid var(--glass-brd-2);border-radius:12px;max-height:260px;overflow-y:auto;display:none;box-shadow:0 14px 34px rgba(0,0,0,.5);padding:5px}
.ac-menu.show{display:block}
.ac-item{padding:9px 12px;border-radius:8px;cursor:pointer;font-size:13px;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ac-item.active,.ac-item:hover{background:var(--fill-hover);color:var(--ink)}
.pp-check{display:flex;align-items:center;gap:8px;margin-top:11px;font-size:12.5px;color:var(--muted);cursor:pointer;user-select:none}
.pp-check input{width:16px;height:16px;accent-color:var(--accent);cursor:pointer;flex:none}

.glass,.panel{background:var(--glass);border:1px solid var(--glass-brd);  box-shadow:var(--shadow),var(--inner)}

.wrap{max-width:1200px;margin:0 auto;padding:0 20px 80px}

/* header */
header.top{position:sticky;top:0;z-index:30;background:rgba(32,34,40,.55)}
.top-inner{max-width:1200px;margin:0 auto;padding:14px 20px;display:flex;gap:14px;align-items:flex-end;justify-content:flex-end;flex-wrap:wrap}
.hgroup{display:flex;gap:14px;align-items:flex-end;flex-wrap:wrap}
.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:10px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);font-weight:600;padding-left:2px}
select,input[type=text],input[type=number],input[type=search]{
  font:inherit;font-size:14px;color:var(--ink);background:var(--glass-2);border:1px solid var(--glass-brd);
  border-radius:var(--radius-sm);padding:10px 13px;outline:none;transition:border-color .15s,box-shadow .15s;
  -webkit-appearance:none;appearance:none}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23948f89' d='M1 1l5 5 5-5'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 12px center;padding-right:32px;cursor:pointer}
select option{background:var(--optbg);color:var(--ink)}
input:focus,select:focus{border-color:var(--accent-brd);box-shadow:0 0 0 3px var(--accent-soft)}
input::placeholder{color:var(--muted2)}
.field input,.field select{width:100%}
.ogr-field{grid-column:1/-1}

/* filtreler */
.filters{padding:18px 20px;margin:22px 0 18px;border-radius:var(--radius);display:grid;grid-template-columns:1.7fr 1fr 1fr;gap:16px 18px;align-items:end}
.filters .search{grid-column:1 / -1}
.chips{display:flex;gap:7px;flex-wrap:wrap}
.chip{font:inherit;font-size:13px;font-weight:600;color:var(--muted);cursor:pointer;background:var(--fill);
  border:1px solid var(--glass-brd);border-radius:999px;padding:8px 15px;transition:.16s}
.chip:hover{color:var(--ink);border-color:var(--glass-brd-2)}
.chip.active{color:var(--accent-ink);background:var(--grad);border-color:transparent;box-shadow:0 5px 18px var(--glow),var(--inner)}
.years-field{grid-column:1/-1}
.ylabel-actions button{font:inherit;font-size:10px;font-weight:700;letter-spacing:.05em;border:0;background:none;color:var(--accent);cursor:pointer;padding:0 6px}
.ylabel-actions button:hover{text-decoration:underline}
.toggles{display:flex;gap:10px;flex-wrap:wrap;grid-column:1 / -1;align-items:center;border-top:1px solid var(--divider);padding-top:16px}
.toggle{display:flex;align-items:center;gap:9px;font-size:13px;color:var(--text);cursor:pointer;user-select:none;
  background:var(--fill);border:1px solid var(--glass-brd);border-radius:999px;padding:8px 14px;transition:.16s}
.toggle:hover{border-color:var(--glass-brd-2)}
.toggle input{display:none}
.sw{width:34px;height:20px;border-radius:999px;background:rgba(255,255,255,.14);position:relative;transition:.18s;flex:none}
.sw::after{content:"";position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;transition:.18s;box-shadow:0 1px 3px rgba(0,0,0,.4)}
.toggle input:checked + .sw{background:var(--grad)}
.toggle input:checked + .sw::after{transform:translateX(14px);background:var(--accent-ink)}
.btn{font:inherit;font-size:13px;font-weight:600;cursor:pointer;border:1px solid var(--glass-brd);border-radius:999px;
  padding:9px 16px;background:var(--fill);color:var(--ink);transition:.16s}
.btn:hover{border-color:var(--glass-brd-2);background:var(--fill-hover)}

/* sonuc bari */
.resbar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:0 2px 14px}
.count{font-size:14px;color:var(--muted)}
.count b{color:var(--ink);font-variant-numeric:tabular-nums;font-size:22px;font-weight:750;letter-spacing:-.01em}
.stat-pills{display:flex;gap:16px;flex-wrap:wrap;margin-left:auto}
.spill{font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.spill b{color:var(--ink);font-weight:700}
.spill.ok b{color:var(--ok)}

/* kartlar */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.grid.listmode{display:block}
.card{padding:16px;border-radius:var(--radius);cursor:pointer;position:relative;overflow:hidden;
  background:var(--glass);border:1px solid var(--glass-brd);box-shadow:var(--shadow-card),var(--inner);  transition:transform .15s,border-color .15s,box-shadow .15s}
.card::before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:linear-gradient(150deg,rgba(255,255,255,.06),transparent 40%)}
.card:hover{transform:translateY(-3px);border-color:var(--accent-brd);box-shadow:0 16px 40px rgba(0,0,0,.5),0 0 0 1px var(--accent-soft),var(--inner)}
.card:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.card .unvan{font-size:15px;font-weight:700;letter-spacing:-.01em;margin:0 0 3px;line-height:1.3;color:var(--ink);padding-right:70px;position:relative}
.card .kurum{font-size:13px;color:var(--muted);margin:0 0 12px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;position:relative}
.meta{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;position:relative}
.mchip{font-size:11.5px;color:var(--text);background:var(--fill);border:1px solid var(--glass-brd);border-radius:7px;padding:3px 9px}
.mchip.donem{color:var(--accent-2);border-color:var(--accent-brd);background:var(--accent-soft);font-weight:600}
.foot{display:flex;align-items:flex-end;justify-content:space-between;gap:10px;border-top:1px solid var(--divider);padding-top:12px;position:relative}
.stat .lbl{font-size:10px;color:var(--muted2);text-transform:uppercase;letter-spacing:.06em;display:block;margin-bottom:1px}
.stat .val{font-size:19px;font-weight:750;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.stat.right{text-align:right}
.stat.right .val{color:var(--accent-2)}
.stat .val.none{font-size:13px;font-weight:600;color:var(--muted2)}
.pill{position:absolute;top:14px;right:14px;font-size:11px;font-weight:700;padding:3px 9px;border-radius:7px}
.pill.ok{color:var(--ok);background:var(--ok-soft);border:1px solid var(--ok-brd)}
.pill.no{color:var(--no);background:var(--no-soft);border:1px solid var(--no-brd)}

/* gorunum anahtari */
.view-toggle{display:inline-flex;background:var(--fill);border:1px solid var(--glass-brd);border-radius:999px;padding:3px;gap:2px;align-self:center}
.view-toggle button{font:inherit;font-size:12.5px;font-weight:600;border:0;background:none;color:var(--muted);cursor:pointer;padding:5px 14px;border-radius:999px;transition:.15s}
.view-toggle button.active{color:var(--accent-ink);background:var(--grad)}

/* liste */
.list-wrap{overflow-x:auto;border-radius:var(--radius);background:var(--glass);border:1px solid var(--glass-brd);
  box-shadow:var(--shadow-card),var(--inner)}
table.list{width:100%;border-collapse:collapse;font-size:13.5px;min-width:720px}
table.list thead th{text-align:left;font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:600;padding:12px 14px;border-bottom:1px solid var(--divider);white-space:nowrap}
table.list th.num{text-align:right}
table.list tbody tr{cursor:pointer;border-bottom:1px solid var(--divider)}
table.list tbody tr:last-child{border-bottom:0}
table.list tbody tr:hover{background:var(--fill)}
table.list tbody tr:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
table.list td{padding:11px 14px;vertical-align:middle;color:var(--text)}
table.list td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:650;color:var(--ink)}
table.list td.none{color:var(--muted2);font-weight:500}
.c-unvan{font-weight:650;color:var(--ink)}
.c-kurum{color:var(--muted);max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.c-elig .yes{color:var(--ok);font-weight:700}
.c-elig .noo{color:var(--no);font-weight:600}

/* durumlar */
.state{padding:56px 20px;text-align:center;color:var(--muted);border-radius:var(--radius)}
.state h3{color:var(--ink);font-size:16px;margin:0 0 6px}
.state code{background:var(--fill);padding:3px 8px;border-radius:6px;display:inline-block;margin-top:8px;color:var(--ink)}
.spinner{width:30px;height:30px;border-radius:50%;border:2.5px solid var(--glass-brd);border-top-color:var(--accent);animation:spin .8s linear infinite;margin:0 auto 14px;box-shadow:0 0 16px var(--glow)}
@keyframes spin{to{transform:rotate(360deg)}}
#sentinel{height:1px}
.more-info{text-align:center;color:var(--muted2);font-size:12.5px;padding:20px}

/* modal */
.overlay{position:fixed;inset:0;z-index:60;background:rgba(6,5,8,.6);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  display:none;align-items:center;justify-content:center;padding:18px}
.overlay.show{display:flex}
.modal{max-width:560px;width:100%;max-height:88vh;overflow-y:auto;border-radius:18px;padding:26px;position:relative;
  background:rgba(30,32,38,.78);border:1px solid var(--glass-brd-2);
  backdrop-filter:blur(30px) saturate(160%);-webkit-backdrop-filter:blur(30px) saturate(160%);
  box-shadow:0 30px 80px rgba(0,0,0,.6),var(--inner);animation:pop .17s ease}
@keyframes pop{from{transform:translateY(8px);opacity:0}to{transform:none;opacity:1}}
.modal .x{position:absolute;top:16px;right:18px;font-size:20px;color:var(--muted);cursor:pointer;background:none;border:0;line-height:1;padding:6px}
.modal .x:hover{color:var(--ink)}
.m-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--accent);font-weight:700}
.m-title{font-size:21px;font-weight:750;letter-spacing:-.02em;margin:5px 40px 4px 0;line-height:1.22;color:var(--ink)}
.m-kurum{font-size:14px;color:var(--muted);margin-bottom:16px}
.m-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--divider);border-radius:12px;overflow:hidden;margin-bottom:18px}
.m-cell{background:rgba(255,255,255,.03);padding:12px 14px}
.m-cell .lbl{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted2);font-weight:600}
.m-cell .val{font-size:16px;font-weight:700;margin-top:2px;color:var(--ink);font-variant-numeric:tabular-nums}
.m-cell.wide{grid-column:1/-1}
.m-badge{display:inline-block;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:8px;margin-bottom:16px}
.m-badge.ok{color:var(--ok);background:var(--ok-soft);border:1px solid var(--ok-brd)}
.m-badge.no{color:var(--no);background:var(--no-soft);border:1px solid var(--no-brd)}
.m-sec{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600;margin:4px 0 9px}
.nit{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.nit li{background:var(--fill);border:1px solid var(--glass-brd);border-radius:8px;padding:9px 12px;font-size:13px;color:var(--text)}
.nit .kod{display:inline-block;font-variant-numeric:tabular-nums;font-size:11px;font-weight:700;color:var(--accent-2);
  background:var(--accent-soft);border:1px solid var(--accent-brd);border-radius:5px;padding:1px 7px;margin-right:8px}
.m-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}
.m-actions a,.m-actions button{text-decoration:none;font:inherit;font-size:13px;font-weight:600;border-radius:999px;padding:10px 18px;cursor:pointer;border:1px solid var(--glass-brd);transition:.15s}
.m-actions .primary{background:var(--grad);color:var(--accent-ink);border-color:transparent;box-shadow:0 5px 16px var(--glow)}
.m-actions .primary:hover{filter:brightness(1.05)}
.m-actions .ghost{background:var(--fill);color:var(--ink)}
.m-actions .ghost:hover{background:var(--fill-hover)}

footer{text-align:center;color:var(--muted2);font-size:12px;padding:36px 10px 10px;line-height:1.7}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);z-index:80;background:var(--grad);color:var(--accent-ink);
  border-radius:999px;padding:10px 20px;font-size:13px;font-weight:600;box-shadow:0 10px 28px var(--glow);opacity:0;pointer-events:none;transition:opacity .22s}
.toast.show{opacity:1}

/* scrollbar */
*{scrollbar-width:thin;scrollbar-color:var(--sb) transparent}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--sb);border-radius:10px;border:3px solid transparent;background-clip:padding-box}
::-webkit-scrollbar-thumb:hover{background:var(--sb-hover)}
::-webkit-scrollbar-corner{background:transparent}

/* frameless titlebar */
.titlebar{display:none}
body.has-titlebar{padding-top:38px}
body.has-titlebar header.top{top:38px}
body.has-titlebar .titlebar{display:flex;position:fixed;top:0;left:0;right:0;height:38px;z-index:200;align-items:stretch;
  background:var(--tb);backdrop-filter:blur(18px) saturate(150%);-webkit-backdrop-filter:blur(18px) saturate(150%);
  border-bottom:1px solid var(--glass-brd)}
.tb-drag{flex:1;display:flex;align-items:center;gap:9px;padding-left:14px;overflow:hidden}
.tb-title{font-size:12px;font-weight:600;color:var(--muted);letter-spacing:.03em;white-space:nowrap}
.tb-dot{width:9px;height:9px;border-radius:50%;background:var(--accent);flex:none;box-shadow:0 0 8px var(--glow)}
.tb-controls{display:flex}
.tb-btn{width:46px;height:38px;border:0;background:none;color:var(--muted);cursor:pointer;display:grid;place-items:center;transition:background .12s,color .12s}
.tb-btn:hover{background:var(--fill);color:var(--ink)}
.tb-btn.tb-close:hover{background:#e23b2e;color:#fff}
.tb-btn svg{width:11px;height:11px;display:block}

@media (max-width:720px){.filters{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}}
@media (max-width:480px){.filters{grid-template-columns:1fr}}
"""

html = open(FP, encoding="utf-8").read()

# <style> blogunu degistir
html = re.sub(r"<style>.*?</style>", "<style>\n" + CSS + "\n</style>", html, count=1, flags=re.S)

# marka blogunu kaldir (logo + baslik + aciklama)
html2 = re.sub(r'\s*<div class="brand">.*?</p></div>\s*</div>', "", html, count=1, flags=re.S)
removed = html2 != html
html = html2

open(FP, "w", encoding="utf-8").write(html)
print("tema uygulandi. marka blogu kaldirildi:", removed)
