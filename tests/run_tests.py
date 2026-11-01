import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_parser as t
for n in sorted(dir(t)):
    if n.startswith('test_'): getattr(t, n)(); print('  PASS', n)
print('  All parser tests passed.')
