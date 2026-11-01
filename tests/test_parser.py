import os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import kla_parser as P
S = os.path.join(os.path.dirname(__file__), '..', '..', 'samples', 'Sample Logs')
if not os.path.isdir(S): S = os.path.join(os.path.dirname(__file__), 'samples')

def f(n): return P.analyze_file(os.path.join(S, n + '.txt'))

def test_lines():
    ev, unk, chat = P.parse_text('[ChatLog]\r\n[Auto] You gained 88 Rupiah (20261101,10:00:23)\r\nYou earned 232 Rupiah (20261101,11:31:43)\r\n'
        'You earned 1021 Prana (20261101,10:00:31)\r\nYou damaged Zarku by 1357 (20261101,11:31:40)\r\n'
        'Zarku Rudhira damaged you by 89 (20261101,11:30:03)\r\n1,811 Rupiah were used to repair X (20261101,11:30:00)\r\nWTB stuff : [Bob]\r\nweird (20261101,11:30:00)\r\n')
    assert [e[1] for e in ev][0] == 'rupiah_auto' and unk == 1 and chat == 1
    r = P.analyze(open(os.devnull).read() + '\n'.join(['You damaged A by 1,000 (20261101,10:00:00)', 'You damaged A by 3000 (20261101,10:10:00)',
                   '[Auto] You gained 100 Rupiah (20261101,10:05:00)', 'You earned 50 Rupiah (20261101,10:06:00)']))
    assert r['damage'] == 4000 and r['avg_hit'] == 2000 and r['rupiah'] == 150 and r['duration_s'] == 600
    assert r['rupiah_h'] == 900 and r['rupiah_24h'] == 21600 and r['duration_label'] == '10 min'
    assert P.fmt_dur(72 * 60) == '1 h 12 min'

def test_all_samples_parse_fully():
    for p in glob.glob(os.path.join(S, '*.txt')):
        r = P.analyze_file(p)
        assert not r['empty'] and r['unknown'] == 0 and r['events'] > 500

def test_sample_values():
    r = f('2026_11_1_3')
    assert r['start'] == '2026-11-01T11:20:10' and r['end'] == '2026-11-01T11:32:02'
    assert (r['rupiah'], r['prana'], r['damage'], r['received']) == (5657, 331852, 109586, 3913)
    r = f('2026_11_1_2'); assert r['rupiah_sold'] == 16000 and r['spent'] == 1873 and r['rupiah'] == 3789 and r['net_rupiah'] == 3789 + 16000 - 1873

def test_merge_dedupes():
    a = P.read_file(os.path.join(S, '2026_10_31_2.txt')); b = P.read_file(os.path.join(S, '2026_10_31_3.txt'))
    m = P.analyze(P.merge_texts([a, b])); x = P.analyze(a)
    assert m['events'] < P.analyze(a)['events'] + P.analyze(b)['events'] and m['rupiah'] >= x['rupiah']
