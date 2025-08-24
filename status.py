from mcstatus import JavaServer
import logging

class ServerStatusFetcher:
    def __init__(self, server_config):
        self.server_config = server_config
        self.logger = logging.getLogger("MinecraftMonitor")
    
    def fetch_status(self):
        """
        获取Minecraft服务器的基本状态和玩家列表。
        :return: 返回元组 (player_count, max_players, latency, version, player_list)
                 如果无法获取某些信息，则对应值为None。
        """
        try:
            server = JavaServer.lookup(self.server_config["MC_SERVER_ADDRESS"])
            
            # 获取基础状态信息
            status = server.status()
            player_count = status.players.online  # 当前在线玩家数
            max_players = status.players.max  # 最大玩家数
            latency = status.latency  # 延迟时间
            version = status.version.name  # 服务器版本

            # 使用自定义地址获取玩家列表
            try:
                query_server = JavaServer(self.server_config["QUERY_SERVER_HOST"], self.server_config["QUERY_SERVER_PORT"])
                query = query_server.query()  # 查询玩家列表
                player_list = query.players.names  # 玩家名字列表
            except Exception as e:
                self.logger.warning(f"无法获取玩家列表: {e}")  # 记录警告信息
                player_list = None  # 设置为空
            
            self.logger.info(f"Fetched server status: {player_count}/{max_players} players online, latency {latency} ms")
            return player_count, max_players, latency, version, player_list
        except Exception as e:
            self.logger.error(f"Failed to fetch server status: {e}")
            return None, None, None, None, None