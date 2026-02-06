from aes_encryption import aes_encryption
import pickle
import datetime

with open('config.ppp', 'rb') as f:
    config = pickle.loads(aes_encryption.decrypt(f.read()))



for i in config:
    print(i, ': ', config[i])

with open('chat.ppp', 'rb') as f:
    tmp = pickle.loads(aes_encryption.decrypt(f.read()))



print('----------------')
msg = f'\n当前时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
for i in tmp:
    # 用户信息
    if i['type'] == 'user':
        msg += f'{i['time']} {config['user_name']} :\n'
        msg += i['msg']
        last_user_time = i['time']
    # ai信息
    elif i['type'] == 'assistant':
        msg += f'{i['time']} {config['assistant_name']} :\n'
        msg += i['msg']
    # 系统信息
    elif i['type'] == 'system':
        msg += f'{i['time']} {i['msg']}\n'

    msg += '\n'

print(msg)
print('----------------')