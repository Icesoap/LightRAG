# LightRAG调优基线测试套件 - 快速入门指南

## 🎯 一分钟快速开始

### 前置要求

- ✅ Python 3.10+
- ✅ LightRAG已安装 (`pip install -e ".[api]"`)
- ✅ RAGAS依赖已安装 (`pip install ragas datasets langfuse httpx`)
- ✅ OpenAI API密钥（或其他LLM提供商）

### 三步启动测试

```bash
# 步骤1: 配置环境变量
cp lightrag/evaluation/.env.bk100_baseline.example .env
# 编辑 .env，填入你的OPENAI_API_KEY

# 步骤2: 启动LightRAG服务
lightrag-server

# 步骤3: 运行测试（新终端窗口）
python lightrag/evaluation/run_bk100_baseline.py
```

**完成！** 🎉 你将看到详细的测试报告和调优建议。

---

## 📦 已创建的测试资源

### 核心文件清单

| 文件 | 用途 | 位置 |
|------|------|------|
| **bk100_baseline_dataset.json** | 10组BK100测试问答 | `lightrag/evaluation/` |
| **bk100_documents/** | 5个测试文档（Markdown） | `lightrag/evaluation/bk100_documents/` |
| **run_bk100_baseline.py** | 一键测试脚本 | `lightrag/evaluation/` |
| **compare_configs.py** | 配置对比工具 | `lightrag/evaluation/` |
| **.env.bk100_baseline.example** | 配置示例 | `lightrag/evaluation/` |
| **BASELINE_TESTING_README.md** | 完整使用手册 | `lightrag/evaluation/` |
| **bk100_documents/README.md** | BK100详细指南 | `lightrag/evaluation/bk100_documents/` |

### 测试文档内容

1. **01_表架弧形板_BK100.md** - PLM物料信息（版本、状态、属性）
2. **02_座架组装_BK100.md** - PLM装配体BOM（6个子组件）
3. **03_表与滑架组装_BK100.md** - PLM装配体BOM（多层级结构）
4. **04_PDM零件文件_BK100.md** - 3个PDM设计文件（材质、重量、设计师）
5. **05_连杆板图纸与螺母物料.md** - PDM工程图审批 + MOM库存数据

---

## 🔍 测试用例预览

### Q1: 物料基本信息
```
问: 表架弧形板(BK100)的物料版本、状态和创建时间是什么？
答: 物料版本是1，版本状态为草稿，创建时间是2023/10/27 18:45:23
```

### Q2: BOM结构查询
```
问: 座架组装(BK100).SLDASM装配体包含哪些子组件？请列出PartReversionId。
答: 包含6个子组件，PartReversionId包括: b1ad5eef-94c5-..., 3d32a934-320e-... 等
```

### Q9: 跨文档聚合
```
问: 在BK100项目中，哪些零件是由栾恭队设计的？请列出它们的材质和重量。
答: 1) 网罩外圈(Q195, 0.220) 2) 码表立管(SPHC1, 0.439) 3) 链盖固定L板(Q235, 0.015)
```

### Q10: 综合分析
```
问: BK100项目中有哪些装配体？它们的BOM版本分别是多少？哪个是最新版本？
答: 两个装配体: 座架组装(版本1, 2026年创建), 表与滑架组装(版本2, 2023年创建)
```

---

## 📊 理解测试结果

### RAGAS指标解读

```
📈 平均指标:
   Faithfulness:          0.9053    ← 答案真实性（无幻觉）
   Answer Relevance:      0.8646    ← 答案相关性（切题程度）
   Context Recall:        1.0000    ← 检索完整性（是否遗漏）
   Context Precision:     1.0000    ← 检索精准度（噪音程度）
   Overall RAGAS Score:   0.9425    ← 综合评分

🎯 性能评估:
   ✅ 优秀 - 系统表现良好，可用于生产环境
```

### 分数评级标准

| 分数范围 | 评级 | 建议 |
|---------|------|------|
| ≥ 0.90 | 优秀 | 可投入生产使用 |
| 0.80-0.90 | 良好 | 基本可用，可继续优化 |
| 0.70-0.80 | 一般 | 需要显著改进 |
| < 0.70 | 较差 | 需要大幅调整配置 |

---

## 🔧 常见调优场景

### 场景1: 提高答案真实性（Faithfulness）

**问题**: 答案包含文档中不存在的信息（幻觉）

**解决**:
```bash
# 方法1: 减小chunk大小（更精确的上下文）
# 在 .env 中添加:
CHUNK_TOKEN_SIZE=800
CHUNK_OVERLAP_TOKEN_SIZE=80

# 方法2: 增加检索数量
TOP_K=15
```

### 场景2: 提高检索完整性（Context Recall）

**问题**: 关键信息未被检索到

**解决**:
```bash
# 使用更强的embedding模型
EMBEDDING_MODEL=text-embedding-3-large

# 降低相似度阈值
COSINE_THRESHOLD=0.15
```

### 场景3: 减少噪音（Context Precision）

**问题**: 检索到大量无关内容

**解决**:
```bash
# 启用重排序
ENABLE_RERANK=true
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_TOP_N=5
```

---

## 🛠️ 高级用法

### 自定义测试数据集

```json
{
  "test_cases": [
    {
      "question": "你的问题",
      "ground_truth": "期望的答案",
      "project": "your_project_name"
    }
  ]
}
```

运行自定义测试：
```bash
python lightrag/evaluation/eval_rag_quality.py \
  --dataset your_dataset.json \
  --ragendpoint http://localhost:9621
```

### 配置对比测试

创建配置文件 `config_v1.json`:
```json
{
  "name": "默认配置",
  "chunk_token_size": 1200,
  "top_k": 10
}
```

创建配置文件 `config_v2.json`:
```json
{
  "name": "优化配置",
  "chunk_token_size": 800,
  "top_k": 15
}
```

运行对比：
```bash
python lightrag/evaluation/compare_configs.py \
  --configs config_v1.json config_v2.json
```

---

## 📖 详细文档索引

| 文档 | 内容 | 阅读时间 |
|------|------|---------|
| [BASELINE_TESTING_README.md](BASELINE_TESTING_README.md) | 完整测试框架说明 | 15分钟 |
| [bk100_documents/README.md](bk100_documents/README.md) | BK100详细使用指南 | 10分钟 |
| [README_EVALUASTION_RAGAS.md](README_EVALUASTION_RAGAS.md) | RAGAS框架原理 | 20分钟 |

---

## 💡 最佳实践

### 1. 建立基线
首次运行时记录初始分数，作为后续优化的基准。

### 2. 单变量测试
每次只调整一个参数，便于定位有效改进。

### 3. 多次验证
每个配置至少运行3次测试，取平均值消除随机性。

### 4. 记录配置
保存所有测试过的配置和对应分数，形成知识库。

### 5. 领域适配
根据实际业务数据特点，定制entity extraction prompt。

---

## ❓ 故障排查

### 问题1: 无法连接到LightRAG服务

```bash
# 检查服务是否运行
curl http://localhost:9621/health

# 如果没有响应，启动服务
lightrag-server

# 或者从源码运行
python -m lightrag.api.lightrag_server
```

### 问题2: RAGAS依赖未安装

```bash
pip install ragas datasets langfuse
```

### 问题3: API密钥错误

检查 `.env` 文件中是否正确设置：
```bash
OPENAI_API_KEY=sk-your-api-key-here
EVAL_LLM_BINDING_API_KEY=sk-your-api-key-here
```

### 问题4: 测试分数异常低

可能原因：
1. 文档未正确索引 → 重新上传文档
2. LLM模型太弱 → 使用更强的模型（≥32B参数）
3. Embedding不合适 → 使用text-embedding-3-large
4. 配置不当 → 参考调优策略部分

---

## 🚀 下一步

1. ✅ 运行基线测试，记录初始分数
2. 📊 分析薄弱环节（哪个指标最低）
3. 🔧 应用对应的调优策略
4. 🔄 重新测试，对比改进效果
5. 📝 记录最佳配置
6. 🎯 达到目标分数后投入生产

---

## 🤝 获取帮助

- 📖 查阅完整文档: [BASELINE_TESTING_README.md](BASELINE_TESTING_README.md)
- 🐛 报告问题: https://github.com/HKUDS/LightRAG/issues
- 💬 社区讨论: GitHub Discussions
- 📧 邮件支持: [项目维护者邮箱]

---

**祝你测试顺利！** 🎉

如有任何问题，欢迎随时查阅文档或提交Issue。
