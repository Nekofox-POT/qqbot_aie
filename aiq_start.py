#
# aiq开始程序
#
import json
import aiq_main
########################################################################################################################
# 开始程序 #
##########
def aiq_start():

    with open('config.json', 'r', encoding='utf-8') as f:
        tmp = json.loads(f.read())

    print(tmp)

    aiq_main.main(tmp)

if __name__ == '__main__':
    aiq_start()