from src.TushareStockData import TushareStockData
from src.stockChartGenerator import StockChartGenerator

def main():
    print("Hello from pythondataprocess!")


if __name__ == "__main__":
    chart_generator = StockChartGenerator()
    
    fig, path = chart_generator.generate_chart(
      data='stock_data/茅台_20230103_20241231.csv',
      chart_type='candle',
      save_path='stock_charts/茅台_20230103_20241231.png'
    )