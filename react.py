import openai
import re
import httpx
import os
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI

load_dotenv()

prompt = """
你在一个思考、建议、Action、PAUSE、观察的循环中运行。
在循环的末尾，你输出一个答案。
使用Thought来描述你对所提问题的想法。
使用Action来执行可用的适当操作，然后返回PAUSE。
观察将是运行这些操作的结果。

你可用的操作有：

calculate:
例如，calculate: 4 * 7 / 3
运行一个计算并返回数字——使用Python，因此如果必要，请确保使用浮点语法。

get_average_price:
例如，get_average_price: Lenovo
当给出型号名称时，返回该笔记本电脑的平均价格。

示例会话：

问题：一台联想笔记本电脑多少钱？
Thought: 我应该使用get_average_price来查找笔记本电脑的价格。

Action: get_average_price: Lenovo
PAUSE

然后你将被再次调用：

观察: 一台联想笔记本电脑的平均价格是400美元。

然后你输出：

答案: 一台联想笔记本电脑的价格是400美元。
""".strip()

client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                     api_version="2024-09-01-preview",
                     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                     azure_deployment='gpt-4o')


class Agent:

    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(model="gpt-4o",
                                                    temperature=0,
                                                    messages=self.messages)
        return completion.choices[0].message.content


def calculate(what):
    return eval(what)


def get_average_price(name):
    if name in "Lenovo":
        return ("a lenovo laptop average price is $400")
    elif name in "Dell":
        return ("a Dell laptop average price is $450.")
    elif name in "Asus":
        return ("a Asus laptop average price is $500")
    else:
        return ("An laptop average price is $430")


known_tools = {"calculate": calculate, "get_average_price": get_average_price}

action_re = re.compile(
    '^Action: (\w+): (.*)$')  # python regular expression to selection action


def query(question, max_turns=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a) for a in result.split('\n')
            if action_re.match(a)
        ]
        if actions:
            print(actions)
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_tools:
                raise Exception("Unknown action: {}: {}".format(
                    action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_tools[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


question = """what is the total cost for 2 lenovo and a Asus laptops"""
query(question)
