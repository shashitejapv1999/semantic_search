from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
from models import db, Document
from utils import allowed_file, generate_embeddings, extract_text, search_documents
import os
from sentence_transformers import SentenceTransformer

# Initialize the model here
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        text = extract_text(file_path)
        embeddings = generate_embeddings(extract_text(file_path))
        new_doc = Document(filename=filename,content = text, embedding=embeddings)
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully!', 'filename': filename}), 200
    return jsonify({'message': 'Invalid file type'}), 400

@app.route('/search', methods=['POST'])
def search():
    query = request.json['query']
    query_embedding = model.encode(query, convert_to_tensor=True)
    #query_embedding = generate_embeddings(query)
    #results = search_documents(query_embedding)
    results = search_documents(query, query_embedding)
    return jsonify(results)


@app.route('/documentsCount', methods=['GET'])
def get_total_documents():
    try:
        total_documents = Document.query.count()
        return jsonify({'total_documents': total_documents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        documents = Document.query.all()
        documents_list = []
        for document in documents:
            documents_list.append({
                'id': document.id,
                'filename': document.filename
            })
        return jsonify({'documents': documents_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/document', methods=['DELETE'])
def delete_document():
    try:
        id = request.json['id']
        document = Document.query.filter_by(id=id).first()
        
        if not document:
            return jsonify({'message': 'Document not found'}), 404

        file_path = os.path.join('uploads', document.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the document from the database
        db.session.delete(document)
        db.session.commit()

        return jsonify({'message': 'Document deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

