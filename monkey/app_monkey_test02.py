# -*- coding : utf-8
# @Time: 2025-06-16

import subprocess
import time
import threading
import os

# Monkey 命令
cmd = [
    "adb", "shell", "monkey",
    "-p", "yl_meta.com.cybercharge",
    "--throttle", "300",
    "--ignore-crashes",
    "--ignore-timeouts",
    "--ignore-security-exceptions",
    "--monitor-native-crashes",
    "--kill-process-after-error",
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

# 路径设置
log_path = r"E:\monkey_log.txt"
logcat_path = r"E:\logcat_anr_fatal.txt"
tombstone_path = r"E:\tombstone_00"
tombstone_summary_path = r"E:\tombstone_summary.txt"


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
        encoding="utf-8",
        errors="ignore"
    )


def monitor_logcat(proc, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for line in proc.stdout:
            if "ANR" in line or "FATAL" in line or "Application Not Responding" in line:
                f.write(line)
                f.flush()


def extract_tombstone_summary(tombstone_path, output_path):
    keywords = [
        "signal", "Abort", "Abort message", "pid", "tid",
        "fault addr", "backtrace", "Build fingerprint", ">>>", "<<<"
    ]
    summary = []
    if os.path.exists(tombstone_path):
        with open(tombstone_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if any(k in line for k in keywords):
                    summary.append(line.strip())
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("【Tombstone 崩溃摘要】\n")
            out.write("\n".join(summary))
        print(f"Tombstone 摘要已生成：{output_path}")
    else:
        print("未找到 tombstone_00 文件，跳过摘要提取。")


# 启动 logcat
logcat_proc = start_logcat_listener()
logcat_thread = threading.Thread(target=monitor_logcat, args=(logcat_proc, logcat_path), daemon=True)
logcat_thread.start()

# 启动 monkey 测试
with open(log_path, "w", encoding="utf-8") as outfile:
    print("启动 Monkey 测试（30分钟）...")
    proc = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.STDOUT)
    try:
        time.sleep(1800)
        print("时间到，准备终止 monkey...")
        proc.terminate()
        stop_monkey_on_device()
    except KeyboardInterrupt:
        print("手动中断，正在清理 monkey 进程...")
        proc.terminate()
        stop_monkey_on_device()

# 停止 logcat
logcat_proc.terminate()
logcat_thread.join(timeout=5)

# 尝试提取 tombstone 摘要
subprocess.run(["adb", "pull", "/data/tombstones/tombstone_00", tombstone_path], shell=True)
extract_tombstone_summary(tombstone_path, tombstone_summary_path)

# 结果输出
print("✅ Monkey 测试完成。")
print(f"📄 Monkey 日志路径：{log_path}")
print(f"📄 异常关键字日志（ANR/FATAL）：{logcat_path}")
print(f"📄 Tombstone 摘要输出路径：{tombstone_summary_path}")
