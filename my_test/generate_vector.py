import hashlib
import numpy as np


def generate_bk100_vector(dim=1024, content=None):
    # 用零件名生成唯一哈希
    # name = "齿盘组(BK100)"
    name = content
    # hash_obj = hashlib.sha256(name.encode())
    # seed = int(hash_obj.hexdigest(), 16) % (10 ** 8)
    #
    # # 固定随机种子 → 每次生成相同向量
    # np.random.seed(seed)
    #
    # # 生成标准化 1024 维向量（L2归一化）
    # vec = np.random.randn(dim).astype(np.float32)
    # vec = vec / np.linalg.norm(vec)  # 归一化，适合向量搜索
    # return vec.round(4).tolist()

 # 用零件名称做种子，保证同一型号向量永久不变
    h = hashlib.sha256(name.encode("utf-8"))
    seed = int(h.hexdigest(), 16) % 99999999
    np.random.seed(seed)

    # 生成随机向量 + L2归一化（余弦相似度必备）
    vec = np.random.rand(dim).astype(np.float32)
    vec = vec / np.linalg.norm(vec)
    # 保留4位小数，方便粘贴
    return np.round(vec, 4).tolist()


if __name__ == '__main__':
    bk100_vec=generate_bk100_vector(1024, "齿盘组(BK100)")
    # 生成
    # bk100_vec = generate_bk100_vector(1024)
    print(bk100_vec)
