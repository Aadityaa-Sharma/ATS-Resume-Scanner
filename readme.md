# 🎯 AI Resume Intelligence Web Application

A comprehensive web-based resume analyzer that provides ATS scoring, job profile matching, and detailed optimization recommendations.

## ✨ Features

- **📊 ATS Score Analysis** - Get detailed ATS compatibility scoring
- **💼 Job Profile Matching** - Match your resume against 6+ tech job profiles
- **🔧 Technical Keyword Analysis** - Analyze technical skills by category
- **📋 Section-by-Section Analysis** - Detailed analysis of each resume section
- **🎯 Prioritized Recommendations** - Get critical, high, and medium priority action items
- **📥 Detailed Reports** - Download comprehensive analysis reports
- **🚀 Beautiful UI** - Modern, responsive web interface
- **⚡ Real-time Analysis** - Fast PDF processing and analysis

## 🚀 Quick Setup & Run

### Option 1: Automated Setup (Recommended)

1. **Download all files** to a single directory:
   - `advanced_resume_analyzer.py` (your existing analyzer)
   - `app.py` (Flask backend)
   - `index.html` (web interface)
   - `requirements.txt` (dependencies)
   - `setup_and_run.py` (setup script)

2. **Run the setup script**:
   ```bash
   python setup_and_run.py
   ```

3. **That's it!** The application will:
   - Check your Python version
   - Install required packages
   - Create necessary directories
   - Start the web server
   - Open your browser automatically

### Option 2: Manual Setup

1. **Install Python 3.7+** (if not already installed)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create directories**:
   ```bash
   mkdir uploads reports
   ```

4. **Start the server**:
   ```bash
   python app.py
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## 📁 File Structure

```
resume-analyzer/
├── advanced_resume_analyzer.py   # Your resume analysis engine
├── app.py                       # Flask web server
├── index.html                   # Web interface
├── requirements.txt             # Python dependencies
├── setup_and_run.py            # Automated setup script
├── README.md                    # This file
├── uploads/                     # Temporary file uploads
└── reports/                     # Generated reports
```

## 🔧 Dependencies

- **Flask 2.3.3** - Web framework
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **pdfplumber 0.9.0** - PDF text extraction
- **Werkzeug 2.3.7** - WSGI utilities

## 📖 How to Use

1. **Upload Resume**: Drag & drop or click to select your PDF resume
2. **Wait for Analysis**: The AI will analyze your resume (usually 10-30 seconds)
3. **Review Results**: Get comprehensive insights including:
   - Overall ATS score (/100)
   - Best job profile match
   - Technical keywords found
   - Improvement potential
4. **View Detailed Analysis**:
   - Job profile compatibility for 6+ roles
   - Section-by-section breakdown
   - Prioritized action plan
5. **Download Report**: Get a detailed text report with all findings

## 🎯 Supported Job Profiles

- **Software Engineer** - Full-stack development roles
- **Frontend Developer** - UI/UX focused positions
- **Backend Developer** - Server-side development
- **Web Developer** - General web development
- **ML/AI Engineer** - Machine learning and AI roles
- **Data Scientist** - Data analysis and research positions

## 📊 Analysis Features

### ATS Score Breakdown
- Technical keywords matching (25 points)
- Action verbs usage (20 points)
- Quantification metrics (20 points)
- Formatting quality (15 points)
- Section completeness (10 points)
- Job relevance (10 points)

### Section Analysis
- **Experience**: Word count, action verbs, metrics, technical details
- **Skills**: Technical keyword density, categorization
- **Projects**: Technical stack, quantifiable results
- **Education**: CGPA recommendations, relevant coursework
- **Achievements**: Quantified accomplishments

### Recommendations Engine
- **Critical Priority**: Must-fix issues that severely impact ATS scoring
- **High Priority**: Important improvements for better job matching
- **Medium Priority**: Polish and optimization suggestions

## 🔒 Privacy & Security

- Files are processed locally on your machine
- Uploaded files are automatically deleted after analysis
- No data is sent to external services
- Reports are stored locally and can be deleted anytime

## 🚀 Performance

- **Fast Processing**: Most resumes analyzed in under 30 seconds
- **Memory Efficient**: Minimal system resource usage
- **Scalable**: Can handle multiple concurrent analyses

## 🛠️ Troubleshooting

### Common Issues:

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**"Port already in use" error:**
- Close other applications using port 5000
- Or modify the port in `app.py` (line with `app.run(port=5000)`)

**PDF extraction fails:**
- Ensure the PDF is not password-protected
- Try converting to a different PDF format
- Check if the PDF contains selectable text

**Browser doesn't open automatically:**
- Manually navigate to `http://localhost:5000`

### Getting Help:

1. Check the terminal/command prompt for error messages
2. Ensure all files are in the same directory
3. Verify Python version is 3.7 or higher
4. Make sure no antivirus is blocking the application

## 🎨 Customization

### Adding New Job Profiles:
Edit the `JOB_PROFILES` dictionary in `advanced_resume_analyzer.py`

### Modifying UI:
Update the HTML/CSS in `index.html`

### Changing Analysis Logic:
Modify functions in `advanced_resume_analyzer.py`

## 📈 Future Enhancements

- Support for DOCX files
- Multiple language support
- Integration with job boards
- Resume builder functionality
- Advanced AI recommendations
- Batch processing capability

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make improvements
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## ⭐ Features Highlight

- **🎯 Precision**: Industry-standard ATS scoring algorithm
- **🚀 Speed**: Real-time analysis and feedback
- **💡 Insights**: Actionable, prioritized recommendations
- **📱 Responsive**: Works on desktop, tablet, and mobile
- **🔧 Extensible**: Easy to customize and extend
- **🛡️ Secure**: All processing done locally

---

## 🎉 Ready to Optimize Your Resume?

Run the application and start getting professional-grade resume insights in minutes!

```bash
python setup_and_run.py
```

**Happy Job Hunting! 🚀**