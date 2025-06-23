from pydantic import BaseModel
from typing import Annotated, List, Generator
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessageChunk
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dbagent.tools import query_db, generate_visualization
from dbagent.prompts import prompts


class  LangState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages] = []
    chart_json: str = ""

# state=ScoutState(messages=[HumanMessage(content="hello"),AIMessage(content="hi")])

# pritn(state.model_dump_json(indent=2))


# llm=ChatOllama(
#     model="llama3.2:3b",
#     temperatur=0.1,
# )


# def assistant_node(state:ScoutState) -> ScoutState:
#     response=llm.invoke("hi sham")
#     state.messages.append(response)
#     return state

# graph_builder=StateGraph(ScountState)
# graph_builder.add_node(assistant_node)
# grpah_builder.add_edge(START,"assistant_node")
# graph_builder.add_edge("assistant_node",END)

# graph=graph_builder.compile(checkpointer=MemorySaver())

# from IPython.display import display,Image
# display(Image(graph.get_graph(xray=True).draw_mermaid_png()))


# config={
#     "configurable":{
#         "thread_id":"1",
#     }}

# result=graph.invoke(input=state,
# config=config)





class Agent:
    """
    Agent class for implementing Langgraph agents.

    Attributes:
        name: The name of the agent.
        tools: The tools available to the agent.
        model: The model to use for the agent.
        system_prompt: The system prompt for the agent.
        temperature: The temperature for the agent.
    """
    def __init__(
            self, 
            name: str, 
            tools: List = [query_db, generate_visualization],
            # model: str = "gpt-4.1-mini-2025-04-14", 
            model:str ="llama3.2:latest",
            system_prompt: str = "You are a helpful assistant.",
            temperature: float = 0.1
            ):
        self.name = name
        self.tools = tools
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        
        self.llm = ChatOllama(
            model=self.model,
            temperature=self.temperature,
            ).bind_tools(self.tools)
        
        self.runnable = self.build_graph()


    def build_graph(self):
        """
        Build the LangGraph application.
        """
        def lang_node(state: LangState) -> LangState:
            response = self.llm.invoke(
                [SystemMessage(content=self.system_prompt)] +
                state.messages
                )
            state.messages = state.messages + [response]
            return state
        
        def router(state: LangState) -> str:
            last_message = state.messages[-1]
            if not last_message.tool_calls:
                return END
            else:
                return "tools"

        builder = StateGraph(LangState)

        builder.add_node("chatbot", lang_node)
        builder.add_node("tools", ToolNode(self.tools))

        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges("chatbot", router, ["tools", END])
        builder.add_edge("tools", "chatbot")

        return builder.compile(checkpointer=MemorySaver())
    

    def inspect_graph(self):
        """
        Visualize the graph using the mermaid.ink API.
        """
        from IPython.display import display, Image

        graph = self.build_graph()
        display(Image(graph.get_graph(xray=True).draw_mermaid_png()))


    def invoke(self, message: str, **kwargs) -> str:
        """Synchronously invoke the graph.

        Args:
            message: The user message.

        Returns:
            str: The LLM response.
        """
        result = self.runnable.invoke(
            input = {
                "messages": [HumanMessage(content=message)]
            },
            **kwargs
        )

        return result["messages"][-1].content
    

    def stream(self, message: str, **kwargs) -> Generator[str, None, None]:
        """Synchronously stream the results of the graph run.

        Args:
            message: The user message.

        Returns:
            str: The final LLM response or tool call response
        """
        for message_chunk, metadata in self.runnable.stream(
            input = {
                "messages": [HumanMessage(content=message)]
            },
            stream_mode="messages",
            **kwargs
        ):
            if isinstance(message_chunk, AIMessageChunk):
                if message_chunk.response_metadata:
                    finish_reason = message_chunk.response_metadata.get("finish_reason", "")
                    if finish_reason == "tool_calls":
                        yield "\n\n"

                if message_chunk.tool_call_chunks:
                    tool_chunk = message_chunk.tool_call_chunks[0]

                    tool_name = tool_chunk.get("name", "")
                    args = tool_chunk.get("args", "")

                    
                    if tool_name:
                        tool_call_str = f"\n\n< TOOL CALL: {tool_name} >\n\n"

                    if args:
                        tool_call_str = args
                    yield tool_call_str
                else:
                    yield message_chunk.content
                continue


# Define and instantiate the agent 
agent = Agent(
        name="Lang",
        system_prompt=prompts.lang_system_prompt
        )
graph = agent.build_graph()
