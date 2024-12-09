import os
import json

CONFIG_FILE = os.path.join(os.environ["LOCALAPPDATA"], "Adex", "config.json")

class Config:
    @staticmethod
    def load_config():
        """加载配置"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_config(config):
        """保存配置"""
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
