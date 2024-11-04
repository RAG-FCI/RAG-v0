import os
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from pypdf import PdfReader
from langchain.docstore.document import Document


def signal_handler(sig, frame):
    print('\nObrigado por usar nosso Chat!')
    sys.exit(0)


# Diretório onde os PDFs estão armazenados
diretorio_pdf = os.getcws()

# Lista para armazenar o conteúdo dos PDFs
docs = []

# Itera sobre todos os arquivos do diretório
for nome_arquivo in os.listdir(diretorio_pdf):
    # Verifica se o arquivo tem extensão .pdf
    if nome_arquivo.endswith('.pdf'):
        caminho_arquivo = os.path.join(diretorio_pdf, nome_arquivo)
        
        # Abre o PDF e lê seu conteúdo
        with open(caminho_arquivo, 'rb') as f:
            reader = PdfReader(f)
            texto = ""
            
            # Itera por cada página e extrai o texto
            for pagina in reader.pages:
                texto += pagina.extract_text()  # Extrai o texto de cada página
            
            # Adiciona o conteúdo do PDF à lista
            docs.append(texto)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# Convert the list of strings to a list of Document objects
docs_for_splitting = [Document(page_content=text) for text in docs]

# Now, split the Document objects
docs = text_splitter.split_documents(docs_for_splitting)

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
vectorstore = Chroma.from_documents(docs, embedding=embedding_function, persist_directory="./chroma_db_nccn")

signal.signal(signal.SIGINT, signal_handler)

last_answer = ""

def generate_rag_prompt(query, context, last_answer=""):
    escaped_context = context.replace("'","").replace('"', "").replace("\n"," ")
    escaped_last_answer = last_answer.replace("'","").replace('"', "").replace("\n"," ")

    prompt = f"""
Você é um bot útil e informativo que responde perguntas sobre a Universidade Presbiteriana Mackenzie usando o texto do contexto de referência incluído abaixo. \
Certifique-se de responder em uma frase completa, sendo abrangente e incluindo todas as informações relevantes. \
Lembre-se de que você está falando com um público não técnico, portanto, deve simplificar conceitos complicados \
e manter um tom amigável e conversacional. \
Se o contexto for irrelevante para a resposta, você pode ignorá-lo. Se for necessário continuar da resposta anterior, aqui está a última resposta:

                ÚLTIMA RESPOSTA: '{escaped_last_answer}'
                PERGUNTA: '{query}'
                CONTEXTO: '{escaped_context}'

              RESPOSTA:
              """
    return prompt

def get_relevant_context_from_db(query):
    context = ""
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)

    search_results = vector_db.similarity_search(query, k=6)

    for result in search_results:
        context += result.page_content + "\n"
    return context

GEMEINI_API_KEY = "AIzaSyB1QMQ-KzX6kEvvuNukUPDlfPum0Z9nNL4"

def generate_answer(prompt):
    genai.configure(api_key=GEMEINI_API_KEY)
    model = genai.GenerativeModel(model_name='gemini-pro')
    answer = model.generate_content(prompt)
    return answer.text


welcome_text = generate_answer("Se apresente brevemente")
print(welcome_text)

while True:
    print("-----------------------------------------------------------------------\n")
    print("O que gostaria de saber?")
    query = input("Resposta: ")

    context = get_relevant_context_from_db(query)

    prompt = generate_rag_prompt(query=query, context=context, last_answer=last_answer)

    answer = generate_answer(prompt=prompt)
    print(answer)
    last_answer = answer
