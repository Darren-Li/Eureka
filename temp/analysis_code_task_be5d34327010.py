import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

os.makedirs('temp', exist_ok=True)

file_path = r'data/uploads\ux_tools_2026.csv'
df = pd.read_csv(file_path)

task_id = 'task_be5d34327010'

def save_chart(fig, step_key):
    path = f'temp/{task_id}_{step_key}.png'
    fig.savefig(path, dpi=100, bbox_inches='tight')
    plt.close(fig)
    return path

step1_charts = []
missing_info = df.isnull().sum().to_dict()
desc_info = df.describe().to_dict()
cat_counts = {col: df[col].value_counts().to_dict() for col in df.select_dtypes(include=['object', 'category']).columns}

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.histplot(data=df, x='competitive_heat_score', kde=True, ax=ax1)
ax1.set_title('Competitive Heat Score Distribution')
path1 = save_chart(fig1, 'step1_quality_dist')
step1_charts.append(path1)

fig2, ax2 = plt.subplots(figsize=(10, 6))
df['launch_year'].value_counts().sort_index().plot(kind='bar', ax=ax2)
ax2.set_title('Tool Launch Year Distribution')
path2 = save_chart(fig2, 'step1_quality_year')
step1_charts.append(path2)

result1 = {
    'missing_values': missing_info,
    'numeric_description': {k: {str(kk): vv for kk, vv in v.items()} for k, v in desc_info.items()},
    'category_counts': cat_counts,
    'total_rows': len(df)
}
save_analysis_step(step_name="数据质量与概览分析", topic="数据完整性与分布", idea="检查缺失值、统计样本量分布、数值型字段分布形态", result=result1, chart_json=step1_charts)

step2_charts = []
numeric_cols = ['competitive_heat_score', 'launch_year']
corr_matrix = df[numeric_cols].corr()
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax3)
ax3.set_title('Numeric Features Correlation Heatmap')
path3 = save_chart(fig3, 'step2_eda_corr')
step2_charts.append(path3)

fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='research_phase', y='competitive_heat_score', ax=ax4)
ax4.set_title('Heat Score by Research Phase')
path4 = save_chart(fig4, 'step2_eda_phase_box')
step2_charts.append(path4)

fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.countplot(data=df, x='is_ai_tool', hue='platform_type', ax=ax5)
ax5.set_title('AI Tool vs Platform Type')
path5 = save_chart(fig5, 'step2_eda_ai_platform')
step2_charts.append(path5)

result2 = {
    'correlation_matrix': corr_matrix.to_dict(),
    'phase_score_summary': df.groupby('research_phase')['competitive_heat_score'].describe().to_dict(),
    'ai_platform_cross': pd.crosstab(df['is_ai_tool'], df['platform_type']).to_dict()
}
save_analysis_step(step_name="探索性数据分析 (EDA)", topic="字段间关系与差异", idea="分析研究阶段与热度差异、AI 工具与平台交叉分布、年份与热度趋势", result=result2, chart_json=step2_charts)

step3_charts = []
df_model = df.copy()
le_ai = LabelEncoder()
le_platform = LabelEncoder()
le_function = LabelEncoder()

if df_model['is_ai_tool'].nunique() > 1:
    df_model['is_ai_tool_enc'] = le_ai.fit_transform(df_model['is_ai_tool'])
    X_cls = df_model[['launch_year']].assign(
        platform_enc=le_platform.fit_transform(df_model['platform_type']),
        function_enc=le_function.fit_transform(df_model['function_dimension'])
    )
    y_cls = df_model['is_ai_tool_enc']
    cls_model = LogisticRegression(max_iter=1000)
    cls_model.fit(X_cls, y_cls)
    cls_pred = cls_model.predict(X_cls)
    cls_acc = accuracy_score(y_cls, cls_pred)
    cls_result = {'model': 'Logistic Regression', 'accuracy': cls_acc, 'features': list(X_cls.columns)}
else:
    cls_result = {'model': 'Skipped', 'reason': 'Single class in target variable'}

X_reg = df_model[['launch_year']].assign(
    platform_enc=le_platform.fit_transform(df_model['platform_type']),
    function_enc=le_function.fit_transform(df_model['function_dimension'])
)
y_reg = df_model['competitive_heat_score']
reg_model = LinearRegression()
reg_model.fit(X_reg, y_reg)
reg_pred = reg_model.predict(X_reg)
reg_rmse = np.sqrt(mean_squared_error(y_reg, reg_pred))
reg_r2 = r2_score(y_reg, reg_pred)
reg_result = {'model': 'Linear Regression', 'rmse': float(reg_rmse), 'r2': float(reg_r2), 'coefficients': dict(zip(X_reg.columns, reg_model.coef_))}

fig6, ax6 = plt.subplots(figsize=(10, 6))
ax6.scatter(y_reg, reg_pred, alpha=0.7)
ax6.plot([y_reg.min(), y_reg.max()], [y_reg.min(), y_reg.max()], 'r--')
ax6.set_xlabel('Actual Heat Score')
ax6.set_ylabel('Predicted Heat Score')
ax6.set_title('Regression Model Performance')
path6 = save_chart(fig6, 'step3_pred_regression')
step3_charts.append(path6)

result3 = {
    'classification': cls_result,
    'regression': reg_result
}
save_analysis_step(step_name="预测模型构建", topic="工具属性与热度预测", idea="基于功能、平台、年份预测是否 AI 工具及热度得分", result=result3, chart_json=step3_charts)

step4_charts = []
median_score = df['competitive_heat_score'].median()
df['score_level'] = df['competitive_heat_score'].apply(lambda x: 'High' if x >= median_score else 'Low')
df['segment'] = df['score_level'] + '_' + df['is_ai_tool']
segment_stats = df.groupby('segment').agg({
    'competitive_heat_score': ['mean', 'count'],
    'launch_year': 'mean'
}).round(2)
segment_stats.columns = ['_'.join(col).strip() for col in segment_stats.columns.values]
segment_stats = segment_stats.reset_index()

fig7, ax7 = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x='segment', y='competitive_heat_score', ax=ax7)
ax7.set_title('Average Heat Score by Segment')
path7 = save_chart(fig7, 'step4_seg_bar')
step4_charts.append(path7)

result4 = {
    'segment_definition': f'Median Score Threshold: {median_score}',
    'segment_statistics': segment_stats.to_dict()
}
save_analysis_step(step_name="价值分群与标签化", topic="工具价值矩阵分群", idea="基于热度高低与 AI 属性进行矩阵分群，统计各群特征", result=result4, chart_json=step4_charts)

step5_charts = []
strategy_text = []
high_ai = df[(df['score_level'] == 'High') & (df['is_ai_tool'] == '是')]
if len(high_ai) > 0:
    strategy_text.append(f"高价值 AI 工具群 ({len(high_ai)}个): 建议资源倾斜，重点推广。平均热度：{high_ai['competitive_heat_score'].mean():.1f}")
else:
    strategy_text.append("高价值 AI 工具群：暂无，建议加强 AI 功能研发。")

low_trad = df[(df['score_level'] == 'Low') & (df['is_ai_tool'] == '否')]
if len(low_trad) > 0:
    strategy_text.append(f"低价值传统工具群 ({len(low_trad)}个): 建议改进功能或考虑淘汰。")
else:
    strategy_text.append("低价值传统工具群：暂无。")

year_trend = df.groupby('launch_year')['competitive_heat_score'].mean()
latest_year = year_trend.idxmax() if not year_trend.empty else 'N/A'
strategy_text.append(f"趋势建议：{latest_year}年发布的工具平均热度最高，建议关注该年份的技术栈。")

result5 = {
    'strategies': strategy_text,
    'high_value_count': len(high_ai),
    'low_value_count': len(low_trad)
}
save_analysis_step(step_name="运营策略制定", topic="产品发展与市场推广建议", idea="针对高价值群提出资源建议，针对低价值群提出改进建议，结合年份趋势给出方向", result=result5, chart_json=step5_charts)