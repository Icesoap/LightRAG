#!/usr/bin/env python3
"""
BK100基线测试快速启动脚本

用法:
    python run_bk100_baseline.py
    
功能:
    1. 检查LightRAG服务是否运行
    2. 自动索引BK100文档（如果尚未索引）
    3. 运行RAGAS评估
    4. 生成测试报告摘要
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class BK100BaselineTester:
    """BK100基线测试执行器"""

    def __init__(self, rag_api_url=None):
        self.rag_api_url = rag_api_url or os.getenv(
            "LIGHTRAG_API_URL", "http://localhost:9621"
        )
        self.dataset_path = Path(__file__).parent / "bk100_baseline_dataset.json"
        self.documents_dir = Path(__file__).parent / "bk100_documents"
        self.results_dir = Path(__file__).parent / "results"

    async def check_service_health(self):
        """检查LightRAG服务是否可用"""
        print("🔍 检查LightRAG服务状态...")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.rag_api_url}/health")
                if response.status_code == 200:
                    print("✅ LightRAG服务运行正常")
                    return True
                else:
                    print(f"❌ LightRAG服务返回异常状态码: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到LightRAG服务: {e}")
            print(f"   请确保服务在 {self.rag_api_url} 运行")
            print(f"   启动命令: lightrag-server")
            return False

    async def index_documents(self):
        """索引BK100文档"""
        print("\n📚 开始索引BK100文档...")

        # 检查文档目录
        if not self.documents_dir.exists():
            print(f"❌ 文档目录不存在: {self.documents_dir}")
            return False

        md_files = list(self.documents_dir.glob("*.md"))
        if not md_files:
            print(f"❌ 未找到Markdown文件在: {self.documents_dir}")
            return False

        print(f"   找到 {len(md_files)} 个文档文件")

        # 通过API上传文档
        success_count = 0
        for md_file in sorted(md_files):
            try:
                print(f"   📄 索引: {md_file.name}")
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                async with httpx.AsyncClient(timeout=60.0) as client:
                    # 使用documents API插入
                    response = await client.post(
                        f"{self.rag_api_url}/documents/text",
                        json={
                            "text": content,
                            "description": f"BK100测试文档: {md_file.stem}",
                        },
                        headers={"Content-Type": "application/json"},
                    )

                    if response.status_code in [200, 201]:
                        print(f"      ✅ 成功")
                        success_count += 1
                    else:
                        print(f"      ❌ 失败: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"      ❌ 错误: {e}")

        print(f"\n✅ 索引完成: {success_count}/{len(md_files)} 个文档成功")
        return success_count > 0

    async def run_evaluation(self):
        """运行RAGAS评估"""
        print("\n🧪 运行RAGAS评估...")

        # 检查数据集文件
        if not self.dataset_path.exists():
            print(f"❌ 数据集文件不存在: {self.dataset_path}")
            return False

        # 导入评估器
        try:
            from lightrag.evaluation import RAGEvaluator

            evaluator = RAGEvaluator(
                test_dataset_path=str(self.dataset_path),
                rag_api_url=self.rag_api_url,
            )

            print("   开始评估，这可能需要几分钟...")
            results = await evaluator.run()

            print("\n✅ 评估完成!")
            return True

        except ImportError as e:
            print(f"❌ 无法导入RAGAS评估器: {e}")
            print("   请安装依赖: pip install ragas datasets langfuse")
            return False
        except Exception as e:
            print(f"❌ 评估过程出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 70)
        print("📊 BK100基线测试摘要")
        print("=" * 70)

        # 查找最新的结果文件
        result_files = sorted(self.results_dir.glob("results_*.json"))
        if not result_files:
            print("⚠️  未找到测试结果文件")
            return

        latest_result = result_files[-1]
        print(f"最新结果: {latest_result.name}")

        try:
            with open(latest_result, "r", encoding="utf-8") as f:
                data = json.load(f)

            stats = data.get("benchmark_stats", {})
            avg_metrics = stats.get("average_metrics", {})

            print("\n📈 平均指标:")
            print(f"   Faithfulness:          {avg_metrics.get('faithfulness', 'N/A')}")
            print(
                f"   Answer Relevance:      {avg_metrics.get('answer_relevance', 'N/A')}"
            )
            print(f"   Context Recall:        {avg_metrics.get('context_recall', 'N/A')}")
            print(
                f"   Context Precision:     {avg_metrics.get('context_precision', 'N/A')}"
            )
            print(f"   Overall RAGAS Score:   {avg_metrics.get('ragas_score', 'N/A')}")

            print(f"\n📊 测试统计:")
            print(f"   总测试数:              {stats.get('total_tests', 'N/A')}")
            print(f"   成功:                  {stats.get('successful_tests', 'N/A')}")
            print(f"   失败:                  {stats.get('failed_tests', 'N/A')}")
            print(f"   成功率:                {stats.get('success_rate', 'N/A')}%")
            print(
                f"   RAGAS分数范围:         {stats.get('min_ragas_score', 'N/A')} - {stats.get('max_ragas_score', 'N/A')}"
            )

            # 性能评估
            overall_score = avg_metrics.get("ragas_score", 0)
            print(f"\n🎯 性能评估:")
            if overall_score >= 0.85:
                print("   ✅ 优秀 - 系统表现良好，可用于生产环境")
            elif overall_score >= 0.70:
                print("   ⚠️  良好 - 系统基本可用，建议进一步优化")
            else:
                print("   ❌ 需优化 - 系统需要显著改进")

            print("\n💡 调优建议:")
            if avg_metrics.get("faithfulness", 1) < 0.8:
                print("   • Faithfulness较低: 减小chunk_size或优化entity extraction prompt")
            if avg_metrics.get("context_recall", 1) < 0.8:
                print("   • Context Recall较低: 使用更强的embedding模型或增加top_k")
            if avg_metrics.get("answer_relevance", 1) < 0.8:
                print("   • Answer Relevance较低: 降低LLM temperature或改进system prompt")
            if avg_metrics.get("context_precision", 1) < 0.8:
                print("   • Context Precision较低: 启用reranker或优化检索策略")

        except Exception as e:
            print(f"❌ 读取结果文件失败: {e}")

    async def run_full_test(self):
        """运行完整测试流程"""
        print("=" * 70)
        print("🚀 BK100 LightRAG基线测试")
        print("=" * 70)
        print(f"API端点: {self.rag_api_url}")
        print(f"数据集: {self.dataset_path}")
        print(f"文档目录: {self.documents_dir}")
        print("=" * 70)

        start_time = time.time()

        # 步骤1: 检查服务
        if not await self.check_service_health():
            print("\n❌ 测试中止: 服务不可用")
            return False

        # 步骤2: 索引文档
        if not await self.index_documents():
            print("\n⚠️  文档索引失败，但继续进行评估...")

        # 等待索引完成
        print("\n⏳ 等待索引处理完成...")
        await asyncio.sleep(5)

        # 步骤3: 运行评估
        if not await self.run_evaluation():
            print("\n❌ 评估失败")
            return False

        # 步骤4: 打印摘要
        elapsed = time.time() - start_time
        self.print_summary()

        print(f"\n⏱️  总耗时: {elapsed:.2f} 秒")
        print("\n" + "=" * 70)
        print("✅ 测试完成!")
        print("=" * 70)

        return True


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="BK100基线测试工具")
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="LightRAG API URL (默认: http://localhost:9621)",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="跳过文档索引步骤",
    )

    args = parser.parse_args()

    tester = BK100BaselineTester(rag_api_url=args.api_url)

    try:
        success = await tester.run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
