FROM python:3.11-slim

WORKDIR /app

# 先复制并安装依赖（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码（包括 skills、llm_assistant 等）
COPY . .

# 列出目录结构用于调试
RUN ls -la && ls -la skills/ | head -5

# 启动命令
WORKDIR /app/llm_assistant/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
