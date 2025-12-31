from langgraph.graph import StateGraph,START,END # type: ignore
from langchain_core.prompts import PromptTemplate # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langchain_core.messages import BaseMessage, HumanMessage # type: ignore
from dotenv import load_dotenv # type: ignore
from typing import TypedDict , Literal , Annotated
import os
from langgraph.graph.message import add_messages # type: ignore
from langgraph.checkpoint.memory import MemorySaver # type: ignore
load_dotenv()

# LLM initialization
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.5)

# state definition
class chatState(TypedDict):
    message : Annotated[list[BaseMessage], add_messages]

# node function
def chat_model(state:chatState):
    messages = state['message']
    response = llm.invoke(messages)
    return {'message': response}

# graph construction
check = MemorySaver()
graph = StateGraph(chatState)

graph.add_node("Chatbot",chat_model)
graph.add_edge(START,"Chatbot")
graph.add_edge("Chatbot",END)

workflow = graph.compile(checkpointer = check)