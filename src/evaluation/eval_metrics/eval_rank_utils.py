import math
from itertools import combinations

def spearman(expected, test):
    """计算斯皮尔曼等级相关系数"""
    if set(expected) != set(test) or len(expected) != len(test):
        raise ValueError("两个排序必须包含相同元素且长度一致")
    
    n = len(expected)
    if n < 2:
        return 1.0
    
    # 创建元素到排名的映射
    expected_rank = {item: i+1 for i, item in enumerate(expected)}
    test_rank = {item: i+1 for i, item in enumerate(test)}
    
    # 计算排名差的平方和
    squared_diff = sum((expected_rank[item] - test_rank[item])**2 for item in expected)
    
    return 1 - (6 * squared_diff) / (n * (n**2 - 1))

def kendall(expected, test):
    """计算肯德尔tau系数"""
    if set(expected) != set(test) or len(expected) != len(test):
        raise ValueError("两个排序必须包含相同元素且长度一致")
    
    n = len(expected)
    if n < 2:
        return 1.0
    
    expected_rank = {item: i for i, item in enumerate(expected)}  # 使用0基索引更方便比较
    concordant = 0
    discordant = 0
    
    # 检查所有元素对的相对顺序
    for (a, b) in combinations(test, 2):
        # 在测试排序中a在b前面
        if expected_rank[a] < expected_rank[b]:
            concordant += 1
        else:
            discordant += 1
    
    total_pairs = n * (n - 1) // 2
    return (concordant - discordant) / total_pairs

def mean_deviation(expected, test):
    """计算平均排名偏差"""
    if set(expected) != set(test) or len(expected) != len(test):
        raise ValueError("两个排序必须包含相同元素且长度一致")
    
    n = len(expected)
    if n == 0:
        return 0.0
    
    expected_rank = {item: i+1 for i, item in enumerate(expected)}
    test_rank = {item: i+1 for i, item in enumerate(test)}
    
    total_diff = sum(abs(expected_rank[item] - test_rank[item]) for item in expected)
    return total_diff / n

def get_ranking_score(expected, ranking):
    """获取单个排序的评分"""
    # 计算各项指标
    s = spearman(expected, ranking)
    k = kendall(expected, ranking)
    m = mean_deviation(expected, ranking)
    
    return {
        "spearman": s,
        "kendall": k,
        "mean_deviation": m
    }

def compare_rankings(expected, ranking1, ranking2):
    """比较两个排序与期望排序的相似度"""
    # 计算各项指标
    s1, s2 = spearman(expected, ranking1), spearman(expected, ranking2)
    k1, k2 = kendall(expected, ranking1), kendall(expected, ranking2)
    m1, m2 = mean_deviation(expected, ranking1), mean_deviation(expected, ranking2)
    
    # 确定每个指标下更优的排序
    better_spearman = "ranking1" if s1 > s2 else "ranking2" if s2 > s1 else "equal"
    better_kendall = "ranking1" if k1 > k2 else "ranking2" if k2 > k1 else "equal"
    better_deviation = "ranking1" if m1 < m2 else "ranking2" if m2 < m1 else "equal"
    
    return {
        "spearman": {"ranking1": s1, "ranking2": s2, "better": better_spearman},
        "kendall": {"ranking1": k1, "ranking2": k2, "better": better_kendall},
        "mean_deviation": {"ranking1": m1, "ranking2": m2, "better": better_deviation}
    }

# 示例用法
if __name__ == "__main__":
    # 直接使用数组作为输入
    # expected = ["A", "B", "C", "D", "E"]
    # ranking1 = ["A", "C", "B", "D", "E"]
    # ranking2 = ["B", "A", "C", "E", "D"]

    expected = [1, 2, 3, 4, 5]
    ranking1 = [1, 3, 2, 4, 5]
    ranking2 = [2, 1, 3, 5, 4]
    
    print("期望排序:", expected)
    print("排序1:", ranking1)
    print("排序2:", ranking2)
    
    # 计算单个指标
    print(f"\n斯皮尔曼系数: {spearman(expected, ranking1):.4f} (排序1) vs {spearman(expected, ranking2):.4f} (排序2)")
    print(f"肯德尔系数: {kendall(expected, ranking1):.4f} (排序1) vs {kendall(expected, ranking2):.4f} (排序2)")
    print(f"平均偏差: {mean_deviation(expected, ranking1):.4f} (排序1) vs {mean_deviation(expected, ranking2):.4f} (排序2)")
    
    # 综合比较
    results = compare_rankings(expected, ranking1, ranking2)
    print("\n综合比较结果:")
    for metric, data in results.items():
        print(f"{metric}: 排序1={data['ranking1']:.4f}, 排序2={data['ranking2']:.4f}, 更优={data['better']}")
    