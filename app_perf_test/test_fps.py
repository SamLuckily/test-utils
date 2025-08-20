# -*- coding : utf-8
# @Time: 2025-04-20
import time
import subprocess  # 用于执行 ADB 命令（调用安卓设备上的系统命令）


class PerfHandle:
    """
    APP页面流畅度测试
    """

    @staticmethod  # 静态方法，无需实例化即可调用
    def cmd_start(cmd):
        """
        通用执行 ADB 命令的方法
        :param cmd:
        :return:
        """
        result = subprocess.check_output(cmd, shell=True)  # 用 subprocess.check_output() 执行传入的 ADB 命令
        return result.splitlines()  # 返回按行切分后的结果列表（每行是字节类型）

    def get_fps(self, package_name="yl_meta.com.cybercharge"):
        """
        获取 App 的当前总帧数（用来估算 FPS）
        :param package_name:
        :return:
        """
        try:
            cmd = f"adb shell dumpsys gfxinfo {package_name}"  # 每秒获取一次帧数（从 dumpsys gfxinfo 中解析），估算当前帧率，并输出当前 App 页面名称和 FPS 值
            results = self.cmd_start(cmd)
            for line in results:  # 执行命令后解析每一行
                decoded = line.decode('utf-8').strip()
                if decoded.startswith("Total frames rendered:"):  # 找到 Total frames rendered: 开头的那一行
                    total_frames = int(decoded.split(":")[-1].strip())
                    return total_frames  # 提取并返回后面的数字
            return 0  # 没找到就返回 0
        except Exception as e:
            print(f"获取FPS失败: {e}")
            return 0

    def get_current_activity(self):
        """
        获取当前 App 正在展示的页面（Activity）
        :return:
        """
        try:
            cmd = 'adb shell "dumpsys window | grep mCurrentFocus"'  # 用 dumpsys window 获取窗口状态
            results = self.cmd_start(cmd)  # 从 mCurrentFocus 一行中提取当前 Activity 名称
            line = results[0].decode("utf-8")
            activity = line.split("u0 ")[-1].split("}")[0]
            return activity  # 返回值形如：包名/Activity类路径
        except Exception as e:
            print(f"获取当前页面失败: {e}")
            return "Unknown"


def test_fps_monitor():
    """
    用于监控帧率并打印结果
    :return:
    """
    perf_handle = PerfHandle()
    fps_a = perf_handle.get_fps()
    time_a = time.time()

    for _ in range(5):  # 进入5次采用循环
        time.sleep(1)  # 每次睡 1 秒，用于采样“每秒的帧率”
        fps_b = perf_handle.get_fps()  # 获取最新帧数
        time_b = time.time()  # 获取当前时间
        activity = perf_handle.get_current_activity()  # 获取当前页面的 Activity 名称
        frame_diff = fps_b - fps_a  # 帧差
        time_diff = time_b - time_a if (time_b - time_a) != 0 else 1  # 时间差
        fps_estimate = int(frame_diff / time_diff)  # 帧差 ÷ 时间差 = FPS，防止除以 0
        # 打印当前时间、页面名、FPS 估算值，格式化时间字符串用于可读性
        print(f"[{time.strftime('%H:%M:%S')}] Activity: {activity} | FPS: {fps_estimate}")
        # 更新上一轮帧数和时间；保存当前这轮的帧数和时间，用于下一轮对比
        fps_a = fps_b
        time_a = time_b

    assert fps_estimate >= 0

