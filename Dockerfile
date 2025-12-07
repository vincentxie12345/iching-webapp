# 使用官方 Python 輕量版
FROM python:3.9-slim

WORKDIR /app

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# 安裝系統工具
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install fastapi uvicorn pydantic

# 複製所有程式碼
COPY . .

# 啟動命令 (改用 shell 格式，比較保險)
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]