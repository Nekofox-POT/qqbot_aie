from aes_encryption import aes_encryption
import pickle

with open('config.ppp', 'rb') as f:
    config = pickle.loads(aes_encryption.decrypt(f.read()))
for i in config:
    print(i, ': ', config[i])

with open('chat.ppp', 'rb') as f:
    tmp = pickle.loads(aes_encryption.decrypt(f.read()))

for i in tmp:
    print(i)