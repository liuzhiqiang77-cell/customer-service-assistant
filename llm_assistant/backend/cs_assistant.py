"""
客户服务助手 - 基于 Moments of Truth 关键时刻
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from collections import Counter
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


@dataclass
class Skill:
    """技能数据类"""
    name: str
    folder: str
    description: str
    content: str
    category: str = ""


class SkillsRAG:
    """Skills 检索系统"""
    
    def __init__(self, skills_path: str = None):
        if skills_path is None:
            # 自动查找 skills 目录（支持本地和 Docker）
            possible_paths = [
                Path(__file__).parent.parent / "skills",  # 本地开发
                Path.cwd() / "skills",  # 当前目录
                Path.cwd().parent / "skills",  # 上级目录（Docker）
                Path(__file__).parent.parent.parent / "skills",  # 项目根目录
                Path("/app/skills"),  # Docker 绝对路径
            ]
            for path in possible_paths:
                if path.exists():
                    skills_path = path
                    print(f"✅ 找到 skills 目录: {path}")
                    break
        else:
            skills_path = Path(skills_path)
        
        self.skills_path = Path(skills_path)
        self.skills: List[Skill] = []
        self.load_skills()
    
    def parse_skill_file(self, file_path: Path) -> Optional[Skill]:
        """解析单个 skill 文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 解析 frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    skill_content = parts[2].strip()
                    
                    return Skill(
                        name=metadata.get('name', file_path.parent.name),
                        folder=file_path.parent.name,
                        description=metadata.get('description', ''),
                        content=skill_content,
                        category=metadata.get('category', self.infer_category(file_path.parent.name))
                    )
            
            # 没有 frontmatter，使用文件名
            return Skill(
                name=file_path.parent.name,
                folder=file_path.parent.name,
                description="",
                content=content,
                category=self.infer_category(file_path.parent.name)
            )
        except Exception as e:
            print(f"⚠️ 解析失败 {file_path}: {e}")
            return None
    
    def infer_category(self, folder_name: str) -> str:
        """根据文件夹名推断分类"""
        category_keywords = {
            "leadership": "领导力",
            "customer": "客户服务",
            "frontline": "前线管理",
            "strategic": "战略",
            "employee": "员工管理",
            "organizational": "组织变革",
            "airline": "航空业",
            "service": "服务策略",
            "pricing": "定价策略",
            "cargo": "货运管理",
            "union": "工会关系",
            "advertising": "营销传播",
            "board": "董事会",
            "moment": "关键时刻",
        }
        
        folder_lower = folder_name.lower()
        for keyword, category in category_keywords.items():
            if keyword in folder_lower:
                return category
        
        return "通用"
    
    def load_skills(self):
        """加载所有 skills"""
        print(f"📁 加载 skills 目录: {self.skills_path}")
        
        skill_files = list(self.skills_path.rglob("SKILL.md"))
        print(f"🔍 找到 {len(skill_files)} 个 skill 文件")
        
        for file_path in skill_files:
            skill = self.parse_skill_file(file_path)
            if skill:
                self.skills.append(skill)
        
        # 统计
        categories = Counter(s.category for s in self.skills)
        print(f"✅ 已加载 {len(self.skills)} 个 skills")
        print(f"📊 分类: {dict(categories)}")
    
    def search(self, query: str, top_k: int = 3) -> List[Skill]:
        """简单关键词搜索"""
        query_words = set(query.lower().split())
        scores = []
        
        for skill in self.skills:
            score = 0
            skill_text = (skill.name + " " + skill.description + " " + skill.content).lower()
            
            for word in query_words:
                if len(word) > 2:  # 忽略短词
                    score += skill_text.count(word)
            
            if score > 0:
                scores.append((score, skill))
        
        scores.sort(reverse=True, key=lambda x: x[0])
        return [skill for _, skill in scores[:top_k]]


class CustomerServiceAssistant:
    """客户服务助手主类"""
    
    def __init__(self):
        self.rag = SkillsRAG()
        self.provider = os.getenv("LLM_PROVIDER", "kimi").lower()
        self.setup_llm()
        
    def setup_llm(self):
        """配置 LLM"""
        if self.provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            default_model = "deepseek-chat"
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            default_model = "gpt-3.5-turbo"
        else:  # kimi
            api_key = os.getenv("KIMI_API_KEY")
            base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
            default_model = "moonshot-v1-32k"
        
        if not api_key:
            raise ValueError(f"请设置 {self.provider.upper()}_API_KEY 环境变量")
        
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("DEFAULT_MODEL", default_model)
        print(f"✅ 使用 {self.provider.upper()} API, 模型: {self.model}")
    
    def build_system_prompt(self, relevant_skills: List[Skill]) -> str:
        """构建系统提示词"""
        skills_context = "\n\n".join([
            f"【{skill.name}】\n{skill.description}\n{skill.content[:1000]}"
            for skill in relevant_skills
        ])
        
        return f"""你是基于《关键时刻》(Moments of Truth) 理论的客户服务专家助手。

《关键时刻》核心理念：
- "关键时刻"是客户与公司的任何接触，通常只持续 15 秒
- 这短暂的接触决定了客户是否将公司视为最佳选择
- 一线员工必须在瞬间做出决定，不能依赖规则手册
- 公司每年被"创造"数百万次，每次 15 秒

可用技能参考：
{skills_context}

回答原则：
1. 始终以客户为中心，从客户视角思考问题
2. 引用《关键时刻》中的具体原则和案例
3. 提供实用的、可执行的建议
4. 强调前线员工授权和快速决策的重要性
5. 使用中文回答

请基于以上理念回答用户问题。"""
    
    async def chat(self, message: str, history: List[tuple] = None, stream: bool = True) -> AsyncGenerator[str, None]:
        """对话方法"""
        if history is None:
            history = []
        
        # 检索相关 skills
        relevant_skills = self.rag.search(message, top_k=3)
        print(f"🔍 找到 {len(relevant_skills)} 个相关技能: {[s.name for s in relevant_skills]}")
        
        # 构建消息
        messages = [
            {"role": "system", "content": self.build_system_prompt(relevant_skills)},
        ]
        
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                temperature=0.7,
            )
            
            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
                
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            yield f"抱歉，调用 AI 服务时出错：{str(e)}\n\n请检查 API Key 是否配置正确。"
    
    async def get_todos(self, context: str) -> List[Dict]:
        """生成待办清单"""
        prompt = f"""基于《关键时刻》理论，为以下客户服务场景生成具体的行动清单：

场景：{context}

请生成 3-5 个具体的行动项，每个包含：
- task: 任务名称
- priority: 优先级（高/中/低）
- timeframe: 时间框架（立即/本周/本月）
- category: 类别（员工授权/流程优化/客户体验/组织变革）

以 JSON 格式返回，只返回数组。"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是客户服务战略专家，擅长将《关键时刻》理论转化为具体行动计划。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            # 提取 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            import json
            todos = json.loads(content.strip())
            return todos[:5]  # 最多返回5个
            
        except Exception as e:
            print(f"❌ 生成待办失败: {e}")
            return [
                {"task": "检查 API 配置", "priority": "高", "timeframe": "立即", "category": "系统"}
            ]


# 全局助手实例
assistant = CustomerServiceAssistant()
