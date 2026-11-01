"""ARCWorks Kathana Log Analyzer 1.0.0 - desktop shell (pywebview + HTML UI)."""
import os, sys, json, webview
import kla_parser as P

APP = 'ARCWorks Kathana Log Analyzer'
VERSION = '1.0.0'
BASE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'ARCWorksPH', 'KathanaLogAnalyzer')
os.makedirs(DATA, exist_ok=True)
SETTINGS = os.path.join(DATA, 'settings.json')

def load_settings():
    try: return json.load(open(SETTINGS, encoding='utf-8'))
    except Exception: return {'recent': [], 'seen_disclaimer': False}

def save_settings(s):
    try: json.dump(s, open(SETTINGS, 'w', encoding='utf-8'), indent=1)
    except Exception: pass

class Api:
    def __init__(self): self.s = load_settings(); self.win = None
    def info(self): return {'app': APP, 'version': VERSION, 'seen_disclaimer': self.s.get('seen_disclaimer', False),
                            'recent': [r for r in self.s.get('recent', []) if os.path.exists(r)][:10]}
    def ack_disclaimer(self): self.s['seen_disclaimer'] = True; save_settings(self.s); return True
    def _remember(self, paths):
        r = [p for p in paths] + [p for p in self.s.get('recent', []) if p not in paths]
        self.s['recent'] = r[:10]; save_settings(self.s)
    def pick_paths(self):
        res = self.win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True,
                                          file_types=('Kathana chat logs (*.txt)', 'All files (*.*)'))
        return list(res or [])
    def pick_files(self):
        res = self.win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True,
                                          file_types=('Kathana chat logs (*.txt)', 'All files (*.*)'))
        return self.open_paths(list(res or []))
    def open_paths(self, paths):
        out = []
        for p in paths:
            try: out.append(P.analyze_file(p))
            except Exception as e: out.append({'name': os.path.basename(p), 'error': str(e)})
        if paths: self._remember(paths)
        return out
    def analyze_text(self, name, text): return P.analyze(text, os.path.splitext(name)[0])
    def merge_texts(self, name, texts): return P.analyze(P.merge_texts(texts), name)
    def merge_paths(self, paths):
        return P.analyze(P.merge_texts([P.read_file(p) for p in paths]),
                         ' + '.join(os.path.splitext(os.path.basename(p))[0] for p in paths))
    def save_report(self, html, suggested):
        res = self.win.create_file_dialog(webview.SAVE_DIALOG, save_filename=suggested,
                                          file_types=('HTML report (*.html)',))
        if not res: return ''
        path = res if isinstance(res, str) else res[0]
        open(path, 'w', encoding='utf-8').write(html)
        return path

def main():
    api = Api()
    api.win = webview.create_window(f'{APP} {VERSION}', os.path.join(BASE, 'ui', 'index.html'),
                                    js_api=api, width=1360, height=880, min_size=(1000, 680), background_color='#0b0f1a')
    webview.start(gui='edgechromium' if sys.platform == 'win32' else None)

if __name__ == '__main__':
    main()
