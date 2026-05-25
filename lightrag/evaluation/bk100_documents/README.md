# BK100项目 - LightRAG调优基线测试案例

## 📋 概述

本目录包含针对BK100项目的完整LightRAG调优基线测试案例，用于评估和优化RAG系统在PLM/PDM/MOM工业数据场景下的性能。

### 测试目标

- **准确性测试**: 验证系统能否准确检索物料属性、BOM结构、设计参数等信息
- **关系推理测试**: 评估系统对装配体层级关系、设计师关联等复杂关系的理解能力
- **跨源数据整合**: 测试系统整合PLM、PDM、MOM多源数据的能力
- **数值精度测试**: 验证重量、尺寸、库存数量等数值信息的准确提取

---

## 📁 文件结构

```
lightrag/evaluation/bk100_documents/
├── 01_表架弧形板_BK100.md              # PLM物料信息
├── 02_座架组装_BK100.md                # PLM装配体BOM（版本1）
├── 03_表与滑架组装_BK100.md            # PLM装配体BOM（版本2）
├── 04_PDM零件文件_BK100.md             # PDM设计文件（3个零件）
├── 05_连杆板图纸与螺母物料.md          # PDM工程图 + MOM库存物料
└── README.md                           # 本文档

bk100_baseline_dataset.json             # 10组测试问答数据集
```

---

## 🚀 快速开始

### 步骤1: 索引文档到LightRAG

#### 方法A: 使用Web UI
1. 启动LightRAG服务: `lightrag-server`
2. 访问 http://localhost:9621
3. 上传 `bk100_documents/` 目录下的所有Markdown文件
4. 等待索引完成

#### 方法B: 使用Python API

```python
import asyncio
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.utils import EmbeddingFunc

async def index_bk100_documents():
    rag = LightRAG(
        working_dir="./rag_storage_bk100",
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=openai_embed
        )
    )
    
    # 批量插入文档
    documents = [
        "lightrag/evaluation/bk100_documents/01_表架弧形板_BK100.md",
        "lightrag/evaluation/bk100_documents/02_座架组装_BK100.md",
        "lightrag/evaluation/bk100_documents/03_表与滑架组装_BK100.md",
        "lightrag/evaluation/bk100_documents/04_PDM零件文件_BK100.md",
        "lightrag/evaluation/bk100_documents/05_连杆板图纸与螺母物料.md"
    ]
    
    for doc_path in documents:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            await rag.ainsert(content)
            print(f"Indexed: {doc_path}")

asyncio.run(index_bk100_documents())
```

#### 方法C: 使用API端点

```bash
curl -X POST http://localhost:9621/documents/upload \
  -F "file=@lightrag/evaluation/bk100_documents/01_表架弧形板_BK100.md"
```

### 步骤2: 运行基线测试

```bash
# 使用默认配置
python lightrag/evaluation/eval_rag_quality.py \
  --dataset lightrag/evaluation/bk100_baseline_dataset.json \
  --ragendpoint http://localhost:9621

# 或使用短参数
python lightrag/evaluation/eval_rag_quality.py \
  -d lightrag/evaluation/bk100_baseline_dataset.json \
  -r http://localhost:9621
```

### 步骤3: 查看测试结果

测试结果将保存在 `lightrag/evaluation/results/` 目录：
- `results_YYYYMMDD_HHMMSS.json` - 详细JSON结果
- `results_YYYYMMDD_HHMMSS.csv` - CSV格式便于Excel分析

---

## 📊 测试用例说明

### 测试用例分类

| 类别 | 用例编号 | 测试重点 | 难度 |
|------|---------|---------|------|
| **单一事实检索** | Q1, Q4, Q5, Q6, Q8 | 物料属性、材质、重量等 | ⭐ |
| **关系查询** | Q2 | BOM子组件列表 | ⭐⭐ |
| **版本对比** | Q3, Q10 | BOM版本、时间对比 | ⭐⭐ |
| **审批流程** | Q7 | 多角色审批信息 | ⭐⭐⭐ |
| **跨文档聚合** | Q9 | 同一设计师的多个零件 | ⭐⭐⭐ |
| **综合分析** | Q10 | 装配体汇总与版本判断 | ⭐⭐⭐⭐ |

### 详细测试用例

#### Q1: 物料基本信息检索
- **问题**: 表架弧形板(BK100)的物料版本、状态和创建时间是什么？
- **测试点**: 版本管理、状态字段、时间戳提取
- **关键实体**: 物料版本=1, 状态=草稿, 创建时间=2023/10/27 18:45:23

#### Q2: BOM结构查询
- **问题**: 座架组装(BK100).SLDASM装配体包含哪些子组件？请列出PartReversionId。
- **测试点**: 复杂JSON关系解析、UUID列表提取
- **关键实体**: 6个PartReversionId

#### Q3: 版本信息查询
- **问题**: 表与滑架组装(BK100).SLDASM的BOM版本是多少？它是什么时候创建的？
- **测试点**: 版本号、时间戳联合检索
- **关键实体**: BOM版本=2, 创建时间=2023/8/28 13:11:33

#### Q4: 零件属性检索
- **问题**: 网罩外圈(BK100).SLDPRT的材质、重量和设计者分别是什么？
- **测试点**: 多属性联合提取
- **关键实体**: 材质=Q195, 重量=0.220, 设计者=栾恭队

#### Q5: 零件类型判断
- **问题**: 码表立管(BK100).SLDPRT是自制件还是外购件？它的材料规格是什么？
- **测试点**: 分类判断、材料规格提取
- **关键实体**: 类型=自制件, 材料=SPHC1

#### Q6: 规格参数检索
- **问题**: 链盖固定L板(BK100).SLDPRT的材质、重量和零件类型是什么？
- **测试点**: 三要素同时检索
- **关键实体**: 材质=Q235, 重量=0.015, 类型=外购件

#### Q7: 审批流程分析
- **问题**: 连杆板(BK100).SLDDRW图纸的审批流程涉及哪些角色？他们的审批日期是什么时候？
- **测试点**: 表格信息提取、多角色多日期关联
- **关键实体**: 6个角色均为Admin, 日期均为2024-10-24

#### Q8: 库存信息查询
- **问题**: I型六角螺母的物料编码、库存数量和单位是什么？
- **测试点**: MOM系统数据检索、数值精度
- **关键实体**: 编码=SRIDD1-30, 库存=7.5, 单位=件

#### Q9: 跨文档聚合查询
- **问题**: 在BK100项目中，哪些零件是由栾恭队设计的？请列出它们的材质和重量。
- **测试点**: 跨文档关联、设计师维度聚合
- **关键实体**: 3个零件及其材质重量

#### Q10: 综合对比分析
- **问题**: BK100项目中有哪些装配体？它们的BOM版本分别是多少？哪个是最新版本？
- **测试点**: 多文档对比、时间推理、版本判断
- **关键实体**: 2个装配体, 版本1和2, 座架组装更新

---

## 🎯 调优指标

### RAGAS评分标准

| 指标 | 优秀 (≥0.9) | 良好 (0.7-0.9) | 需优化 (<0.7) |
|------|------------|---------------|--------------|
| **Faithfulness** | 答案完全基于检索内容，无幻觉 | 少量无关信息 | 大量幻觉或错误 |
| **Answer Relevance** | 答案完全回答问题 | 部分相关但有冗余 | 答非所问 |
| **Context Recall** | 所有关键信息都被检索到 | 遗漏次要信息 | 遗漏关键信息 |
| **Context Precision** | 检索内容高度相关无噪音 | 少量无关内容 | 大量无关内容 |
| **Overall RAGAS** | ≥0.85 | 0.70-0.85 | <0.70 |

### 调优建议

#### 如果Faithfulness低（出现幻觉）
1. **调整chunk大小**: 减小chunk_size使上下文更精确
2. **优化prompt**: 增强entity extraction prompt的结构化
3. **提高top_k**: 增加检索数量确保覆盖关键信息

```python
# 示例：调整LightRAG配置
rag = LightRAG(
    chunk_token_size=1200,  # 减小chunk
    chunk_overlap_token_size=100,
    top_k=15,  # 增加检索数量
    ...
)
```

#### 如果Context Recall低（遗漏信息）
1. **优化embedding模型**: 使用更强的embedding如text-embedding-3-large
2. **调整相似度阈值**: 降低threshold召回更多候选
3. **启用混合检索**: 结合向量检索和关键词检索

```python
# 示例：使用更强的embedding
from lightrag.llm.openai import openai_embed

embedding_func=EmbeddingFunc(
    embedding_dim=3072,  # text-embedding-3-large维度
    max_token_size=8192,
    func=lambda texts: openai_embed(texts, model="text-embedding-3-large")
)
```

#### 如果Answer Relevance低（答非所问）
1. **优化query改写**: 增强query理解能力
2. **调整LLM温度**: 降低temperature提高准确性
3. **改进system prompt**: 明确回答规范

```python
# 示例：降低LLM温度
llm_model_func=lambda prompts, kwargs: gpt_4o_mini_complete(
    prompts, 
    temperature=0.1,  # 降低随机性
    **kwargs
)
```

#### 如果Context Precision低（噪音多）
1. **启用重排序**: 使用reranker对检索结果重新排序
2. **优化索引策略**: 调整graph和vector索引权重
3. **过滤低质量chunk**: 设置最小chunk长度

```python
# 示例：启用reranker
from lightrag.rerank import bge_rerank

rag = LightRAG(
    rerank_model_func=bge_rerank,
    rerank_top_n=5,  # 重排序后保留top 5
    ...
)
```

---

## 📈 性能基准

### 预期表现

基于BK100数据集的特点，预期RAGAS评分：

| 用例类型 | Faithfulness | Answer Relevance | Context Recall | Context Precision | Overall |
|---------|-------------|------------------|----------------|-------------------|---------|
| 单一事实检索 | 0.95+ | 0.90+ | 0.95+ | 0.90+ | 0.92+ |
| 关系查询 | 0.85+ | 0.85+ | 0.80+ | 0.85+ | 0.84+ |
| 跨文档聚合 | 0.80+ | 0.85+ | 0.75+ | 0.80+ | 0.80+ |
| 综合分析 | 0.75+ | 0.80+ | 0.70+ | 0.75+ | 0.75+ |

**整体目标**: Average RAGAS Score ≥ 0.85

### 记录基线

首次运行后，记录以下指标作为基线：
```
Baseline Date: ___________
Average Faithfulness: _______
Average Answer Relevance: _______
Average Context Recall: _______
Average Context Precision: _______
Average RAGAS Score: _______
Min RAGAS Score: _______
Max RAGAS Score: _______
```

---

## 🔧 高级调优技巧

### 1. 自定义Entity Extraction Prompt

针对PLM/PDM数据优化实体提取：

```python
# 修改 lightrag/prompt.py 中的 GRAPH_FIELD_SEP 和 entity extraction prompt
CUSTOM_ENTITY_PROMPT = """
Given a document about PLM/PDM manufacturing data, extract entities including:
- Part names and IDs (e.g., "表架弧形板(BK100)", "03c84d2d-4828-49e0-8565-6d2a8d7e63b2")
- Material specifications (e.g., "Q195", "SPHC1", "Q235")
- Measurements (e.g., weight "0.220", dimension "3423")
- Dates and timestamps (e.g., "2023/10/27 18:45:23")
- Person names (e.g., "栾恭队", "Admin")
- BOM relationships and hierarchy
- Workflow status and approval information

Return entities in a structured format with types and values.
"""
```

### 2. 领域特定Embedding微调

如果有大量PLM数据，考虑微调embedding模型：

```python
# 使用领域特定的embedding模型
from sentence_transformers import SentenceTransformer

domain_embedding_model = SentenceTransformer('path/to/fine-tuned-model')

def custom_embed(texts):
    return domain_embedding_model.encode(texts).tolist()
```

### 3. 混合检索策略

结合多种检索方式提高recall：

```python
# 启用keyword + vector + graph混合检索
results = await rag.aquery(
    query,
    mode="hybrid",  # 混合模式
    param={
        "vector_weight": 0.4,
        "keyword_weight": 0.3,
        "graph_weight": 0.3
    }
)
```

### 4. Query重写增强

添加query预处理提高理解：

```python
def enhance_query(original_query):
    """添加领域关键词提高检索精度"""
    plm_keywords = ["物料", "BOM", "装配体", "零件", "材质", "重量"]
    
    if any(kw in original_query for kw in plm_keywords):
        return f"BK100项目 {original_query}"
    
    return original_query
```

---

## 📝 测试报告模板

每次调优后填写此报告：

```markdown
# BK100基线测试报告

**测试日期**: YYYY-MM-DD  
**LightRAG版本**: x.x.x  
**配置变更**: [描述本次调优的配置改动]

## 测试结果

| 指标 | 基线 | 当前 | 变化 |
|------|------|------|------|
| Average Faithfulness | ___ | ___ | ___ |
| Average Answer Relevance | ___ | ___ | ___ |
| Average Context Recall | ___ | ___ | ___ |
| Average Context Precision | ___ | ___ | ___ |
| Average RAGAS Score | ___ | ___ | ___ |

## 问题分析

### 表现良好的用例
- Q#: [描述]
- Q#: [描述]

### 需要改进的用例
- Q#: [问题描述] - [可能原因] - [改进方案]

## 下一步计划

1. [优化项1]
2. [优化项2]
3. [优化项3]
```

---

## 🤝 贡献与反馈

如果在测试过程中发现问题或有改进建议：

1. **记录失败用例**: 保存失败的query和response
2. **分析根因**: 是检索问题、提取问题还是生成问题
3. **提交Issue**: 包含测试配置、失败样例、期望输出
4. **分享最佳实践**: 成功的调优经验可以补充到此文档

---

## 📚 相关资源

- [LightRAG官方文档](https://github.com/HKUDS/LightRAG)
- [RAGAS评估框架](https://docs.ragas.io/)
- [RAG系统调优指南](../README_EVALUASTION_RAGAS.md)
- [PLM数据建模最佳实践](../../docs/)

---

**最后更新**: 2026-05-20  
**维护者**: LightRAG Team
