# 🤖 Eureka - An Agentic Analytics Platform

一个智能体驱动的数据分析平台

![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

[![English](https://img.shields.io/badge/English-d9d9d9?style=for-the-badge)](README.md)
[![简体中文](https://img.shields.io/badge/简体中文-d9d9d9?style=for-the-badge)](docs/readme/zh-CN.md)

---

## 📖 项目简介

- Eureka 是一个智能体驱动的数据分析平台，通过上传数据并定义分析需求，平台可自动理解用户意图，拆解分析任务，生成并执行分析代码，最终输出结构化、可视化、专业级分析报告，实现从数据到洞察的全流程自动化。

---

## ✨ 功能

- 📂 功能 1: 数据管理
- ⚠️ 功能 2: 模型配置
- 👥 功能 3: 智能分析
- 📈 功能 4: 查看报告

---

## ⚙️ 安装和使用
```
git clone https://github.com/Darren-Li/Eureka.git
cd Eureka
```

安装python依赖包
```python
pip install -r requirements.txt
```

▶️ 启动
```
streamlit run Eureka.py
```

---

## ▶️ 示例效果
- 🎬 Demo Website: https://aha-Eureka.streamlit.app/

- 📂 数据管理
	![demo](/docs/img/1.data_management.png)
- ⚠️ 模型配置
	![demo](/docs/img/2.Configure_Your_LLMs.png)
- 👥 智能分析
	![demo](/docs/img/3.data_analysis.png)
- 📈 查看报告
	![demo](/docs/img/4.1analysis_report.png)
	![demo](/docs/img/4.2analysis_report.png)
	![demo](/docs/img/4.3analysis_report.png)
	![demo](/docs/img/4.4analysis_report.png)


### Demo数据及分析参数示例：
### Demo1：
	主题：
		2026年全球UX工具全景分析
	文件：
		ux_tools_2026.csv
	文件描述：
		这是2026年全网UC工具及使用情况的统计数据
	字段描述：
		工具名称
		研究阶段
		功能维度
		是否是AI工具
		竞赛热度得分
		发布年份
		平台类型
	分析提示：
		生成2026 UX工具全景报告，包含分类统计、TOP10排名、AI渗透率分析、趋势洞察
### Demo2：
	文件：ecommerce_data.csv
	文件描述：
		电商消费数据
	字段描述：
		xxx
	分析提示：
		分析不同用户分层（user_segment）的消费能力（avg_order_value）和购买频率（purchase_frequency），识别高价值用户群体；
		探究商品类别（product_category）与折扣应用（discount_applied）对销售额（total_amount）和退货率（return_status）的影响；
		分析会员等级（membership_level）、设备类型（device_type）与客户评分（customer_rating）的相关性，优化用户体验策略。
### Demo3:
	主题：
		银行用户购买倾向性及营销分群分析
	文件：response_revenue_model samples.csv
	文件描述：
		这是一份消费者购买银行理财产品的数据，包括消费者基本属性数据和过去一段时间消费者与银行的营销活动及购买银行理财产品的互动行为。数据中r_id是用户id； dv_response 是用户是否在未来一年内进行消费，1代表会，0代表不会, dv_balance 是如果消费的消费金额
	字段描述：
	分析提示：
		先分析数据情况，给出数据探索分析结果；再进行用户的购买可能行预测（dv_response），和如果购买会花费多少金额（dv_balance）；再基于预测结果进行用户分群，在购买意向和消费金额维度识别出高价值用户，并从营销角度对用户群进行打标签，给出用户群特点及数据统计结果，最后给出不同用户群的运营策略。
### Demo4:
	主题：
		消费健康品牌全区渠道营销广告归因分析
	文件：MMM demo data.csv
	文件描述：
		这是一份消费健康品牌的市场活动投放及结果数据，数据是在月度粒度上统计的，包括月份时间字段date_key，销售收入变量omni_consumption，不同营销渠道广告投放花费成本数据，影响销售额的其他外生变量。
	字段描述：

	分析提示：
		先分析数据情况，给出数据探索分析结果，包括年度全渠道销售（omni_consumption）收入趋势和年度变化率，ATL、EC、TMKT类别下汇总的营销花费和年度变化率，Control类别下各特征的趋势；
		再对全渠道销售额（omni_consumption）进行归因分析，分析ATL、EC、TMKT、Control下每个特征对其影响，并给出贡献及占比；并在年度粒度汇总计算营销渠道每个特征的贡献及ROAS（贡献/营销投入）；
		最后，综合分析，给出不同营销渠道未来的营销投入建议，比如哪些渠道可以多投入，多投入多少，哪些渠道需要控制，最后给出营销组合投资建议及估算调整前后的营收变化。
