import json
import os

class ConfigManager:
    def __init__(self, config_path='data.json'):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, config_path)
        self.temp_file_path = os.path.join(self.script_dir, 'player_temp.json')
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        
        with open(self.config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    
    def get_config(self):
        """获取配置"""
        return self.config
    
    def load_previous_players(self, server_name):
        """加载之前保存的玩家列表"""
        if os.path.exists(self.temp_file_path):
            with open(self.temp_file_path, 'r', encoding='utf-8') as temp_file:
                previous_players = json.load(temp_file).get(server_name, [])
        else:
            previous_players = []
        return previous_players
    
    def save_current_players(self, server_name, player_list):
        """保存当前的玩家列表"""
        if os.path.exists(self.temp_file_path):
            with open(self.temp_file_path, 'r', encoding='utf-8') as temp_file:
                data = json.load(temp_file)
        else:
            data = {}

        data[server_name] = player_list
        with open(self.temp_file_path, 'w', encoding='utf-8') as temp_file:
            json.dump(data, temp_file, ensure_ascii=False, indent=4)