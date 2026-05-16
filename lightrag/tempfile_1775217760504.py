用户提问："机器学习和人工智能的关系"
    ↓
1️⃣ 向量检索 (Vector Search)
   - 将问题转换为向量
   - 在 entities_vdb 中找相似实体 → ["Machine Learning", "AI"]
   - 在 relationships_vdb 中找相似关系 → ["includes"]
    ↓
2️⃣ 图检索 (Graph Traversal)
   - 从检索到的实体出发，在图中遍历邻居
   - 获取完整的关系路径和属性
   - AI --includes--> ML
    ↓
3️⃣ 结果融合
   - 合并向量检索和图检索的结果
   - 生成最终答案
