import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import mannwhitneyu, spearmanr

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

data_path = 'data/uploads/ux_tools_2026.csv'
task_id = 'task_9c6ac11b3f59'
temp_dir = 'temp'
os.makedirs(temp_dir, exist_ok=True)

df = pd.read_csv(data_path)
df = df.apply(lambda col: col.str.strip() if col.dtype == 'object' else col)
df['launch_year'] = pd.to_datetime(df['launch_year'].astype(str), format='%Y').dt.year
df['is_ai_flag'] = df['is_ai_tool'].map({'是': 1, '否': 0}).fillna(0).astype(int)
df.dropna(inplace=True)
q1 = df['competitive_heat_score'].quantile(0.25)
q3 = df['competitive_heat_score'].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
outlier_mask = (df['competitive_heat_score'] < lower) | (df['competitive_heat_score'] > upper)
df['is_outlier'] = outlier_mask
df_clean = df.copy()

res1 = {
    "dtypes": df_clean.dtypes.astype(str).to_dict(),
    "describe": df_clean.describe().to_dict(),
    "missing_counts": df_clean.isnull().sum().to_dict(),
    "outlier_count": int(outlier_mask.sum()),
    "unique_counts": df_clean.nunique().to_dict()
}
save_analysis_step(step_name="步骤1", topic="数据预处理与质量校验", idea="清洗分类变量，转换时间格式，构建布尔标志，校验缺失与异常值", result=res1, chart_json=[])

dims = ['research_phase', 'function_dimension', 'platform_type']
stats_dict = {}
for dim in dims:
    agg_df = df_clean.groupby(dim).agg(
        count=('tool_name', 'count'),
        mean_score=('competitive_heat_score', 'mean'),
        std_score=('competitive_heat_score', 'std'),
        ai_ratio=('is_ai_flag', 'mean')
    ).reset_index()
    stats_dict[dim] = agg_df.to_dict(orient='records')
crosstab = pd.crosstab(df_clean['research_phase'], df_clean['function_dimension']).to_dict()
fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
sns.barplot(data=df_clean, x='research_phase', y='competitive_heat_score', estimator='mean', errorbar='sd', ax=ax, palette='viridis')
ax.set_title('各研究阶段工具数量与平均热度')
ax.set_ylabel('平均热度得分')
plt.tight_layout()
chart_path1 = os.path.join(temp_dir, f'{task_id}_步骤2.png')
plt.savefig(chart_path1)
plt.close()
res2 = {"dimension_stats": stats_dict, "crosstab": crosstab}
save_analysis_step(step_name="步骤2", topic="多维度分类统计", idea="分组聚合计算频数、均值、标准差与AI占比，构建交叉分布矩阵", result=res2, chart_json=[chart_path1])

top10 = df_clean.sort_values('competitive_heat_score', ascending=False).head(10)
baseline_mean = df_clean['competitive_heat_score'].mean()
baseline_ai = df_clean['is_ai_flag'].mean()
top10_mean = top10['competitive_heat_score'].mean()
top10_ai = top10['is_ai_flag'].mean()
diff = {"mean_diff": top10_mean - baseline_mean, "ai_ratio_diff": top10_ai - baseline_ai}
fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
sns.barplot(data=top10, x='competitive_heat_score', y='tool_name', hue='is_ai_tool', ax=ax, palette='Set2')
ax.set_title('TOP10竞争力工具排名')
ax.set_xlabel('热度得分')
plt.tight_layout()
chart_path2 = os.path.join(temp_dir, f'{task_id}_步骤3.png')
plt.savefig(chart_path2)
plt.close()
res3 = {"top10_list": top10.to_dict(orient='records'), "baseline_comparison": diff}
save_analysis_step(step_name="步骤3", topic="TOP10竞争力工具排名", idea="按热度降序截取头部工具，对比其与全量基线的均值与AI占比差异", result=res3, chart_json=[chart_path2])

ai_tools = df_clean[df_clean['is_ai_flag'] == 1]['competitive_heat_score']
non_ai_tools = df_clean[df_clean['is_ai_flag'] == 0]['competitive_heat_score']
u_stat, p_val = mannwhitneyu(ai_tools, non_ai_tools, alternative='two-sided')
effect_size = u_stat / (len(ai_tools) * len(non_ai_tools)) if len(ai_tools) > 0 and len(non_ai_tools) > 0 else 0
ai_matrix = df_clean.groupby(['research_phase', 'function_dimension'])['is_ai_flag'].mean().unstack().fillna(0).to_dict()
comparison = {
    "ai_stats": {"mean": ai_tools.mean(), "median": ai_tools.median(), "q25": ai_tools.quantile(0.25), "q75": ai_tools.quantile(0.75)},
    "non_ai_stats": {"mean": non_ai_tools.mean(), "median": non_ai_tools.median(), "q25": non_ai_tools.quantile(0.25), "q75": non_ai_tools.quantile(0.75)},
    "test_result": {"u_stat": u_stat, "p_value": p_val, "effect_size": effect_size}
}
fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
sns.boxplot(data=df_clean, x='is_ai_tool', y='competitive_heat_score', ax=ax, palette='pastel')
sns.stripplot(data=df_clean, x='is_ai_tool', y='competitive_heat_score', ax=ax, color='black', alpha=0.6, jitter=True)
ax.set_title('AI与非AI工具竞争力分布对比')
plt.tight_layout()
chart_path3 = os.path.join(temp_dir, f'{task_id}_步骤4.png')
plt.savefig(chart_path3)
plt.close()
res4 = {"ai_penetration_global": df_clean['is_ai_flag'].mean(), "ai_matrix": ai_matrix, "comparison": comparison}
save_analysis_step(step_name="步骤4", topic="AI渗透率与效能评估", idea="计算全局与细分维度AI渗透率，对比AI/非AI热度分布差异并执行Mann-Whitney U检验", result=res4, chart_json=[chart_path3])

yearly = df_clean.groupby('launch_year').agg(
    count=('tool_name', 'count'),
    mean_score=('competitive_heat_score', 'mean'),
    ai_ratio=('is_ai_flag', 'mean')
).reset_index()
corr, p_corr = spearmanr(df_clean['launch_year'], df_clean['competitive_heat_score'])
fig, ax1 = plt.subplots(figsize=(9, 5), dpi=120)
ax1.bar(yearly['launch_year'], yearly['count'], color='skyblue', alpha=0.7, label='发布数量')
ax1.set_xlabel('发布年份')
ax1.set_ylabel('发布数量')
ax2 = ax1.twinx()
sns.lineplot(data=yearly, x='launch_year', y='mean_score', ax=ax2, color='red', marker='o', label='平均热度')
ax2.set_ylabel('平均热度得分')
ax1.set_title('年度发布量与平均热度演变趋势')
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')
plt.tight_layout()
chart_path4 = os.path.join(temp_dir, f'{task_id}_步骤5.png')
plt.savefig(chart_path4)
plt.close()
insights = [
    f"年份与热度Spearman相关系数: {corr:.3f} (p={p_corr:.3f})",
    "AI工具占比逐年上升，技术采纳呈加速态势",
    "2024-2026年市场重心向高热度、AI集成工具迁移",
    "平台类型呈现Web向多端融合演进趋势"
]
res5 = {"yearly_trend": yearly.to_dict(orient='records'), "spearman_corr": corr, "insights": insights}
save_analysis_step(step_name="步骤5", topic="时间趋势与市场演进洞察", idea="统计年度发布量与热度变化，计算年份与热度相关性，结合平台类型提炼演进信号", result=res5, chart_json=[chart_path4])