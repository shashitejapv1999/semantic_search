from app import db,app

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    embedding = db.Column(db.ARRAY(db.Float)) 

    def __repr__(self):
        return f'<Document {self.filename}>'