from openai import OpenAI

LM_STUDIO_BASE_URL = "http://172.21.208.1:1234/v1"
MODEL_NAME = "google/gemma-4-e4b"

client = OpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key="lm-studio"
)


def ask_llm(user_input: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是 MATLAB/Simulink 智慧實驗代理人的 LLM 核心。"
                    "你的任務是理解使用者的實驗需求，並用繁體中文清楚回答。"
                    "目前你先負責一般文字理解與回覆，之後才會加入工具呼叫能力。"
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response.choices[0].message.content


def main():
    print("MATLAB/Simulink Experiment Agent")
    print("請輸入實驗需求：")

    user_input = input("> ")

    try:
        answer = ask_llm(user_input)
        print("\nLLM 回覆：")
        print(answer)
    except Exception as e:
        print("\n執行失敗：")
        print(str(e))


if __name__ == "__main__":
    main()