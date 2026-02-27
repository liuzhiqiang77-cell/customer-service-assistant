# 🎯 客户服务助手 - 关键时刻

基于 Jan Carlzon《关键时刻》(Moments of Truth) 理论的客户服务智能助手。

## 核心理念

《关键时刻》强调：
- 任何客户与公司的接触都是"关键时刻"，通常只持续 **15 秒**
- 这短暂的接触决定了客户是否将公司视为最佳选择
- 一线员工必须被授权在瞬间做出决策，不能依赖规则手册
- 公司每年被"创造"数百万次，每次 15 秒

## 功能

- 💬 **智能对话**：基于 46 个客户服务技能回答问题
- 📝 **行动清单**：为具体场景生成可执行的行动建议
- 🔍 **技能检索**：自动匹配最相关的理论知识

## 技术栈

- **后端**：FastAPI + OpenAI/Kimi API
- **前端**：原生 HTML/JS
- **部署**：Render

## 部署

### Render 部署

1. 连接 GitHub 仓库
2. 选择 "Python 3" 或 "Docker" 运行时
3. 设置环境变量（见 render.yaml）
4. 部署完成

## 本地开发

```bash
cd llm_assistant/backend
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8000
