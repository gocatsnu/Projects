# Multi-Sport Models

This repository hosts lightweight pipelines for predicting outcomes across multiple sports. Each sport lives in its own subpackage under `sports/` and can run independently.

## Quick Start

```bash
python sports/nba/pipeline.py
python sports/wnba/pipeline.py
python sports/pga/pipeline.py
```

Model outputs are saved to the `outputs/` directory or pushed to Google Sheets.
