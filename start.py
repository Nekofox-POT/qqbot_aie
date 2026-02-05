#
# aiq/aie 开始程序
#
version = '3.1'    # 版本号
########################################################################################################################
# 资源准备 #

###########
# 第三方库 #
##########
import pickle

############
# 自创建模块 #
############
try:
    from aes_encryption import aes_encryption
except:
    print('请先运行aes_encryption/aes_create.py 生成 aes_encryption.py')
    input('按任意键继续>|')
    from aes_encryption import aes_encryption
import aie_main
from first_start_guide_child import first_start_guide
from update import update_manager

#########
# 变量池 #
########

########################################################################################################################
# 开始程序 #
##########
def aiq_start():

    ### 读取文件 ###
    try:
        ### 读取 ###
        with open('config.ppp', 'rb') as f:
            config = pickle.loads(aes_encryption.decrypt(f.read()))
        ### 检查版本更新 ###
        config = update_manager.update(config)
        with open('config.ppp', 'wb') as f:
            f.write(aes_encryption.encrypt(pickle.dumps(config)))
        if config['version'] != version:
            # 版本号不对，报错
            print('警告：版本号不一致！')
            print(f'当前数据库版本号：{config}')
            raise IOError
    except:
        # 读取失败，重新创建
        print('配置文件读取失败.')
        print('可能是第一次启动，亦或者是文件损坏.')
        print('点击Enter创建（新的）配置文件...')
        input('>|')
        config = first_start_guide.guide(version)
        print('初始化...')
        print('>|')

    ### 启动 ###
    aie_main.main(config)

if __name__ == '__main__':
    aiq_start()