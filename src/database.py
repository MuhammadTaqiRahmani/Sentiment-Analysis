from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_url = db.Column(db.String(255), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Review {self.id} - {self.sentiment}>'

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    rating = db.Column(db.String(50), nullable=False)

    review = db.relationship('Review', backref='analysis_results')

    def __repr__(self):
        return f'<AnalysisResult {self.id} - Rating: {self.rating}>'