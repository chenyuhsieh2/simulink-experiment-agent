
FROM docker.io/library/python:3.11-slim

WORKDIR /app

# 複製並安裝 Python 套件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Agent 與 Tools
COPY main.py agent.py tools.py ./

# 預設執行 LangGraph Agent
CMD ["python", "agent.py"]
