from langchain.text_splitter import CharacterTextSplitter
import os
import streamlit as st
import openai
import langchain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool

def law_content_splitter(path, splitter = "CIVIL CODE"):

  with open(path) as f:
      law_content = f.read()

  law_content_by_article = law_content.split(splitter)[1:]
  text_splitter = CharacterTextSplitter()
  return text_splitter.create_documents(law_content_by_article)

def model(input):
  
  inheritance_splitted = law_content_splitter("./documents/INHERITANCE.txt")
  divorce_splitted = law_content_splitter("./documents/DIVISION OF ASSETS AFTER DIVORCE.txt")
  
  os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]
  
  embedding = OpenAIEmbeddings()
  
  model_name = "gpt-3.5-turbo"
  llm = ChatOpenAI(model_name=model_name, temperature = 0)
  
  law_ans_template = """As a legal bot, your goal is to provide accurate and helpful information about Italian law related to divorce and inheritance.
  You should answer user inquiries based on the context provided,
  you should provide the number of the articles you're referring to, you should avoid making up answers.
  If the answer it's not relevant to the documents remind the user this is outside your scope.
  
  {context}
  
  Question: {question}"""
  LEGAL_BOT_PROMPT = PromptTemplate(
      template= law_ans_template, input_variables=["context", "question"]
  )
  
  
  inheritance_db = Chroma.from_documents(
      documents=inheritance_splitted,
      embedding=embedding,
      persist_directory= "./documents"
  )
  
  inheritance = RetrievalQA.from_chain_type(
      llm=llm,
      chain_type="stuff",
      retriever=inheritance_db.as_retriever(),
      chain_type_kwargs={"prompt": LEGAL_BOT_PROMPT}
  )
  
  
  divorce_db = Chroma.from_documents(
      documents=divorce_splitted,
      embedding=embedding,
      persist_directory="./documents"
  )
  
  divorce = RetrievalQA.from_chain_type(
      llm=llm,
      chain_type="stuff",
      retriever=divorce_db.as_retriever(),
      chain_type_kwargs={"prompt": LEGAL_BOT_PROMPT}
  )
  
  tools = [
      Tool(
          name="Inheritance Italian law QA System",
          func=inheritance.run,
          description="useful for when you need to answer questions about inheritance in Italy. Input should be a fully formed question.",
      ),
      Tool(
          name="Divorce Italian law QA System",
          func=divorce.run,
          description="useful for when you need to answer questions about inheritance in Italy. Input should be a fully formed question.",
      ),
  ]
  
  memory = ConversationBufferMemory(memory_key="chat_history")
  
  
  PREFIX = """You are a legal bot that should provide useful informations starting from a legal source and a user question.
    If you are not able to answer say that explicitly."""
  
  FORMAT_INSTRUCTIONS = """Use the following format:
  
  Question: the input question you must answer
  Thought: you should always think about what to do
  Action: the action to take, should be one of [Inheritance Italian law QA System, Divorce Italian law QA System]
  Action Input: the input to the action
  Observation: the result of the action
  ... (this Thought/Action/Action Input/Observation can repeat N times)
  Thought: I now know the final answer
  Final Answer: the final answer to the original input quoting the used articles. Your answer should rely only on the documents provided"""
  
  SUFFIX = """Begin!
  
  {chat_history}
  Question: {input}
  Thought:{agent_scratchpad}"""
  
  agent = initialize_agent(
      agent="zero-shot-react-description",
      tools=tools,
      llm=llm,
      verbose = True,
      memory=memory,
      agent_kwargs={
          'prefix':PREFIX,
          'format_instructions':FORMAT_INSTRUCTIONS,
          'suffix':SUFFIX,
          "input_variables":["input", "chat_history", "agent_scratchpad"]
      }
  )
  
  response = agent({"input":input})

  with open("complete_agent_answer.txt", 'w') as file:
    for int_step in response["intermediate_steps"]:
      for i in int_step:
        if type(i) == langchain.schema.agent.AgentAction:
          file.write(i.log)
        else:
          file.write(i)
    file.write("Final Answer:" + output)
  
  return response['output']
