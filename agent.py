
import json
import os
from typing import TypedDict

from openai import OpenAI
from tools import list_simulink_models, check_simulink_model
from langgraph.graph import StateGraph, START, END


client = OpenAI(
    base_url=os.getenv(
        "LM_STUDIO_BASE_URL",
        "http://172.21.208.1:1234/v1"
    ),
    api_key="lm-studio",
    timeout=120.0
)

MODEL = "google/gemma-4-e4b"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "list_simulink_models",
        "description": "查詢專案中實際存在的 Simulink 模型",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}]


TOOLS.append({
    "type": "function",
    "function": {
        "name": "check_simulink_model",
        "description": "檢查指定的 Simulink .slx 模型檔案是否存在",
        "parameters": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "要查詢的模型檔名，例如 AEBTestBench.slx"
                }
            },
            "required": ["model_name"],
            "additionalProperties": False
        }
    }
})


class AgentState(TypedDict):
    messages: list[dict]
    tool_calls: list[dict]
    llm_calls: int


def llm_node(state: AgentState):
    # 避免模型無限重複呼叫工具
    if state["llm_calls"] >= 3:
        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": "已達最大決策次數，任務停止。"
            }],
            "tool_calls": []
        }

    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=state["messages"],
            tools=TOOLS,
            tool_choice="auto",
            temperature=0
        )

    except Exception as exc:
        error_type = type(exc).__name__

        print(f"[Error] LLM API 呼叫失敗：{error_type}")

        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": (
                    f"LM Studio API 呼叫失敗（{error_type}）。"
                    "請確認 Server 是否啟動，以及 IP、Port 是否正確。"
                    "本次任務未完成。"
                )
            }],
            "tool_calls": [],
            "llm_calls": state["llm_calls"] + 1
        }


    message = response.choices[0].message

    if message.tool_calls:
        calls = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments
                }
            }
            for call in message.tool_calls
        ]

        print("[Decision] LLM 決定呼叫工具")

        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": calls
            }],
            "tool_calls": calls,
            "llm_calls": state["llm_calls"] + 1
        }

    print("[Decision] LLM 產生最終回答")

    return {
        "messages": state["messages"] + [{
            "role": "assistant",
            "content": message.content or ""
        }],
        "tool_calls": [],
        "llm_calls": state["llm_calls"] + 1
    }


def tool_node(state: AgentState):
    messages = list(state["messages"])

    for call in state["tool_calls"]:
        name = call["function"]["name"]

        print(f"[Tool Call] {name}")

        try:
            arguments = json.loads(
                call["function"]["arguments"]
            )
            if name == "list_simulink_models" and arguments == {}:
                result = list_simulink_models()

            elif (
                name == "check_simulink_model"
                and isinstance(arguments, dict)
                and set(arguments) == {"model_name"}
                and isinstance(arguments["model_name"], str)
            ):
                result = check_simulink_model(arguments["model_name"])

            else:
                result = {
                    "status": "error",
                    "message": "未知工具或無效參數"
                }


        except Exception as exc:
            result = {
                "status": "error",
                "message": str(exc)
            }

        print(f"[Observation] {result}")

        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": json.dumps(result, ensure_ascii=False)
        })

    return {"messages": messages, "tool_calls": []}


def route(state: AgentState):
    return "tool" if state["tool_calls"] else END


builder = StateGraph(AgentState)

builder.add_node("llm", llm_node)
builder.add_node("tool", tool_node)

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", route)
builder.add_edge("tool", "llm")

agent = builder.compile()


if __name__ == "__main__":
    question = input("請輸入實驗需求：\n> ")

    result = agent.invoke({
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是 MATLAB/Simulink 實驗代理人。"
                    "查詢模型時必須使用工具。"
                    "只能依據工具結果回答。"
                    "不可虛構模型或模擬數據。"
                    "目前尚未支援真正的 MATLAB 模擬執行。"
                )
            },
            {"role": "user", "content": question}
        ],
        "tool_calls": [],
        "llm_calls": 0
    })

    print("\n[Final Answer]")
    print(result["messages"][-1]["content"])
