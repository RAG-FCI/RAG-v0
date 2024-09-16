from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF para operações de leitura em PDFs
import numpy as np
import datasets  # Biblioteca Hugging Face 'datasets'

# Função para ler conteúdo do PDF
def ler_pdf(caminho_arquivo):
    doc = fitz.open(caminho_arquivo)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()  # Extraindo o texto de cada página
    return texto

# Inicializa o modelo de embeddings e carrega os textos dos PDFs
def inicializar_textos_e_embeddings(caminhos_pdfs):
    modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    textos = []
    vetores = []
    titulos = []

    # Ler o conteúdo dos PDFs e converter em embeddings
    for i, caminho in enumerate(caminhos_pdfs):
        conteudo_pdf = ler_pdf(caminho)
        textos.append(conteudo_pdf)  # Armazena o texto original
        vetor = modelo.encode(conteudo_pdf).astype('float32')  # Gerar embedding do texto
        vetores.append(vetor)
        titulos.append(f"Documento {i+1}")  # Gera um título baseado no índice do documento

    return titulos, textos, np.array(vetores)

# Função para criar um dataset a partir dos textos, embeddings e títulos
def criar_dataset(titulos, textos, embeddings):
    # Criar um dataset usando os títulos, textos e embeddings
    dataset = datasets.Dataset.from_dict({
        "title": titulos,
        "text": textos,
        "embeddings": [embedding.tolist() for embedding in embeddings]  # Converter embeddings para listas
    })
    # Indexar os embeddings no dataset para que possam ser usados no retriever
    dataset.add_faiss_index(column="embeddings")
    return dataset

# Caminhos dos arquivos PDF
caminhos_pdfs = ["arquivo1.pdf", "arquivo2.pdf", "arquivo3.pdf"]

# Inicializa os títulos, textos e os embeddings dos PDFs
titulos, textos, embeddings = inicializar_textos_e_embeddings(caminhos_pdfs)

# Cria o dataset com os títulos, textos e embeddings
dataset = criar_dataset(titulos, textos, embeddings)

# Inicializa o modelo RAG
tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", indexed_dataset=dataset)
generator = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq")

# Inicializa o Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Rota para processar o prompt
@app.route('/interpretar', methods=['POST'])
def interpretar():
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "Prompt não fornecido"}), 400    

        # Tokenizar o prompt usando o tokenizer do RAG
        inputs = tokenizer([prompt], return_tensors="pt")

        # Usar o retriever para buscar os documentos relevantes
        retrieved_docs = retriever(inputs["input_ids"], return_tensors="pt")

        # Gerar a resposta usando o modelo RAG com base no prompt e nos documentos recuperados
        generated = generator.generate(input_ids=inputs["input_ids"], context_input_ids=retrieved_docs["context_input_ids"])

        # Decodificar a resposta
        resposta = tokenizer.decode(generated[0], skip_special_tokens=True)

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicializa a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)
