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
import re
import json
import requests
import io
import base64
import random
from PIL import Image

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

#############
# json格式化 #
#############
def extract_json(text):
    # 更精确的模式来匹配你的JSON格式
    pattern = r'\{\s*"type":\s*"[^"]*".*?"context":\s*"[^"]*"\s*\}'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        json_str = match.group(0)
        try:
            json_obj = json.loads(json_str)
            return json.dumps(json_obj, ensure_ascii=False)
        except json.JSONDecodeError:
            pass

    return None

###########
# 链接获取 #
##########
def url_to_base64(url):
    # 下载处理
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
    # 处理GIF
    if img.format == 'GIF':
        img = img.convert('RGB')
    # 确保非RGB模式的图片转换为RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    # 保存为JPG格式
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    # 转换为base64
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

########################################################################################################################
# 开始程序 #
##########
def main(model_url, api_key, url):

    ### 生成 ###
    try:
        tmp = openai.OpenAI(
            base_url=model_url,
            api_key=api_key
        ).chat.completions.create(
            model="glm-4.6v",
            stream=False,
            messages=[
                {"role": "system", "content": "判断并简述图片的内容\n判断分类图片类型为“动画表情”还是“图片”。\n使用json输出\n输出示例：{\"type\": \"动画表情\", \"context\": 描述的内容}"},
                {"role": "user", "content": [{"type": "image_url", "image_url": {"url": url_to_base64(url)}}]}
            ]
        )
        tmp = json.loads(extract_json(tmp.choices[0].message.content))
        return f'[{tmp['type']}: {tmp['context']}]'
    except Exception as e:
        log(f'解析失败：{e}')
        return None

def main(model_list, model_random, url):

    # 随机模式
    if model_random:

        model = random.choice(model_list)
        log(f'使用模型：{model[1]}')
        log('（随机模式）开始在线生成...')
        try:
            result = openai.OpenAI(
                base_url=model[0],
                api_key=model[2],
            ).chat.completions.create(
                model=model[1],
                stream=False,
                messages=[
                    {"role": "system", "content": "判断并简述图片的内容\n判断分类图片类型为“动画表情”还是“图片”。\n使用json输出\n输出示例：{\"type\": \"动画表情\", \"context\": 描述的内容}"},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": url_to_base64(url)}}]}
                ]
            ).choices[0].message.content
            return json.loads(extract_json(result))
        except Exception as e:
            log(f'{model[1]}生成失败：{e}')
            log('切换顺序模式重试...')

    # 顺序模式

    ### 生成 ###
    for i in model_list:
        log(f'使用模型：{i[1]}')
        log('（顺序模式）开始在线生成...')
        try:
            result = openai.OpenAI(
                base_url=i[0],
                api_key=i[2],
            ).chat.completions.create(
                model=i[1],
                stream=False,
                messages=[
                    {"role": "system", "content": "判断并简述图片的内容\n判断分类图片类型为“动画表情”还是“图片”。\n使用json输出\n输出示例：{\"type\": \"动画表情\", \"context\": 描述的内容}"},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": url_to_base64(url)}}]}
                ]
            ).choices[0].message.content
            return json.loads(extract_json(result))
        except Exception as e:
            log(f'{i[1]}生成失败：{e}')
            log('下一个模型重试.')

    return None