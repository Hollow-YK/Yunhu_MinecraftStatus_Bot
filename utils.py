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