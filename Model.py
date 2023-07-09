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
    persist_directory=persist_directory
)

def find_related_contents(query):
  related_contents_docs =text_db.similarity_search(query,k=1)
  related_contents_docs = [d.page_content for d in related_contents_docs]
  return "\n\n".join(related_contents_docs)


def from_user_query_to_llm_query(query):
  template = """ You are a legal bot that should provide useful informations starting from a legal source and a user question.
  If you are not able to answer say that explicitly. Before you reply, attend, think and remember all the instructions set here.


  EXAMPLE:

  SOURCE:
  457
  DEVOLUTION OF THE INHERITANCE
  The estate is devolved by law or by will.
  Legitimate succession does not take place unless when testamentary succession is lacking in whole or in part.
  Testamentary dispositions must not affect the rights reserved by law for the legitimates.

  QUESTION:
  Tell me something about the devolution of the inheritance

  YOUR ANSWER SHOULD BE SOMETHING LIKE:
  According to the article number 457, The estate is devolved by law or by will.

  Then you can continue with other information you can extract from the source.

  SOURCE:
  {similar_docs}

  QUESTION:
  {user_input}

  YOUR ANSWER:

  """

  prompt = PromptTemplate(
          input_variables = ["user_input", "similar_docs"],
          template=template
  )

  promptValue = prompt.format(user_input = query, similar_docs = find_related_contents(query))
  return promptValue


llm = OpenAI(model_name="gpt-3.5-turbo", temperature = 0)

def model(input):
  query= from_user_query_to_llm_query(input)
  return llm(query)
