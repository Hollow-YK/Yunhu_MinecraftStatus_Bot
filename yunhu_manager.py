import time
import json
import logging
from yunhu.openapi import Openapi

class YunhuBoardManager:
    def __init__(self, yunhu_token, log_with_board=False):
        self.openapi = Openapi(yunhu_token)
        self.log_with_board = log_with_board
        self.logger = logging.getLogger("MinecraftMonitor")
    
    def sync_status(self, player_count, max_players, latency, version, server_address, 
                   player_list=None, board_config=None, player_changes=None):
        """
        将Minecraft服务器状态同步到云湖看板。
        """
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 处理缺失字段
        if player_count is None:
            player_count = "<span style='color:red;'>加载失败</span>"
        if max_players is None:
            max_players = "<span style='color:red;'>加载失败</span>"
        if latency is None:
            latency = "<span style='color:red;'>加载失败</span>"
            delay_color = "red"
        else:
            from utils import get_delay_color
            delay_color = get_delay_color(latency)
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
        <p>服务器地址：<code>{server_address}</code></p>
        <hr>
        <h2>在线玩家列表</h2>
        {player_html}
        {player_change_html}
        """
        
        # 如果启用了HTML日志输出，记录HTML内容
        if self.log_with_board:
            self.logger.debug(f"同步到云湖看板的HTML内容:\n{content}")
        
        expire_time = int(time.time()) + 60
        
        try:
            res = self.openapi.SetBotBoard(board_config["chatId"], board_config["chatType"], "", "html", content, expire_time)
            response_json = res.json()
            if response_json.get('code') == 1:
                self.logger.info("成功推送服务器状态到云湖看板")
                return True
            else:
                self.logger.error(f"推送失败: {response_json.get('message', '未知错误')}")
                return False
        except json.JSONDecodeError:
            self.logger.error("无法解析云湖API返回的JSON格式")
            return False
        except AttributeError:
            self.logger.error("响应对象缺少 'json' 方法")
            return False
        except Exception as e:
            self.logger.error(f"发生异常: {e}")
            return False
    
    def sync_offline_status(self, board_config):
        """
        向云湖看板推送服务器离线状态。
        """
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        content = f"""
        <h1>服务器好像没有开启</h1>
        <small><p>状态更新时间：{current_time}</p></small>
        <p>服务器状态获取失败。</p>
        """
        
        # 如果启用了HTML日志输出，记录HTML内容
        if self.log_with_board:
            self.logger.debug(f"同步到云湖看板的HTML内容:\n{content}")
        
        expire_time = int(time.time()) + 60
        
        try:
            res = self.openapi.SetBotBoard(board_config["chatId"], board_config["chatType"], "", "html", content, expire_time)
            response_json = res.json()
            if response_json.get('code') == 1:
                self.logger.info("成功推送服务器离线状态到云湖看板")
                return True
            else:
                self.logger.error(f"推送离线状态失败: {response_json.get('message', '未知错误')}")
                return False
        except json.JSONDecodeError:
            self.logger.error("无法解析云湖API返回的JSON格式")
            return False
        except AttributeError:
            self.logger.error("响应对象缺少 'json' 方法")
            return False
        except Exception as e:
            self.logger.error(f"发生异常: {e}")
            return False