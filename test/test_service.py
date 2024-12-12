data = {
    "2024年加班申请.xlsx": {
        "path": "https://onebox.huawei.com/v/2809b3987797ef63749bbbf7966297b4?type=1&sheet=%E6%9C%AA%E6%8A%A5%E5%8A%A0%E7%8F%AD&time=1724935202172",
        "type": "url"
    },
    "2024休假表.xlsx": {
        "path": "https://onebox.huawei.com/v/83100b1192ededdb652cd02bf94abb51?type=1",
        "type": "url"
    },
    "休假管理": {
        "path": "https://www.starling.huawei.com/web/microAppCenter/#/app/sheet/7fb08fc8d8354da953284b79509aeb8d/undefined/180eb117aa0fd5d19a6e51ef1acaef64/undefined?tenantId=WeGo_ACN_EU&appName=%E4%BC%91%E5%81%87%E7%AE%A1%E7%90%86&worksheetName=%E4%BC%91%E5%81%87%E7%94%B3%E8%AF%B7&status=running&visitRandom=v24",
        "type": "url"
    }
}

def get_nth_element(data, n):
    """获取字典中第 n 个元素"""
    items = list(data.items())  # 转换为按插入顺序排列的列表
    if n < 0 or n >= len(items):  # 检查 n 是否在有效范围
        raise IndexError("索引超出范围")
    key, value = items[n]  # 获取第 n 个键值对
    return key, value

# 示例：获取第 2 个元素（索引从 0 开始）
n = 2
key, value = get_nth_element(data, n)
print(f"第 {n+1} 个元素的 Key: {key}")
print(f"第 {n+1} 个元素的 Value: {value}")
