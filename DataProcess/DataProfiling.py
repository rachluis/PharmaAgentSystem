import pandas as pd
import io
import os
import numpy as np
from collections import defaultdict

# ================= 配置区域 =================
# 请将此处修改为你实际的CSV文件名
FILE_PATH = r"E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv"
OUTPUT_FILE = 'data_report.txt'
# 设置分块大小，每次读取10万行，用于减少内存占用
CHUNK_SIZE = 100000 
# ======================================================

def analyze_data_in_chunks(file_path):
    print(f"正在使用分块读取模式分析文件: {file_path}，CHUNK_SIZE={CHUNK_SIZE}...")
    
    # 尝试第一次读取获取列名和数据类型（只读头部）
    try:
        df_head = pd.read_csv(file_path, nrows=0, low_memory=False)
        columns = df_head.columns
        total_rows = 0
        stats = defaultdict(lambda: {'count': 0, 'unique': set(), 'dtype': 'unknown'})
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}，请检查路径。")
        return
    except Exception as e:
        print(f"错误: 无法读取文件头部以确定列名和类型。可能编码或分隔符有问题。详细错误: {e}")
        return

    # 迭代读取数据块并累积统计信息
    try:
        reader = pd.read_csv(file_path, chunksize=CHUNK_SIZE, low_memory=False)
        
        for i, chunk in enumerate(reader):
            total_rows += len(chunk)
            print(f"-> 正在处理第 {i+1} 个数据块 (已处理行数: {total_rows})", end='\r')
            
            for col in columns:
                # 累积非空计数
                stats[col]['count'] += chunk[col].count()
                # 累积唯一值（使用集合set来节省内存，只记录前500个唯一值）
                unique_vals = chunk[col].dropna().astype(str).unique()
                for val in unique_vals:
                    if len(stats[col]['unique']) < 500: # 限制集合大小防止内存溢出
                         stats[col]['unique'].add(val)
                # 记录数据类型 (以第一个非空块的类型为准)
                if stats[col]['dtype'] == 'unknown' and chunk[col].dtype != np.dtype('object'):
                    stats[col]['dtype'] = str(chunk[col].dtype)

        print("\n数据块处理完毕。正在生成报告...")
    except Exception as e:
        print(f"\n分块读取过程中发生错误: {e}")
        return

    # 生成报告
    buffer = io.StringIO()
    buffer.write(f"=== 数据概览报告 (分块读取结果) ===\n")
    buffer.write(f"文件名: {FILE_PATH}\n")
    buffer.write(f"总行数: {total_rows}\n")
    buffer.write(f"总列数: {len(columns)}\n\n")
    
    buffer.write("=== 字段清单与类型 ===\n")
    buffer.write(f"{'字段名':<30} {'数据类型':<15} {'非空值数量':<15} {'缺失率':<10} {'唯一值数量/示例'}\n")
    buffer.write("-" * 90 + "\n")
    
    for col in columns:
        col_stats = stats[col]
        non_null = col_stats['count']
        missing_rate = ((total_rows - non_null) / total_rows) * 100 if total_rows else 0
        unique_count = len(col_stats['unique'])
        dtype = col_stats['dtype'] if col_stats['dtype'] != 'unknown' else str(df_head[col].dtype)
        
        unique_display = f"{unique_count} Unique"
        if unique_count > 0:
             # 随机选择3个示例
             sample = list(col_stats['unique'])[:3]
             unique_display += f" (Ex: {', '.join(sample)})"

        buffer.write(f"{col:<30} {dtype:<15} {non_null:<15} {missing_rate:.2f}%     {unique_display}\n")
        
    buffer.write("\n=== 预处理与特征工程建议 ===\n")
    buffer.write("请结合以上报告，手动执行特征筛选与清洗。\n")

    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(buffer.getvalue())
        
    print(f"\n分析完成！报告已保存至: {OUTPUT_FILE}")
    print("请将此报告文件的内容发送给 Cursor AI，让它进行后续分析。")

if __name__ == "__main__":
    if not os.path.exists(FILE_PATH):
        print("未检测到真实数据，请修改 FILE_PATH 变量并确保文件存在。")
    else:
        analyze_data_in_chunks(FILE_PATH)