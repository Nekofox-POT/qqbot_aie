#
# aiq/aie 开始程序
#
version = '3.0.0'    # 版本号
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
import first_start_guide

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
        ### 检查版本 ###
        if config['version'] != version:
            # 更新
            print('版本号不一致')
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