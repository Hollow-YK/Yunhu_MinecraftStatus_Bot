import time
import argparse
from config import ConfigManager
from status import ServerStatusFetcher
from yunhu_manager import YunhuBoardManager
from player_tracker import PlayerTracker
from log_manager import LogManager

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Minecraft服务器状态监控程序')
    parser.add_argument('--log-with-board', action='store_true', 
                       help='输出日志时将每次要同步至yunhu的html一并输出至日志')
    parser.add_argument('--no-file-log', action='store_true', 
                       help='保存日志时创建日志文件，但日志文件仅内写入"no-file-log"')
    parser.add_argument('--log-no-info', action='store_true', 
                       help='输出日志时忽略INFO级别的日志')
    parser.add_argument('--log-file-no-info', action='store_true', 
                       help='保存日志时忽略INFO级别的日志，但仍输出至控制台')
    
    args = parser.parse_args()
    
    # 检查参数冲突
    arg_count = sum([args.log_with_board, args.no_file_log, args.log_no_info, args.log_file_no_info])
    if arg_count > 1:
        print("\033[0;33mWARN: 检测到多个参数同时使用，将忽略所有参数并按默认设置运行\033[0m")
        # 重置所有参数
        args = argparse.Namespace(
            log_with_board=False,
            no_file_log=False,
            log_no_info=False,
            log_file_no_info=False
        )
    
    return args

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    log_manager = LogManager(args)
    logger = log_manager.get_logger()
    
    # 记录启动信息和参数
    logger.info("启动 Minecraft 状态监控服务...")
    logger.info(f"命令行参数: log_with_board={args.log_with_board}, no_file_log={args.no_file_log}, "
                f"log_no_info={args.log_no_info}, log_file_no_info={args.log_file_no_info}")
    logger.info(f"日志文件: {log_manager.get_log_filepath()}")
    
    try:
        # 初始化各个组件
        config_manager = ConfigManager()
        config = config_manager.get_config()
        yunhu_manager = YunhuBoardManager(config["YUNHU_TOKEN"], args.log_with_board)
        player_tracker = PlayerTracker(config_manager)
        
        while True:
            for server_config in config["servers"]:
                logger.info(f"正在查询 {server_config['name']} 服务器状态...")
                
                # 获取服务器状态
                status_fetcher = ServerStatusFetcher(server_config)
                player_count, max_players, latency, version, player_list = status_fetcher.fetch_status()

                # 判断是否全部字段都为 None（即完全获取失败）
                if all(val is None for val in [player_count, max_players, latency, version]):
                    logger.warning("服务器状态全部获取失败，推送离线状态到云湖看板")
                    for board_config in config["boards"]:
                        yunhu_manager.sync_offline_status(board_config)
                else:
                    logger.info("部分或全部服务器状态已获取，同步状态到云湖看板")
                    
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
        logger.info("检测到键盘中断，正在退出程序...")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        logger.info("已安全退出。")

if __name__ == '__main__':
    main()