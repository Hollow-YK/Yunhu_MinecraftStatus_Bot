import time

class PlayerTracker:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def track_changes(self, server_name, current_players):
        """
        比较前后两次玩家列表，记录玩家的进出情况。
        :return: 玩家进出记录列表
        """
        previous_players = self.config_manager.load_previous_players(server_name)
        changes = []

        # 找出新加入的玩家
        joined_players = set(current_players or []) - set(previous_players)
        for player in joined_players:
            changes.append({"player": player, "action": "join", "time": time.strftime("%Y-%m-%d %H:%M", time.localtime())})

        # 找出离开的玩家
        left_players = set(previous_players) - set(current_players or [])
        for player in left_players:
            changes.append({"player": player, "action": "leave", "time": time.strftime("%Y-%m-%d %H:%M", time.localtime())})

        # 保存当前玩家列表
        self.config_manager.save_current_players(server_name, current_players or [])
        
        return changes