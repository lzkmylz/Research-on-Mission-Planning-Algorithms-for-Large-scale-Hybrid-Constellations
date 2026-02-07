"""
结果可视化工具

生成算法性能对比图表（柱状图、雷达图、收敛曲线）。
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

# 设置中文字体（根据系统情况可能需要调整）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """结果可视化工具"""
    
    def __init__(self, output_dir: str = "benchmark_dataset/evaluation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_comparison_bar_chart(
        self,
        df: pd.DataFrame,
        metric: str,
        title: str,
        filename: str
    ):
        """绘制对比柱状图"""
        if metric not in df.columns:
            return
            
        plt.figure(figsize=(10, 6))
        
        # 绘制
        bars = plt.bar(df.index, df[metric], color='skyblue', edgecolor='black', alpha=0.7)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}',
                     ha='center', va='bottom')
        
        plt.title(title)
        plt.xlabel('Algorithm')
        plt.ylabel(metric)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"✓ 图表已保存: {output_path}")
    
    def plot_radar_chart(
        self,
        df: pd.DataFrame,
        title: str,
        filename: str
    ):
        """绘制雷达图 (归一化数据)"""
        # 选择需要在雷达图中展示的指标
        metrics = [
            "Completion Rate", 
            "Total Value", 
            "Targets Covered", 
            "Avg Storage Usage", 
            "Avg Energy Usage"
        ]
        
        # 确保指标存在
        available_metrics = [m for m in metrics if m in df.columns]
        if not available_metrics:
            return
            
        # 数据归一化 (Min-Max Scaling)
        df_norm = df[available_metrics].copy()
        for col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            if max_val > min_val:
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 1.0  # 如果都一样，设为1
        
        # 准备绘图
        labels = available_metrics
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # 闭合
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # 绘制每个算法的雷达图
        colors = ['b', 'r', 'g', 'c', 'm', 'y']
        for i, (idx, row) in enumerate(df_norm.iterrows()):
            values = row.tolist()
            values += values[:1]  # 闭合
            
            color = colors[i % len(colors)]
            ax.plot(angles, values, color=color, linewidth=2, label=idx)
            ax.fill(angles, values, color=color, alpha=0.1)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.title(title, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"✓ 雷达图已保存: {output_path}")
    
    def visualize_all(
        self,
        df: pd.DataFrame,
        scenario_name: str
    ):
        """生成该场景的所有可视化图表"""
        if df.empty:
            return
            
        print(f"\n[正在生成 {scenario_name} 的可视化图表...]")
        
        # 1. 任务完成率对比
        self.plot_comparison_bar_chart(
            df, 
            "Completion Rate", 
            f"Task Completion Rate Comparison - {scenario_name}",
            f"{scenario_name}_completion_rate.png"
        )
        
        # 2. 总收益对比
        self.plot_comparison_bar_chart(
            df,
            "Total Value",
            f"Total Value Comparison - {scenario_name}",
            f"{scenario_name}_total_value.png"
        )
        
        # 3. 运行时间对比
        self.plot_comparison_bar_chart(
            df,
            "Runtime (s)",
            f"Runtime Comparison - {scenario_name}",
            f"{scenario_name}_runtime.png"
        )
        
        # 4. 综合雷达图
        self.plot_radar_chart(
            df,
            f"Performance Radar - {scenario_name}",
            f"{scenario_name}_radar.png"
        )


def main():
    """测试可视化工具"""
    print("=" * 60)
    print("可视化工具测试")
    print("=" * 60)
    
    # 构造模拟数据
    data = {
        "Algorithm": ["GA", "Tabu", "SA", "ACO"],
        "Completion Rate": [0.85, 0.78, 0.82, 0.88],
        "Total Value": [12000, 11000, 11500, 12500],
        "Runtime (s)": [120, 45, 80, 150],
        "Targets Covered": [850, 780, 820, 880],
        "Completion Time (h)": [18.5, 20.0, 19.2, 18.0],
        "Avg Storage Usage": [0.6, 0.5, 0.55, 0.65],
        "Avg Energy Usage": [0.7, 0.6, 0.65, 0.75]
    }
    df = pd.DataFrame(data).set_index("Algorithm")
    
    visualizer = Visualizer()
    visualizer.visualize_all(df, "test_scenario")
    
    print("\n" + "=" * 60)
    print("✓ 测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
