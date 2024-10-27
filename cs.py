from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

from openai import AzureOpenAI
from swarm import Swarm, Agent

aoai_client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                          api_version="2024-09-01-preview",
                          azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                          azure_deployment='gpt-4o')

four_o_client = Swarm(aoai_client)


def transfer_to_pay_agent():
    '''转移给支付客服'''
    return pay_agent


def transfer_to_mute_agent():
    '''转移给禁言客服'''
    return mute_agent


def create_ticket(user_id):
    '''创建ticket'''
    print(f'为用户{user_id}创建ticket')
    return True


agent_main = Agent(name="主控客服",
                   instructions="""
你是公司的游戏客服
你的任务是回答玩家关于游戏的知识
玩家如果提问如何查看id，可以告知用户点击自己头像查看。
如果用户询问支付问题，就转接给支付客服；如果用户询问禁言问题，就转接给禁言客服。""",
                   functions=[transfer_to_pay_agent, transfer_to_mute_agent])

pay_agent = Agent(
    name="支付客服",
    instructions="""你是公司的游戏客服
你的任务是解决用户的支付问题
如果用户对支付有疑问，你就告知用户，目前支付系统故障""",
)

mute_agent = Agent(name="禁言客服",
                   instructions="""
你是公司的游戏客服
你的任务是解决玩家被禁言解禁的问题
需要确认用户的用户id
如果用户id是2，则告诉用户"用户是首次被永久禁言。禁言原因是卖账号，你需要让玩家完整发'保证不会再犯'文字，并告知只有一次机会，玩家必须明确保证不在犯错，才能使用create_ticket方法创建解封表单，用户给你回复这句话以后，你就使用create_ticket，告知用户你已经创建ticket
""",
                   functions=[create_ticket])

user_messages = ["你好", "我无法支付", "什么时候会好", "好的，我被禁言了", "我的用户id为2", "保证不会再犯"]
history_messages = []

for message in user_messages:
    print(f'User: {message}')
    history_messages.append({'role': 'user', 'content': message})
    response = four_o_client.run(agent=agent_main,
                                 messages=history_messages,
                                 debug=True)
    res = response.messages[-1]["content"]
    history_messages.append({'role': 'assistant', 'content': res})
    print(f'客服: {response.messages[-1]["content"]}')
# print(history_messages)
