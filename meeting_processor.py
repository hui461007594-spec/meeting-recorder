
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv


load_dotenv()


class MeetingProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            except ImportError:
                self.client = None
        else:
            self.client = None
    
    def generate_minutes(self, transcript: str, custom_prompt: Optional[str] = None) -&gt; str:
        prompt = custom_prompt or """
请将以下会议转录内容整理成规范的会议记录，包括：
1. 会议主题
2. 参会人员（如果提到）
3. 会议时间
4. 会议主要内容
5. 讨论要点
6. 达成的共识

请用中文输出，格式清晰易读。

会议转录内容：
"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的会议记录助手。"},
                        {"role": "user", "content": prompt + transcript}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"API调用失败: {e}")
                return self._generate_minutes_fallback(transcript)
        else:
            return self._generate_minutes_fallback(transcript)
    
    def _generate_minutes_fallback(self, transcript: str) -&gt; str:
        return f"""会议记录
==========

会议转录内容：
{transcript}

（注：如需更智能的会议记录整理，请配置OpenAI API密钥）"""
    
    def extract_todos(self, transcript: str, minutes: str, custom_prompt: Optional[str] = None) -&gt; str:
        prompt = custom_prompt or """
请从以下会议记录和转录内容中提炼出所有的待办事项和需求，包括：
1. 需要完成的具体任务
2. 负责人（如果提到）
3. 截止时间（如果提到）
4. 需求和建议

请用中文输出，格式为列表，每条待办事项清晰明了。

会议记录：
{minutes}

会议转录内容：
{transcript}
"""
        
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的任务管理助手。"},
                        {"role": "user", "content": prompt.format(minutes=minutes, transcript=transcript)}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"API调用失败: {e}")
                return self._extract_todos_fallback(transcript, minutes)
        else:
            return self._extract_todos_fallback(transcript, minutes)
    
    def _extract_todos_fallback(self, transcript: str, minutes: str) -&gt; str:
        return """待办事项和需求
==============

（注：如需更智能的待办事项提炼，请配置OpenAI API密钥）

请人工从以下内容中提炼待办事项：
"""


if __name__ == "__main__":
    processor = MeetingProcessor()
    print("MeetingProcessor class loaded successfully")
