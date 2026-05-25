#!/usr/bin/env python3
"""
LightRAG配置对比测试工具

用于比较不同配置下的RAGAS评分，帮助找到最优配置。

用法:
    python compare_configs.py --configs config1.json config2.json
    
配置示例 (config1.json):
{
  "name": "默认配置",
  "chunk_token_size": 1200,
  "top_k": 10,
  "embedding_model": "text-embedding-3-large"
}
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ConfigComparator:
    """配置对比测试器"""

    def __init__(self, dataset_path: str, api_base_url: str = "http://localhost:9621"):
        self.dataset_path = dataset_path
        self.api_base_url = api_base_url
        self.results = []

    async def test_config(self, config: Dict) -> Dict:
        """测试单个配置"""
        print(f"\n{'='*70}")
        print(f"🧪 测试配置: {config.get('name', '未命名')}")
        print(f"{'='*70}")
        print(f"配置详情:")
        for key, value in config.items():
            if key != "name":
                print(f"  • {key}: {value}")

        # TODO: 这里需要实现实际的重启LightRAG服务并测试的逻辑
        # 由于需要重启服务，这里提供框架代码
        
        print("\n⚠️  注意: 完整实现需要:")
        print("  1. 停止当前LightRAG服务")
        print("  2. 使用新配置启动服务")
        print("  3. 重新索引文档")
        print("  4. 运行RAGAS评估")
        print("  5. 记录结果")
        print("  6. 恢复原始配置")
        
        # 占位符结果
        result = {
            "config_name": config.get("name", "未命名"),
            "config": config,
            "timestamp": datetime.now().isoformat(),
            "status": "not_implemented",
            "metrics": {
                "faithfulness": None,
                "answer_relevance": None,
                "context_recall": None,
                "context_precision": None,
                "ragas_score": None,
            }
        }
        
        return result

    async def run_comparison(self, configs: List[Dict]):
        """运行配置对比"""
        print("=" * 70)
        print("🔬 LightRAG配置对比测试")
        print("=" * 70)
        print(f"数据集: {self.dataset_path}")
        print(f"配置数量: {len(configs)}")
        print("=" * 70)

        for config in configs:
            result = await self.test_config(config)
            self.results.append(result)

        # 生成对比报告
        self.generate_report()

    def generate_report(self):
        """生成对比报告"""
        print("\n" + "=" * 70)
        print("📊 配置对比报告")
        print("=" * 70)

        if not self.results:
            print("⚠️  没有测试结果")
            return

        # 打印表格
        print(f"\n{'配置名称':<20} {'Faith':<8} {'Rel':<8} {'Recall':<8} {'Prec':<8} {'RAGAS':<8}")
        print("-" * 70)

        for result in self.results:
            metrics = result["metrics"]
            name = result["config_name"][:18]
            
            faith = f"{metrics['faithfulness']:.3f}" if metrics['faithfulness'] else "N/A"
            rel = f"{metrics['answer_relevance']:.3f}" if metrics['answer_relevance'] else "N/A"
            recall = f"{metrics['context_recall']:.3f}" if metrics['context_recall'] else "N/A"
            prec = f"{metrics['context_precision']:.3f}" if metrics['context_precision'] else "N/A"
            ragas = f"{metrics['ragas_score']:.3f}" if metrics['ragas_score'] else "N/A"
            
            print(f"{name:<20} {faith:<8} {rel:<8} {recall:<8} {prec:<8} {ragas:<8}")

        # 找出最佳配置
        valid_results = [r for r in self.results if r["metrics"]["ragas_score"] is not None]
        if valid_results:
            best = max(valid_results, key=lambda x: x["metrics"]["ragas_score"])
            print(f"\n🏆 最佳配置: {best['config_name']}")
            print(f"   RAGAS Score: {best['metrics']['ragas_score']:.4f}")

        # 保存报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "dataset": self.dataset_path,
            "results": self.results,
        }

        report_dir = Path(__file__).parent / "comparison_reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 报告已保存: {report_file}")


async def main():
    parser = argparse.ArgumentParser(description="LightRAG配置对比测试")
    parser.add_argument(
        "--configs",
        nargs="+",
        required=True,
        help="配置文件路径列表 (JSON格式)",
    )
    parser.add_argument(
        "--dataset",
        default="lightrag/evaluation/bk100_baseline_dataset.json",
        help="测试数据集路径",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:9621",
        help="LightRAG API URL",
    )

    args = parser.parse_args()

    # 加载配置
    configs = []
    for config_path in args.configs:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                configs.append(config)
        except Exception as e:
            print(f"❌ 加载配置文件失败 {config_path}: {e}")
            sys.exit(1)

    # 运行对比
    comparator = ConfigComparator(
        dataset_path=args.dataset,
        api_base_url=args.api_url,
    )
    
    await comparator.run_comparison(configs)


if __name__ == "__main__":
    asyncio.run(main())
