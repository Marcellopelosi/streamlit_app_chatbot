from langchain.text_splitter import CharacterTextSplitter
import os
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import BaseTool
from langchain import LLMMathChain, SerpAPIWrapper

def law_content_splitter(path, splitter = "CIVIL CODE"):

  with open(path) as f:
      law_content = f.read()

  law_content_by_article = law_content.split(splitter)[1:]
  text_splitter = CharacterTextSplitter()
  return text_splitter.create_documents(law_content_by_article)


