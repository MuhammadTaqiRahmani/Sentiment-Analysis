from flask import Flask, render_template, request, redirect, url_for, jsonify
from main import process_reviews, evaluate_sentiment, calculate_sentiment_stats
from db_handler import DatabaseHandler
import json
from datetime import datetime

app = Flask(__name__)
db = DatabaseHandler()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        url = request.form.get('product_url')
        try:
            app.config['CURRENT_STATUS'] = 'Initializing review extraction...'
            analysis_results = process_reviews(url)
            
            if not analysis_results:
                return jsonify({'error': "No reviews found. Please check the URL and try again."}), 404

            # Enhanced analysis data
            analysis_data = {
                'url': url,
                'product_name': url.split('/')[-1],
                'sentiment_counts': analysis_results['sentiment_distribution'],
                'average_rating': analysis_results['average_score'],
                'total_reviews': len(analysis_results.get('reviews', [])),
                'reviews': [{
                    'text': review['text'],
                    'sentiment': review['sentiment'],
                    'highlight': len(review['text']) > 50  # Mark longer reviews as highlights
                } for review in analysis_results.get('reviews', [])],
                'most_common_sentiment': analysis_results['most_common'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            try:
                db.add_analysis(url, analysis_data)
                return jsonify({
                    'success': True,
                    'data': analysis_data
                })
            except Exception as db_error:
                print(f"Database error: {db_error}")
                return jsonify({'error': "Failed to save analysis"}), 500
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return jsonify({'error': str(e)}), 500
            
    return render_template('analyze.html')

@app.route('/get_analysis_status')
def get_analysis_status():
    status = getattr(app.config, 'CURRENT_STATUS', 'Processing...')
    progress = getattr(app.config, 'CURRENT_PROGRESS', 50)
    return jsonify({
        'status': 'processing',
        'progress': progress,
        'message': status
    })

@app.route('/results')
def results():
    data = request.args.get('data')
    if data:
        results = json.loads(data)
        return render_template('results.html', results=results)
    return redirect(url_for('analyze'))

@app.route('/history')
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    analyses = db.get_analyses(page, per_page)
    total_pages = db.get_total_pages(per_page)
    return render_template('history.html', 
                         analyses=analyses,
                         current_page=page,
                         total_pages=total_pages)

@app.route('/delete_analysis/<int:analysis_id>')
def delete_analysis(analysis_id):
    db.delete_analysis(analysis_id)
    return redirect(url_for('history'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)