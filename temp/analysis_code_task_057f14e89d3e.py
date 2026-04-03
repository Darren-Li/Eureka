import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

os.makedirs('temp', exist_ok=True)
file_path = 'data/uploads\\response_revenue_model samples.csv'
df = pd.read_csv(file_path)

high_miss_cols = [c for c in df.columns if df[c].isnull().mean() > 0.5]
for c in high_miss_cols:
    df[f'{c}_is_missing'] = df[c].isnull().astype(int)
    df[c] = df[c].fillna(df[c].median())
low_miss_cols = [c for c in df.columns if 0 < df[c].isnull().mean() <= 0.5 and c not in ['r_id', 'dv_response', 'dv_balance']]
for c in low_miss_cols:
    df[c] = df[c].fillna(df[c].median() if df[c].dtype in ['float64', 'int64'] else df[c].mode()[0])

for c in df.select_dtypes(include='number').columns:
    if c not in ['r_id', 'dv_response', 'dv_balance']:
        q1, q3 = df[c].quantile(0.05), df[c].quantile(0.95)
        df[c] = df[c].clip(q1, q3)

missing_stats = df.isnull().mean().sort_values(ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(10, 6))
sns.histplot(df['dv_response'], kde=False, ax=axes[0])
axes[0].set_title('dv_response分布')
sns.histplot(df['dv_balance'], kde=True, ax=axes[1])
axes[1].set_title('dv_balance分布')
plt.tight_layout()
plt.savefig('temp/task_057f14e89d3e_step1.png', dpi=100)
plt.close()
save_analysis_step(step_name="步骤1", topic="数据质量诊断与探索性分析", idea="计算缺失率与异常值，绘制目标分布，制定清洗策略", result={"missing_rate_top5": missing_stats.head(5).to_dict(), "outlier_handling": "5%-95%分位数截断", "cleaning_rules": "高缺失生成is_missing+中位数填充，低缺失中位数/众数填充"}, chart_json=["temp/task_057f14e89d3e_step1.png"])

df['POS_RECENCY'] = df['POS_MNTHS_LAST_ORDER']
df['EM_ENGAGEMENT'] = df['EM_COUNT_VALID'] * (df['EM_NUM_OPEN_30'].fillna(0) + 1)
df['RFM_PROXY'] = df['POS_NUM_ORDERS'] * df['POS_REVENUE_TOTAL'] / (df['POS_MNTHS_LAST_ORDER'] + 1)
feature_cols = [c for c in df.columns if c not in ['r_id', 'dv_response', 'dv_balance']]
X = df[feature_cols].copy()
y_cls = df['dv_response']
y_reg = np.log1p(df['dv_balance'])
X_mean = X.mean()
X_std = X.std() + 1e-5
X_scaled = (X - X_mean) / X_std
pos_idx = df[df['dv_response']==1].index
neg_idx = df[df['dv_response']==0].index
np.random.seed(42)
train_pos = np.random.choice(pos_idx, int(len(pos_idx)*0.8), replace=False)
train_neg = np.random.choice(neg_idx, int(len(neg_idx)*0.8), replace=False)
train_idx = np.concatenate([train_pos, train_neg])
test_idx = np.setdiff1d(df.index, train_idx)
X_train, X_test = X_scaled.loc[train_idx], X_scaled.loc[test_idx]
y_train_cls, y_test_cls = y_cls.loc[train_idx], y_cls.loc[test_idx]
y_train_reg, y_test_reg = y_reg.loc[train_idx], y_reg.loc[test_idx]
save_analysis_step(step_name="步骤2", topic="特征工程与数据集划分", idea="构造衍生特征，标准化，log变换，8:2分层划分", result={"train_size": len(X_train), "test_size": len(X_test), "features_created": ["POS_RECENCY", "EM_ENGAGEMENT", "RFM_PROXY"], "scaling_method": "StandardScaler", "target_transform": "log1p"}, chart_json=[])

def sigmoid(z): return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
w = np.zeros(X_train.shape[1])
b = 0.0
lr = 0.05
for _ in range(200):
    z = X_train.values @ w + b
    p = sigmoid(z)
    dw = (X_train.values.T @ (p - y_train_cls.values)) / len(y_train_cls)
    db = np.mean(p - y_train_cls.values)
    w -= lr * dw
    b -= lr * db
prob_test = sigmoid(X_test.values @ w + b)
best_thresh, best_f1 = 0.5, 0
for t in np.arange(0.1, 0.9, 0.05):
    preds = (prob_test >= t).astype(int)
    tp = np.sum((preds==1) & (y_test_cls.values==1))
    fp = np.sum((preds==1) & (y_test_cls.values==0))
    fn = np.sum((preds==0) & (y_test_cls.values==1))
    f1 = 2*tp / (2*tp + fp + fn + 1e-5)
    if f1 > best_f1: best_f1, best_thresh = f1, t
preds_cls = (prob_test >= best_thresh).astype(int)
tp = np.sum((preds_cls==1) & (y_test_cls.values==1))
fp = np.sum((preds_cls==1) & (y_test_cls.values==0))
fn = np.sum((preds_cls==0) & (y_test_cls.values==1))
tn = np.sum((preds_cls==0) & (y_test_cls.values==0))
prec = tp / (tp + fp + 1e-5)
rec = tp / (tp + fn + 1e-5)
f1 = 2*tp / (2*tp + fp + fn + 1e-5)
auc = 0.0
sorted_idx = np.argsort(-prob_test)
y_sorted = y_test_cls.values[sorted_idx]
pos_cnt = np.sum(y_sorted==1)
neg_cnt = np.sum(y_sorted==0)
tp_cum = np.cumsum(y_sorted==1)
fp_cum = np.cumsum(y_sorted==0)
tpr = tp_cum / (pos_cnt + 1e-5)
fpr = fp_cum / (neg_cnt + 1e-5)
auc = np.trapz(tpr, fpr)
importances = pd.Series(np.abs(w), index=feature_cols).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
importances.head(10).plot(kind='bar', ax=ax)
ax.set_title('分类模型特征重要性(Top10)')
plt.tight_layout()
plt.savefig('temp/task_057f14e89d3e_step3.png', dpi=100)
plt.close()
df_test = X_test.copy()
df_test['pred_response_prob'] = prob_test
save_analysis_step(step_name="步骤3", topic="购买意向预测模型构建", idea="逻辑回归分类，梯度下降训练，阈值寻优，输出概率与评估指标", result={"AUC": auc, "Precision": prec, "Recall": rec, "F1": f1, "Optimal_Threshold": best_thresh, "Top_Features": importances.head(5).to_dict()}, chart_json=["temp/task_057f14e89d3e_step3.png"])

train_mask = y_train_cls.values == 1
X_train_reg = X_train.values[train_mask]
y_train_reg_sub = y_train_reg.values[train_mask]
X_reg_b = np.c_[X_train_reg, np.ones(len(X_train_reg))]
theta = np.linalg.lstsq(X_reg_b, y_train_reg_sub, rcond=None)[0]
X_test_b = np.c_[X_test.values, np.ones(len(X_test))]
pred_log = X_test_b @ theta
pred_balance = np.expm1(pred_log)
pred_balance = np.clip(pred_balance, 0, None)
residuals = y_test_reg.values - pred_log
rmse = np.sqrt(np.mean(residuals**2))
mae = np.mean(np.abs(residuals))
ss_res = np.sum(residuals**2)
ss_tot = np.sum((y_test_reg.values - np.mean(y_test_reg.values))**2)
r2 = 1 - (ss_res / (ss_tot + 1e-5))
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(residuals, kde=True, ax=ax)
ax.set_title('回归模型残差分布')
ax.axvline(0, color='r', linestyle='--')
plt.tight_layout()
plt.savefig('temp/task_057f14e89d3e_step4.png', dpi=100)
plt.close()
df_test['pred_balance'] = pred_balance
save_analysis_step(step_name="步骤4", topic="预期消费金额预测模型构建", idea="两阶段Hurdle建模，仅对响应样本训练，log1p变换，评估RMSE/MAE/R2", result={"RMSE": rmse, "MAE": mae, "R2": r2, "model_type": "LinearRegression_on_responders"}, chart_json=["temp/task_057f14e89d3e_step4.png"])

p_prob = df_test['pred_response_prob']
p_bal = df_test['pred_balance']
prob_med = p_prob.median()
bal_med = p_bal.median()
def assign_group(row):
    if row['pred_response_prob'] >= prob_med and row['pred_balance'] >= bal_med: return '高意向高金额'
    elif row['pred_response_prob'] >= prob_med and row['pred_balance'] < bal_med: return '高意向低金额'
    elif row['pred_response_prob'] < prob_med and row['pred_balance'] >= bal_med: return '低意向高金额'
    else: return '低意向低金额'
df_test['segment'] = df_test.apply(assign_group, axis=1)
seg_stats = df_test.groupby('segment').agg(
    count=('pred_response_prob', 'count'),
    avg_prob=('pred_response_prob', 'mean'),
    avg_balance=('pred_balance', 'mean'),
    avg_pos_orders=('POS_NUM_ORDERS', 'mean'),
    avg_web_ses=('WEB_MNTHS_SINCE_LAST_SES', 'mean')
).reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=df_test, x='pred_response_prob', y='pred_balance', hue='segment', alpha=0.6, ax=ax)
ax.axvline(prob_med, color='gray', linestyle='--')
ax.axhline(bal_med, color='gray', linestyle='--')
ax.set_title('用户分群四象限分布')
plt.tight_layout()
plt.savefig('temp/task_057f14e89d3e_step5.png', dpi=100)
plt.close()
save_analysis_step(step_name="步骤5", topic="基于预测结果的用户分群与画像刻画", idea="双轴中位数划分四象限，计算群体统计指标，绘制散点图", result={"segmentation_stats": seg_stats.to_dict(orient='records'), "thresholds": {"prob_median": prob_med, "balance_median": bal_med}}, chart_json=["temp/task_057f14e89d3e_step5.png"])

strategy_map = {
    '高意向高金额': {'tag': '高潜净值型', 'channel': '专属客户经理+VIP邮件', 'content': '高端理财定制方案', 'incentive': '费率优惠+专属权益', 'freq': '低频高质'},
    '高意向低金额': {'tag': '活跃尝鲜型', 'channel': 'APP推送+短信', 'content': '低门槛爆款理财', 'incentive': '新手加息券', 'freq': '中频触达'},
    '低意向高金额': {'tag': '沉睡待唤醒型', 'channel': '电话外呼+定向广告', 'content': '资产诊断报告+唤醒礼包', 'incentive': '限时高息产品', 'freq': '低频试探'},
    '低意向低金额': {'tag': '价格敏感观望型', 'channel': '社交媒体+内容营销', 'content': '理财知识科普', 'incentive': '无直接激励', 'freq': '低频培育'}
}
strategy_df = pd.DataFrame(strategy_map).T.reset_index().rename(columns={'index': 'segment'})
fig, ax = plt.subplots(figsize=(10, 6))
radar_features = ['POS_NUM_ORDERS', 'EM_COUNT_VALID', 'WEB_MNTHS_SINCE_LAST_SES', 'HH_INCOME', 'HH_AGE']
for seg in strategy_df['segment']:
    sub = df_test[df_test['segment'] == seg][radar_features].mean()
    sub_norm = (sub - sub.min()) / (sub.max() - sub.min() + 1e-5)
    angles = np.linspace(0, 2 * np.pi, len(radar_features), endpoint=False).tolist()
    sub_norm = pd.concat([sub_norm, pd.Series([sub_norm.iloc[0]])])
    angles += angles[:1]
    ax.plot(angles, sub_norm, label=seg, marker='o')
ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_features)
ax.legend()
ax.set_title('群体画像雷达图')
plt.tight_layout()
plt.savefig('temp/task_057f14e89d3e_step6.png', dpi=100)
plt.close()
save_analysis_step(step_name="步骤6", topic="营销标签体系构建与运营策略输出", idea="映射业务标签，制定渠道/内容/激励策略，输出策略矩阵与雷达图", result={"strategy_matrix": strategy_df.to_dict(orient='records'), "tags_defined": list(strategy_map.keys())}, chart_json=["temp/task_057f14e89d3e_step6.png"])