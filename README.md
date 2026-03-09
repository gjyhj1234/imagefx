# imagefx – 口腔全景片智能分析 / Dental Panoramic X-ray Analysis

基于图像处理的口腔全景片自动分析系统，可识别牙齿问题并生成标准牙周检查报告。

An image-processing-based dental panoramic radiograph analysis system that identifies dental issues and generates standard periodontal examination reports.

## 功能特性 / Features

- **自动牙齿检测** – 基于 FDI 国际牙位编号系统识别每颗牙齿
- **多种问题检测** – 龋坏、缺失、阻生、牙槽骨吸收、牙周病、修复体等
- **混合牙列识别** – 自动判断患者是否处于替牙期（适用于儿童患者）
- **三种输出格式**:
  1. **JSON** – 结构化数据，适合系统集成
  2. **患者报告** – 中英文对照的患者讲解文本
  3. **综合评分** – 0-100分口腔健康评分及原因分析

## 快速开始 / Quick Start

```bash
# 安装依赖
pip install -r requirements.txt

# 分析自带样例图片
python main.py

# 分析指定图片
python main.py /path/to/panoramic.jpg --patient-id P-001 --output-dir ./output
```

## 输出示例 / Output Example

分析完成后，`output/` 目录下生成三个文件：

| 文件 | 说明 |
|------|------|
| `analysis_result.json` | 结构化 JSON 结果 |
| `patient_report.txt` | 患者讲解文本（中英文） |
| `score_summary.txt` | 口腔综合评分及原因 |

## 项目结构 / Project Structure

```
├── main.py                          # 命令行入口
├── patient-dental-img.jpg           # 样例全景片
├── requirements.txt                 # Python 依赖
├── src/
│   ├── models/
│   │   ├── dental.py                # 数据模型（牙周检查、评分等）
│   │   └── tooth_map.py             # FDI 牙位编号映射
│   ├── analyzer/
│   │   ├── image_preprocessing.py   # 图像预处理（CLAHE、降噪、分区）
│   │   ├── dental_analysis.py       # 核心分析引擎
│   │   └── scoring.py               # 口腔健康评分
│   └── output/
│       └── formatter.py             # 输出格式化（JSON / 文本 / 评分）
└── tests/                           # 单元测试
```

## 技术说明 / Technical Notes

- 使用 OpenCV 进行图像预处理（对比度增强、降噪、边缘检测）
- 使用强度分析、区域统计等启发式方法检测牙齿异常
- 本系统为辅助分析工具，**不能替代专业牙科医生的诊断**

## 测试 / Testing

```bash
python -m pytest tests/ -v
```

## 免责声明 / Disclaimer

> 本报告仅供参考，请以专业牙科医生的诊断为准。
>
> This report is for reference only. Please consult a qualified dental professional for clinical diagnosis.
