import os, sys

root = '.'
changed = []
text_exts = {'.py','.md','.txt','.yaml','.yml','.json','.csv','.ini','.conf','.bat','.sh','.html'}

for dirpath, dirnames, filenames in os.walk(root):
    if '.git' in dirpath.split(os.sep):
        continue
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        ext = os.path.splitext(fn)[1].lower()
        try:
            with open(path, 'rb') as f:
                data = f.read()
            if ext not in text_exts:
                if b'\x00' in data:
                    continue
            try:
                s = data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    s = data.decode('cp1252')
                except Exception:
                    continue
            s2 = s.encode('cp1252', errors='ignore').decode('cp1252')
            if s2 != s:
                with open(path, 'w', encoding='cp1252', errors='ignore') as f:
                    f.write(s2)
                changed.append(path)
        except Exception:
            pass

print('Stripped non-cp1252 from', len(changed), 'files')
for p in changed:
    print(p)
