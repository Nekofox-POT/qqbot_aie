#
# aie配置文件升级程序
#

########################################################################################################################
# 资源准备

###########
# 第三方库 #
##########
import openai

############
# 自创建模块 #
###########

#########
# 变量池 #
########
test_image_base64 = (
    '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUG'
    'BIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAEAAQADAS'
    'IAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaE'
    'II0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKj'
    'pKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcIC'
    'QoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERU'
    'ZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uP'
    'k5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9U6KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACi'
    'iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKTIpaACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoopO1AC0Vwv'
    'xp1q70D4O+PNTspDFe2OhX91C44KulvIyn8wK+A/wBnP4e/tS/H74QaB48039o2bQrPVRMqWM+mrM8flTyw8t3z5efxoA/TaivhYfsoftaH/m6X/w'
    'Ao615B+1L4d/ai/Zd+F7eNtW/aNutbslvIrM29ppaI+6Tdg5Pb5TQB+pFFZnh6d59HtJJGLO0YJJ7183/F39trV/hh8QdU8MWfwN+IPi+Kx2Aatom'
    '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'
)

########################################################################################################################
# 升级程序

#################
# 3.0.0 → 3.1.x #
#################
def v300to31(config):

    ##############
    # 模型添加函数 #
    #############
    def add_model():

        while True:

            print('请选择添加的模型：')
            print('1.ChatGLM    glm-4.6v')
            print('2.Qwen       qwen3-vl-plus')
            print('3.Doubao     doubao-seed-1-8-251228')
            print('4.Kimi       kimi-k2.5')
            print('')
            print('0.自定义')
            print('')
            tmp = str(input('>'))
            if tmp == '1':
                print('已选择: "ChatGLM"')
                api = 'https://open.bigmodel.cn/api/paas/v4/'
                model = 'glm-4.6v'
            elif tmp == '2':
                print('已选择: "Qwen"')
                api = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
                model = 'qwen3-vl-plus'
            elif tmp == '3':
                print('已选择: "Doubao"')
                api = 'https://ark.cn-beijing.volces.com/api/v3'
                model = 'doubao-seed-1-8-251228'
            elif tmp == '4':
                print('已选择: "Kimi"')
                api = 'https://api.moonshot.cn/v1'
                model = 'kimi-k2.5'
            elif tmp == '0':
                print('自定义.')
                print('请输入模型地址：')
                api = str(input('>'))
                print(f'输入了: "{api}"')
                print('请输入使用的模型：')
                model = str(input('>'))
                print(f'输入了: "{model}"')
            else:
                print('请输入正确的选项.')
                continue
            print('请输入api_key：')
            key = str(input('>'))
            print(f'输入了: "{key}"')

            # 测试
            print('测试api可用性...')
            try:
                openai.OpenAI(
                    api_key=key,
                    base_url=api
                ).chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "简述图片的内容"},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{test_image_base64}"
                                    }
                                }
                            ]
                        },
                    ],
                    stream=False
                )
                print('测试成功.')
                return [api, model, key]
            except Exception as e:
                print('测试失败，请检查api_key是否正确或模型地址是否正确')
                print(f'失败原因：{e}')
                print('1.重新写入 2.取消写入 3.仍要写入')
                while True:
                    tmp = str(input('>'))
                    if tmp == '1':
                        print('重新写入...')
                        break
                    elif tmp == '2':
                        print('取消写入.')
                        return None
                    elif tmp == '3':
                        print('写入.')
                        return [api, model, key]
                    else:
                        print('请输入正确的选项.')

    print('----------------------------')
    print('Version 3.0.x → 3.1.x')
    print('----------------------------')
    print('')
    print('应3.1.x版本要求，本次更新需要添加全新的视觉模型。')

    ### 添加视觉模型 ###
    # 扫描
    vision_model_list = []
    for i in config['model_list']:
        # 如果有预制的模型
        if i[0] == 'https://open.bigmodel.cn/api/paas/v4/':
            vision_model_list.append([i[0], 'glm-4.6v', i[2]])
        elif i[0] == 'https://ark.cn-beijing.volces.com/api/v3/chat/completions':
            vision_model_list.append([i[0], 'doubao-seed-1-8-251228', i[2]])
        elif i[0] == 'https://dashscope.aliyuncs.com/compatible-mode/v1':
            vision_model_list.append([i[0], 'qwen3-vl-plus', i[2]])
        elif i[0] == 'https://api.moonshot.cn/v1':
            vision_model_list.append([i[0], 'kimi-k2.5', i[2]])
    # 如果有
    if vision_model_list:
        print('检测到有以下可添加的视觉模型：')
        for i in vision_model_list:
            print(f'模型名称："{i[1]}" 模型地址："{i[0]}" api_key："{i[2]}"')
        print('是否添加？')
        print('1.是 2.否 (默认：是)')
        choice = str(input('>'))
        if choice == '' or choice == '1':
            print('添加.')
        else:
            print('取消.')
            vision_model_list = []
    # 添加操作
    while True:

        ### 展示 ###
        print('当前大模型列表')
        print('')
        if len(vision_model_list) == 0:
            print('0. 空')
        else:
            for i in range(len(vision_model_list)):
                print(f'{i + 1}. 模型名称："{vision_model_list[i][1]}" 模型地址："{vision_model_list[i][0]}" api_key："{vision_model_list[i][2]}"')
        print('')

        ### 添加 ###
        print('1.添加 2.重新添加 3.就用这么多')
        tmp = str(input('>'))
        if tmp == '1':

            ### 添加模型 ###
            tmp = add_model()
            if tmp:
                vision_model_list.append(tmp)

        elif tmp == '2':
            print('确定要全部重写吗？')
            print('1.确定 2：取消')
            tmp = str(input('>'))
            if tmp == '1':
                vision_model_list = []
                print('已重置.')
            if tmp == '2':
                print('已取消.')
            else:
                print('请输入正确的选项.')
        elif tmp == '3':
            if len(vision_model_list) == 0:
                print('当前没有模型，请添加模型.')
            else:
                break
        else:
            print('请输入正确的选项.')
    # 写入
    config['vision_model_list'] = vision_model_list

    ### 修改变量 ###
    config['allow_model_random'] = config['model_random']
    del config['model_random']

    ### 修改版本号 ###
    config['version'] = '3.1'

    ### 返回 ###
    return config