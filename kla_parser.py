"""ARCWorks Kathana Log Analyzer - chat log parser + metrics. Pure python, no deps."""
import re, os
from datetime import datetime

TS = re.compile(r'\s*\((\d{8}),(\d{2}):(\d{2}):(\d{2})\)\s*$')
N = r'(\d[\d,]*)'
RULES = [
    ('rupiah_auto', re.compile(r'^\[Auto\] You gained ' + N + r' Rupiah$')),
    ('rupiah_earn', re.compile(r'^You earned ' + N + r' Rupiah$')),
    ('rupiah_sell', re.compile(r'^' + N + r' Rupiah was earned by selling (.+)$')),
    ('prana', re.compile(r'^You earned ' + N + r' Prana$')),
    ('repair', re.compile(r'^' + N + r' Rupiah were used to repair (.+)$')),
    ('warp', re.compile(r'^You used ' + N + r' Rupiah for the warp fee$')),
    ('hit', re.compile(r'^You damaged (.+?) by ' + N + r'$')),
    ('hurt', re.compile(r'^(.+?) damaged you by ' + N + r'$')),
    ('dodge', re.compile(r"^You have evaded (.+?)'s attack$")),
    ('miss', re.compile(r'^(.+?) has evaded attack$')),
    ('item', re.compile(r'^You have earned (.+)$')),
    ('party_item', re.compile(r'^\[Auto Division\] (\S+) have earned (.+)$')),
    ('ah_on', re.compile(r'^Auto-Hunt Enabled$')),
    ('ah_off', re.compile(r'^Auto-Hunt Disabled$')),
    ('bag_full', re.compile(r'^Not enough inventory space$')),
    ('kicked', re.compile(r'^You have been kicked out$')),
    ('player_chat', re.compile(r'^[A-Za-z0-9_\[\]\.\-]{2,20}: .*$')),
    ('system', re.compile(r'^(Cannot pick up item yet|Incorrect distance between item and character|Skill is on cooldown|\[AH\] .*|This action is not allowed.*|Party Created|Automatic|Normal)$')),
]
IDLE_GAP_S = 120

def num(s): return int(s.replace(',', ''))

def parse_text(text):
    """Return list of events (oldest first). Unknown/timestamp-less lines counted."""
    ev, unknown, chat = [], 0, 0
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    for raw in lines:
        line = raw.strip()
        if not line or line == '[ChatLog]': continue
        m = TS.search(line)
        if not m: chat += 1; continue  # trade/world chat (no timestamp)
        d, hh, mm, ss = m.groups()
        try: t = datetime(int(d[:4]), int(d[4:6]), int(d[6:]), int(hh), int(mm), int(ss))
        except ValueError: unknown += 1; continue
        body = line[:m.start()].strip()
        for kind, rx in RULES:
            r = rx.match(body)
            if r: ev.append((t, kind, r.groups())); break
        else:
            unknown += 1
    ev.sort(key=lambda e: e[0])  # file is newest-first; stable sort keeps order within same second
    return ev, unknown, chat

def read_file(path):
    b = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'utf-16', 'cp1252'):
        try:
            if enc == 'utf-16' and not b[:2] in (b'\xff\xfe', b'\xfe\xff'): continue
            return b.decode(enc)
        except UnicodeDecodeError: pass
    return b.decode('latin-1')

def fmt_dur(sec):
    m = int(round(sec / 60))
    if m < 60: return f'{m} min'
    return f'{m // 60} h {m % 60} min'

def analyze(text, name='log'):
    ev, unknown, chat = parse_text(text)
    if not ev: return {'name': name, 'empty': True, 'unknown': unknown, 'chat': chat}
    t0, t1 = ev[0][0], ev[-1][0]
    dur = max((t1 - t0).total_seconds(), 1)
    s = dict(rup=0, rup_auto=0, rup_earn=0, rup_sell=0, prana=0, dmg=0, hits=0, maxhit=0, recv=0, recvhits=0,
             dodges=0, misses=0, spent=0, items=0, party_items=0, prana_drops=0, bagfull=0, kicked=0)
    mobs, loot, timeline = {}, {}, []
    def mob(n): return mobs.setdefault(n, {'name': n, 'hits': 0, 'dmg': 0, 'max': 0, 'recv': 0, 'recvhits': 0, 'dodged': 0, 'missed': 0})
    acts = []
    for t, k, g in ev:
        sec = (t - t0).total_seconds(); dr = dp = dd = 0; active = True
        if k in ('rupiah_auto', 'rupiah_earn', 'rupiah_sell'):
            v = num(g[0])
            if k != 'rupiah_sell': s['rup'] += v; dr = v  # selling items to NPC is not farming income
            s[{'rupiah_auto': 'rup_auto', 'rupiah_earn': 'rup_earn', 'rupiah_sell': 'rup_sell'}[k]] += v
        elif k == 'prana': v = num(g[0]); s['prana'] += v; s['prana_drops'] += 1; dp = v
        elif k in ('repair', 'warp'): s['spent'] += num(g[0])
        elif k == 'hit':
            v = num(g[1]); s['dmg'] += v; s['hits'] += 1; s['maxhit'] = max(s['maxhit'], v); dd = v
            m = mob(g[0]); m['hits'] += 1; m['dmg'] += v; m['max'] = max(m['max'], v)
        elif k == 'hurt':
            v = num(g[1]); s['recv'] += v; s['recvhits'] += 1; m = mob(g[0]); m['recv'] += v; m['recvhits'] += 1
        elif k == 'dodge': s['dodges'] += 1; mob(g[0])['dodged'] += 1
        elif k == 'miss': s['misses'] += 1; mob(g[0])['missed'] += 1
        elif k == 'item': s['items'] += 1; loot[g[0]] = loot.get(g[0], 0) + 1
        elif k == 'party_item': s['party_items'] += 1
        elif k == 'bag_full': s['bagfull'] += 1; active = False
        elif k == 'kicked': s['kicked'] += 1
        else: active = False
        if active: acts.append(sec)
        timeline.append((sec, dr, dp, dd))
    # idle gaps
    gaps = []; prev = 0.0
    for a in acts:
        if a - prev > IDLE_GAP_S: gaps.append({'start': prev, 'len': a - prev})
        prev = a
    if dur - prev > IDLE_GAP_S: gaps.append({'start': prev, 'len': dur - prev})
    idle = sum(g['len'] for g in gaps); active_s = max(dur - idle, 1)
    # per-minute buckets + cumulative
    nb = int(dur // 60) + 1
    per_min = [[0, 0, 0] for _ in range(nb)]
    for sec, dr, dp, dd in timeline:
        b = per_min[min(int(sec // 60), nb - 1)]; b[0] += dr; b[1] += dp; b[2] += dd
    cum = []; cr = cp = 0
    for i, b in enumerate(per_min): cr += b[0]; cp += b[1]; cum.append([i, cr, cp])
    def peak(idx):  # best 10-minute window
        w = min(10, nb); best = (0, 0)
        run = sum(per_min[i][idx] for i in range(w)); best = (run, 0)
        for i in range(w, nb):
            run += per_min[i][idx] - per_min[i - w][idx]
            if run > best[0]: best = (run, i - w + 1)
        return {'value': best[0], 'start_min': best[1], 'minutes': w}
    h = dur / 3600; ah = active_s / 3600
    kills = s['prana_drops']
    mob_list = sorted(mobs.values(), key=lambda m: -m['dmg'])
    for m in mob_list: m['avg'] = round(m['dmg'] / m['hits'], 2) if m['hits'] else 0
    return {
        'name': name, 'empty': False,
        'start': t0.isoformat(), 'end': t1.isoformat(),
        'start_label': t0.strftime('%A, %B %d, %Y, %I:%M:%S %p').replace(' 0', ' '),
        'end_label': t1.strftime('%A, %B %d, %Y, %I:%M:%S %p').replace(' 0', ' '),
        'duration_s': dur, 'duration_label': fmt_dur(dur),
        'active_s': active_s, 'active_label': fmt_dur(active_s), 'idle_gaps': gaps,
        'rupiah': s['rup'], 'rupiah_auto': s['rup_auto'], 'rupiah_earned': s['rup_earn'], 'rupiah_sold': s['rup_sell'],
        'rupiah_h': s['rup'] / h, 'rupiah_24h': s['rup'] / h * 24, 'rupiah_h_active': s['rup'] / ah,
        'prana': s['prana'], 'prana_h': s['prana'] / h, 'prana_24h': s['prana'] / h * 24, 'prana_h_active': s['prana'] / ah,
        'damage': s['dmg'], 'hits': s['hits'], 'avg_hit': s['dmg'] / s['hits'] if s['hits'] else 0, 'max_hit': s['maxhit'],
        'dps_min': s['dmg'] / (dur / 60),
        'received': s['recv'], 'received_hits': s['recvhits'], 'received_h': s['recv'] / h,
        'avg_received': s['recv'] / s['recvhits'] if s['recvhits'] else 0,
        'dodges': s['dodges'], 'misses': s['misses'],
        'dodge_rate': s['dodges'] / (s['dodges'] + s['recvhits']) if (s['dodges'] + s['recvhits']) else 0,
        'miss_rate': s['misses'] / (s['misses'] + s['hits']) if (s['misses'] + s['hits']) else 0,
        'spent': s['spent'], 'net_rupiah': s['rup'] + s['rup_sell'] - s['spent'],
        'kills_est': kills, 'kills_h': kills / h,
        'rupiah_per_kill': s['rup'] / kills if kills else 0, 'prana_per_kill': s['prana'] / kills if kills else 0,
        'items': s['items'], 'party_items': s['party_items'], 'loot': sorted(loot.items(), key=lambda x: -x[1]),
        'bag_full': s['bagfull'], 'kicked': s['kicked'],
        'mobs': mob_list, 'per_min': per_min, 'cum': cum,
        'peak_rupiah': peak(0), 'peak_prana': peak(1), 'peak_damage': peak(2),
        'events': len(ev), 'unknown': unknown, 'chat': chat,
    }

def merge_texts(texts):
    """Merge several exports of the same session; duplicate lines (overlap) are kept once."""
    seen, out = set(), []
    for t in texts:
        for l in t.replace('\r\n', '\n').split('\n'):
            k = l.strip()
            if k and k != '[ChatLog]' and TS.search(k):
                if k in seen: continue
                seen.add(k)
            out.append(l)
    return '\n'.join(out)

def analyze_file(path):
    return analyze(read_file(path), os.path.splitext(os.path.basename(path))[0])
