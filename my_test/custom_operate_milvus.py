import os
import re
import json
from pymilvus import MilvusClient


def load_env_file(env_path: str = ".env") -> dict:
    """
    从.env文件加载环境变量

    Args:
        env_path: .env文件路径

    Returns:
        dict: 环境变量字典
    """
    env_vars = {}

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释行和空行
                if not line or line.startswith("#"):
                    continue

                # 解析 key=value 格式
                if "=" in line:
                    key, value = line.split("=", 1)
                    # 去除引号
                    value = value.strip("'\"")
                    env_vars[key] = value
    except FileNotFoundError:
        print(f"警告：未找到.env文件: {env_path}")

    return env_vars


def create_milvus_client():
    """
    创建Milvus客户端连接

    Returns:
        MilvusClient: 客户端实例，如果连接失败返回None
    """
    # 加载.env文件
    env_vars = load_env_file("../.env")

    # 从环境变量获取Milvus连接信息
    milvus_uri = os.environ.get("MILVUS_URI") or env_vars.get("MILVUS_URI")
    milvus_db_name = os.environ.get("MILVUS_DB_NAME") or env_vars.get("MILVUS_DB_NAME")

    print(f"Milvus连接信息:")
    print(f"  URI: {milvus_uri}")
    print(f"  DB_NAME: {milvus_db_name}")

    # 创建Milvus客户端
    client_kwargs = {"uri": milvus_uri}
    if milvus_db_name:
        client_kwargs["db_name"] = milvus_db_name

    try:
        client = MilvusClient(**client_kwargs)
        print("Milvus连接成功")
        return client
    except Exception as e:
        print(f"连接Milvus失败: {e}")
        return None


def find_entities_with_pipe_in_name(client):
    """
    查找Milvus数据库中entity_name包含|的实体，
    提取|前面的值，并作为条件查询entity_name

    Args:
        client: Milvus客户端实例

    Returns:
        dict: 包含原始实体和匹配结果的字典
    """
    if not client:
        print("Milvus客户端未连接")
        return {}

    try:
        # 获取所有集合
        collections = client.list_collections()
        print(f"\nMilvus中的集合: {collections}")

        # 查找包含entities的集合
        entity_collections = [col for col in collections if "entities" in col.lower()]

        if not entity_collections:
            print("\n未找到包含'entities'的集合")
            return {}

        print(f"\n找到的实体集合: {entity_collections}")

        # 存储结果
        results = {}

        # 遍历所有实体集合
        for collection_name in entity_collections:
            try:
                # 查询所有entity_name包含|的实体
                filter_expr = "entity_name LIKE '%|%'"

                pipe_entities = client.query(
                    collection_name=collection_name,
                    filter=filter_expr,
                    output_fields=["id", "entity_name", "file_path", "created_at"]
                )

                for entity in pipe_entities:
                    entity_name = entity.get("entity_name", "")
                    if "|" in entity_name:
                        # 如果file_path不为空，则排除掉这个实体
                        file_path = entity.get("file_path", "")
                        if file_path and str(file_path).strip():
                            continue
                        # 提取|前面的值
                        prefix = entity_name.split("|")[0].strip()

                        # 使用前缀作为条件查询entity_name
                        if prefix and prefix.isdigit():
                            # 查询所有entity_name等于该前缀的实体
                            prefix_filter = f"entity_name == '{prefix}'"
                            matched_entities = client.query(
                                collection_name=collection_name,
                                filter=prefix_filter,
                                output_fields=["id", "entity_name", "file_path", "created_at"]
                            )

                            # 如果matched_entities不为空，排除原始实体
                            if matched_entities:
                                # 过滤掉原始实体
                                filtered_matched = [
                                    e for e in matched_entities
                                    if e.get("entity_name") != entity_name
                                ]

                                if filtered_matched:
                                    results[entity_name] = {
                                        "prefix": prefix,
                                        "original_entity": entity,
                                        "matched_entities": filtered_matched,
                                        "collection_name": collection_name
                                    }

            except Exception as e:
                print(f"查询集合 {collection_name} 时出错: {e}")

        return results

    except Exception as e:
        print(f"执行查询时出错: {e}")
        return {}


def delete_entities_by_prefix(pipe_results, client):
    """
    使用pipe_results中的prefix作为条件，删除entity_name=prefix的实体

    Args:
        pipe_results: find_entities_with_pipe_in_name返回的结果字典
        client: Milvus客户端实例
    """
    if not client:
        print("Milvus客户端未连接")
        return

    if not pipe_results:
        print("没有需要删除的数据")
        return

    print("\n" + "=" * 60)
    print("准备删除以下实体:")
    print("=" * 60)

    # 收集所有需要删除的实体ID
    entities_to_delete = []
    for original_name, data in pipe_results.items():
        prefix = data["prefix"]
        collection_name = data["collection_name"]

        # 查询entity_name等于prefix的实体
        filter_expr = f"entity_name == '{prefix}'"
        try:
            entities = client.query(
                collection_name=collection_name,
                filter=filter_expr,
                output_fields=["id", "entity_name"]
            )

            for entity in entities:
                entities_to_delete.append({
                    "collection_name": collection_name,
                    "id": entity["id"],
                    "entity_name": entity["entity_name"]
                })
                print(f"  - {entity['entity_name']} (ID: {entity['id']}, 集合: {collection_name})")
        except Exception as e:
            print(f" 查询要删除的实体时出错: {e}")

    if not entities_to_delete:
        print("没有找到需要删除的实体")
        return

    # 确认删除
    confirm = input(f"\n确认删除以上 {len(entities_to_delete)} 个实体吗? (y/N): ")
    if confirm.lower() != 'y':
        print("取消删除操作")
        return

    # 执行删除
    deleted_count = 0
    for item in entities_to_delete:
        try:
            # 使用filter条件删除
            filter_expr = f"id == '{item['id']}'"
            result = client.delete(
                collection_name=item["collection_name"],
                filter=filter_expr
            )

            if result and result.get("delete_count", 0) > 0:
                print(f"已删除: {item['entity_name']} (ID: {item['id']})")
                deleted_count += 1
            else:
                print(f"删除失败: {item['entity_name']} (ID: {item['id']})")
        except Exception as e:
            print(f"删除 {item['entity_name']} 时出错: {e}")

    print(f"\n删除完成，共删除 {deleted_count} 个实体")


if __name__ == "__main__":
    # 创建Milvus客户端
    print("=" * 60)
    print("连接Milvus数据库")
    print("=" * 60)
    client = create_milvus_client()

    if not client:
        print("无法连接Milvus，程序退出")
        exit(1)

    try:
        # 查找entity_name包含|的实体
        print("\n" + "=" * 60)
        print("查找entity_name包含|的实体")
        print("=" * 60)

        pipe_results = find_entities_with_pipe_in_name(client)

        if pipe_results:
            # 输出JSON格式结果
            print("\n" + "=" * 60)
            print("查询结果(JSON格式):")
            print("=" * 60)
            json_output = json.dumps(pipe_results, ensure_ascii=False, indent=2)
            print(json_output)

            # 删除entity_name=prefix的实体
            delete_entities_by_prefix(pipe_results, client)
        else:
            print("\n没有找到entity_name包含|的实体")

    finally:
        # 确保客户端关闭
        if client:
            client.close()
            print("\nMilvus连接已关闭")