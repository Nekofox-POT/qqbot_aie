#
# 名称
#

########################################################################################################################
# 资源准备

###########
# 第三方库 #
##########
import openai
import datetime

############
# 自创建模块 #
###########

#########
# 变量池 #
########

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
# 开始程序 #
##########
def main(api_key, msg):

    ### 生成 ###
    try:
        return openai.OpenAI(
            base_url='https://open.bigmodel.cn/api/paas/v4/',
            api_key=api_key
        ).chat.completions.create(
            model="glm-4.6v-flash",
            stream=False,
            messages=[
                {"role": "system", "content": "描述图片的内容"},
                {"role": "user", "content": msg}
            ]
        ).choices[0].message.content
    except Exception as e:
        log(f'解析失败：{e}')
        return None