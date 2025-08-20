# -*- coding : utf-8
# @Time: 2025-06-24
import matplotlib

matplotlib.use('Agg')  # 非GUI后端，防止 FigureCanvas 报错
import matplotlib.pyplot as plt

# 设置中文字体为 SimHei（黑体），防止中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
# 避免负号 '-' 显示为方块
plt.rcParams['axes.unicode_minus'] = False
import pandas as pd

jtl_file = 'test_500.jtl'
df = pd.read_csv(jtl_file)

df_success = df[df['success'] == True].copy()

# 基础统计
total_requests = len(df)
success_requests = len(df_success)
success_rate = success_requests / total_requests * 100

print(f"总请求数: {total_requests}")
print(f"成功请求数: {success_requests}")
print(f"成功率: {success_rate:.2f}%")

elapsed = df_success['elapsed']
print(f"平均响应时间: {elapsed.mean():.2f} ms")
print(f"中位响应时间: {elapsed.median():.2f} ms")
print(f"最大响应时间: {elapsed.max()} ms")
print(f"最小响应时间: {elapsed.min()} ms")
print(f"95% 响应时间: {elapsed.quantile(0.95)} ms")

df_success['timeStamp'] = pd.to_datetime(df_success['timeStamp'], unit='ms')
df_success.set_index('timeStamp', inplace=True)

# 每秒吞吐量 TPS
tps = df_success['elapsed'].resample('1s').count()

plt.figure(figsize=(12, 6))
plt.plot(tps.index, tps.values, label='TPS')
plt.xlabel('时间')
plt.ylabel('每秒请求数 (TPS)')
plt.title('吞吐量曲线')
plt.legend()
plt.grid(True)
plt.savefig('tps.png')  # 保存图像文件
plt.close()

# 响应时间直方图
plt.figure(figsize=(12, 6))
plt.hist(elapsed, bins=50, color='skyblue')
plt.xlabel('响应时间 (ms)')
plt.ylabel('请求数')
plt.title('响应时间分布')
plt.grid(True)
plt.savefig('response_hist.png')
plt.close()
