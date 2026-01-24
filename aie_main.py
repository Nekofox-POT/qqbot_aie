#
# AIQ / AIE 主程序
#

########################################################################################################################
# 资源准备

###########
# 第三方库 #
##########
import multiprocessing
import time
import json
import threading
import datetime

############
# 自创建模块 #
############
import msg_receive

#########
# 变量池 #
########
last_heart_post = int(time.time())  # 上一次心跳上报时间
msg_queue = multiprocessing.Queue() # fastapi队列
cmd_queue = multiprocessing.Queue() # 命令队列
msg_list = []   # 消息列表
msg_list_lock = threading.RLock() # 消息工作锁

########################################################################################################################
# 小组件

###########
# 日志记录 #
##########
def log(msg):
    print(msg)
    # 读取文件
    try:
        with open('aie_log.txt', 'r', encoding='utf-8') as f:
            tmp = f.readlines()
    except:
        with open('aie_log.txt', 'w', encoding='utf-8') as f:
            f.close()
        with open('aie_log.txt', 'r', encoding='utf-8') as f:
            tmp = f.readlines()
    if len(tmp) > 65536:
        tmp = tmp[1:]
    # 写入
    tmp.append(f'{datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {msg}\n')
    with open('aie_log.txt', 'w', encoding='utf-8') as f:
        f.writelines(tmp)
        f.close()

########################################################################################################################
# 信息处理

###########
# 信息储存 #
##########
def msg_store():

    global last_heart_post

    ### 启动fastapi ###
    log('启动fastapi')
    ps_fastapi = multiprocessing.Process(target=msg_receive.main, args=(config['port'], msg_queue, cmd_queue, config['user_id']))
    ps_fastapi.start()

    while True:
        try:

            ### 获取 ###
            tmp = msg_queue.get_nowait()

            ### 解码 ###
            # 心跳
            if tmp['type'] == 'heart':
                last_heart_post = int(time.time())
            # 用户
            elif tmp['type'] == 'user':
                msg_list.append(tmp)
            # 撤回
            elif tmp['type'] == 'recall':
                for i in range(len(msg_list)):
                    if msg_list[i]['msg_id'] == tmp['msg_id']:
                        msg_list.pop(i)
                        break
            # ai
            elif tmp['type'] == 'assistant':
                msg_list.append(tmp)
            # 系统消息
            elif tmp['type'] == 'system':
                msg_list.append(tmp)

        except:
            pass

        # 性能限制
        time.sleep(0.1)

###########
# 信息获取 #
##########
def msg_get():
    pass
########################################################################################################################
# ai模块

########################################################################################################################
# 主程序 #
########
def main(input_config):

    log('AIQ启动.')

    ### 配置变量 ###
    global config
    config = input_config

    ### Windows安全声明 ###
    multiprocessing.freeze_support()

    ### 开启信息接收器 ###
    ps_msg_store = threading.Thread(target=msg_store)
    ps_msg_store.start()

    while True:
        # 每隔10秒输出一次
        print('-----------------------------')
        print(msg_get())
        print('-----------------------------')
        time.sleep(30)

########################################################################################################################
if __name__ == '__main__':
    import start
    start.aiq_start()