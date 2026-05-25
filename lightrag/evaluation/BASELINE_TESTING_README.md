# LightRAG调优基线测试套件

## 📋 概述

本目录提供完整的LightRAG调优基线测试框架，包含：
- **BK100工业数据测试集**: 基于真实PLM/PDM/MOM数据的10组问答测试
- **自动化测试工具**: 一键运行评估并生成报告
- **配置对比工具**: 比较不同参数配置的优劣
- **详细文档**: 调优指南和最佳实践

---

## 🎯 测试目标

### 主要指标
使用**RAGAS框架**评估以下核心指标：

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **Faithfulness** | 答案是否基于检索内容（无幻觉） | ≥ 0.85 |
| **Answer Relevance** | 答案是否切题 | ≥ 0.85 |
| **Context Recall** | 是否检索到所有相关信息 | ≥ 0.80 |
| **Context Precision** | 检索内容是否精准无噪音 | ≥ 0.80 |
| **Overall RAGAS** | 综合评分 | ≥ 0.85 |

### 测试场景覆盖

✅ **单一事实检索**: 物料属性、规格参数  
✅ **关系查询**: BOM结构、装配关系  
✅ **版本对比**: 多版本文档对比  
✅ **审批流程**: 工作流信息提取  
✅ **跨文档聚合**: 设计师关联查询  
✅ **综合分析**: 多维度数据整合  

---

## 📁 文件结构

```
lightrag/evaluation/
├── bk100_baseline_dataset.json          # BK100测试数据集（10组问答）
├── bk100_documents/                     # BK100测试文档
│   ├── 01_表架弧形板_BK100.md
│   ├── 02_座架组装_BK100.md
│   ├── 03_表与滑架组装_BK100.md
│   ├── 04_PDM零件文件_BK100.md
│   ├── 05_连杆板图纸与螺母物料.md
│   └── README.md                        # BK100详细使用说明
├── run_bk100_baseline.py                # 一键测试脚本
├── compare_configs.py                   # 配置对比工具
├── .env.bk100_baseline.example          # 配置示例
├── eval_rag_quality.py                  # RAGAS评估引擎（现有）
├── sample_dataset.json                  # 通用测试集（现有）
├── sample_documents/                    # 通用测试文档（现有）
└── README_EVALUASTION_RAGAS.md         # RAGAS框架说明（现有）
```

---

## 🚀 快速开始

### 方法一：一键测试（推荐）

```bash
# 1. 安装依赖
pip install ragas datasets langfuse httpx

# 2. 配置环境变量
cp lightrag/evaluation/.env.bk100_baseline.example .env
# 编辑 .env 文件，填入API密钥

# 3. 启动LightRAG服务
lightrag-server

# 4. 运行基线测试（新终端）
python lightrag/evaluation/run_bk100_baseline.py
```

### 方法二：手动测试

```bash
# 1. 索引文档
# 通过Web UI或API上传 bk100_documents/*.md 文件

# 2. 运行评估
python lightrag/evaluation/eval_rag_quality.py \
  --dataset lightrag/evaluation/bk100_baseline_dataset.json \
  --ragendpoint http://localhost:9621

# 3. 查看结果
ls -lh lightrag/evaluation/results/
```

### 方法三：配置对比测试

```bash
# 创建两个配置文件
cat > config_v1.json << EOF
{
  "name": "默认配置",
  "chunk_token_size": 1200,
  "top_k": 10
}
EOF

cat > config_v2.json << EOF
{
  "name": "优化配置",
  "chunk_token_size": 800,
  "top_k": 15
}
EOF

# 运行对比
python lightrag/evaluation/compare_configs.py \
  --configs config_v1.json config_v2.json \
  --dataset lightrag/evaluation/bk100_baseline_dataset.json
```

---

## 📊 测试用例详解

### BK100数据集特点

| 特性 | 说明 |
|------|------|
| **数据来源** | PLM (产品生命周期管理)、PDM (产品数据管理)、MOM (制造运营管理) |
| **数据类型** | 物料信息、BOM结构、CAD文件属性、审批流程、库存数据 |
| **语言** | 中文为主，包含英文技术术语 |
| **复杂度** | 涵盖简单检索到复杂推理的多个层次 |

### 10组测试问题

1. **Q1**: 表架弧形板的物料版本、状态和创建时间
   - 类型: 单一事实检索
   - 难度: ⭐

2. **Q2**: 座架组装的子组件PartReversionId列表
   - 类型: 关系查询
   - 难度: ⭐⭐

3. **Q3**: 表与滑架组装的BOM版本和创建时间
   - 类型: 版本查询
   - 难度: ⭐⭐

4. **Q4**: 网罩外圈的材质、重量和设计者
   - 类型: 多属性检索
   - 难度: ⭐

5. **Q5**: 码表立管的零件类型和材料规格
   - 类型: 分类判断
   - 难度: ⭐⭐

6. **Q6**: 链盖固定L板的材质、重量和零件类型
   - 类型: 三要素检索
   - 难度: ⭐⭐

7. **Q7**: 连杆板图纸的审批角色和日期
   - 类型: 表格信息提取
   - 难度: ⭐⭐⭐

8. **Q8**: I型六角螺母的编码、库存和单位
   - 类型: MOM系统数据
   - 难度: ⭐

9. **Q9**: 栾恭队设计的所有零件及其属性
   - 类型: 跨文档聚合
   - 难度: ⭐⭐⭐

10. **Q10**: BK100项目装配体汇总与版本对比
    - 类型: 综合分析
    - 难度: ⭐⭐⭐⭐

---

## 🔧 调优策略

### 常见问题与解决方案

#### 问题1: Faithfulness低（出现幻觉）

**症状**: 答案包含文档中不存在的信息

**解决**:
```python
# 方案A: 减小chunk大小
CHUNK_TOKEN_SIZE=800
CHUNK_OVERLAP_TOKEN_SIZE=80

# 方案B: 优化entity extraction prompt
# 修改 lightrag/prompt.py 中的提取提示词

# 方案C: 增加检索数量
TOP_K=15
```

#### 问题2: Context Recall低（遗漏信息）

**症状**: 关键信息未被检索到

**解决**:
```python
# 方案A: 使用更强的embedding模型
EMBEDDING_MODEL=text-embedding-3-large  # 3072维

# 方案B: 降低相似度阈值
COSINE_THRESHOLD=0.15

# 方案C: 启用混合检索
# 在query时指定 mode="hybrid"
```

#### 问题3: Answer Relevance低（答非所问）

**症状**: 答案不直接回答问题

**解决**:
```python
# 方案A: 降低LLM温度
temperature=0.1

# 方案B: 改进system prompt
# 明确要求"直接回答问题，不要添加无关信息"

# 方案C: 启用query重写
# 使用更强的query理解模型
```

#### 问题4: Context Precision低（噪音多）

**症状**: 检索到大量无关内容

**解决**:
```python
# 方案A: 启用reranker
ENABLE_RERANK=true
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_TOP_N=5

# 方案B: 优化索引策略
# 调整graph和vector权重

# 方案C: 过滤短chunk
MIN_CHUNK_LENGTH=50
```

### 调优流程建议

```
1. 运行基线测试 → 记录初始分数
         ↓
2. 分析薄弱环节 → 确定优先优化指标
         ↓
3. 调整单个参数 → 每次只改一个变量
         ↓
4. 重新测试 → 对比分数变化
         ↓
5. 重复步骤2-4 → 逐步优化
         ↓
6. 记录最佳配置 → 形成最佳实践
```

---

## 📈 性能基准

### 预期表现（基于OpenAI GPT-4o-mini + text-embedding-3-large）

| 测试类型 | Faithfulness | Relevance | Recall | Precision | Overall |
|---------|-------------|-----------|--------|-----------|---------|
| 单一事实 | 0.95+ | 0.90+ | 0.95+ | 0.90+ | 0.92+ |
| 关系查询 | 0.85+ | 0.85+ | 0.80+ | 0.85+ | 0.84+ |
| 跨文档聚合 | 0.80+ | 0.85+ | 0.75+ | 0.80+ | 0.80+ |
| 综合分析 | 0.75+ | 0.80+ | 0.70+ | 0.75+ | 0.75+ |
| **平均** | **0.84+** | **0.85+** | **0.80+** | **0.83+** | **0.83+** |

**目标**: Average RAGAS Score ≥ 0.85

---

## 🛠️ 高级工具

### 1. 自动化测试脚本 (run_bk100_baseline.py)

功能：
- ✅ 自动检查服务状态
- ✅ 批量索引文档
- ✅ 运行RAGAS评估
- ✅ 生成测试报告摘要
- ✅ 提供调优建议

用法：
```bash
python lightrag/evaluation/run_bk100_baseline.py \
  --api-url http://localhost:9621
```

### 2. 配置对比工具 (compare_configs.py)

功能：
- ✅ 批量测试多个配置
- ✅ 自动生成对比表格
- ✅ 找出最佳配置
- ✅ 保存对比报告

用法：
```bash
python lightrag/evaluation/compare_configs.py \
  --configs config1.json config2.json config3.json
```

### 3. RAGAS评估引擎 (eval_rag_quality.py)

功能：
- ✅ 标准RAGAS指标计算
- ✅ 支持自定义数据集
- ✅ 导出JSON/CSV结果
- ✅ 详细的结果表格

用法：
```bash
python lightrag/evaluation/eval_rag_quality.py \
  -d bk100_baseline_dataset.json \
  -r http://localhost:9621
```

---

## 📝 测试报告模板

每次测试后填写：

```markdown
# BK100基线测试报告

**测试日期**: 2026-05-20  
**LightRAG版本**: x.x.x  
**LLM模型**: gpt-4o-mini  
**Embedding模型**: text-embedding-3-large  
**配置变更**: [描述本次测试的配置]

## 测试结果

| 指标 | 分数 | 评级 |
|------|------|------|
| Average Faithfulness | 0.XX | 优秀/良好/需优化 |
| Average Answer Relevance | 0.XX | 优秀/良好/需优化 |
| Average Context Recall | 0.XX | 优秀/良好/需优化 |
| Average Context Precision | 0.XX | 优秀/良好/需优化 |
| **Average RAGAS Score** | **0.XX** | **优秀/良好/需优化** |

## 问题分析

### 表现良好的用例
- Q1: [描述]
- Q4: [描述]

### 需要改进的用例
- Q9: 跨文档聚合召回率低 - 原因: embedding未能捕捉设计师关联 - 改进: 增强实体链接

## 下一步计划

1. [ ] 优化entity extraction prompt
2. [ ] 尝试不同的chunk大小
3. [ ] 启用reranker测试
```

---

## 🤝 贡献指南

### 添加新的测试数据集

1. 创建测试文档目录: `new_project_documents/`
2. 编写Markdown格式文档
3. 创建测试问答集: `new_project_dataset.json`
4. 更新本README

### 分享最佳实践

如果您发现了有效的调优技巧：
1. 记录配置参数和测试结果
2. 说明适用场景和数据特点
3. 提交Pull Request或Issue

---

## 📚 相关资源

- [RAGAS官方文档](https://docs.ragas.io/)
- [LightRAG主文档](../../README.md)
- [RAGAS评估详细说明](README_EVALUASTION_RAGAS.md)
- [BK100详细使用指南](bk100_documents/README.md)

---

## ❓ 常见问题

### Q: 为什么我的RAGAS分数很低？

A: 可能原因：
1. LLM模型太弱（建议使用≥32B参数模型）
2. Embedding模型不合适（推荐text-embedding-3-large）
3. Chunk大小不合理（尝试800-1200 tokens）
4. 检索数量不足（尝试top_k=10-15）

### Q: 如何加速测试过程？

A: 
1. 使用更快的LLM（如gpt-4o-mini而非gpt-4）
2. 减少测试用例数量进行快速验证
3. 启用LLM缓存避免重复调用
4. 使用本地部署的LLM（如Ollama）

### Q: 可以自定义评估指标吗？

A: 可以。修改 `eval_rag_quality.py` 中的metrics定义，添加自定义的RAGAS指标。

### Q: 如何在CI/CD中集成测试？

A: 使用 `run_bk100_baseline.py` 脚本，设置返回码检查：
```bash
python run_bk100_baseline.py && echo "测试通过" || echo "测试失败"
```

---

## 📞 支持与反馈

遇到问题或有改进建议？
- 📧 提交Issue: https://github.com/HKUDS/LightRAG/issues
- 💬 参与讨论: GitHub Discussions
- 📖 查阅文档: 本项目README和docs目录

---

**维护者**: LightRAG Team  
**最后更新**: 2026-05-20  
**版本**: 1.0.0
