#!/usr/bin/env python3
"""
Flask Backend for Resume Analyzer Web Application
"""

import os
import uuid
import json
import tempfile
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Import your existing resume analyzer
from advanced_resume_analyzer import (
    extract_resume_text,
    parse_resume_sections,
    analyze_technical_keywords,
    calculate_job_profile_match,
    analyze_section_details,
    calculate_comprehensive_ats_score,
    generate_comprehensive_report,
    JOB_PROFILES
)

app = Flask(__name__)

# --- CORS Configuration ---
# Get the allowed origin from the environment variable you set on Render.
# Provide a fallback for local development (e.g., http://localhost:5173)
allowed_origin = os.environ.get('CORS_ORIGIN', 'http://localhost:5173')

# Initialize CORS to only allow requests from your specific frontend URL.
CORS(app, resources={r"/*": {"origins": allowed_origin}}, supports_credentials=True)


# --- App Configuration ---
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Main endpoint for resume analysis"""
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload PDF or TXT files only.'})
        
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{file_id}.{file_extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        
        file.save(filepath)
        logger.info(f"File saved: {filepath}")
        
        resume_text = extract_resume_text(filepath)
        if not resume_text:
            os.remove(filepath)
            return jsonify({'success': False, 'error': 'Could not extract text from the file'})
        
        logger.info("Text extraction successful")
        
        analysis_result = perform_comprehensive_analysis(resume_text, file_id)
        
        report_filename = f"{file_id}_analysis_report.txt"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        generate_comprehensive_report(resume_text, report_path)
        
        os.remove(filepath)
        
        logger.info("Analysis completed successfully")
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'})

def perform_comprehensive_analysis(resume_text, file_id):
    """Perform comprehensive resume analysis and return structured data"""
    sections = parse_resume_sections(resume_text)
    tech_keywords = analyze_technical_keywords(resume_text)
    job_matches = calculate_job_profile_match(resume_text, sections)
    ats_score, score_breakdown = calculate_comprehensive_ats_score(resume_text, sections, job_matches)
    best_match = max(job_matches.items(), key=lambda x: x[1]['score'])
    section_analyses = {name: analyze_section_details(name, content) for name, content in sections.items()}
    recommendations = generate_recommendations(job_matches, section_analyses, ats_score)
    improvement_potential = min(ats_score + 15, 95)
    
    return {
        'report_id': file_id,
        'ats_score': round(ats_score, 1),
        'best_job_match': best_match[0],
        'match_percentage': round(best_match[1]['score'], 1),
        'tech_keywords_found': sum(len(kw) for kw in tech_keywords.values()),
        'improvement_potential': round(improvement_potential, 1),
        'total_words': len(resume_text.split()),
        'job_matches': job_matches,
        'sections': section_analyses,
        'score_breakdown': score_breakdown,
        'recommendations': recommendations,
        'tech_keywords': tech_keywords
    }

def generate_recommendations(job_matches, section_analyses, ats_score):
    """Generate prioritized recommendations"""
    recs = {'critical': [], 'high': [], 'medium': []}
    best_match_data = max(job_matches.values(), key=lambda x: x['score'])
    
    if best_match_data['missing_required']:
        recs['critical'].append(f"🚨 Add missing critical keywords: {', '.join(best_match_data['missing_required'][:3])}")
    
    for name, analysis in section_analyses.items():
        if analysis['improvement_priority'] == 'CRITICAL' and analysis['issues']:
            recs['critical'].append(f"🚨 Fix {name} section: {analysis['issues'][0].split(': ', 1)[1]}")

    if ats_score < 70:
        recs['high'].append("⚡ Increase technical keyword density throughout resume")
    recs['high'].extend([
        "📈 Add more quantifiable metrics and achievements",
        "💪 Increase action verb usage in experience descriptions",
        "🎯 Expand technical skills section with relevant technologies"
    ])
    if best_match_data['missing_preferred']:
        recs['high'].append(f"⭐ Consider adding preferred keywords: {', '.join(best_match_data['missing_preferred'][:3])}")

    recs['medium'].extend([
        "✨ Optimize formatting and visual consistency",
        "🔗 Add portfolio/GitHub links if missing",
        "📚 Include relevant certifications or recent courses",
        "🎨 Tailor summary/objective for target roles",
        "📊 Ensure consistent bullet point formatting"
    ])
    return recs

@app.route('/download/<report_id>')
def download_report(report_id):
    """Download the detailed analysis report"""
    try:
        report_filename = f"{secure_filename(report_id)}_analysis_report.txt"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"resume_analysis_report.txt",
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({'error': 'Failed to download report'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Resume Analyzer API is running'})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 10MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or fallback to 5000 locally
    print("🚀 Starting Resume Analyzer Web Application...")
    print(f"📊 Server will be available at: http://0.0.0.0:{port}")
    print("💡 Make sure to place advanced_resume_analyzer.py in the same directory")
    print("📋 Supported file types: PDF, TXT")
    print("🔧 Maximum file size: 10MB")
    print("-" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)

