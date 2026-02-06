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
import threading
import datetime
import os
import signal
import random
import pickle

############
# 自创建模块 #
############
import msg_receive
from chat import chat_api, chat_local, chat_doi, chat_img
import send_api
from aes_encryption import aes_encryption

#########
# 变量池 #
########

# 示例提示词
prompt_example = (
    '[角色]\n'
    '你将扮演一个19岁的女生，名字叫“XX”。\n'
    '\n'
    '[角色性格]\n'
    '性格时腼腆时撒娇调皮。\n'
    '\n'
    '[外表]\n'
    '穿着时尚，头发长而顺。脸上总是挂着微笑。\n'
    '\n'
    '[喜好]\n'
    '喜欢听音乐，喜欢陪伴在男朋友的身旁。\n'
    '\n'
    '[用户角色]\n'
    '20岁男生，名字叫“OO”。\n'
    '\n'
    '[用户角色性格]\n'
    '喜欢调戏对象，但对对象非常体贴。\n'
    '\n'
    '[经历]\n'
    '在高中时期与男朋友相识。现在两人考入了不同的大学，仍然保持紧密的联系\n'
)

power = True    # 电源
last_heart_post = int(time.time())  # 上一次心跳上报时间
msg_queue = multiprocessing.Queue() # fastapi队列
cmd_queue = multiprocessing.Queue() # 命令队列
msg_list = []   # 消息列表
msg_list_lock = threading.RLock()   # 消息工作锁
last_action_time = int(time.time()) # 最后一次空闲时间
action_free_status = True   # 空闲状态
last_user_time = 0  # 用户最后一次发言时间
doi_mode = False    # doi模式
last_doi_list_range = 0   # 最后一个激活爱爱的语句指针

# 睡眠类
sleep_time = [random.choice([22, 23, 0, 1, 2, 3, 4]), random.randint(5, 54)] # 随机睡眠时间段
is_sleep = False    # 睡觉指示
sleep_notice = True # 睡眠提示

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
def plog(msg):
    log(msg)
    if config['report_error']:
        r = send_api.send_private_msg(config['post_addres'], config['user_id'], msg)
        if r:
            log(f'日志上报失败：{r}')

########################################################################################################################
# 信息处理

################
# 用户信息格式化 #
###############
def process_user_msg(raw_msg):
    # 遍历消息
    msg = ''
    for i in raw_msg:
        ### 文本 ###
        if i['type'] == 'text':
            msg += i['data']['text']
            msg += '\n'
        ### 回复 ###
        if i['type'] == 'reply':
            # 获取原信息
            text = send_api.get_msg(config['post_addres'], i['data']['id'])
            msg += '(\n'
            if text['user_id'] == config['user_id']:
                msg += f'回复 "{config['user_name']}" :\n'
            else:
                msg += f'回复 "{config['assistant_name']}" :\n'
            # 遍历消息
            msg += process_user_msg(text['message'])
            msg += '\n)\n'
        ### 图片/表情 ###
        if i['type'] == 'image':
            log('接收到图片.')
            # 解析图片
            img = chat_img.main(config['vision_model_list'], config['allow_model_random'], i['data']['url'])
            if img:
                msg += img
                msg += '\n'
    msg = msg[:-1]
    return msg

###########
# 信息收集 #
##########
def msg_collect():

    global msg_list, last_heart_post, doi_mode, last_doi_list_range, is_sleep
    tmp_list = []

    ### 读数据 ###
    with msg_list_lock:
        try:
            with open('chat.ppp', 'rb') as f:
                msg_list = pickle.loads(aes_encryption.decrypt(f.read()))
        except:
            msg_list = []

    ### 启动fastapi ###
    log('启动fastapi.')
    ps_fastapi = multiprocessing.Process(target=msg_receive.main, args=(config['port'], msg_queue, cmd_queue, config['user_id']))
    ps_fastapi.start()

    while power:
        try:

            ### 获取 ###
            tmp = msg_queue.get_nowait()

            ### 解码 ###
            with msg_list_lock:

                # 心跳
                if tmp['type'] == 'heart':
                    last_heart_post = int(time.time())
                    if not tmp['status'] and config['heart_check']:
                        plog('设备已离线，请检查设备是否正常！')
                # 用户
                elif tmp['type'] == 'user':
                    # 遍历处理消息
                    msg = process_user_msg(tmp['msg'])
                    # 添加
                    if msg:
                        log(f'收到消息：{msg}')
                        msg_list.append({
                            'type': 'user',
                            'msg': msg,
                            'msg_id': tmp['msg_id'],
                            'time': tmp['time'],
                        })
                # 撤回
                elif tmp['type'] == 'recall':
                    for i in range(len(msg_list)):
                        if msg_list[i].get('msg_id') == tmp['msg_id']:
                            log(f'消息撤回：{msg_list.pop(i)}')
                            break
                # ai
                elif tmp['type'] == 'assistant':
                    log(f'回复: {tmp['msg']}')
                    # 爱爱
                    if tmp['msg'] == 'use_doi':
                        log('爱爱❤~')
                        doi_mode = True
                        # 初始化最后用户发言的指针
                        e = False
                        for i in range(len(msg_list)):
                            # 如果是用户/系统
                            if msg_list[len(msg_list) - 1 - i]['type'] == 'user' or msg_list[len(msg_list) - 1 - i]['type'] == 'system':
                                # 头为0则直接添加
                                if len(msg_list) - 1 - i == 0:
                                    last_doi_list_range = 0
                                else:
                                    # 标记
                                    e = True
                            # 如果不是
                            else:
                                if e:
                                    last_doi_list_range = len(msg_list) - i
                    # 睡觉
                    elif tmp['msg'] == 'sleep':
                        log('该睡觉了.')
                        is_sleep = True
                    # 结束话题
                    elif tmp['msg'] == 'end':
                        msg_queue.put({
                            'type': 'assistant',
                            'msg': ['动画表情'],
                            'time': datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
                        })
                    # 普通消息
                    else:
                        # 发送
                        r = send_api.send_private_msg(config['post_addres'], config['user_id'], tmp['msg'])
                        if r:
                            log(f'发送失败：{r}')
                            continue
                        msg_list.append(tmp)
                # 系统消息
                elif tmp['type'] == 'system':
                    # 爱爱结束
                    if tmp['msg'] == 'end_doi':
                        if config['allow_doi'] and doi_mode:
                            log('爱爱结束.')
                            # 合并发言
                            if last_doi_list_range == 0:
                                msg_list = []
                            else:
                                msg_list = msg_list[:last_doi_list_range - 1]
                            msg_queue.put({
                                'type': 'system',
                                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'msg': '{系统提示：你们刚才经历了一次文爱}',
                                'notice': True
                            })
                            doi_mode = False
                        else:
                            # 转发
                            msg_queue.put({
                                'type': 'user',
                                'msg': {'type': 'text', 'data': {'text': '（爱你~）'}},
                                'msg_id': tmp['msg_id'],
                                'time': tmp['time']
                            })
                    # 普通消息
                    else:
                        log(f'[{tmp['msg']}]')
                        msg_list.append(tmp)

        except:

            ### 溢出检测(大于4k) ###
            #↑# doi模式不删除 #↑#
            if len(str(msg_list)) > 4 * 1024 and not doi_mode:
                del msg_list[0]

        ### 储存 ###
        with msg_list_lock:
            if tmp_list != msg_list:
                tmp_list = msg_list.copy()
                with open('chat.ppp', 'wb') as f:
                    f.write(aes_encryption.encrypt(pickle.dumps(tmp_list)))
        # 性能限制
        time.sleep(0.1)

    ### 关机 ###
    os.kill(ps_fastapi.pid, signal.SIGTERM)

###########
# 信息获取 #
##########
def msg_get():

    global last_user_time, last_doi_list_range

    with msg_list_lock:
        ### 新消息提醒 ###
        new_msg = False
        try:
            if msg_list[-1]['type'] == 'user':
                new_msg = True
            elif msg_list[-1]['type'] == 'system':
                if msg_list[-1]['notice']:
                    new_msg = True
                else:
                    if msg_list[-2]['type'] == 'user':
                        new_msg = True
        except:
            pass
        msg = f'\n当前时间：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'

        ### 格式化 ###
        tmp_range = 0
        # 爱爱模式（要限制大小）
        if doi_mode and len(msg_list) > 25:
            tmp_range = len(msg_list) - 25
        for i in msg_list[tmp_range:]:
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

    return [new_msg, msg, last_user_time]

########################################################################################################################
# ai模块

#########
# 动作流 #
#########
def action(jump = False):

    if not jump:

        global last_action_time, sleep_time, is_sleep, sleep_notice

        ### 睡眠操作 ###
        # 该睡觉了
        if is_sleep:
            # 睡眠（随机6-9小时）
            msg_queue.put({
                'type': 'system',
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'msg': '{系统提示：你睡着了}',
                'notice': True
            })
            tmp = random.randint(5 * 60, 9 * 60)
            log(f'开始睡眠，时长{tmp}分钟...')
            time.sleep(tmp * 60)
            is_sleep = False
            log('醒来.')
            msg_queue.put({
                'type': 'system',
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'msg': '{系统提示：你醒了}',
                'notice': True
            })
            sleep_time = [random.choice([22, 23, 0, 1, 2, 3, 4]), random.randint(5, 54)]
            sleep_notice = True
            log(f'睡眠时间重置：{sleep_time}')
            time.sleep(30)
        # 睡觉提示
        if time.localtime().tm_hour == sleep_time[0] and sleep_time[1] - 5 <= time.localtime().tm_min <= sleep_time[1] + 5 and sleep_notice:
            msg_queue.put({
                'type': 'system',
                'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'msg': '{系统提示：你有点困，想睡觉了}',
                'notice': True
            })
            sleep_notice = False
            time.sleep(5)

        # 暂停15s
        time.sleep(1)

        # 记录
        last_action_time = int(time.time())

#############
# ai运行核心 #
############
def assistant_core():

    re_generate = False

    ### 启动 ###
    log('启动ai模块.')
    log(f'睡眠时间重置：{sleep_time}')
    while power:

        ### 普通模式 ###
        if not doi_mode:

            ### 执行动作流 ###
            if re_generate:
                action(True)
                re_generate = False
            else:
                action()

            ### 等待读取信息 ###
            while True:
                # 获取新信息
                tmp = msg_get()
                time.sleep(10)
                # 有更新则重新等
                if msg_get()[2] != tmp[2]:
                    continue
                break
            # 如果没有新的消息就不管
            if not tmp[0]:
                continue
            # 记录最后信息
            last_time = tmp[2]

            ### 生成(在线ai) ###
            result = chat_api.main(config['model_list'], config['allow_model_random'], config['allow_doi'], config['prompt'], tmp[1])

            ### 没有则本地生成 ###
            if not result and config['local_model']:
                result = chat_local.main(config['allow_doi'], config['prompt'], tmp[1])

            ### 还是没有 ###
            if not result:
                plog('生成失败.')
                continue

            ###  若生成后有新的信息，则重新生成 ###
            tmp = msg_get()
            if tmp[2] != last_time:
                log('有新消息，重新生成...')
                re_generate = True
                continue

            ### 回复 ###
            for i in result:
                # 添加消息队列
                for e in i:
                    time.sleep(random.uniform(0.2, 1.2))
                msg_queue.put({
                    'type': 'assistant',
                    'msg': i,
                    'time': datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
                })

            ### 如果是爱爱则需要等待切换 ###
            if result == ['use_doi']:
                while not doi_mode:
                    time.sleep(0.1)

        ### doi模式 ###
        else:

            ### 等待读取 ###
            while True:
                # 获取新信息
                tmp = msg_get()
                time.sleep(30)
                # 有更新则重新等
                if msg_get()[2] != tmp[2]:
                    continue
                break

            # 如果没有新的消息就不管
            if not tmp[0]:
                continue

            ### 如果模式被改变了，立即退出 ###
            if not doi_mode:
                continue

            ###  生成(本地ai) ###
            result = chat_doi.main(config['prompt'], tmp[1])

            ### 没有 ###
            if not result:
                plog('生成失败.')
                continue

            ### 回复 ###
            for i in result:
                # 添加消息队列
                for e in i:
                    time.sleep(random.uniform(0.2, 1.2))
                msg_queue.put({
                    'type': 'assistant',
                    'msg': i,
                    'time': datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'),
                })

#########################################################################################################################
# 指令集 #
########
def cmd(msg):

    ### 重置聊天列表 ###
    def clear():
        global msg_list
        msg_list = []
        r = send_api.send_private_msg(config['post_addres'], config['user_id'], 'ok.')
        if r:
            log(f'发送失败：{r}')
        log('聊天列表已重置.')
    ### 重载人设 ###
    def reload():
        global config
        try:
            with open('role_set.txt', 'r', encoding='utf-8') as f:
                tmp = f.read()
        except:
            plog('Error：文件读取失败，请检查文件。（已重新生成一份，本次不作录入）')
            with open('role_set.txt', 'w', encoding='utf-8') as f:
                f.write(prompt_example)
        else:
            config['prompt'] = tmp
            with open('config.ppp', 'wb') as f:
                f.write(aes_encryption.encrypt(pickle.dumps(config)))
            log('人设已重载.')
            r = send_api.send_private_msg(config['post_addres'], config['user_id'], 'ok.')
            if r:
                log(f'发送失败：{r}')
    ### 关机 ###
    def shutdown():
        global power
        r = send_api.send_private_msg(config['post_addres'], config['user_id'], '再见哦！')
        if r:
            log(f'发送失败：{r}')
        log('设置关机状态.')
        power = False

    command = [
        ['清空', clear, '清空所有聊天记录'],
        ['重载', reload, '重新载入人设'],
        ['再见', shutdown, '关闭系统']
    ]

    log(f'收到指令：{msg}')
    if msg == 'h':
        tmp = ''
        for i in command:
            tmp += f'{i[0]}：{i[2]}\n'
        if config['allow_doi']:
            tmp += '（爱你~）：结束爱爱。（此指令不需要打“：”）'
        r = send_api.send_private_msg(config['post_addres'], config['user_id'], tmp)
        if r:
            log(f'发送失败：{r}')
        return None
    is_cmd = False
    for i in command:
        if i[0] == msg:
            is_cmd = True
            i[1]()
            break
    if not is_cmd:
        log(f'未知指令：{msg}')
    return None

########################################################################################################################
# 主程序 #
########
def main(input_config):

    log('aie启动.')

    ### 配置变量 ###
    global config
    config = input_config

    ### Windows安全声明 ###
    multiprocessing.freeze_support()

    ### 开启信息接收器 ###
    ps_msg_collect = threading.Thread(target=msg_collect)
    ps_msg_collect.start()

    ### 开启ai模块 ###
    ps_assistant_core = threading.Thread(target=assistant_core)
    ps_assistant_core.start()

    ### 等待结束（处理指令） ###
    while power:
        try:
            tmp = cmd_queue.get_nowait()
            cmd(tmp)
        except:
            time.sleep(0.1)
            continue

    ### 结束 ###
    ps_msg_collect.join()
    ps_assistant_core.join()
    log('aie关闭.')

########################################################################################################################
if __name__ == '__main__':
    import start
    start.aiq_start()