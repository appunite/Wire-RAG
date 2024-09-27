
# DataAnalyzer

**Version**: 2.5.0  
**Author**: Tech Innovations

## Overview

The `DataAnalyzer` package provides a fast, optimized approach to data analysis, particularly for small datasets. 
It is designed for personal and academic projects rather than large-scale datasets.

## Functions:

1. `process_data(dataset: list) -> dict`
   This function processes the dataset and returns basic statistics such as:
   - Mean
   - Mode
   - Variance

   Example:
   ```python
   from DataAnalyzer import process_data
   
   dataset = [2, 8, 22, 18, 25]
   stats = process_data(dataset)
   ```

2. `graph_data(dataset: list, chart: str = 'scatter') -> None`
   This function generates a chart based on the dataset. The default chart type is 'scatter'.

## Installation

- Install via pip:
  ```bash
  pip install analyzer-package
  ```

## Dependencies
- Python 3.6+
- `pandas`
- `seaborn`
