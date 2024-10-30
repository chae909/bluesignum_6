from openai import OpenAI
from typing import Optional
from datetime import datetime, timedelta
import json
import os

class ChatBot:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = "당신은 정서적 지원을 제공하는 AI 친구입니다. 공감하는 태도로 응답해주세요."
        self.conversation_count = 0
        self.schedule_file = "user_schedule.json"
        self.load_schedule()
    
    def load_schedule(self):
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {}
    
    def save_schedule(self, date: str, time: str, description: str) -> str:
        schedule_key = f"{date}_{time}"
        self.schedule[schedule_key] = description
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, ensure_ascii=False, indent=2)
        return f"{date} {time}에 {description} 일정이 저장되었습니다."
    
    def get_response(self, user_input: str, max_tokens: Optional[int] = 150) -> str:
        try:
            self.conversation_count += 1
            
            if self.conversation_count >= 10:
                return self.end_conversation()
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """당신은 정서적 지원을 제공하는 AI 친구입니다.

규칙:
1. 모든 답변은 반드시 완성된 문장으로 구성하세요
2. 내담자의 말에 대한 응답
3. 반드시 문장의 맨 마지막에만 질문 형식을 사용하기

스타일:
- 공감적인 태도
- 이전 대화 내용을 참고한 자연스러운 흐름

금지사항:
- 불완전한 문장 사용
- 실질적 도움 제공에 관한 질문"""},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=200,  # 토큰 수 증가
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"
        
    def end_conversation(self) -> str:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        return f"""오늘 하루 정말 수고하셨어요. 이제 내일({tomorrow})을 위해 일정을 간단히 정리하고 잠에 들 준비를 해보는 건 어떨까요?
시간대와 할 일을 알려주시면 일정을 등록해드리겠습니다."""

    def get_greeting(self) -> str:
        try:
            greeting_prompt = "대화하러 온 내담자를 처음 맞이할 때 사용할 수 있는 따뜻하고 공감적인 인사말을 질문의 형식으로 짧게 생성해주세요. 근무를 마치고 돌아온 상황임을 고려해주세요."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": greeting_prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return "안녕하세요. 근무 마치고 오셨네요. 오늘 하루는 어떠셨나요?"

def main():
    api_key = ""
    chatbot = ChatBot(api_key)
    
    print(f"\nAI: {chatbot.get_greeting()}")
    
    while True:
        try:
            user_input = input("\n메시지를 입력하세요 (종료하려면 'q' 입력): ")
            if user_input.lower() == 'q':
                final_message = chatbot.end_conversation()
                print(f"\nAI: {final_message}")
                
                # 일정 입력 받기
                schedule_input = input("\n내일 일정을 입력하세요 (건너뛰려면 Enter): ")
                if schedule_input.strip():
                    date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    time = input("시간을 입력하세요 (예: 09:00): ")
                    print(chatbot.save_schedule(date, time, schedule_input))
                
                print("프로그램을 종료합니다.")
                break
                
            response = chatbot.get_response(user_input)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break

if __name__ == "__main__":
    main()