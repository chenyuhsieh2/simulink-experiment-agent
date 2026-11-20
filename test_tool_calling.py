
from openai import OpenAI

client = OpenAI(
    base_url="http://172.21.208.1:1234/v1",
    api_key="lm-studio",
    timeout=120.0
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_simulink_models",
            "description": "查詢目前專案中可用的 Simulink 模型檔案",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

response = client.chat.completions.create(
    model="google/gemma-4-e4b",
    messages=[
        {
            "role": "system",
            "content": (
                "你是 MATLAB/Simulink 實驗代理人。"
                "當使用者要求查詢模型時，應選擇適當工具。"
                "不可虛構模型清單。"
            )
        },
        {
            "role": "user",
            "content": "請幫我查詢目前有哪些 Simulink 模型？"
        }
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0
)

message = response.choices[0].message

print("Finish Reason:", response.choices[0].finish_reason)
print("Tool Calls:", message.tool_calls)
print("LLM Content:", message.content)
