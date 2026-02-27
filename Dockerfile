FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码
COPY . .

# 设置 Python 路径并启动
ENV PYTHONPATH=/app
CMD ["sh", "-c", "cd /app/llm_assistant/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
