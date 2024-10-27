from swarm import Agent
from swarm import Swarm
from swarm.types import Result
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
# 模拟公司快递打包，包括物流工程师和SF快递员

aoai_client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                          api_version="2024-09-01-preview",
                          azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                          azure_deployment='gpt-4o')
four_o_client = Swarm(aoai_client)


def sf_instruction(context_variables):
    '''SF快递员的指令'''
    return f"你是一名SF快递员，负责将快递送到客户手中,你只需要回答'{context_variables['item_name']}已经送达'即可"


sf_agent = Agent(
    name="SF Agent",
    instructions=sf_instruction,
)


def pack_express():
    '''打包快递'''
    print("打包快递!")


def send_express():
    '''发送快递'''
    print("发送快递!")


def transfer_to_sf_agent():
    '''转接给SF快递员'''
    return sf_agent


logistic_agent = Agent(
    name="Logistic Agent",
    functions=[pack_express, send_express, transfer_to_sf_agent],
    instructions="你是一名物流工程师，负责发送公司物流,你的任务是分别执行打包快递，发送快递，并将快递交给SF快递员",
)


def trans_to_logistic_agent():
    '''转接到物流代理'''
    return Result(value="Done", agent=logistic_agent)


main_agent = Agent(name="Main Agent",
                   functions=[trans_to_logistic_agent],
                   instructions="你是一名客服，负责将快递交给物流工程师发出")
response = four_o_client.run(agent=main_agent,
                             messages=[{
                                 "role": "user",
                                 "content": "发送快递"
                             }],
                             debug=True,
                             context_variables={"item_name": "书籍"})
print(response.messages[-1]["content"])
