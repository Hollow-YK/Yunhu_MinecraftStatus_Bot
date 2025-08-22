<!-- markdownlint-disable -->

<div align="center">

# Yunhu_MinecraftStatus_Bot

<br>
<div>
    <img alt="platform" src="https://img.shields.io/badge/platform-Windows-blueviolet">
</div>
<div>
    <img alt="license" src="https://img.shields.io/github/license/Hollow-YK/Yunhu_MinecraftStatus_Bot">
    <img alt="commit" src="https://img.shields.io/github/commit-activity/m/Hollow-YK/Yunhu_MinecraftStatus_Bot?color=%23ff69b4">
</div>
<div>
    <img alt="stars" src="https://img.shields.io/github/stars/Hollow-YK/Yunhu_MinecraftStatus_Bot?style=social">
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/Hollow-YK/Yunhu_MinecraftStatus_Bot/total?style=social">
</div>
<br>

<!-- markdownlint-restore -->


将Minecraft服务器状态同步至云湖群聊看板的机器人

基于[云湖官方Python SDK](https://github.com/yhchat/bot-python-sdk/)与[mcstatus库](https://github.com/py-mine/mcstatus/)。

</div>

## 下载与安装

请阅读本 `README.md` 后前往 [Releases](https://github.com/Hollow-YK/Yunhu_MinecraftStatus_Bot/releases/) 下载，并参考 `README.md` 进行使用。

## 功能

- 获取指定Minecraft服务器信息，包括**版本**、**服务器地址**、**服务器在线人数**、**服务器最大在线人数**
- 将获取的信息同步至云湖指定群聊看板或指定用户看板
- 获取服务器成员列表，并列出服务器成员进出情况（此功能可能存在Bug，欢迎提交更改）
- 支持多群、多用户同步
- 详细日志记录，便于故障排查
- 命令行参数支持，灵活控制日志输出

## 使用说明

### 安装依赖

安装 [Python 3](https://www.python.org/) 与 [pip](https://pypi.org/project/pip/) ，请保证版本满足 [云湖官方Python SDK](https://github.com/yhchat/bot-python-sdk/) 、 [mcstatus](https://github.com/py-mine/mcstatus/) 与 [requests](https://github.com/psf/requests/) 的要求。

安装所需的依赖：

[云湖官方Python SDK](https://github.com/yhchat/bot-python-sdk/)

```bash
pip install yunhu
```

[mcstatus库](https://github.com/py-mine/mcstatus/)

```bash
pip install mcstatus
```

[requests库](https://github.com/psf/requests/)

```bash
pip install requests
```

### 获取云湖机器人Token

按照云湖官方文档等创建云湖机器人，并前往[控制台](https://www.yhchat.com/control/)获取机器人的Token

~~记住这个Token，后面要考~~

### 快速开始

建议为本程序单独建立一个文件夹，推荐使用不带空格的纯英文路径 ~~（如果不是也能用，但是可能麻烦点）~~ 。

下载所有源代码文件，并在其同目录下创建 `data.json`

填写 `data.json` 的内容，示例如下：

```json
{
  "YUNHU_TOKEN": "f0100860fa1145van14e11240d000721",
  "servers": [
    {
      "name": "My Server",
      "MC_SERVER_ADDRESS": "example.com:12345",
      "QUERY_SERVER_HOST": "example.com",
      "QUERY_SERVER_PORT": 54321
    }
  ],
  "boards": [
    {
      "chatId": "1234567",
      "chatType": "group",
      "track_player_changes": true,
      "max_player_records": 10
    },
    {
      "chatId": "7654321",
      "chatType": "user",
      "track_player_changes": false,
      "max_player_records": 5
    }
  ]
}
```

`YUNHU_TOKEN`的值应填写你在前面步骤中获得的Token，~~示例中的Token是我编的无效Token~~。

`servers`中的内容为你的Minecraft服务器信息。现阶段只**支持Java版服务器**，若需用于基岩版服务器可自行将代码中`from mcstatus import JavaServer`改为`from mcstatus import BedrockServer`并进行其它调整。

`MC_SERVER_ADDRESS`是你的服务器地址，需要填写端口。此处是你的服务器正常游玩时的地址。

若要使用当前在线玩家列表等功能，需要你的服务器开启Query功能（即`server.properties`配置文件中需要`enable-query=true`）

`QUERY_SERVER_HOST`和`QUERY_SERVER_PORT`需填写你的服务器的Query功能的地址与端口。Query端口通常在服务器的`server.properties`配置文件中`query.port=<端口号>`有设定。再次强调需要你的服务器开启了Query功能。另外，Query功能使用的是UDP而非TCP，请保证Query功能可用。

`boards`中的内容是你要同步的云湖群聊/用户看板相关信息，你可用填写多条。

`chatId`为群聊或用户的ID，即群号或云湖ID。

`chatType`可以填写`group`或`user`，分别代表此ID对应的是群聊/用户。

`track_player_changes`可以填写`true`或`false`，代表是否向该群聊/用户展示服务器在线成员变化。

`max_player_records`代表最多为该群聊/用户展示多少在线成员，以避免在线成员列表过长。虽然填写0并不代表无限制，但是你可用填写一个比服务器最大在线人数更大的值。注意不要填得太大了。

在完成了 `data.json` 的配置之后，就可用直接运行本程序了。本程序经测试可在Windows10/11上运行，暂未测试其它平台。你可用通过下面的指令运行：

```bash
python main.py
```

另外，你也可用通过创建一个bat来便捷地使用该程序。下面是内容：

```
@echo off
chcp 65001 >nul
cd /d "%~dp0%"
echo Starting Minecraft Status Bot...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Program exited abnormally. Please check:
    echo 1. Python is properly installed
    echo 2. mcstatus library is installed
    echo 3. yunhu library is installed
    echo 4. requests library is installed
    echo 5. All script files are present
    echo 6. Config filename is correct
    echo 7. Network connection is working
    echo ========================================
    echo.
)
pause
```

### 命令行参数

1.1.1版本新增了命令行参数支持，可以更灵活地控制日志输出：

不将日志输出到日志文件：

注意，程序仍会创建日志文件，但只写入"no-file-log"（不记录详细日志）

```bash
python main.py --no-file-log
```

不输出INFO级别日志（但是日志文件中仍会记录）

```bash
python main.py --log-no-info
```

不将INFO级别的日志记录至日志文件：

注意，控制台仍会输出INFO

```bash
python main.py --log-file-no-info
```

注意：以上参数不能同时使用，如果同时指定多个参数，程序将忽略所有参数并按默认设置运行。

## 致谢

### 开源库

- 云湖官方Python SDK：[bot-python-sdk](https://github.com/yhchat/bot-python-sdk/)
- Minecraft服务器状态获取：[mcstatus](https://github.com/py-mine/mcstatus/)
- HTTP请求处理：[requests](https://github.com/psf/requests/)

### 其它

- `README.md`参考了[MaaAssistantArknights](https://github.com/MaaAssistantArknights/MaaAssistantArknights/)
- `README.md`使用了[shields.io](https://shields.io/)、[contrib.rocks](https://contrib.rocks/)提供的内容

### 贡献/参与者

感谢所有参与到开发/测试中的朋友们(\*´▽｀)ノノ

~~好像只有我自己~~

[![Contributors](https://contrib.rocks/image?repo=Hollow-YK/Yunhu_MinecraftStatus_Bot&max=105&columns=15)](https://github.com/Hollow-YK/Yunhu_MinecraftStatus_Bot/graphs/contributors)

## 声明

- 本软件使用 [GNU Affero General Public License v3.0 only](https://spdx.org/licenses/AGPL-3.0-only.html) 开源。
- 本软件开源、免费，仅供学习交流使用。

## 广告

Minecraft服务端交流 云湖群：[Minecraft服务端交流（群ID: 739397733）](https://yhfx.jwznb.com/share?key=cqRdc9EcXOjZ&ts=1755597067)

如果觉得软件对你有帮助，帮忙点个 Star 吧！~（网页最上方右上角的小星星），这就是对我们最大的支持了！