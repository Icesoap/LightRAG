import json
import pandas as pd
from datetime import datetime


def compare_evaluations(before_file, after_file):
    """对比调优前后的评估结果"""

    with open(before_file, 'r', encoding='utf-8') as f:
        before_data = json.load(f)

    with open(after_file, 'r', encoding='utf-8') as f:
        after_data = json.load(f)

    # 提取基准统计
    before_stats = before_data.get('benchmark_stats', {})
    after_stats = after_data.get('benchmark_stats', {})

    print("=" * 80)
    print("📊 LightRAG 调优效果对比报告")
    print("=" * 80)
    print(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试用例数: {before_stats['total_tests']}")
    print()

    # 对比各项指标
    metrics = ['faithfulness', 'answer_relevance', 'context_recall',
               'context_precision']

    print(f"{'指标':<25} {'调优前':>10} {'调优后':>10} {'变化':>10} {'改善':>8}")
    print("-" * 80)

    for metric in metrics:
        before_val = before_stats['average_metrics'].get(metric, 0)
        after_val = after_stats['average_metrics'].get(metric, 0)
        change = after_val - before_val
        improvement = "✅" if change > 0 else "❌" if change < 0 else "➖"

        print(f"{metric:<25} {before_val:>10.4f} {after_val:>10.4f} "
              f"{change:>+10.4f} {improvement:>8}")

    # 综合评分对比
    before_ragas = before_stats['average_metrics'].get('ragas_score', 0)
    after_ragas = after_stats['average_metrics'].get('ragas_score', 0)
    ragas_change = after_ragas - before_ragas

    print("-" * 80)
    print(f"{'RAGAS 综合评分':<25} {before_ragas:>10.4f} {after_ragas:>10.4f} "
          f"{ragas_change:>+10.4f} {'✅' if ragas_change > 0 else '❌':>8}")
    print()

    # 成功率对比
    before_success = before_stats['success_rate']
    after_success = after_stats['success_rate']
    print(f"成功率: {before_success}% → {after_success}% "
          f"({'+' if after_success > before_success else ''}"
          f"{after_success - before_success:.2f}%)")

    # 详细问题级对比
    print("\n" + "=" * 80)
    print("📋 各测试问题详细对比")
    print("=" * 80)

    before_results = {r['test_number']: r for r in before_data['results']}
    after_results = {r['test_number']: r for r in after_data['results']}

    for test_num in sorted(before_results.keys()):
        before_r = before_results[test_num]
        after_r = after_results.get(test_num)

        if not after_r:
            continue

        before_score = before_r.get('ragas_score', 0)
        after_score = after_r.get('ragas_score', 0)
        question = before_r['question'][:50] + "..." if len(before_r['question']) > 50 else before_r['question']

        status = "✅" if after_score > before_score else "❌" if after_score < before_score else "➖"

        print(f"\n问题 #{test_num}: {question}")
        print(f"  调优前: {before_score:.4f} | 调优后: {after_score:.4f} | "
              f"变化: {after_score - before_score:+.4f} {status}")

    return before_stats, after_stats


if __name__ == "__main__":
    # 替换为实际的文件路径
    compare_evaluations(
        "lightrag/evaluation/results/results_before_tuning.json",
        "lightrag/evaluation/results/results_after_tuning.json"
    )
