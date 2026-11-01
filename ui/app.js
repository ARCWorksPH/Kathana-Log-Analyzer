// ARCWorks Kathana Log Analyzer 1.0.0 UI
const COLORS = ['#ff5a6a', '#3db8ff', '#3ddc97', '#ffc94a', '#b28dff', '#ff9f43'];
const MAX = 6;
let logs = [], base = 0, charts = {}, tab = 'overview';
const $ = s => document.querySelector(s);
const api = () => (window.pywebview && window.pywebview.api) || null;
const n0 = v => Math.round(v).toLocaleString('en-US');
const n2 = v => v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pct = v => (v * 100).toFixed(1) + '%';
const dur = s => { const m = Math.round(s / 60); return m < 60 ? m + ' min' : Math.floor(m / 60) + ' h ' + (m % 60) + ' min'; };
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function toast(t) { const e = $('#toast'); e.textContent = t; e.classList.remove('hidden'); clearTimeout(e._t); e._t = setTimeout(() => e.classList.add('hidden'), 2600); }

// metric: key, label, icon, format, higher-is-better
const METRICS = [
  ['duration_s', 'Log duration', '⏱', dur, null],
  ['rupiah', 'Total Rupiah gained', '💰', n0, 1], ['rupiah_h', 'Rupiah per hour', '💰', n0, 1], ['rupiah_24h', 'Est. Rupiah per 24 h', '💰', n0, 1],
  ['prana', 'Total Prana gained', '✨', n0, 1], ['prana_h', 'Prana per hour', '✨', n0, 1], ['prana_24h', 'Est. Prana per 24 h', '✨', n0, 1],
  ['damage', 'Total damage dealt', '🗡', n0, 1], ['avg_hit', 'Average damage per hit', '🗡', n2, 1], ['max_hit', 'Biggest hit', '💥', n0, 1],
  ['received', 'Damage received', '🛡', n0, 0], ['received_h', 'Damage received per hour', '🛡', n0, 0],
  ['kills_est', 'Est. kills (Prana rewards)', '☠', n0, 1], ['kills_h', 'Est. kills per hour', '☠', n0, 1],
  ['rupiah_per_kill', 'Rupiah per kill', '💰', n0, 1], ['prana_per_kill', 'Prana per kill', '✨', n0, 1],
  ['dodge_rate', 'You dodged', '💨', pct, 1], ['miss_rate', 'Mobs dodged you', '🎯', pct, 0],
];

function score(l) { return l.rupiah_h / avg('rupiah_h') + l.prana_h / avg('prana_h'); }
function avg(k) { return logs.reduce((a, l) => a + l[k], 0) / logs.length || 1; }
function bestIndex() { if (logs.length < 2) return -1; let b = 0; logs.forEach((l, i) => { if (score(l) > score(logs[b])) b = i; }); return b; }

function addLogs(list) {
  for (const r of list) {
    if (r.error) { toast('Could not read ' + r.name + ': ' + r.error); continue; }
    if (r.empty) { toast(r.name + ' has no timed lines - is it a Kathana chat log?'); continue; }
    if (logs.length >= MAX) { toast('Max ' + MAX + ' logs at once - remove one first'); break; }
    logs.push(r);
  }
  render();
}
function color(i) { return COLORS[i % COLORS.length]; }

function render() {
  $('#empty').classList.toggle('hidden', logs.length > 0);
  document.querySelectorAll('.tab').forEach(s => s.classList.toggle('hidden', !logs.length || s.id !== tab));
  if (base >= logs.length) base = 0;
  $('#chips').innerHTML = logs.map((l, i) => `<div class="chip ${i === base && logs.length > 1 ? 'base' : ''}" title="Click to make this the baseline for differences" data-i="${i}">
    <i style="background:${color(i)}"></i><b>${esc(l.name)}</b><span>${dur(l.duration_s)}</span><span class="x" data-x="${i}">✕</span></div>`).join('');
  if (!logs.length) return;
  renderOverview(); renderCompare(); renderMobs(); if (tab === 'charts') renderCharts();
}

function tipFor(l) {
  const t = [];
  if (l.idle_gaps.length) t.push(`😴 ${l.idle_gaps.length} idle break${l.idle_gaps.length > 1 ? 's' : ''} (${dur(l.duration_s - l.active_s)}). Active-time rate: <b>${n0(l.rupiah_h_active)}</b> Rupiah/h.`);
  if (l.bag_full > 50) t.push(`🎒 "Inventory full" showed up ${n0(l.bag_full)} times - you probably missed loot.`);
  if (l.rupiah_sold) t.push(`🏪 Sold items to NPC for ${n0(l.rupiah_sold)} Rupiah (not counted as farming income).`);
  if (l.spent) t.push(`🔧 Spent ${n0(l.spent)} Rupiah on repairs/warps. Net: <b>${n0(l.net_rupiah)}</b>.`);
  if (l.kicked) t.push('⚡ You got kicked out during this log.');
  const pk = l.peak_prana; if (pk.value) t.push(`🔥 Best ${pk.minutes} min: minute ${pk.start_min}–${pk.start_min + pk.minutes} with ${n0(pk.value)} Prana.`);
  return t.length ? `<div class="tip">${t.join('<br>')}</div>` : '';
}

function renderOverview() {
  const b = bestIndex();
  $('#overview').innerHTML = `<div class="cols">` + logs.map((l, i) => `
  <div class="card" style="--c:${color(i)}">${i === b ? '<div class="badge">🏆 BEST SESSION</div>' : ''}
    <h2><i></i>${esc(l.name)}</h2>
    <div class="when">📅 ${esc(l.start_label)} → ${esc(l.end_label.split(', ').pop())}<br>⏱ ${dur(l.duration_s)} logged · ${dur(l.active_s)} active</div>
    <div class="big">
      <div class="stat r"><div class="l">💰 Rupiah</div><div class="v">${n0(l.rupiah)}</div><div class="s">${n0(l.rupiah_h)}/h · ${n0(l.rupiah_24h)}/24h</div></div>
      <div class="stat p"><div class="l">✨ Prana</div><div class="v">${n0(l.prana)}</div><div class="s">${n0(l.prana_h)}/h · ${n0(l.prana_24h)}/24h</div></div>
      <div class="stat d"><div class="l">🗡 Damage dealt</div><div class="v">${n0(l.damage)}</div><div class="s">${n2(l.avg_hit)} avg · ${n0(l.max_hit)} max</div></div>
      <div class="stat h"><div class="l">🛡 Damage received</div><div class="v">${n0(l.received)}</div><div class="s">${n0(l.received_h)}/h · dodged ${pct(l.dodge_rate)}</div></div>
    </div>
    <div class="mini"><span>☠ ~<b>${n0(l.kills_est)}</b> kills</span><span>💰 <b>${n0(l.rupiah_per_kill)}</b>/kill</span><span>✨ <b>${n0(l.prana_per_kill)}</b>/kill</span><span>🎁 <b>${l.items}</b> drops</span><span>👥 <b>${l.party_items}</b> party drops</span></div>
    ${tipFor(l)}
  </div>`).join('') + `</div>`;
}

function renderCompare() {
  if (logs.length < 2) { $('#compare').innerHTML = '<div class="metric"><h3>Add at least one more log to compare ⚖</h3></div>'; return; }
  const B = logs[base];
  $('#compare').innerHTML = `<p style="color:var(--mu)">Differences are against <b style="color:var(--gold)">${esc(B.name)}</b> (click a log chip above to change). 👑 = best.</p>` +
    METRICS.map(([k, label, ic, f, hib]) => {
      const vals = logs.map(l => l[k]), mx = Math.max(...vals) || 1;
      const best = hib === null ? -1 : vals.indexOf(hib ? Math.max(...vals) : Math.min(...vals));
      return `<div class="metric"><h3><span>${ic} ${label}</span></h3><div class="bars">` + logs.map((l, i) => {
        const d = l[k] - B[k], p = B[k] ? d / B[k] : 0, good = hib === null ? null : (hib ? d > 0 : d < 0);
        const df = i === base ? '<span style="color:var(--mu)">baseline</span>' : (d === 0 ? '±0' :
          `<span class="${good === null ? '' : good ? 'up' : 'down'}">${d > 0 ? '▲ +' : '▼ '}${k === 'duration_s' ? dur(Math.abs(d)) : f(d)} (${(p * 100).toFixed(1)}%)</span>`);
        return `<div class="bar"><span>${i === best ? '<span class="crown">👑</span> ' : ''}${esc(l.name)}</span><div class="track"><div class="fill" style="--c:${color(i)};width:${Math.max(2, l[k] / mx * 100)}%"></div></div><span class="val">${f(l[k])}</span><span class="diff">${df}</span></div>`;
      }).join('') + `</div></div>`;
    }).join('');
}

function renderMobs() {
  $('#mobs').innerHTML = `<div class="cols">` + logs.map((l, i) => `<div class="card" style="--c:${color(i)}"><h2><i></i>${esc(l.name)}</h2>
    <table class="mobtable"><tr style="color:var(--mu);font-size:12px"><td>Mob</td><td>Your hits</td><td>Avg hit</td><td>Hurt you</td></tr>` +
    l.mobs.slice(0, 8).map(m => `<tr class="mobrow"><td>👹 ${esc(m.name)}</td><td>${n0(m.hits)}</td><td>${n0(m.avg)}</td><td>${n0(m.recv)}</td></tr>`).join('') +
    `</table><h3 style="font-size:13px;margin:12px 0 6px">🎁 Your drops</h3><div class="loot">${l.loot.slice(0, 14).map(([n, c]) => `<span>${esc(n)} ×${c}</span>`).join('') || '<span>none in this log</span>'}</div></div>`).join('') + `</div>`;
}

Chart.defaults.color = '#8b95b5'; Chart.defaults.borderColor = '#232b45'; Chart.defaults.font.family = 'Segoe UI, system-ui';
function mk(id, cfg) { if (charts[id]) charts[id].destroy(); charts[id] = new Chart(document.getElementById(id), cfg); }
function renderCharts() {
  const opt = (y) => ({ responsive: true, maintainAspectRatio: false, animation: false, interaction: { mode: 'nearest', intersect: false },
    scales: { x: { type: 'linear', title: { display: true, text: 'minutes into log' } }, y: { title: { display: true, text: y }, ticks: { callback: v => v.toLocaleString('en-US') } } },
    plugins: { legend: { labels: { boxWidth: 12 } } } });
  const line = (idx) => logs.map((l, i) => ({ label: l.name, borderColor: color(i), backgroundColor: color(i) + '22', pointRadius: 0, tension: .25, borderWidth: 2.5,
    data: l.cum.map(c => ({ x: c[0], y: c[idx] })) }));
  mk('cRup', { type: 'line', data: { datasets: line(1) }, options: opt('Rupiah (total)') });
  mk('cPra', { type: 'line', data: { datasets: line(2) }, options: opt('Prana (total)') });
  mk('cDmg', { type: 'line', data: { datasets: logs.map((l, i) => ({ label: l.name, borderColor: color(i), pointRadius: 0, tension: .3, borderWidth: 2, data: l.per_min.map((b, m) => ({ x: m, y: b[2] })) })) }, options: opt('damage / minute') });
  mk('cBar', { type: 'bar', data: { labels: ['Rupiah / h', 'Prana / h ÷10', 'Damage / h ÷10', 'Received / h'],
      datasets: logs.map((l, i) => ({ label: l.name, backgroundColor: color(i), borderRadius: 6,
        data: [l.rupiah_h, l.prana_h / 10, l.damage / (l.duration_s / 3600) / 10, l.received_h] })) },
    options: { responsive: true, maintainAspectRatio: false, animation: false, scales: { y: { ticks: { callback: v => v.toLocaleString('en-US') } } } } });
}

function setTab(t) { tab = t; document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === t)); render(); }

async function openLogs() {
  if (api()) addLogs(await api().pick_files());
  else { const i = document.createElement('input'); i.type = 'file'; i.multiple = true; i.accept = '.txt'; i.onchange = () => readFiles(i.files); i.click(); }
}
async function readFiles(files) {
  for (const f of files) {
    const text = await f.text();
    if (api()) addLogs([await api().analyze_text(f.name, text)]); else toast('Open the app to analyze files');
  }
}
async function mergeLogs() {
  if (!api()) return;
  toast('Pick 2+ exports from the SAME session - overlapping lines are counted once');
  const p = await api().pick_paths(); if (!p || !p.length) return;
  addLogs(p.length < 2 ? await api().open_paths(p) : [await api().merge_paths(p)]);
}

async function exportReport() {
  if (!logs.length) return toast('Load some logs first');
  const prev = tab; setTab('charts');
  const imgs = Object.values(charts).map(c => `<img src="${c.toBase64Image()}" style="width:48%;margin:1%;background:#141a2b;border-radius:12px">`).join('');
  const css = [...document.styleSheets].map(s => { try { return [...s.cssRules].map(r => r.cssText).join('\n'); } catch (e) { return ''; } }).join('\n');
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Kathana Log Report</title><style>${css} body{display:block;padding:20px}</style></head><body>
  <h1>⚔ Kathana Log Report</h1><p style="color:#8b95b5">Made with ARCWorks Kathana Log Analyzer 1.0.0 · ${new Date().toLocaleString()}</p>
  ${$('#overview').innerHTML}<h2>⚖ Compare</h2>${$('#compare').innerHTML}<h2>📈 Charts</h2>${imgs}
  <footer>${$('footer').innerHTML}</footer></body></html>`;
  setTab(prev);
  if (api()) { const p = await api().save_report(html, 'Kathana-Log-Report.html'); if (p) toast('Saved: ' + p); }
  else { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' })); a.download = 'Kathana-Log-Report.html'; a.click(); }
}

$('#tabs').onclick = e => { const b = e.target.closest('button'); if (b) setTab(b.dataset.tab); };
$('#chips').onclick = e => { const x = e.target.dataset.x; if (x !== undefined) { logs.splice(+x, 1); if (base == x) base = 0; return render(); }
  const c = e.target.closest('.chip'); if (c) { base = +c.dataset.i; render(); } };
$('#btnOpen').onclick = openLogs; $('#btnMerge').onclick = mergeLogs; $('#btnExport').onclick = exportReport;
$('#btnAbout').onclick = () => $('#modal').classList.remove('hidden');
$('#btnOk').onclick = () => { $('#modal').classList.add('hidden'); api() && api().ack_disclaimer(); };
document.addEventListener('dragover', e => { e.preventDefault(); document.querySelector('.drop').classList.add('over'); });
document.addEventListener('dragleave', () => document.querySelector('.drop').classList.remove('over'));
document.addEventListener('drop', e => { e.preventDefault(); document.querySelector('.drop').classList.remove('over'); readFiles(e.dataTransfer.files); });

let booted = false;
async function boot() {
  if (booted) return; booted = true;
  if (window.DEMO) { addLogs(window.DEMO); if (window.DEMO_TAB) setTab(window.DEMO_TAB); return; }
  const a = api(); if (!a) { $('#modal').classList.remove('hidden'); return; }
  const info = await a.info();
  if (!info.seen_disclaimer) $('#modal').classList.remove('hidden');
  $('#recent').innerHTML = info.recent.length ? '<div style="color:var(--mu)">Recent files</div>' + info.recent.map(p => `<a data-p="${esc(p)}">📄 ${esc(p.split(/[\\/]/).pop())}</a>`).join('') : '';
  $('#recent').onclick = async e => { const p = e.target.dataset.p; if (p) addLogs(await a.open_paths([p])); };
}
if (window.pywebview) boot(); else window.addEventListener('pywebviewready', boot);
setTimeout(() => { if (!window.pywebview) boot(); }, 400);
