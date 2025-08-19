import time
from mcstatus import JavaServer  # 导入mcstatus库来查询Minecraft服务器的状态
from yunhu.openapi import Openapi  # 导入云湖官方PythonSDK的Openapi库来调用云湖API
import logging  # 导入logging库来进行日志记录
import json  # 导入json库来处理JSON数据
import os

# 打印当前工作目录
print(f"Current working directory: {os.getcwd()}")

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'data.json')
temp_file_path = os.path.join(script_dir, 'player_temp.json')

# 读取配置文件，使用UTF-8编码
with open(config_path, 'r', encoding='utf-8') as config_file:
    CONFIG = json.load(config_file)

# 初始化Openapi客户端
openapi = Openapi(CONFIG["YUNHU_TOKEN"])

def fetch_mc_server_status(server_config):
    """
    获取Minecraft服务器的基本状态和玩家列表。
    :param server_config: 包含服务器配置的字典
    :return: 返回元组 (player_count, max_players, latency, version, player_list)
             如果无法获取某些信息，则对应值为None。
    """
    try:
        server = JavaServer.lookup(server_config["MC_SERVER_ADDRESS"])
        
        # 获取基础状态信息
        status = server.status()
        player_count = status.players.online  # 当前在线玩家数
        max_players = status.players.max  # 最大玩家数
        latency = status.latency  # 延迟时间
        version = status.version.name  # 服务器版本

        # 使用自定义地址获取玩家列表
        try:
            query_server = JavaServer(server_config["QUERY_SERVER_HOST"], server_config["QUERY_SERVER_PORT"])
            query = query_server.query()  # 查询玩家列表
            player_list = query.players.names  # 玩家名字列表
        except Exception as e:
            logging.warning(f"无法获取玩家列表: {e}")  # 记录警告信息
            player_list = None  # 设置为空
        
        logging.info(f"Fetched server status: {player_count}/{max_players} players online, latency {latency} ms")  # 记录基本信息
        return player_count, max_players, latency, version, player_list
    except Exception as e:
        logging.error(f"Failed to fetch server status: {e}")  # 记录错误信息
        return None, None, None, None, None

def sync_to_yunhu_board(player_count, max_players, latency, version, player_list=None, board_config=None, player_changes=None):
    """
    将Minecraft服务器状态同步到云湖看板。
    :param player_count: 当前在线玩家数
    :param max_players: 最大玩家数
    :param latency: 延迟时间
    :param version: 服务器版本
    :param player_list: 在线玩家名单，默认为None
    :param board_config: 包含看板配置的字典
    :param player_changes: 玩家进出记录，默认为None
    """
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 获取当前时间

    # 处理缺失字段
    if player_count is None:
        player_count = "<span style='color:red;'>加载失败</span>"
    if max_players is None:
        max_players = "<span style='color:red;'>加载失败</span>"
    if latency is None:
        latency = "<span style='color:red;'>加载失败</span>"
        delay_color = "red"
    else:
        delay_color = get_delay_color(latency)  # 根据延迟确定颜色
    if version is None:
        version = "<span style='color:red;'>加载失败</span>"

    # 构造玩家列表HTML部分
    if player_list is not None and len(player_list) > 0:
        player_html = "<ul>" + "".join([f"<li>{name}</li>" for name in player_list]) + "</ul>"
    elif player_list is not None and len(player_list) == 0:
        player_html = "<p>当前没有玩家在线</p>"
    else:
        player_html = "<p>玩家列表加载失败（需服务器开启 enable-query）</p>"

    # 构造玩家进出记录HTML部分
    player_change_html = ""
    if player_changes is not None:
        player_change_html += "<h2>最近玩家进出记录</h2><ul>"
        for change in player_changes[:board_config.get("max_player_records", 10)]:
            action = "加入" if change["action"] == "join" else "离开"
            player_change_html += f"<li>{change['player']} 于 {change['time']} {action}</li>"
        player_change_html += "</ul>"

    content = f"""
    <h1>服务器实时状态</h1>
    <small><p>状态更新时间：{current_time}</p></small>
    <p>服务器当前人数/最大人数: {player_count}/{max_players}</p>
    <p>服务器延迟: <span style="color: {delay_color};">{latency:.2f} ms</span></p>
    <hr>
    <h1>服务器信息</h1>
    <p>服务器版本：<code>{version}</code></p>
    <p>服务器地址：<code>{CONFIG['servers'][0]['MC_SERVER_ADDRESS']}</code></p>
    <hr>
    <h2>在线玩家列表</h2>
    {player_html}
    {player_change_html}
    """
    
    expire_time = int(time.time()) + 60  # 设置过期时间为1分钟后
    
    try:
        res = openapi.SetBotBoard(board_config["chatId"], board_config["chatType"], "", "html", content, expire_time)  # 调用云湖API设置指定群看板
        response_json = res.json()  # 将Response对象转换为JSON格式
        if response_json.get('code') == 1:
            logging.info("成功推送服务器状态到云湖看板")
        else:
            logging.error(f"推送失败: {response_json.get('message', '未知错误')}")
    except json.JSONDecodeError:
        logging.error("无法解析云湖API返回的JSON格式")
    except AttributeError:
        logging.error("响应对象缺少 'json' 方法")
    except Exception as e:
        logging.error(f"发生异常: {e}")

def sync_to_yunhu_board_offline(board_config=None):
    """
    向云湖看板推送服务器离线状态。
    :param board_config: 包含看板配置的字典
    """
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    content = f"""
    <h1>服务器好像没有开启</h1>
    <small><p>状态更新时间：{current_time}</p></small>
    <p>服务器状态获取失败。</p>
    """
    
    expire_time = int(time.time()) + 60  # 设置过期时间为1分钟后
    
    try:
        res = openapi.SetBotBoard(board_config["chatId"], board_config["chatType"], "", "html", content, expire_time)
        response_json = res.json()
        if response_json.get('code') == 1:
            logging.info("成功推送服务器离线状态到云湖看板")
        else:
            logging.error(f"推送离线状态失败: {response_json.get('message', '未知错误')}")
    except json.JSONDecodeError:
        logging.error("无法解析云湖API返回的JSON格式")
    except AttributeError:
        logging.error("响应对象缺少 'json' 方法")
    except Exception as e:
        logging.error(f"发生异常: {e}")

def get_delay_color(latency):
    """
    根据延迟时间返回对应的HTML颜色。
    :param latency: 延迟时间（毫秒）
    :return: HTML颜色字符串
    """
    if latency < 100:
        return "green"
    elif latency < 200:
        return "yellow"
    else:
        return "red"

def load_previous_players(server_name):
    """
    加载之前保存的玩家列表。
    :param server_name: 服务器名称
    :return: 上次保存的玩家列表
    """
    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            previous_players = json.load(temp_file).get(server_name, [])
    else:
        previous_players = []
    return previous_players

def save_current_players(server_name, player_list):
    """
    保存当前的玩家列表。
    :param server_name: 服务器名称
    :param player_list: 当前玩家列表
    """
    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
            data = json.load(temp_file)
    else:
        data = {}

    data[server_name] = player_list
    with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        json.dump(data, temp_file, ensure_ascii=False, indent=4)

def track_player_changes(previous_players, current_players):
    """
    比较前后两次玩家列表，记录玩家的进出情况。
    :param previous_players: 上次保存的玩家列表
    :param current_players: 当前玩家列表
    :return: 玩家进出记录列表
    """
    changes = []

    # 找出新加入的玩家
    joined_players = set(current_players) - set(previous_players)
    for player in joined_players:
        changes.append({"player": player, "action": "join", "time": time.strftime("%Y-%m-%d %H:%M", time.localtime())})

    # 找出离开的玩家
    left_players = set(previous_players) - set(current_players)
    for player in left_players:
        changes.append({"player": player, "action": "leave", "time": time.strftime("%Y-%m-%d %H:%M", time.localtime())})

    return changes

if __name__ == '__main__':
    # 配置日志记录：输出到控制台
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("启动 Minecraft 状态监控服务...")

    try:
        while True:
            for server_config in CONFIG["servers"]:
                logging.info(f"正在查询 {server_config['name']} 服务器状态...")
                player_count, max_players, latency, version, player_list = fetch_mc_server_status(server_config)

                # 判断是否全部字段都为 None（即完全获取失败）
                if all(val is None for val in [player_count, max_players, latency, version]):
                    logging.warning("服务器状态全部获取失败，推送离线状态到云湖看板")
                    for board_config in CONFIG["boards"]:
                        sync_to_yunhu_board_offline(board_config=board_config)
                else:
                    logging.info("部分或全部服务器状态已获取，同步状态到云湖看板")
                    previous_players = load_previous_players(server_config["name"])
                    player_changes = []

                    for board_config in CONFIG["boards"]:
                        if board_config.get("track_player_changes", False):
                            player_changes = track_player_changes(previous_players, player_list or [])
                            sync_to_yunhu_board(player_count, max_players, latency, version, player_list, board_config=board_config, player_changes=player_changes)
                        else:
                            sync_to_yunhu_board(player_count, max_players, latency, version, player_list, board_config=board_config)

                    save_current_players(server_config["name"], player_list or [])

            time.sleep(15)  # 每15s更新一次
    except KeyboardInterrupt:
        logging.info("检测到键盘中断，正在退出程序...")
        logging.info("已安全退出。")
