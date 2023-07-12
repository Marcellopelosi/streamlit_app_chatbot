from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
import os
import openai
import langchain
import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains import ConversationChain



def openai_setting():
  os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]
  embedding = OpenAIEmbeddings()
  model_name = "gpt-3.5-turbo"
  llm = ChatOpenAI(model_name=model_name, temperature = 0)
  return embedding, llm

def law_content_splitter(path, splitter = "CIVIL CODE"):

  with open(path) as f:
      law_content = f.read()

  law_content_by_article = law_content.split(splitter)[1:]
  text_splitter = CharacterTextSplitter()
  return text_splitter.create_documents(law_content_by_article)


inheritance_splitted = law_content_splitter("./documents/INHERITANCE.txt")
divorce_splitted = law_content_splitter("./documents//DIVISION OF ASSETS AFTER DIVORCE.txt")
embedding, llm = openai_setting()

text_db = Chroma.from_documents(
    documents=inheritance_splitted + divorce_splitted, #I due documenti, splittati per articolo, vengono uniti
    embedding=embedding,
    persist_directory= "./documents"
)

def find_related_contents(query):
  related_contents_docs =text_db.similarity_search(query,k=1)
  related_contents_docs = [d.page_content for d in related_contents_docs]
  return "\n\n".join(related_contents_docs)

from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate


def create_prompt_from_source(source = ''):
  template = """ You are a legal bot that should provide useful informations starting from a legal source and a user question.
    If you are not able to answer say that explicitly.

    EXAMPLE:

    SOURCE:
    457
    DEVOLUTION OF THE INHERITANCE
    The estate is devolved by law or by will.
    Legitimate succession does not take place unless when testamentary succession is lacking in whole or in part.
    Testamentary dispositions must not affect the rights reserved by law for the legitimates.

    QUESTION:
    Tell me something about its devolution

    YOUR ANSWER SHOULD BE SOMETHING LIKE:
    According to the article number 457, The estate is devolved by law or by will.

    Then you can continue with other information you can extract from the source.

    SOURCE:
    {similar_docs}
    """.format(similar_docs = source) +  """
    {chat_history}
    Human: {human_input}
    Chatbot:"""
  prompt = PromptTemplate(
      input_variables=["chat_history", "human_input"], template=template
  )
  return prompt

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=create_prompt_from_source(),
    verbose=False,
    memory=memory,
)

def answer(query, memory):
  llm_chain.prompt = create_prompt_from_source(source = find_related_contents(query))
  llm_chain.memory = memory
  res = llm_chain.predict(human_input=query)
  return res, llm_chain.memory
