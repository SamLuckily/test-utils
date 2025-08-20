# -*- coding : utf-8
# @Time: 2025-04-05
import json
import csv
import time
from selenium import webdriver
import os


def analyze_performance(timing):
    """
    h5页面性能指标测试
    :param timing:
    :return:
    """
    nav_start = timing["navigationStart"]
    return {
        "dns_time": timing["domainLookupEnd"] - timing["domainLookupStart"],
        "tcp_time": timing["connectEnd"] - timing["connectStart"],
        "ssl_time": timing["connectEnd"] - timing["secureConnectionStart"],
        "request_time": timing["responseEnd"] - timing["requestStart"],
        "white_screen_time": timing["responseStart"] - nav_start,
        "dom_build_time": timing["domInteractive"] - timing["domLoading"],
        "dom_ready_time": timing["domInteractive"] - nav_start,
        "first_screen_time": timing["domContentLoadedEventEnd"] - nav_start,
        "dcl_event_duration": timing["domContentLoadedEventEnd"] - timing["domContentLoadedEventStart"],
        "total_page_load_time": timing["loadEventEnd"] - nav_start,
        "after_dcl_load_time": timing["loadEventEnd"] - timing["domContentLoadedEventEnd"]
    }


class TestPerformance:
    def test_page_performance(self):
        url = "https://invite.cybercharge.cc/bindingInviter?channelId=2&safeTop=40.0&token=eyJ0eXAiOiJqd3QifQ.eyJzdWIiOiIxIiwiaXNzIjoiaHR0cDpcL1wvOiIsImV4cCI6MTc0NjA5MDA3MiwiaWF0IjoxNzQ0ODgwNDcyLCJuYmYiOjE3NDQ4ODA0NzIsInVpZCI6MTAxMTE4LCJzIjoiTEJoQXU2IiwianRpIjoiMTdlNzIzZWYxZjM5YjVmZWY4Zjg1ODhmM2U2MDVjMTMifQ.ODJmYjY4ZmE0NjMyNTEyY2YxYTEwNGZkNDM0ZDhkOGM0YWEyZGYwNg&language=zh-Hant&platform=android&build_type=preTest"
        # url = "https://appassets.androidplatform.net/html/index.html?StatusBarHeight=120&NavigationBarHeight=48&language=zh-Hant&build_type=release&token=eyJ0eXAiOiJqd3QifQ.eyJzdWIiOiIxIiwiaXNzIjoiaHR0cDpcL1wvOiIsImV4cCI6MTc0OTA5NDI3NCwiaWF0IjoxNzQ3ODg0Njc0LCJuYmYiOjE3NDc4ODQ2NzQsInVpZCI6MjU4NTM4LCJzIjoid0J3Nmo4IiwianRpIjoiZWY3NDI5OThiZTBjZWQyY2FiZjY1NmNjMDkyMThmZjEifQ.MTA1YzZlMDczMzUwMjZkZDI0NjM4OTI1YTc1NDhlN2JjYzZhYjA0Mw&code="
        csv_file = "E:\元链APP\YL-APP\CyberCharge-Stress-Test\h5_perf_test\h5_perf_metrics.csv"

        driver = webdriver.Chrome()
        driver.get(url)

        # 等页面加载完成后获取性能数据
        timing_json = driver.execute_script("return JSON.stringify(window.performance.timing)")
        timing = json.loads(timing_json)
        driver.quit()

        # 分析性能指标
        metrics = analyze_performance(timing)
        metrics["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        metrics["url"] = url

        # 添加中文描述
        metrics_with_cn = {
            "时间戳": metrics["timestamp"],
            "网址": metrics["url"],
            "DNS解析时间": metrics["dns_time"],
            "TCP连接时间": metrics["tcp_time"],
            "SSL连接时间": metrics["ssl_time"],
            "请求时间": metrics["request_time"],
            "白屏时间": metrics["white_screen_time"],
            "DOM构建时间": metrics["dom_build_time"],
            "DOM就绪时间": metrics["dom_ready_time"],
            "首屏渲染时间": metrics["first_screen_time"],
            "DCL事件时长": metrics["dcl_event_duration"],
            "总加载时间": metrics["total_page_load_time"],
            "DCL后加载时间": metrics["after_dcl_load_time"]
        }

        # 打印出带有中文描述的性能数据
        print("📦 收集到的性能数据：", metrics_with_cn)

        # 保存结果到 CSV
        self.write_to_csv(metrics_with_cn, csv_file)

    def write_to_csv(self, data, file_path):
        # 检查文件是否存在，如果存在则以追加模式打开，不删除文件
        file_exists = os.path.exists(file_path)

        # 写入 CSV 文件并加上 BOM，确保 Excel 识别中文字符
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["时间戳", "网址", "DNS解析时间", "TCP连接时间", "SSL连接时间", "请求时间", "白屏时间",
                          "DOM构建时间", "DOM就绪时间", "首屏渲染时间", "DCL事件时长", "总加载时间", "DCL后加载时间"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # 如果文件不存在则写入表头
            if not file_exists:
                writer.writeheader()

            writer.writerow(data)


# ✅ 运行示例
if __name__ == "__main__":
    tester = TestPerformance()
    tester.test_page_performance()
