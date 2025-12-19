import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

try:
    from TushareStockData import TushareStockData
except ImportError:
    from .TushareStockData import TushareStockData


class StockChartGenerator:
    def __init__(self):
        """
        初始化StockChartGenerator类
        """
        # 设置中文字体，避免中文显示问题
        self._setup_chinese_fonts()
        plt.rcParams['axes.unicode_minus'] = False

    def _setup_chinese_fonts(self):
        """
        设置中文字体
        """
        import matplotlib.font_manager as fm
        import platform

        # 获取系统信息
        system = platform.system()

        # 查找合适的中文字体
        chinese_fonts = []
        fonts = fm.findSystemFonts()

        for font in fonts:
            try:
                font_prop = fm.FontProperties(fname=font)
                font_name = font_prop.get_name()

                # 检查是否是中文字体
                if any(keyword in font_name.lower() for keyword in [
                    'simhei', 'simsun', 'simkai', 'simfang', 'microsoft', 'wenquan',
                    'noto sans cjk', 'noto sans sc', 'noto sans tc', 'source han',
                    'noto sans mono cjk', 'pingfang', 'heiti', 'stheiti',
                    '思源', '黑体', '宋体', '楷体', '仿宋', '微软雅黑', '苹方'
                ]):
                    chinese_fonts.append(font_name)
            except:
                pass

        # 根据系统设置字体优先级
        if system == "Darwin":  # macOS
            preferred_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Arial Unicode MS', 'Noto Sans CJK SC']
        elif system == "Windows":  # Windows
            preferred_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'Noto Sans CJK SC']
        else:  # Linux 或其他
            preferred_fonts = ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'WenQuanYi Micro Hei', 'AR PL UMing CN', 'DejaVu Sans']

        # 合并优先字体和发现的中文字体
        all_fonts = preferred_fonts + list(set(chinese_fonts))

        # 设置字体
        plt.rcParams['font.sans-serif'] = all_fonts
        plt.rcParams['font.family'] = 'sans-serif'

        # 打印使用的字体信息
        print(f"系统: {system}")
        print(f"设置的中文字体列表: {all_fonts[:8]}")  # 显示前8个字体

    def prepare_data(self, df):
        """
        准备数据，确保数据格式符合mplfinance要求

        Args:
            df: DataFrame，包含股票数据

        Returns:
            DataFrame: 格式化后的数据
        """
        # 复制数据避免修改原数据
        data = df.copy()

        # 确保日期列是datetime类型并设置为索引
        if 'trade_date' in data.columns:
            # 尝试不同的日期格式
            try:
                # 首先尝试 %Y%m%d 格式（如 20230103）
                data['Date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d')
            except:
                try:
                    # 如果失败，尝试自动解析
                    data['Date'] = pd.to_datetime(data['trade_date'])
                except:
                    # 如果都失败，尝试手动转换
                    data['Date'] = data['trade_date'].apply(lambda x: pd.to_datetime(str(x)))
            data = data.set_index('Date')
        elif 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')

        # 重命名列以符合mplfinance要求
        column_mapping = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume',
            'volume': 'Volume'
        }

        # 先转换为小写，再映射到标准列名
        data.columns = data.columns.str.lower()
        data = data.rename(columns=column_mapping)

        # 确保必要的列存在
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"数据缺少必要的列: {missing_columns}")

        # 按日期排序
        data = data.sort_index()

        return data

    def generate_chart(self, data, chart_type='candle', title=None,
                      volume=True, style='yahoo', figsize=(12, 8),
                      save_path=None, show=False, **kwargs):
        """
        生成金融图表

        Args:
            data: DataFrame或CSV文件路径
            chart_type: 图表类型 ('candle', 'ohlc', 'line', 'renko', 'pnf')
            title: 图表标题
            volume: 是否显示成交量
            style: 图表样式 ('yahoo', 'charles', 'checkers', 'mike', 'sas', 'nightclouds')
            figsize: 图表尺寸
            save_path: 保存路径，如果为None则不保存
            show: 是否显示图表
            **kwargs: 其他mplfinance参数

        Returns:
            tuple: (图表对象, 保存路径)
        """
        # 如果data是字符串，则认为是CSV文件路径
        if isinstance(data, str):
            df = pd.read_csv(data)
        else:
            df = data

        # 准备数据
        chart_data = self.prepare_data(df)

        # 设置标题
        if title is None:
            if 'stock_name' in df.columns:
                stock_name = df['stock_name'].iloc[0]
                start_date = chart_data.index[0].strftime('%Y-%m-%d')
                end_date = chart_data.index[-1].strftime('%Y-%m-%d')
                title = f"{stock_name} K线图 ({start_date} 至 {end_date})"
            else:
                title = "K线图"

        # 配置图表参数
        plot_params = {
            'type': chart_type,
            'volume': volume,
            'style': style,
            'figsize': figsize,
            'datetime_format': '%Y-%m-%d',
            'xrotation': 45,
            'show_nontrading': False
        }

        # 标题通过returnfig后设置，避免mplfinance字体问题
        if title:
            plot_params['title'] = title

        # 添加额外的参数
        plot_params.update(kwargs)

        # 创建图表
        try:
            fig, _ = mpf.plot(chart_data, **plot_params, returnfig=True)
        except Exception as e:
            # 如果mplfinance出错，回退到使用matplotlib直接绘制
            print(f"mplfinance绘图出错，使用回退方案: {e}")
            fig = self._fallback_plot(chart_data, title, volume, figsize)

        # 保存图表
        saved_path = None
        if save_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # 保存时使用支持中文的字体
            try:
                # 尝试使用系统中文字体保存
                import matplotlib
                from matplotlib import font_manager as fm

                # 查找中文字体
                chinese_fonts = []
                for font in fm.findSystemFonts():
                    try:
                        font_prop = fm.FontProperties(fname=font)
                        font_name = font_prop.get_name()
                        if any(keyword in font_name.lower() for keyword in [
                            'pingfang', 'heiti', 'microsoft', 'noto sans cjk', 'noto sans sc'
                        ]):
                            chinese_fonts.append(font_name)
                    except:
                        pass

                if chinese_fonts:
                    # 临时设置保存时的字体
                    with matplotlib.rc_context({'font.family': 'sans-serif', 'font.sans-serif': chinese_fonts}):
                        fig.savefig(save_path, dpi=300, bbox_inches='tight')
                else:
                    # 如果没有找到中文字体，直接保存
                    fig.savefig(save_path, dpi=300, bbox_inches='tight')
            except:
                # 如果出错，直接保存
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
            saved_path = save_path

        # 显示图表
        if show:
            plt.show()

        return fig, saved_path

    def _fallback_plot(self, data, title, volume, figsize):
        """
        回退方案：使用matplotlib直接绘制K线图
        """
        import matplotlib.pyplot as plt

        # 创建图形
        if volume:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize,
                                          gridspec_kw={'height_ratios': [3, 1]},
                                          sharex=True)
        else:
            fig, ax1 = plt.subplots(figsize=figsize)
            ax2 = None

        # 绘制K线图
        for i, (_, row) in enumerate(data.iterrows()):
            color = 'r' if row['Close'] >= row['Open'] else 'g'
            ax1.plot([i, i], [row['Low'], row['High']], color='k', linewidth=0.8)
            ax1.plot([i, i], [row['Open'], row['Close']], color=color, linewidth=3)

        # 设置标题和标签 - 直接使用已设置的中文字体
        ax1.set_title(title, fontsize=14, pad=20)
        ax1.set_ylabel('价格', fontsize=12)
        ax1.grid(True, alpha=0.3)

        # 设置x轴
        ax1.set_xlim(0, len(data))

        # 每N天显示一个日期标签
        n = max(1, len(data) // 10)
        ax1.set_xticks(range(0, len(data), n))
        ax1.set_xticklabels([data.index[i].strftime('%Y-%m-%d') for i in range(0, len(data), n)],
                           rotation=45)

        # 绘制成交量（如果需要）
        if volume and ax2:
            ax2.bar(range(len(data)), data['Volume'], alpha=0.7, width=0.8)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.grid(True, alpha=0.3)

            # 设置x轴标签
            ax2.set_xticks(range(0, len(data), n))
            ax2.set_xticklabels([data.index[i].strftime('%Y-%m-%d') for i in range(0, len(data), n)],
                               rotation=45)

        plt.tight_layout()
        return fig

    def generate_chart_from_stock(self, stock_name=None, stock_code=None,
                                 start_date=None, end_date=None,
                                 chart_type='candle', title=None,
                                 volume=True, style='yahoo', figsize=(12, 8),
                                 output_dir='stock_charts', filename=None,
                                 show=False, **kwargs):
        """
        直接从股票名称或代码生成图表（集成TushareStockData）

        Args:
            stock_name: 股票名称
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            chart_type: 图表类型
            title: 图表标题
            volume: 是否显示成交量
            style: 图表样式
            figsize: 图表尺寸
            output_dir: 输出目录
            filename: 文件名，如果为None则自动生成
            show: 是否显示图表
            **kwargs: 其他参数

        Returns:
            tuple: (图表对象, 数据DataFrame, 保存路径)
        """
        # 创建TushareStockData实例
        tushare_data = TushareStockData()

        # 获取股票数据
        df = tushare_data.get_stock_data(
            stock_name=stock_name,
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            print("未获取到数据，无法生成图表")
            return None, df, None

        # 自动生成文件名
        if filename is None:
            stock_name_str = stock_name or stock_code or 'unknown'
            start_date_str = start_date or '20100101'
            end_date_str = end_date or datetime.now().strftime('%Y%m%d')
            filename = f"{stock_name_str}_{chart_type}_{start_date_str}_{end_date_str}.png"

        # 构建保存路径
        save_path = os.path.join(output_dir, filename)

        # 生成图表
        fig, saved_path = self.generate_chart(
            data=df,
            chart_type=chart_type,
            title=title,
            volume=volume,
            style=style,
            figsize=figsize,
            save_path=save_path,
            show=show,
            **kwargs
        )

        return fig, df, saved_path

    def generate_multiple_charts(self, stock_list, chart_types=['candle'],
                               output_dir='stock_charts', **kwargs):
        """
        为多个股票生成图表

        Args:
            stock_list: 股票列表，可以是名称列表或字典列表
            chart_types: 图表类型列表
            output_dir: 输出目录
            **kwargs: 其他参数

        Returns:
            list: 生成的图表信息列表
        """
        results = []

        for stock in stock_list:
            if isinstance(stock, dict):
                stock_name = stock.get('name')
                stock_code = stock.get('code')
                start_date = stock.get('start_date')
                end_date = stock.get('end_date')
            else:
                stock_name = stock
                stock_code = None
                start_date = None
                end_date = None

            for chart_type in chart_types:
                print(f"正在生成 {stock_name or stock_code} 的 {chart_type} 图表...")

                try:
                    fig, df, saved_path = self.generate_chart_from_stock(
                        stock_name=stock_name,
                        stock_code=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        chart_type=chart_type,
                        output_dir=output_dir,
                        show=False,
                        **kwargs
                    )

                    if fig and saved_path:
                        results.append({
                            'stock_name': stock_name or stock_code,
                            'chart_type': chart_type,
                            'data_rows': len(df),
                            'saved_path': saved_path
                        })
                except Exception as e:
                    print(f"生成图表失败: {e}")
                    results.append({
                        'stock_name': stock_name or stock_code,
                        'chart_type': chart_type,
                        'error': str(e)
                    })

        return results


# 使用示例
if __name__ == "__main__":
    # 创建图表生成器实例
    chart_generator = StockChartGenerator()

    # 示例1：从CSV文件生成图表
    print("=== 示例1：从CSV文件生成图表 ===")
    # 注意：这里需要一个CSV文件路径
    # fig1, path1 = chart_generator.generate_chart(
    #     data='stock_data/浦发银行_20230101_20231231.csv',
    #     chart_type='candle',
    #     title='浦发银行2023年K线图',
    #     save_path='stock_charts/浦发银行_2023.png',
    #     show=False
    # )

    # 示例2：直接从股票名称生成图表
    print("\n=== 示例2：直接从股票名称生成图表 ===")
    fig2, df2, path2 = chart_generator.generate_chart_from_stock(
        stock_name='浦发银行',
        start_date='20230101',
        end_date='20231231',
        chart_type='candle',
        style='yahoo',
        volume=True,
        show=False
    )

    # 示例3：生成多种类型的图表
    print("\n=== 示例3：生成多种类型的图表 ===")
    results = chart_generator.generate_multiple_charts(
        stock_list=['浦发银行', '贵州茅台'],
        chart_types=['candle', 'line', 'ohlc'],
        start_date='20230101',
        end_date='20231231',
        output_dir='stock_charts'
    )

    # 打印结果
    print("\n=== 图表生成结果 ===")
    for result in results:
        if 'error' in result:
            print(f"❌ {result['stock_name']} - {result['chart_type']}: {result['error']}")
        else:
            print(f"✅ {result['stock_name']} - {result['chart_type']}: {result['saved_path']} ({result['data_rows']}条数据)")