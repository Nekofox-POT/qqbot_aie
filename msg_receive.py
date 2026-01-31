#
# 信息收集器
#

########################################################################################################################
# 资源准备 #

###########
# 第三方库 #
##########
import fastapi
import uvicorn
import json
import time
import datetime

############
# 自创建模块 #
############

#########
# 变量池 #
########
app = fastapi.FastAPI() # fastapi初始化
user_id = ''    # user_id初始化

########################################################################################################################
# fastapi接口 #
##############

@app.post("/aiq")
async def index(request: fastapi.Request):
    try:

        ### 接收 ###
        tmp = await request.body()
        tmp = json.loads(tmp.decode('utf-8'))

        ### 解析 ###
        # 心跳
        if tmp.get('post_type') == 'meta_event':
            msg_queue.put({'type': 'heart', 'time': int(time.time()), 'status': tmp['status']['online']})
        # 私聊信息
        elif tmp.get('post_type') == 'message':
            if tmp.get('message_type') == 'private' and tmp.get('user_id') == user_id:
                # 爱爱
                if tmp['raw_message'] == '（爱你~）':
                    msg_queue.put({
                        'type': 'system',
                        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'msg': 'end_doi',
                        'notice': True
                    })
                # 指令
                elif tmp['raw_message'][0] in [':', '：']:
                    cmd_queue.put(tmp['raw_message'][1:])
                # 普通信息
                else:
                    msg_queue.put({
                        'type': 'user',
                        'msg': tmp['message'],
                        'raw_msg': tmp['raw_message'],
                        'msg_id': tmp['message_id'],
                        'time': f'{datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")}'
                    })
        # 撤回
        elif tmp.get('post_type') == 'notice':
            if tmp.get('notice_type') == 'friend_recall' and tmp.get('user_id') == user_id:
                msg_queue.put({'type': 'recall', 'msg_id': tmp['message_id']})

    except:
        pass
    return ''

########################################################################################################################
# 主函数 #
########
def main(port, msg_que, cmd_que, qid):
    global cmd_queue
    global msg_queue
    global user_id
    user_id = qid
    msg_queue = msg_que
    cmd_queue = cmd_que
    uvicorn.run(app, host="0.0.0.0", port=port)