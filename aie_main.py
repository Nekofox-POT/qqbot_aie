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
import os
import signal
import random

############
# 自创建模块 #
############
import msg_receive
from chat import chat_api
import send_api

#########
# 变量池 #
########
power = True    # 电源
last_heart_post = int(time.time())  # 上一次心跳上报时间
msg_queue = multiprocessing.Queue() # fastapi队列
cmd_queue = multiprocessing.Queue() # 命令队列
msg_list = []   # 消息列表
msg_list_lock = threading.RLock()   # 消息工作锁
last_action_time = int(time.time()) # 最后一次空闲时间
action_free_status = True   # 空闲状态

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
    log('启动fastapi.')
    # 这个要将target_account修改成user_id
    ps_fastapi = multiprocessing.Process(target=msg_receive.main, args=(config['port'], msg_queue, cmd_queue, config['user_id']))
    ps_fastapi.start()

    while power:
        try:

            ### 获取 ###
            tmp = msg_queue.get_nowait()

            ### 解码 ###
            # 心跳
            if tmp['type'] == 'heart':
                last_heart_post = int(time.time())
            # 用户
            elif tmp['type'] == 'user':
                log(f'收到消息：{tmp['raw_msg']}')
                if len(tmp['msg']) == 1 and tmp['raw_msg'][0] != '[':
                    msg_list.append({
                        'type': 'user',
                        'msg': tmp['raw_msg'],
                        'msg_id': tmp['msg_id'],
                        'time': tmp['time'],
                    })
            # 撤回
            elif tmp['type'] == 'recall':
                for i in range(len(msg_list)):
                    if msg_list[i]['msg_id'] == tmp['msg_id']:
                        log(f'消息撤回：{msg_list.pop(i)}')
                        break
            # ai
            elif tmp['type'] == 'assistant':
                log(f'回复: {tmp['msg']}')
                msg_list.append(tmp)
            # 系统消息
            elif tmp['type'] == 'system':
                log(tmp['msg'])
                msg_list.append(tmp)

        except:

            ### 溢出检测(大于4k) ###
            if len(str(msg_list)) > 4 * 1024:
                del msg_list[0]

        # 性能限制
        time.sleep(0.1)

    ### 关机 ###
    os.kill(ps_fastapi.pid, signal.SIGTERM)

###########
# 信息获取 #
##########
def msg_get():

    ### 初始化 ###
    new_msg = False
    try:
        if msg_list[-1]['type'] == 'user':
            new_msg = True
        elif msg_list[-1]['type'] == 'system':
            if msg_list[-2]['type'] == 'user':
                new_msg = True
    except:
        pass
    msg = f'\n当前时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'

    ### 格式化 ###
    for i in msg_list:
        msg += '\n'

        # 用户信息
        if i['type'] == 'user':
            msg += f'{i['time']} {config['user_name']} :\n'
            msg += i['msg']
        # ai信息
        elif i['type'] == 'assistant':
            msg += f'{i['time']} {config['assistant_name']} :\n'
            msg += i['msg']
        # 系统信息
        elif i['type'] == 'system':
            pass

        msg += '\n'

    return [new_msg, msg]


########################################################################################################################
# ai模块

#########
# 动作流 #
#########
def action():

    global last_action_time

    # 暂停15s
    time.sleep(10)

    # 记录
    last_action_time = int(time.time())

#############
# ai运行核心 #
############
def assistant_core():

    ### 启动 ###
    log('启动ai模块.')
    while power:

        ### 执行动作流 ###
        action()

        ### 读取信息 ###
        tmp = msg_get()
        print(tmp)
        # 如果没有新的消息就不管
        if not tmp[0]:
            continue

        ### 生成(在线ai) ###
        result = []
        for i in range(1, 4):
            # 读取提示词
            try:
                with open('role_set.txt', 'r', encoding='utf-8') as f:
                    prompt = f.read()
            except:
                log('文件读取出错，请检查文件完整性.')
                break
            # 生成
            result = chat_api.main(config['model_list'], config['model_random'], prompt, tmp[1])
            try:
                result = json.loads(result)
                print('json格式正常.')
                break
            except:
                print(f'json格式错误，尝试重新生成 ({i} / 3)')
                continue

        ### 回复 ###
        for i in result:
            time.sleep(len(i) * random.randint(2, 20) * 0.1)
            msg_list.append({
                'type': 'assistant',
                'msg': i,
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            tmp = send_api.send_private_msg(config['post_addres'], config['user_id'], i)
            if tmp:
                log(f'发送失败：{tmp}')



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

    ### 开启ai模块 ###
    ps_assistant_core = threading.Thread(target=assistant_core)
    ps_assistant_core.start()
    ps_assistant_core.join()

########################################################################################################################
if __name__ == '__main__':
    import start
    start.aiq_start()