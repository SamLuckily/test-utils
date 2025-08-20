# -*- coding: utf-8 -*-
# @Time: 2025-06-16
import subprocess
import time

# Monkey 命令
cmd = [
    "adb", "shell", "monkey",
    "-p", "yl_meta.com.cybercharge",  # 目标 App 包名
    "--throttle", "300",  # 每次事件间隔 300ms
    "--ignore-crashes",
    "--ignore-timeouts",
    "--ignore-security-exceptions",
    "--monitor-native-crashes",
    "--kill-process-after-error",  # 若异常发生，终止 Monkey
    "--bugreport",

    "--pct-touch", "50",
    "--pct-motion", "10",
    "--pct-nav", "10",
    "--pct-majornav", "5",
    "--pct-appswitch", "10",
    "--pct-anyevent", "10",
    "--pct-syskeys", "0",
    "--pct-flip", "5",

    "-s", "12345",
    "-v", "-v", "-v",
    "10000000"
]

log_path = r"E:\monkey_log.txt"
logcat_path = r"E:\logcat_anr_fatal.txt"


def stop_monkey_on_device():
    print("正在尝试终止设备上的 monkey 进程...")
    try:
        subprocess.run(["adb", "shell", "pkill", "-f", "com.android.commands.monkey"], check=True)
        print("设备 monkey 进程已终止。")
    except subprocess.CalledProcessError:
        print("未找到正在运行的 monkey 进程或已停止。")


def start_logcat_listener():
    print("启动 logcat 监听（ANR / FATAL）...")
    return subprocess.Popen(
        ["adb", "logcat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",  # ✅ 强制使用 utf-8 解码
        errors="ignore"  # ✅ 忽略非法字符（防止崩溃）
    )


def monitor_logcat(proc, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in proc.stdout:
            if "ANR" in line or "FATAL" in line or "Application Not Responding" in line:
                f.write(line)
                f.flush()


# 启动 logcat 监听进程（后台线程）
logcat_proc = start_logcat_listener()
import threading

logcat_thread = threading.Thread(target=monitor_logcat, args=(logcat_proc, logcat_path), daemon=True)
logcat_thread.start()

# 启动 monkey 测试
with open(log_path, "w", encoding="utf-8") as outfile:
    print("启动 Monkey 测试（30分钟）...")
    proc = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    try:
        time.sleep(1800)  # 等待 30 分钟
        print("时间到，准备终止 monkey...")
        proc.terminate()
        stop_monkey_on_device()
    except KeyboardInterrupt:
        print("手动中断，正在清理 monkey 进程...")
        proc.terminate()
        stop_monkey_on_device()

# 结束 logcat
logcat_proc.terminate()
logcat_thread.join(timeout=5)

print("Monkey 测试完成。")
print(f"Monkey 日志路径：{log_path}")
print(f"异常关键字日志（ANR/FATAL）：{logcat_path}")
