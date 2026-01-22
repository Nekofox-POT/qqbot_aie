from pickle import load, dump
try:
    with open('version.ppp', 'rb') as f:
        a = load(f)
    print(f'当前版本号：{a}')
except:
    pass
a = str(input('输入版本号>'))
with open('version.ppp', 'wb') as f:
    dump(a, f)