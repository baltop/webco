### 질문: langgraph와 smolagents를 동시에 이용해서 agent를 개발하려고 해. 우선 큰틀에서 langgraph를 사용하고 langgraph의 노드에서 호출하는 다른 평션 노드를 smolagents를 이용해서 구성할 수 있는지 알려주고, 샘플 코드를 만들어줘.

네, LangGraph와 smolagents를 동시에 사용하여 에이전트를 개발하는 것은 가능하며 매우 유용한 접근 방식입니다. LangGraph를 사용하여 전체적인 에이전트 워크플로우를 관리하고, 각 워크플로우의 특정 단계나 복잡한 로직을 처리하기 위해 smolagents를 활용할 수 있습니다.
LangGraph의 노드에서 smolagents를 사용하는 방법:
LangGraph의 각 노드는 상태를 입력으로 받고 상태 업데이트를 출력하는 Python 함수로 정의될 수 있습니다. 이 함수 내에서 smolagents의 에이전트를 생성하고 실행하여 특정 작업을 수행할 수 있습니다. smolagents는 LLM을 엔진으로 사용하며 도구를 활용하여 작업을 해결하므로, LangGraph 워크플로우의 한 단계에서 LLM 기반의 복잡한 의사 결정이나 코드 실행, 도구 사용 등을 smolagents에게 위임할 수 있습니다.
샘플 코드:
다음은 LangGraph를 사용하여 기본적인 워크플로우를 정의하고, 그중 하나의 노드에서 간단한 CodeAgent를 사용하여 Fibonacci 수열의 특정 숫자를 계산하는 예시입니다.
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
코드 설명:
1.
AgentState: LangGraph의 상태를 정의합니다. 여기에는 메시지 목록과 계산된 Fibonacci 숫자를 저장할 필드가 포함됩니다.
2.
model = HfApiModel(): smolagents에서 사용할 LLM 모델을 초기화합니다. 필요에 따라 다른 모델이나 설정을 사용할 수 있습니다.
3.
calculate_fibonacci(state: AgentState) -> Dict[str, int]: LangGraph의 노드로 사용될 함수입니다.
◦
입력으로 현재 LangGraph의 상태(AgentState)를 받습니다.
◦
상태에서 사용자 쿼리를 추출합니다.
◦
**smolagents.CodeAgent**를 도구 없이 초기화하고, add_base_tools=True로 설정하여 기본적인 Python 코드 실행 기능을 활성화합니다.
◦
agent.run(user_query)를 호출하여 Fibonacci 수열 계산 작업을 smolagents 에이전트에게 위임합니다.
◦
에이전트의 결과에서 Fibonacci 숫자를 간단히 파싱하여 딕셔너리 형태로 반환합니다. 실제로는 에이전트의 출력 형식에 맞춰 더 robust한 파싱 로직이 필요할 수 있습니다.
4.
workflow = StateGraph(AgentState): LangGraph 워크플로우를 초기화합니다.
5.
workflow.add_node("fibonacci_calculator", calculate_fibonacci): Fibonacci 계산을 담당하는 노드를 워크플로우에 추가합니다.
6.
workflow.set_entry_point("fibonacci_calculator"): 워크플로우의 시작점을 fibonacci_calculator 노드로 설정합니다.
7.
workflow.add_edge("fibonacci_calculator", END): fibonacci_calculator 노드의 출력을 워크플로우의 종료점으로 연결합니다.
8.
graph = workflow.compile(): 정의된 워크플로우를 실행 가능한 그래프로 컴파일합니다.
9.
graph.stream(inputs): 초기 입력과 함께 LangGraph 워크플로우를 실행합니다.
이 예시에서는 매우 간단한 작업을 smolagents에게 위임했지만, 더 복잡한 도구 사용, 웹 검색, 외부 API 호출 등 smolagents가 제공하는 다양한 기능을 LangGraph 워크플로우 내에서 활용할 수 있습니다. 예를 들어, 특정 정보를 검색해야 하는 LangGraph 노드에서 CodeAgent에 웹 검색 도구를 제공하여 작업을 수행하게 할 수 있습니다.
이처럼 LangGraph는 전체적인 구조와 흐름을 관리하고, smolagents는 각 단계에서 필요한 LLM 기반의 지능적인 작업을 수행하도록 통합하여 강력하고 유연한 에이전트 시스템을 구축할 수 있습니다.
