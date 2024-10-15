import os
from sentence_transformers import SentenceTransformer,util
from models import Document
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

model = SentenceTransformer('all-MiniLM-L6-v2')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}

def extract_text(file_path):
    extension = os.path.splitext(file_path)[1]
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        return None

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding='utf-8') as file:
        text = file.read()
    return text

def generate_embeddings(text):
    embeddings = model.encode(text)  # This returns a numpy array
    return [float(x) for x in embeddings.tolist()]  # Convert numpy array elements to floats explicitly

def search_documents(query, query_embedding):
    documents = Document.query.all()
    best_sentences = []

    for doc in documents:
        # Tokenize the document content into sentences
        sentences = sent_tokenize(doc.content)
        sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
        
        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, sentence_embeddings)

        # Find the best matching sentence in this document
        best_sentence_index = similarities.argmax()
        if len(sentences[best_sentence_index]) > 150:
            sentences[best_sentence_index] = sentences[best_sentence_index][:150]
        best_sentences.append((sentences[best_sentence_index], similarities[0, best_sentence_index].item(), doc.filename))


    # Sort by best similarity score across all documents
    best_sentences.sort(key=lambda x: x[1], reverse=True)
    return [{'sentence': match[0], 'similarity': match[1], 'filename': match[2]} for match in best_sentences[:3]]

