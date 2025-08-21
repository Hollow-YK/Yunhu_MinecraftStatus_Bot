import time
import logging
from config import ConfigManager
from status import ServerStatusFetcher
from yunhu_manager import YunhuBoardManager
from player_tracker import PlayerTracker

def setup_logging():
    """配置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """主函数"""
    setup_logging()
    logging.info("启动 Minecraft 状态监控服务...")
    
    try:
        # 初始化各个组件
        config_manager = ConfigManager()
        config = config_manager.get_config()
        yunhu_manager = YunhuBoardManager(config["YUNHU_TOKEN"])
        player_tracker = PlayerTracker(config_manager)
        
        while True:
            for server_config in config["servers"]:
                logging.info(f"正在查询 {server_config['name']} 服务器状态...")
                
                # 获取服务器状态
                status_fetcher = ServerStatusFetcher(server_config)
                player_count, max_players, latency, version, player_list = status_fetcher.fetch_status()

                # 判断是否全部字段都为 None（即完全获取失败）
                if all(val is None for val in [player_count, max_players, latency, version]):
                    logging.warning("服务器状态全部获取失败，推送离线状态到云湖看板")
                    for board_config in config["boards"]:
                        yunhu_manager.sync_offline_status(board_config)
                else:
                    logging.info("部分或全部服务器状态已获取，同步状态到云湖看板")
                    
                    for board_config in config["boards"]:
                        if board_config.get("track_player_changes", False):
                            player_changes = player_tracker.track_changes(server_config["name"], player_list)
                            yunhu_manager.sync_status(
                                player_count, max_players, latency, version, 
                                server_config["MC_SERVER_ADDRESS"], player_list, 
                                board_config, player_changes
                            )
                        else:
                            yunhu_manager.sync_status(
                                player_count, max_players, latency, version, 
                                server_config["MC_SERVER_ADDRESS"], player_list, 
                                board_config
                            )

            time.sleep(15)  # 每15s更新一次
            
    except KeyboardInterrupt:
        logging.info("检测到键盘中断，正在退出程序...")
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
    finally:
        logging.info("已安全退出。")

if __name__ == '__main__':
    main()