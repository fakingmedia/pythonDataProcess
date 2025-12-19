import tushare as ts
import pandas as pd
from datetime import datetime
import os

class TushareStockData:
    def __init__(self, token=None):
        """
        初始化TushareStockData类

        Args:
            token: tushare的API token，如果不提供则使用默认token
        """
        if token:
            ts.set_token(token)
        else:
            # 使用默认token
            ts.set_token('d6e458b77cb193155e4a82b824f89d144a2f0d9031e33edb3a064f1f')
        self.pro = ts.pro_api()

    def get_stock_code_by_name(self, stock_name):
        """
        根据股票名称获取股票代码

        Args:
            stock_name: 股票名称

        Returns:
            str: 股票代码（如'600000.SH'）
        """
        # 获取所有股票的基本信息
        stock_list = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

        # 根据名称查找股票代码
        result = stock_list[stock_list['name'] == stock_name]

        if result.empty:
            # 尝试模糊匹配
            result = stock_list[stock_list['name'].str.contains(stock_name, na=False)]

        if result.empty:
            raise ValueError(f"未找到股票名称 '{stock_name}' 对应的股票代码")

        # 返回第一个匹配的股票代码
        return result.iloc[0]['ts_code']

    def get_stock_data(self, stock_name=None, stock_code=None, start_date=None, end_date=None):
        """
        获取股票历史数据

        Args:
            stock_name: 股票名称（可选，与stock_code二选一）
            stock_code: 股票代码（可选，与stock_name二选一）
            start_date: 开始日期，格式为'YYYYMMDD'（可选，默认为20100101）
            end_date: 结束日期，格式为'YYYYMMDD'（可选，默认为今天）

        Returns:
            DataFrame: 股票历史数据
        """
        # 检查输入参数
        if not stock_name and not stock_code:
            raise ValueError("必须提供stock_name或stock_code中的一个")

        # 获取股票代码
        if stock_name:
            ts_code = self.get_stock_code_by_name(stock_name)
        else:
            ts_code = stock_code

        # 设置默认日期
        if not start_date:
            start_date = '20100101'
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')

        # 获取股票历史数据
        df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        if df.empty:
            print(f"未获取到股票 '{stock_name or stock_code}' 在指定时间范围内的数据")
            return pd.DataFrame()

        # 按日期排序
        df = df.sort_values('trade_date')

        # 添加股票名称
        if stock_name:
            df['stock_name'] = stock_name
        else:
            # 尝试获取股票名称
            try:
                stock_info = self.pro.stock_basic(ts_code=ts_code, fields='name')
                if not stock_info.empty:
                    df['stock_name'] = stock_info.iloc[0]['name']
            except:
                df['stock_name'] = ts_code

        return df

    def save_to_csv(self, df, filename=None, output_dir='stock_data'):
        """
        将股票数据保存为CSV文件

        Args:
            df: 股票数据DataFrame
            filename: CSV文件名（可选，如果不提供则自动生成）
            output_dir: 输出目录（可选，默认为'stock_data'）

        Returns:
            str: 保存的文件路径
        """
        if df.empty:
            print("数据为空，无法保存")
            return None

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 自动生成文件名
        if not filename:
            stock_name = df['stock_name'].iloc[0] if 'stock_name' in df.columns else 'unknown'
            start_date = df['trade_date'].min()
            end_date = df['trade_date'].max()
            filename = f"{stock_name}_{start_date}_{end_date}.csv"

        # 确保文件名以.csv结尾
        if not filename.endswith('.csv'):
            filename += '.csv'

        # 构建完整路径
        filepath = os.path.join(output_dir, filename)

        # 保存数据
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath}")

        return filepath

    def get_and_save_stock_data(self, stock_name=None, stock_code=None,
                               start_date=None, end_date=None,
                               filename=None, output_dir='stock_data'):
        """
        获取股票数据并保存为CSV文件的便捷方法

        Args:
            stock_name: 股票名称（可选）
            stock_code: 股票代码（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            filename: CSV文件名（可选）
            output_dir: 输出目录（可选）

        Returns:
            tuple: (DataFrame, 文件路径)
        """
        # 获取数据
        df = self.get_stock_data(stock_name=stock_name, stock_code=stock_code,
                                start_date=start_date, end_date=end_date)

        if df.empty:
            return df, None

        # 保存数据
        filepath = self.save_to_csv(df, filename=filename, output_dir=output_dir)

        return df, filepath


# 使用示例
if __name__ == "__main__":
    # 创建实例
    tushare_data = TushareStockData()

    # 示例1：根据股票名称获取数据
    print("=== 示例1：根据股票名称获取浦发银行数据 ===")
    df1, filepath1 = tushare_data.get_and_save_stock_data(
        stock_name='浦发银行',
        start_date='20230101',
        end_date='20231231',
        filename='浦发银行2023年数据.csv'
    )
    print(f"获取到 {len(df1)} 条记录")

    # 示例2：根据股票代码获取数据
    print("\n=== 示例2：根据股票代码获取数据 ===")
    df2, filepath2 = tushare_data.get_and_save_stock_data(
        stock_code='000001.SZ',
        start_date='20230101',
        end_date='20231231'
    )
    print(f"获取到 {len(df2)} 条记录")

    # 示例3：获取当前日期往前一年的数据
    print("\n=== 示例3：获取贵州茅台最近一年数据 ===")
    df3, filepath3 = tushare_data.get_and_save_stock_data(
        stock_name='贵州茅台'
    )
    print(f"获取到 {len(df3)} 条记录")

    # 显示数据前几行
    if not df1.empty:
        print("\n浦发银行数据预览：")
        print(df1.head())