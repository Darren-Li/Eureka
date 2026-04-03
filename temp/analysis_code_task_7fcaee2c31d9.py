import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import os

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv(r'data/uploads\MMM demo data.csv')
df['date_key'] = pd.to_datetime(df['date_key'])
df['year'] = df['date_key'].dt.year

spend_cols = [c for c in df.columns if 'spend' in c]
ctrl_cols = [c for c in df.columns if c.startswith('ctrl_')]
df.loc[:, spend_cols] = df[spend_cols].fillna(0)
df.loc[:, ctrl_cols] = df[ctrl_cols].ffill().fillna(0)

os.makedirs('temp', exist_ok=True)

# 步骤1
missing_info = df.isnull().sum().to_dict()
save_analysis_step(
    step_name="数据预处理与基础清洗",
    topic="数据清洗",
    idea="转换日期格式提取年份，营销花费缺失值填0表示未投放，控制变量前向填充后补0",
    result={"缺失值统计": missing_info, "数据形状": df.shape, "处理字段": spend_cols + ctrl_cols},
    chart_json=[]
)

# 步骤2
annual = df.groupby('year').agg({
    'omni_consumption': 'sum',
    **{c: 'sum' for c in spend_cols},
    **{c: 'mean' for c in ctrl_cols}
}).reset_index()
annual['sales_yoy'] = annual['omni_consumption'].pct_change()

ec_c = [c for c in spend_cols if c.startswith('ec_')]
atl_c = [c for c in spend_cols if c.startswith('atl_')]
tmkt_c = [c for c in spend_cols if c.startswith('tmkt_')]
annual['ec_sum'] = annual[ec_c].sum(axis=1)
annual['atl_sum'] = annual[atl_c].sum(axis=1)
annual['tmkt_sum'] = annual[tmkt_c].sum(axis=1)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
sns.lineplot(x='year', y='omni_consumption', data=annual, marker='o', ax=axes[0], color='b')
axes[0].set_title('年度销售额趋势')
axes[0].set_ylabel('销售额')

sns.barplot(x='year', y='ec_sum', data=annual, ax=axes[1], color='g', label='EC')
sns.barplot(x='year', y='atl_sum', data=annual, ax=axes[1], color='orange', label='ATL', bottom=annual['ec_sum'])
sns.barplot(x='year', y='tmkt_sum', data=annual, ax=axes[1], color='r', label='TMKT', bottom=annual['ec_sum']+annual['atl_sum'])
axes[1].set_title('年度营销花费堆积')
axes[1].legend()

for c in ctrl_cols[:3]:
    sns.lineplot(x='year', y=c, data=annual, marker='o', ax=axes[2], label=c)
axes[2].set_title('Control特征趋势(示例)')
axes[2].legend()
fig.tight_layout()
path2 = 'temp/task_7fcaee2c31d9_年度趋势探索分析.png'
fig.savefig(path2, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="年度趋势探索分析",
    topic="趋势洞察",
    idea="按年汇总销售额与各类别花费，计算同比变化率，绘制趋势与堆积组合图",
    result=annual[['year', 'omni_consumption', 'sales_yoy', 'ec_sum', 'atl_sum', 'tmkt_sum']].to_dict('records'),
    chart_json=[path2]
)

# 步骤3
X = df[spend_cols + ctrl_cols].copy()
y = df['omni_consumption']
X_const = sm.add_constant(X)
model = sm.OLS(y, X_const).fit()
coeffs = model.params.drop('const')
pvals = model.pvalues.drop('const')
r2 = model.rsquared
sig = pvals[pvals < 0.05].index.tolist()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=coeffs.values, y=coeffs.index, ax=ax, palette='viridis')
ax.axvline(0, color='k', lw=1)
ax.set_title('各特征回归系数 (OLS)')
ax.set_xlabel('系数值')
fig.tight_layout()
path3 = 'temp/task_7fcaee2c31d9_归因建模与效率评估.png'
fig.savefig(path3, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="归因建模与效率评估",
    topic="归因模型",
    idea="构建多元线性回归，检验显著性，提取系数评估各渠道与控制变量贡献",
    result={"R2": r2, "显著特征": sig, "系数": coeffs.to_dict(), "P值": pvals.to_dict()},
    chart_json=[path3]
)

# 步骤4
annual_roas = annual.copy()
for col in spend_cols:
    if col in coeffs.index:
        annual_roas[f'{col}_contrib'] = annual_roas[col] * coeffs[col]
        annual_roas[f'{col}_roas'] = annual_roas[f'{col}_contrib'] / annual_roas[col].replace(0, np.nan)
    else:
        annual_roas[f'{col}_contrib'] = 0
        annual_roas[f'{col}_roas'] = 0

b_data = []
for col in spend_cols:
    for _, row in annual_roas.iterrows():
        if row[col] > 0 and pd.notna(row[f'{col}_roas']):
            b_data.append({'channel': col, 'year': row['year'], 'spend': row[col], 'contrib': row[f'{col}_contrib'], 'roas': row[f'{col}_roas']})
b_df = pd.DataFrame(b_data)

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(x='spend', y='contrib', size='roas', sizes=(50, 500), data=b_df, ax=ax, alpha=0.7, legend=False)
for i, row in b_df.iterrows():
    ax.annotate(f"{row['channel']}\n{row['year']}", (row['spend'], row['contrib']), fontsize=8)
ax.set_xlabel('投入金额')
ax.set_ylabel('归因贡献')
ax.set_title('渠道投入-贡献气泡图 (大小=ROAS)')
fig.tight_layout()
path4 = 'temp/task_7fcaee2c31d9_年度汇总与ROAS计算.png'
fig.savefig(path4, dpi=100)
plt.close(fig)

save_analysis_step(
    step_name="年度汇总与ROAS计算",
    topic="ROAS评估",
    idea="基于回归系数计算年度归因贡献与ROAS，绘制气泡图评估效率",
    result=b_df.to_dict('records'),
    chart_json=[path4]
)

# 步骤5
avg_roas = b_df.groupby('channel')['roas'].mean()
med = avg_roas.median()
high = avg_roas[avg_roas > med].index.tolist()
low = avg_roas[avg_roas <= med].index.tolist()

sim_annual = annual_roas.copy()
shift_amt = sim_annual[low].sum().sum() * 0.2
sim_annual[low] = sim_annual[low] * 0.8
sim_annual[high] = sim_annual[high] + (shift_amt / max(len(high), 1))

delta = 0
for col in spend_cols:
    if col in coeffs.index:
        delta += (sim_annual[col].sum() - annual_roas[col].sum()) * coeffs[col]

res5 = {
    "高效渠道": high,
    "低效渠道": low,
    "转移预算": shift_amt,
    "预估营收增长": delta,
    "建议": f"将低效渠道({', '.join(low)})20%预算转至高效渠道({', '.join(high)})，预计增收{delta:.2f}"
}
save_analysis_step(
    step_name="策略建议与效果模拟",
    topic="策略优化",
    idea="识别高低效渠道，模拟预算重分配，基于模型系数估算营收变化",
    result=res5,
    chart_json=[]
)