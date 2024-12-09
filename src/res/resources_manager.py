import os
import json
import shutil

# 资源文件路径
RESOURCE_FILE = os.path.join(os.environ["LOCALAPPDATA"], "Adex", "resources.json")
CURRENT_RESOURCE_FILE = os.path.join(os.getcwd(), "src\\res\\resources.json")

# 默认资源
DEFAULT_RESOURCES = {
    "notepad": ("notepad.exe", "file"),
    "calculator": ("calc.exe", "file"),
    "documents": (os.path.expanduser("~/Documents"), "file"),
    "downloads": (os.path.expanduser("~/Downloads"), "file"),
    "google": ("https://www.google.com", "url"),
    "github": ("https://www.github.com", "url")
}

def load_and_process_resources():
    """加载并处理资源文件"""
    if not os.path.exists(RESOURCE_FILE):
        sync_resources()
    if not os.path.exists(RESOURCE_FILE):
        print(f"资源文件不存在: {RESOURCE_FILE}")
        return DEFAULT_RESOURCES  # 如果没有资源文件，则返回默认资源

    with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
        raw_resources = json.load(f)

    # 处理资源格式
    # return process_resources(raw_resources)
    return raw_resources

def process_resources(raw_resources):
    """处理资源格式，转换成标准格式"""
    processed_resources = {}
    for name, data in raw_resources.items():
        path = data.get("path")
        res_type = data.get("type")

        if path and res_type:
            if res_type == "file" and not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)  # 如果路径是相对路径则转换为绝对路径
            processed_resources[name] = (path, res_type)
    return processed_resources

def save_resources(resources):
    """保存资源到文件"""
    with open(RESOURCE_FILE, "w") as f:
        json.dump(resources, f, indent=4)

def sync_resources():
    """同步资源配置文件"""
    if os.path.exists(CURRENT_RESOURCE_FILE):
        os.makedirs(os.path.dirname(RESOURCE_FILE), exist_ok=True)
        shutil.copy(CURRENT_RESOURCE_FILE, RESOURCE_FILE)
        print(f"资源文件已从 {CURRENT_RESOURCE_FILE} 同步到 {RESOURCE_FILE}")
    else:
        print(f"没有找到当前目录下的 resource.json: {CURRENT_RESOURCE_FILE}")
