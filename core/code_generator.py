from core.llm_client import call_llm_code

def generate_analysis_code(plan, probe, file_path, task_id, error_text):
   code_prompt = f"""
   你是一名资深数据科学家和Python工程师，请基于给定信息生成**可直接运行的完整Python代码**，用于执行数据分析任务。

   ==================
   【输入信息】
   分析计划:
   {plan}

   数据特征:
   {probe}

   数据文件路径:
   {file_path}

   任务ID:
   {task_id}
   ==================

   【核心目标】
   按照“分析计划”的步骤顺序执行数据分析，并在每一步结束后记录结果。

   ==================
   【强制执行规范（必须100%遵守）】

   1. 【步骤执行 + 结果记录】
   每完成一个分析步骤，必须立即调用函数：
   save_analysis_step(
       step_name="步骤名称",
       topic="分析主题",
       idea="分析思路",
       result=分析结果,
       chart_json=图表路径列表
   )

   - 不允许遗漏任何步骤
   - result 必须是结构化数据（dict/list/str）

   ------------------

   2. 【数据处理要求】
   必须包含：
   - 读取数据（支持 csv / excel）
   - 缺失值处理（删除或填充）
   - 异常值基础处理（如极端值过滤或说明）

   ------------------

   3. 【绘图规范】
   - 仅允许使用：matplotlib / seaborn
   - 优先使用 seaborn
   - 必须设置中文字体（避免乱码）
   - 每张图：
       - figsize=(9,5)
       - dpi=120
   - 保存格式：
       temp/{task_id}_步骤名.png

   注意：
   - 文件名不能有空格
   - 不要在 savefig 中使用 figsize 参数
   - chart_json 必须是列表，例如 ["temp/xxx.png"]

   ------------------

   4. 【代码规范】
   - 仅导入必要库：pandas / numpy / matplotlib / seaborn / os
   - 代码必须完整、可运行
   - 不允许定义 save_analysis_step（直接调用）
   - 路径必须使用变量，不要硬编码

   ------------------

   5. 【输出要求（极其重要）】
   - 只输出 Python 代码
   - 不要解释
   - 不要注释
   - 不要 markdown
   - 不要 ```python
   - 代码必须一次性完整输出

   ==================

   【代码结构要求（必须遵守）】

   代码必须严格按照如下结构生成：

   1. 导入库
   2. 设置中文字体
   3. 读取数据
   4. 数据清洗
   5. 按步骤执行分析：
      - 计算
      - 绘图（如需要）
      - 保存图片
      - 调用 save_analysis_step

   ==================

   【错误规避（必须避免）】
   {error_text}

   ==================

   请严格按照以上规范生成代码。
   """
   code = call_llm_code(code_prompt)
   return code