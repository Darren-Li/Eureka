import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
from scipy import stats

warnings.filterwarnings('ignore')
os.makedirs('temp', exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('data/uploads\\ecommerce_data.csv')

date_cols = ['registration_date', 'order_date', 'last_purchase_date']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

df['discount_applied'] = df['discount_applied'].replace({'Yes': 1, 'No': 0}).astype(int)
df['return_status'] = df['return_status'].replace({'Yes': 1, 'No': 0}).astype(int)

num_cols = ['age', 'product_price', 'quantity', 'total_amount', 'shipping_time', 'customer_rating', 'purchase_frequency', 'avg_order_value']
outlier_log = {}
for col in num_cols:
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    outlier_log[col] = f'Clipped to [{lower:.2f}, {upper:.2f}]'
    df[col] = df[col].clip(lower, upper)

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data=df, x='total_amount', kde=True, ax=ax, palette='Set2')
ax.set_title('订单金额分布校验')
ax.set_xlabel('订单金额')
plt.tight_layout()
path1 = 'temp/task_4a34cefe6e7f_数据预处理与特征标准化.png'
fig.savefig(path1, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="数据预处理与特征标准化",
    topic="数据清洗与标准化",
    idea="日期转datetime，文本映射0/1，IQR处理异常值，分布校验",
    result={'date_types': {c: str(df[c].dtype) for c in date_cols}, 'outlier_handling': outlier_log},
    chart_json=[path1]
)

seg_stats = df.groupby('user_segment').agg(
    aov_mean=('avg_order_value', 'mean'),
    aov_median=('avg_order_value', 'median'),
    aov_std=('avg_order_value', 'std'),
    pf_mean=('purchase_frequency', 'mean'),
    pf_median=('purchase_frequency', 'median'),
    pf_std=('purchase_frequency', 'std')
).reset_index()

med_aov = df['avg_order_value'].median()
med_pf = df['purchase_frequency'].median()
df['value_quadrant'] = np.where(
    (df['avg_order_value'] >= med_aov) & (df['purchase_frequency'] >= med_pf), '高价值',
    np.where((df['avg_order_value'] >= med_aov) & (df['purchase_frequency'] < med_pf), '高消费低频',
    np.where((df['avg_order_value'] < med_aov) & (df['purchase_frequency'] >= med_pf), '低消费高频', '低价值')))

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df, x='purchase_frequency', y='avg_order_value', hue='user_segment', style='value_quadrant', ax=ax, palette='Set2', s=100)
ax.axhline(med_aov, color='gray', linestyle='--', label='客单价中位数')
ax.axvline(med_pf, color='gray', linestyle='--', label='频率中位数')
ax.set_title('用户价值分层散点图')
ax.set_xlabel('购买频率')
ax.set_ylabel('平均订单价值')
ax.legend()
plt.tight_layout()
path2 = 'temp/task_4a34cefe6e7f_用户分层价值评估.png'
fig.savefig(path2, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="用户分层价值评估",
    topic="用户价值矩阵构建",
    idea="基于客单价与购买频率中位数划分四象限，评估各分层特征",
    result=seg_stats.to_dict(orient='records'),
    chart_json=[path2]
)

pivot_sales = df.pivot_table(values='total_amount', index='product_category', columns='discount_applied', aggfunc='mean', fill_value=0)
pivot_return = df.pivot_table(values='return_status', index='product_category', columns='discount_applied', aggfunc='mean', fill_value=0)

fig, axes = plt.subplots(1, 2, figsize=(10, 6))
sns.heatmap(pivot_return, annot=True, fmt='.2%', cmap='viridis', ax=axes[0])
axes[0].set_title('退货率热力图')
axes[0].set_xlabel('折扣(0:否, 1:是)')
axes[0].set_ylabel('品类')

sns.barplot(data=df, x='product_category', y='total_amount', hue='discount_applied', ax=axes[1], palette='Set2')
axes[1].set_title('折扣对销售额影响')
axes[1].set_xlabel('品类')
axes[1].set_ylabel('平均销售额')
plt.tight_layout()
path3 = 'temp/task_4a34cefe6e7f_品类与折扣策略效能分析.png'
fig.savefig(path3, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="品类与折扣策略效能分析",
    topic="促销策略与退货风险",
    idea="交叉透视分析折扣对销售额与退货率的影响，热力图与柱状图对比",
    result={'sales_matrix': pivot_sales.to_dict(), 'return_matrix': pivot_return.to_dict()},
    chart_json=[path3]
)

group_stats = df.groupby(['membership_level', 'device_type'])['customer_rating'].agg(['mean', 'std', 'count']).reset_index()

groups_mem = [g['customer_rating'].values for _, g in df.groupby('membership_level')]
_, p_mem = stats.kruskal(*groups_mem)
groups_dev = [g['customer_rating'].values for _, g in df.groupby('device_type')]
_, p_dev = stats.kruskal(*groups_dev)

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='membership_level', y='customer_rating', hue='device_type', ax=ax, palette='Set2')
ax.set_title('会员等级与设备终端满意度分布')
ax.set_xlabel('会员等级')
ax.set_ylabel('客户评分')
plt.tight_layout()
path4 = 'temp/task_4a34cefe6e7f_会员设备与满意度关联分析.png'
fig.savefig(path4, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="会员设备与满意度关联分析",
    topic="体验与渠道关联洞察",
    idea="箱线图展示评分分布，Kruskal-Wallis检验组间差异显著性",
    result={'group_stats': group_stats.to_dict(orient='records'), 'p_values': {'membership_level': p_mem, 'device_type': p_dev}},
    chart_json=[path4]
)