# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
names = ['이석우', '박준형', '조준형', '김재덕']
for n in names:
    print(f"'{n}': '{n.encode('unicode_escape').decode()}'")
