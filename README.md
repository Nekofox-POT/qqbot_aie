# AIE

### 一个电子女友
![基于onebot11构建](https://img.shields.io/badge/OneBot-11-blue?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHAAAABwCAMAAADxPgR5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAAxQTFRF////29vbr6+vAAAAk1hCcwAAAAR0Uk5T////AEAqqfQAAAKcSURBVHja7NrbctswDATQXfD//zlpO7FlmwAWIOnOtNaTM5JwDMa8E+PNFz7g3waJ24fviyDPgfhz8fHP39cBcBL9KoJbQUxjA2iYqHL3FAnvzhL4GtVNUcoSZe6eSHizBcK5LL7dBr2AUZlev1ARRHCljzRALIEog6H3U6bCIyqIZdAT0eBuJYaGiJaHSjmkYIZd+qSGWAQnIaz2OArVnX6vrItQvbhZJtVGB5qX9wKqCMkb9W7aexfCO/rwQRBzsDIsYx4AOz0nhAtWu7bqkEQBO0Pr+Ftjt5fFCUEbm0Sbgdu8WSgJ5NgH2iu46R/o1UcBXJsFusWF/QUaz3RwJMEgngfaGGdSxJkE/Yg4lOBryBiMwvAhZrVMUUvwqU7F05b5WLaUIN4M4hRocQQRnEedgsn7TZB3UCpRrIJwQfqvGwsg18EnI2uSVNC8t+0QmMXogvbPg/xk+Mnw/6kW/rraUlvqgmFreAA09xW5t0AFlHrQZ3CsgvZm0FbHNKyBmheBKIF2cCA8A600aHPmFtRB1XvMsJAiza7LpPog0UJwccKdzw8rdf8MyN2ePYF896LC5hTzdZqxb6VNXInaupARLDNBWgI8spq4T0Qb5H4vWfPmHo8OyB1ito+AysNNz0oglj1U955sjUN9d41LnrX2D/u7eRwxyOaOpfyevCWbTgDEoilsOnu7zsKhjRCsnD/QzhdkYLBLXjiK4f3UWmcx2M7PO21CKVTH84638NTplt6JIQH0ZwCNuiWAfvuLhdrcOYPVO9eW3A67l7hZtgaY9GZo9AFc6cryjoeFBIWeU+npnk/nLE0OxCHL1eQsc1IciehjpJv5mqCsjeopaH6r15/MrxNnVhu7tmcslay2gO2Z1QfcfX0JMACG41/u0RrI9QAAAABJRU5ErkJggg==)

###### 来群里聊天吧（求求了！），如果有bug、乐子可以砸群u头上
###### ~~（发石也可以，群主是xnn）~~
###### qq群：1080024537

---

## 🌟 项目特性

- **多对话模式**：支持本地模型和API接口两种对话方式
- **多平台支持**：可在Wi10 1903 2004 21H1 21H2 22H2和win11 21H2 22H2 23H2 24H2 25H2等系统上运行
- 
- （以上都是ai乱写的，实际上根本没有特性）
- 
- **其他特性**：
- **对话模式**：可使用API接口和本地模型（基于ollama）主备生成
- **特殊模式**：特定场景下会解锁隐藏CG

## 🚀 快速开始

### 运行前准备

```bash
确保安装好前端环境（llbot，napcat等）
（本地部署需要）安装好ollama。
```
#### llbot项目地址：https://www.llonebot.com/guide/introduction
#### ollama项目地址：https://ollama.com/

### 运行程序

```bash
运行 start.exe
配置好http端口，接口
```

### 关于前端配置请看这里（以llbot为例）：
[llbot配置参考](guide_md/llbot_set.md)

首次运行时会自动启动配置引导程序，按照提示完成配置即可。

## 🔧 功能说明

### 目前支持的指令（在聊天框内使用“：” + “{指令}”）：
- **清空**：清空所有聊天记录
- **重载**：重新载入人设
- **再见**：关闭系统
##### 还有一个隐藏指令，请在特定模式下聊天框内输入"：h"查看。
![命令示例](guide_md/img/cmd.png)

## ⚙️ 配置说明

程序运行时会创建以下配置文件：
- `config.ppp`：配置文件
- `chat.ppp`：聊天记录文件
- `aie_log.txt`：运行日志文件