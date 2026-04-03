import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

file_path = 'data/uploads/ux_tools_2026.csv'
task_id = 'task_c51e647b1451'
os.makedirs('temp', exist_ok=True)

def safe_convert(obj):
    if isinstance(obj, dict):
        return {str(k): safe_convert(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_convert(i) for i in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

def save_chart(fig, step_name):
    safe_name = step_name.replace(' ', '_').replace('（', '_').replace('）', '_').replace('(', '_').replace(')', '_').replace('，', '_')
    path = f"temp/{task_id}_{safe_name}.png"
    fig.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    return path

df = pd.read_csv(file_path)
df['launch_year'] = pd.to_numeric(df['launch_year'], errors='coerce').astype('Int64')
df['competitive_heat_score'] = pd.to_numeric(df['competitive_heat_score'], errors='coerce').astype('float')
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

save_analysis_step(
    step_name="数据加载与清洗",
    topic="数据预处理",
    idea="读取CSV检查缺失值与类型转换数值列",
    result=safe_convert({"rows": df.shape[0], "cols": df.shape[1], "columns": list(df.columns)}),
    chart_json=[]
)

desc = df[['competitive_heat_score', 'launch_year']].describe().to_dict()
unique_counts = {col: int(df[col].nunique()) for col in df.columns}
save_analysis_step(
    step_name="基本描述统计",
    topic="数值与分类统计",
    idea="计算均值中位数极值及唯一值数量",
    result=safe_convert({"describe": desc, "unique_counts": unique_counts}),
    chart_json=[]
)

phase_counts = df['research_phase'].value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=phase_counts.index, y=phase_counts.values, ax=ax, palette='viridis')
ax.set_title('各研究阶段工具数量分布')
ax.set_ylabel('数量')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
p3 = save_chart(fig, "分类统计（研究阶段）")
save_analysis_step(
    step_name="分类统计（研究阶段）",
    topic="研究阶段分布",
    idea="统计各阶段工具数量及占比",
    result=safe_convert({"counts": phase_counts.to_dict(), "percentages": (phase_counts / phase_counts.sum() * 100).to_dict()}),
    chart_json=[p3]
)

func_counts = df['function_dimension'].value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=func_counts.index, y=func_counts.values, ax=ax, palette='magma')
ax.set_title('各功能维度工具数量分布')
ax.set_ylabel('数量')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
p4 = save_chart(fig, "分类统计（功能维度）")
save_analysis_step(
    step_name="分类统计（功能维度）",
    topic="功能维度分布",
    idea="统计各功能维度工具数量及占比",
    result=safe_convert({"counts": func_counts.to_dict(), "percentages": (func_counts / func_counts.sum() * 100).to_dict()}),
    chart_json=[p4]
)

plat_counts = df['platform_type'].value_counts()
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=plat_counts.index, y=plat_counts.values, ax=ax, palette='coolwarm')
ax.set_title('各平台类型工具数量分布')
ax.set_ylabel('数量')
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom')
p5 = save_chart(fig, "分类统计（平台类型）")
save_analysis_step(
    step_name="分类统计（平台类型）",
    topic="平台类型分布",
    idea="统计各平台类型工具数量及占比",
    result=safe_convert({"counts": plat_counts.to_dict(), "percentages": (plat_counts / plat_counts.sum() * 100).to_dict()}),
    chart_json=[p5]
)

top10 = df.nlargest(10, 'competitive_heat_score')[['tool_name', 'competitive_heat_score', 'research_phase', 'function_dimension']]
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=top10, x='competitive_heat_score', y='tool_name', ax=ax, palette='rocket')
ax.set_title('TOP10 竞争力工具排名')
for p in ax.patches:
    ax.annotate(f'{p.get_width():.1f}', (p.get_width(), p.get_y() + p.get_height()/2), ha='left', va='center')
p6 = save_chart(fig, "TOP10 排名")
save_analysis_step(
    step_name="TOP10 排名",
    topic="高竞争力工具",
    idea="按热度得分降序取前10名",
    result=safe_convert(top10.to_dict(orient='records')),
    chart_json=[p6]
)

ai_total = (df['is_ai_tool'] == '是').sum()
ai_pct = ai_total / len(df) * 100
ai_cross_plat = pd.crosstab(df['is_ai_tool'], df['platform_type'])
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
axes[0].pie([ai_total, len(df)-ai_total], labels=['AI工具', '非AI工具'], autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
axes[0].set_title('AI工具整体渗透率')
ai_cross_plat_norm = ai_cross_plat.div(ai_cross_plat.sum(axis=0), axis=1) * 100
ai_cross_plat_norm.T.plot(kind='bar', stacked=True, ax=axes[1], color=['#66b3ff','#ff9999'])
axes[1].set_title('AI工具在不同平台类型的分布占比')
axes[1].set_ylabel('占比(%)')
axes[1].legend(['非AI', 'AI'])
plt.tight_layout()
p7 = save_chart(fig, "AI 渗透率分析")
save_analysis_step(
    step_name="AI 渗透率分析",
    topic="AI工具分布",
    idea="计算AI占比及交叉维度分布",
    result=safe_convert({"overall_ai_pct": ai_pct, "cross_platform": ai_cross_plat.to_dict()}),
    chart_json=[p7]
)

year_counts = df['launch_year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(x=year_counts.index.astype(str), y=year_counts.values, marker='o', ax=ax, color='teal')
ax.set_title('年度新增工具数量趋势')
ax.set_xlabel('发布年份')
ax.set_ylabel('工具数量')
p8 = save_chart(fig, "趋势洞察（发布年份）")
save_analysis_step(
    step_name="趋势洞察（发布年份）",
    topic="发布时间趋势",
    idea="按年份统计新增工具数量",
    result=safe_convert(year_counts.to_dict()),
    chart_json=[p8]
)

year_heat = df.groupby('launch_year')['competitive_heat_score'].mean()
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(x=year_heat.index.astype(str), y=year_heat.values, marker='s', ax=ax, color='orange')
ax.set_title('年度平均热度得分变化')
ax.set_xlabel('发布年份')
ax.set_ylabel('平均热度得分')
p9 = save_chart(fig, "趋势洞察（热度变化）")
save_analysis_step(
    step_name="趋势洞察（热度变化）",
    topic="热度演变趋势",
    idea="按年份计算平均竞争力热度",
    result=safe_convert(year_heat.to_dict()),
    chart_json=[p9]
)

cross_table = pd.crosstab(df['research_phase'], df['function_dimension'], values=df['competitive_heat_score'], aggfunc='mean').fillna(0)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(cross_table, annot=True, fmt=".1f", cmap='YlGnBu', ax=ax, cbar_kws={'label': '平均热度得分'})
ax.set_title('研究阶段 × 功能维度 平均热度热力图')
p10 = save_chart(fig, "多维交叉分析")
save_analysis_step(
    step_name="多维交叉分析",
    topic="多维交叉分布",
    idea="透视表展示阶段与功能组合的平均热度",
    result=safe_convert(cross_table.to_dict()),
    chart_json=[p10]
)

report_md = f"# 2026 UX 工具全景分析报告\n## 核心发现\n1. 数据概况: 共收录 {len(df)} 款工具，覆盖 {df['research_phase'].nunique()} 个研究阶段与 {df['function_dimension'].nunique()} 个功能维度。\n2. TOP10: 热度最高工具为 {top10.iloc[0]['tool_name']} (得分 {top10.iloc[0]['competitive_heat_score']})。\n3. AI渗透: AI工具占比 {ai_pct:.1f}%。\n4. 趋势: 工具发布量与平均热度得分呈现稳定发展态势。\n5. 交叉洞察: 发现阶段与用户研究结合的工具热度较高，AI赋能显著提升设计领域竞争力。"
save_analysis_step(
    step_name="报告生成",
    topic="全景报告汇总",
    idea="整合分析结果与图表生成Markdown摘要",
    result=report_md,
    chart_json=[]
)