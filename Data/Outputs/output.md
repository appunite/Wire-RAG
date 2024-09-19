# DataAnalyzer Project Documentation

## Module Name: DataAnalyzer
## Version: 2.5.0
## Author: Tech Solutions

## Overview:
The DataAnalyzer project provides a fast and optimized approach to data analysis, suitable for small datasets in personal and academic projects. It offers various functions for processing datasets and generating basic statistics and visualizations.

## Functions:
1. **process_data(dataset: list) -> dict**
   This function processes the dataset and returns basic statistics such as:
   - Mean
   - Mode
   - Variance
   Usage Example:
   ```python
   from DataAnalyzer import process_data
   dataset = [2, 8, 22, 18, 25]
   stats = process_data(dataset)
   ```

2. **graph_data(dataset: list, chart: str = 'scatter') -> None**
   This function generates a chart based on the dataset. The default chart type is 'scatter'.
   Example:
   ```python
   from DataAnalyzer import graph_data
   dataset = [2, 8, 22, 18, 25]
   graph_data(dataset, 'scatter')
   ```

## Installation:
Install the DataAnalyzer package via pip:
```
pip install analyzer-package
```

## Dependencies:
- Python 3.6+
- pandas
- seaborn

## Notes:
- The function `process_data` replaces `analyze_data`.
- Default chart type for `graph_data` changed from `bar` to `scatter`.
- Added support for new chart types: 'heatmap' and 'pie'.
- Improved performance for small datasets.