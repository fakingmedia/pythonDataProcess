# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在操作此代码库时的指导。

## 项目概述

这是一个使用以下技术的 Python 数据处理项目：
- **Python 3.14**（在 .python-version 中指定）
- **UV 包管理器** 用于依赖管理和虚拟环境
- **现代 Python 打包** 使用 pyproject.toml
- **数据科学库**：NumPy、Pandas、Statsmodels、mplfinance
- **Tushare API**：中国股票市场数据集成

## 开发命令

```bash
# 运行主脚本
uv run main.py

# 安装/更新依赖
uv sync

# 添加新依赖
uv add <包名>

# 构建包（在 dist/ 中创建 wheel 和 tarball）
uv build

# 使用项目依赖运行 Python 交互模式
uv run python
```

## 架构

项目遵循现代 Python 打包标准：
- `pyproject.toml` - 项目配置和依赖
- `src/` - 源代码目录，包含：
  - `TushareStockData.py` - 股票数据检索和 CSV 导出功能
  - `stockChartGenerator.py` - 使用 mplfinance 的金融图表生成
- `main.py` - 演示图表生成的入口脚本
- `.venv/` - UV 管理的虚拟环境
- `uv.lock` - 用于可重现构建的锁定文件

## 关键模块

### TushareStockData
- 通过 Tushare API 检索中国股票市场数据的类接口
- 功能包括股票名称到代码查找、数据检索和 CSV 导出
- 处理 API 速率限制和错误恢复

### StockChartGenerator
- 使用 mplfinance 生成金融图表（K 线、OHLC、折线图）
- 支持跨平台（macOS、Windows、Linux）的中文字体显示
- 与 TushareStockData 集成，实现一键图表生成
- 当 mplfinance 遇到问题时，提供 matplotlib 绘图回退方案

## 代码质量

项目使用 Ruff 进行代码检查（存在缓存目录 `.ruff_cache/`）。未找到显式配置文件，因此 Ruff 使用默认设置。

## 当前状态

项目现在包括：
- 完整的股票数据检索系统，集成 Tushare
- 支持中文字体的金融图表生成
- CSV 数据导出功能
- main.py 中演示图表生成的示例用法
- 未配置测试框架
- 空的 README.md