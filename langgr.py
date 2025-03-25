from typing import Annotated, List, Dict, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from smolagents import CodeAgent, HfApiModel

# LangGraph 상태 정의
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    fibonacci_number: int

# smolagents 모델 초기화 (본인의 허깅페이스 토큰이 필요할 수 있습니다)
model = HfApiModel()

# smolagents 에이전트를 실행하는 LangGraph 노드 함수
def calculate_fibonacci(state: AgentState) -> Dict[str, int]:
    user_query = state['messages'][-1].content
    # 간단한 도구 없이 CodeAgent 초기화
    agent = CodeAgent(tools=[], model=model, add_base_tools=True)
    result = agent.run(user_query)
    # 결과에서 Fibonacci 숫자를 추출 (실제 구현에서는 에이전트의 출력 방식에 따라 파싱이 필요할 수 있습니다)
    try:
        number = int(result.split(' ')[-1].replace('.', '')) # 간단한 파싱 예시
    except ValueError:
        number = -1 # 파싱 실패 시 오류 처리
    return {"fibonacci_number": number}

# LangGraph 워크플로우 정의
workflow = StateGraph(AgentState)

# Fibonacci 계산 노드 추가
workflow.add_node("fibonacci_calculator", calculate_fibonacci)

# 워크플로우 시작점 설정
workflow.set_entry_point("fibonacci_calculator")

# 워크플로우 종료점 설정
workflow.add_edge("fibonacci_calculator", END)

# 그래프 컴파일
graph = workflow.compile()

# 워크플로우 실행
inputs = {"messages": [HumanMessage(content="Could you give me the 10th number in the Fibonacci sequence?")], "fibonacci_number": 0}
for output in graph.stream(inputs):
    if "fibonacci_number" in output:
        print(f"Fibonacci Number: {output['fibonacci_number']}")