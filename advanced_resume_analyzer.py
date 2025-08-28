#!/usr/bin/env python3
"""
Advanced Resume Intelligence System
Comprehensive analysis with job profile matching and detailed recommendations
"""

import re
import os
import argparse
import sys
from collections import defaultdict, Counter
import pdfplumber

# Job Profile Definitions with Required Keywords
JOB_PROFILES = {
    'software_engineer': {
        'title': 'Software Engineer',
        'required_keywords': [
            'python', 'java', 'javascript', 'c++', 'algorithms', 'data structures',
            'git', 'github', 'api', 'sql', 'database', 'testing', 'debugging',
            'agile', 'scrum', 'ci/cd', 'docker', 'kubernetes'
        ],
        'preferred_keywords': [
            'leetcode', 'system design', 'microservices', 'aws', 'azure', 'gcp',
            'redis', 'mongodb', 'postgresql', 'linux', 'bash'
        ],
        'action_verbs': [
            'developed', 'implemented', 'designed', 'optimized', 'built', 'created',
            'integrated', 'deployed', 'tested', 'debugged', 'maintained'
        ]
    },
    'web_developer': {
        'title': 'Web Developer',
        'required_keywords': [
            'html', 'css', 'javascript', 'react', 'node.js', 'express',
            'mongodb', 'sql', 'api', 'rest', 'git', 'responsive', 'bootstrap'
        ],
        'preferred_keywords': [
            'next.js', 'vue.js', 'angular', 'typescript', 'sass', 'webpack',
            'tailwind', 'figma', 'ui/ux', 'jquery', 'php', 'laravel'
        ],
        'action_verbs': [
            'designed', 'developed', 'built', 'created', 'implemented',
            'optimized', 'enhanced', 'crafted', 'styled', 'deployed'
        ]
    },
    'frontend_developer': {
        'title': 'Frontend Developer',
        'required_keywords': [
            'html', 'css', 'javascript', 'react', 'vue.js', 'angular',
            'typescript', 'sass', 'webpack', 'responsive', 'ui/ux'
        ],
        'preferred_keywords': [
            'next.js', 'redux', 'tailwind', 'bootstrap', 'figma', 'adobe',
            'jquery', 'babel', 'eslint', 'git', 'npm', 'yarn'
        ],
        'action_verbs': [
            'designed', 'crafted', 'built', 'developed', 'styled', 'created',
            'implemented', 'enhanced', 'optimized', 'delivered'
        ]
    },
    'backend_developer': {
        'title': 'Backend Developer',
        'required_keywords': [
            'python', 'java', 'node.js', 'express', 'flask', 'django',
            'api', 'rest', 'sql', 'mongodb', 'postgresql', 'redis'
        ],
        'preferred_keywords': [
            'microservices', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'graphql', 'rabbitmq', 'kafka', 'nginx', 'linux', 'bash'
        ],
        'action_verbs': [
            'developed', 'implemented', 'built', 'designed', 'optimized',
            'deployed', 'integrated', 'maintained', 'scaled', 'architected'
        ]
    },
    'ml_engineer': {
        'title': 'ML/AI Engineer',
        'required_keywords': [
            'python', 'tensorflow', 'pytorch', 'machine learning', 'deep learning',
            'pandas', 'numpy', 'scikit-learn', 'data science', 'statistics'
        ],
        'preferred_keywords': [
            'keras', 'opencv', 'nlp', 'computer vision', 'jupyter', 'colab',
            'aws', 'azure', 'gcp', 'docker', 'mlops', 'airflow'
        ],
        'action_verbs': [
            'trained', 'developed', 'implemented', 'analyzed', 'optimized',
            'researched', 'designed', 'deployed', 'evaluated', 'experimented'
        ]
    },
    'data_scientist': {
        'title': 'Data Scientist',
        'required_keywords': [
            'python', 'r', 'sql', 'pandas', 'numpy', 'matplotlib', 'seaborn',
            'statistics', 'machine learning', 'data analysis', 'visualization'
        ],
        'preferred_keywords': [
            'tableau', 'power bi', 'jupyter', 'colab', 'spark', 'hadoop',
            'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'scikit-learn'
        ],
        'action_verbs': [
            'analyzed', 'researched', 'investigated', 'discovered', 'modeled',
            'predicted', 'visualized', 'interpreted', 'evaluated', 'optimized'
        ]
    }
}

# Technical Categories for Analysis
TECH_CATEGORIES = {
    'programming_languages': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'dart', 'scala', 'r'
    ],
    'web_technologies': [
        'html', 'css', 'react', 'vue.js', 'angular', 'node.js', 'express',
        'next.js', 'nuxt.js', 'svelte', 'jquery', 'bootstrap', 'tailwind'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
        'cassandra', 'dynamodb', 'elasticsearch', 'neo4j'
    ],
    'cloud_platforms': [
        'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'vercel', 'netlify'
    ],
    'devops_tools': [
        'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
        'terraform', 'ansible', 'nginx', 'apache'
    ],
    'ml_ai_tools': [
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'opencv', 'huggingface', 'jupyter', 'colab'
    ]
}

# Industry benchmarks and standards
SECTION_BENCHMARKS = {
    'experience': {
        'min_words': 100,
        'ideal_words': 200,
        'min_action_verbs': 5,
        'min_metrics': 3
    },
    'projects': {
        'min_words': 80,
        'ideal_words': 150,
        'min_tech_terms': 5,
        'min_metrics': 2
    },
    'skills': {
        'min_tech_terms': 10,
        'ideal_tech_terms': 20
    },
    'achievements': {
        'min_metrics': 5,
        'ideal_metrics': 10
    }
}

def clean_and_fix_text(text):
    """Advanced text cleaning and spacing fixes"""
    if not text:
        return ""
    
    # Fix common PDF extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # CamelCase
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)  # Letter-number
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)  # Number-letter
    text = re.sub(r'([.,:;!?])([A-Za-z])', r'\1 \2', text)  # Punctuation
    text = re.sub(r'([a-zA-Z])\(', r'\1 (', text)  # Before parentheses
    text = re.sub(r'\)([a-zA-Z])', r') \1', text)  # After parentheses
    text = re.sub(r'([a-zA-Z])([+\-])', r'\1 \2', text)  # Before operators
    text = re.sub(r'([+\-])([a-zA-Z])', r'\1 \2', text)  # After operators
    text = re.sub(r'\s{2,}', ' ', text)  # Multiple spaces
    text = re.sub(r'\s+([.,:;!?])', r'\1', text)  # Space before punctuation
    
    return text.strip()

def extract_resume_text(file_path):
    """Extract and clean text from PDF or TXT files"""
    if file_path.lower().endswith('.pdf'):
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([page.extract_text() or '' for page in pdf.pages])
            return clean_and_fix_text(text)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    elif file_path.lower().endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return clean_and_fix_text(f.read())
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return None
    else:
        print("Unsupported file format. Please use PDF or TXT files.")
        return None

def parse_resume_sections(text):
    """Advanced section parsing with better detection"""
    sections = {}
    
    section_patterns = {
        'contact': r'(contact|personal|info)',
        'summary': r'(summary|profile|objective|about)',
        'education': r'(education|academic|degree|university|college|school)',
        'experience': r'(experience|employment|work|career|internship|intern)',
        'projects': r'(projects?|portfolio|work)',
        'skills': r'(skills?|technical|competencies|technologies|tools)',
        'achievements': r'(achievements?|awards?|accomplishments?|certifications?|honors?)',
        'languages': r'(languages?|linguistic)',
        'interests': r'(interests?|hobbies|activities)'
    }
    
    lines = text.split('\n')
    current_section = 'header'
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        is_section_header = False
        line_words = line.lower().split()
        
        for section_name, pattern in section_patterns.items():
            if (re.search(pattern, line.lower()) and 
                len(line_words) <= 4 and 
                not any(char.isdigit() for char in line)):
                
                if current_content:
                    sections[current_section] = current_content
                current_section = section_name
                current_content = []
                is_section_header = True
                break
        
        if not is_section_header:
            current_content.append(line)
    
    # Add the last section
    if current_content:
        sections[current_section] = current_content
    
    return sections

def analyze_technical_keywords(text):
    """Analyze technical keywords by category"""
    text_lower = text.lower()
    found_keywords = {}
    
    for category, keywords in TECH_CATEGORIES.items():
        found = [kw for kw in keywords if kw.lower() in text_lower]
        if found:
            found_keywords[category] = found
    
    return found_keywords

def calculate_job_profile_match(text, sections):
    """Calculate match percentage for each job profile"""
    text_lower = text.lower()
    matches = {}
    
    for profile_id, profile in JOB_PROFILES.items():
        required_found = sum(1 for kw in profile['required_keywords'] if kw in text_lower)
        preferred_found = sum(1 for kw in profile['preferred_keywords'] if kw in text_lower)
        action_verbs_found = sum(1 for verb in profile['action_verbs'] if verb in text_lower)
        
        # Calculate match percentage
        required_score = (required_found / len(profile['required_keywords'])) * 60
        preferred_score = (preferred_found / len(profile['preferred_keywords'])) * 25
        action_verb_score = (action_verbs_found / len(profile['action_verbs'])) * 15
        
        total_score = required_score + preferred_score + action_verb_score
        
        # Find missing keywords
        missing_required = [kw for kw in profile['required_keywords'] if kw not in text_lower]
        missing_preferred = [kw for kw in profile['preferred_keywords'] if kw not in text_lower]
        
        matches[profile_id] = {
            'title': profile['title'],
            'score': round(total_score, 1),
            'required_found': required_found,
            'required_total': len(profile['required_keywords']),
            'preferred_found': preferred_found,
            'preferred_total': len(profile['preferred_keywords']),
            'action_verbs_found': action_verbs_found,
            'missing_required': missing_required[:10],  # Top 10 missing
            'missing_preferred': missing_preferred[:10]
        }
    
    return matches

def analyze_section_details(section_name, content):
    """Enhanced detailed analysis of each section with industry benchmarks"""
    analysis = {
        'word_count': 0,
        'sentence_count': 0,
        'action_verbs': [],
        'technical_terms': [],
        'numbers_metrics': [],
        'issues': [],
        'strengths': [],
        'recommendations': [],
        'industry_insights': [],
        'improvement_priority': 'Medium',
        'benchmark_score': 0
    }
    
    if not content:
        analysis['issues'].append("❌ CRITICAL: Section is completely empty")
        analysis['improvement_priority'] = 'CRITICAL'
        return analysis
    
    full_text = ' '.join(content)
    words = full_text.split()
    analysis['word_count'] = len(words)
    analysis['sentence_count'] = len([s for s in full_text.split('.') if s.strip()])
    
    # Find action verbs
    for verb_list in JOB_PROFILES.values():
        for verb in verb_list['action_verbs']:
            if verb.lower() in full_text.lower():
                analysis['action_verbs'].append(verb)
    analysis['action_verbs'] = list(set(analysis['action_verbs']))
    
    # Find technical terms
    for category, keywords in TECH_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in full_text.lower():
                analysis['technical_terms'].append(keyword)
    
    # Find numbers and metrics
    analysis['numbers_metrics'] = re.findall(r'\d+[%x+]?|\d+\.\d+[%]?', full_text)
    
    # Section-specific detailed analysis
    if section_name == 'experience':
        benchmark = SECTION_BENCHMARKS['experience']
        
        # Word count analysis
        if analysis['word_count'] < benchmark['min_words']:
            analysis['issues'].append(f"🚨 CRITICAL: Too brief ({analysis['word_count']} words) - Industry minimum: {benchmark['min_words']} words")
            analysis['improvement_priority'] = 'CRITICAL'
        elif analysis['word_count'] < benchmark['ideal_words']:
            analysis['issues'].append(f"⚠️ MODERATE: Could be more detailed ({analysis['word_count']} words) - Industry ideal: {benchmark['ideal_words']} words")
        else:
            analysis['strengths'].append(f"✅ EXCELLENT: Good length ({analysis['word_count']} words)")
        
        # Action verbs analysis
        if len(analysis['action_verbs']) < benchmark['min_action_verbs']:
            analysis['issues'].append(f"🚨 CRITICAL: Insufficient action verbs ({len(analysis['action_verbs'])}) - Need minimum: {benchmark['min_action_verbs']}")
            analysis['improvement_priority'] = 'CRITICAL'
        else:
            analysis['strengths'].append(f"✅ GOOD: Strong action verbs usage ({len(analysis['action_verbs'])} found)")
        
        # Metrics analysis
        if len(analysis['numbers_metrics']) < benchmark['min_metrics']:
            analysis['issues'].append(f"⚠️ MODERATE: Lacks quantifiable achievements ({len(analysis['numbers_metrics'])}) - Need minimum: {benchmark['min_metrics']}")
        else:
            analysis['strengths'].append(f"✅ EXCELLENT: Good quantification ({len(analysis['numbers_metrics'])} metrics)")
        
        # Industry-specific recommendations
        analysis['recommendations'].extend([
            "📈 Add specific metrics (increased efficiency by X%, reduced costs by $Y)",
            "🎯 Use STAR method (Situation, Task, Action, Result) for each bullet point",
            "💡 Include technologies used in each role",
            "📊 Quantify team size, project scope, or impact where possible"
        ])
        
        analysis['industry_insights'].extend([
            "🏢 Recruiters spend 6 seconds scanning experience section - make it count",
            "📈 Quantified achievements are 40% more likely to get interviews",
            "🎯 Action verbs should start 80% of your experience bullets",
            "💼 Include company context if working at lesser-known organizations"
        ])
    
    elif section_name == 'skills':
        benchmark = SECTION_BENCHMARKS['skills']
        
        if len(analysis['technical_terms']) < benchmark['min_tech_terms']:
            analysis['issues'].append(f"⚠️ MODERATE: Limited technical skills ({len(analysis['technical_terms'])}) - Industry minimum: {benchmark['min_tech_terms']}")
        elif len(analysis['technical_terms']) >= benchmark['ideal_tech_terms']:
            analysis['strengths'].append(f"✅ EXCELLENT: Comprehensive technical skills ({len(analysis['technical_terms'])} found)")
        else:
            analysis['strengths'].append(f"✅ GOOD: Decent technical skills coverage ({len(analysis['technical_terms'])} found)")
        
        analysis['recommendations'].extend([
            "🔧 Organize skills by categories (Languages, Frameworks, Tools, etc.)",
            "⭐ Highlight your strongest/most relevant skills first",
            "📚 Add proficiency levels (Beginner/Intermediate/Advanced) if space allows",
            "🎯 Align skills with job requirements you're targeting"
        ])
        
        analysis['industry_insights'].extend([
            "🤖 ATS systems heavily weight technical skills matching",
            "📊 Include both hard and soft skills for balanced profile",
            "🔄 Keep skills section updated with latest technologies",
            "💡 Skills section is often the first place recruiters look"
        ])
    
    elif section_name == 'projects':
        benchmark = SECTION_BENCHMARKS['projects']
        
        if analysis['word_count'] < benchmark['min_words']:
            analysis['issues'].append(f"⚠️ MODERATE: Projects need more detailed descriptions ({analysis['word_count']} words)")
        
        if len(analysis['technical_terms']) < benchmark['min_tech_terms']:
            analysis['issues'].append(f"🚨 CRITICAL: Missing technical stack details ({len(analysis['technical_terms'])} terms)")
            analysis['improvement_priority'] = 'HIGH'
        
        if len(analysis['numbers_metrics']) < benchmark['min_metrics']:
            analysis['issues'].append("💡 SUGGESTION: Add project metrics (users, performance improvements, etc.)")
        
        analysis['recommendations'].extend([
            "🚀 Include live demo links and GitHub repositories",
            "🛠️ Describe technical challenges and how you solved them",
            "📊 Add project impact metrics (users, performance, etc.)",
            "🎯 Highlight your specific role and contributions"
        ])
        
        analysis['industry_insights'].extend([
            "💼 Projects often matter more than GPA for technical roles",
            "🔗 Include portfolio links - 65% of recruiters check them",
            "🎯 Show progression in project complexity over time",
            "💡 Personal projects demonstrate passion and initiative"
        ])
    
    elif section_name == 'achievements':
        benchmark = SECTION_BENCHMARKS['achievements']
        
        if len(analysis['numbers_metrics']) < benchmark['min_metrics']:
            analysis['issues'].append(f"⚠️ MODERATE: Need more quantified achievements ({len(analysis['numbers_metrics'])}) - Target: {benchmark['min_metrics']}+")
        else:
            analysis['strengths'].append(f"✅ EXCELLENT: Well-quantified achievements ({len(analysis['numbers_metrics'])} metrics)")
        
        analysis['recommendations'].extend([
            "🏆 Include academic honors, competition wins, certifications",
            "📈 Add context to achievements (out of how many participants?)",
            "🎯 Prioritize achievements relevant to target role",
            "💡 Include recent online course completions or certifications"
        ])
    
    elif section_name == 'education':
        # Enhanced GPA/CGPA detection and recommendation logic
        text_lower = full_text.lower()
        
        # Check for existing GPA/CGPA mentions
        has_gpa = any(term in text_lower for term in ['gpa', 'cgpa', 'grade point', 'cumulative'])
        
        # Extract any numerical grades mentioned
        grade_patterns = [
            r'gpa[:\s]*(\d+\.?\d*)',
            r'cgpa[:\s]*(\d+\.?\d*)',
            r'grade[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*/\s*10',
            r'(\d+\.?\d*)\s*/\s*4'
        ]
        
        extracted_grades = []
        for pattern in grade_patterns:
            matches = re.findall(pattern, text_lower)
            extracted_grades.extend(matches)
        
        # Analyze grades and provide recommendations
        if has_gpa and extracted_grades:
            try:
                # Convert found grades to float and analyze
                numeric_grades = [float(grade) for grade in extracted_grades if grade.replace('.', '').isdigit()]
                if numeric_grades:
                    max_grade = max(numeric_grades)
                    
                    # Determine if it's good based on scale
                    if max_grade >= 8.0 and max_grade <= 10.0:  # CGPA out of 10
                        analysis['strengths'].append(f"✅ EXCELLENT: Strong CGPA ({max_grade}/10) prominently displayed")
                    elif max_grade >= 3.5 and max_grade <= 4.0:  # GPA out of 4
                        analysis['strengths'].append(f"✅ EXCELLENT: Strong GPA ({max_grade}/4.0) prominently displayed")
                    elif max_grade >= 6.0 and max_grade < 8.0:  # Lower CGPA
                        analysis['recommendations'].append("📊 Consider highlighting other academic achievements since CGPA is moderate")
                    elif max_grade >= 2.5 and max_grade < 3.5:  # Lower GPA
                        analysis['recommendations'].append("📊 Focus on projects and skills rather than GPA")
            except ValueError:
                pass
        
        elif not has_gpa:
            # No GPA mentioned - provide conditional recommendation
            analysis['recommendations'].append("📊 Add CGPA/GPA only if 8.0+ out of 10 (or 3.5+ out of 4.0) - strong grades boost profile")
            analysis['industry_insights'].append("🎯 Good CGPA (8.0+/10) can significantly strengthen entry-level applications")
        
        # Standard education recommendations
        analysis['recommendations'].extend([
            "🎓 Include relevant coursework for entry-level positions",
            "🏆 Highlight academic honors, dean's list, scholarships",
            "📚 Include major projects or thesis topics if relevant",
            "💼 Add internships or academic projects in this section"
        ])
        
        analysis['industry_insights'].extend([
            "🎯 Education matters most for entry-level positions",
            "📈 Relevant coursework can substitute for work experience",
            "💡 Include online certifications and bootcamps",
            "🔄 Recent graduates should put education before experience"
        ])
    
    # Calculate benchmark score
    score_factors = []
    if section_name in SECTION_BENCHMARKS:
        benchmark = SECTION_BENCHMARKS[section_name]
        if 'min_words' in benchmark:
            score_factors.append(min(analysis['word_count'] / benchmark['ideal_words'], 1.0) * 30)
        if 'min_tech_terms' in benchmark:
            score_factors.append(min(len(analysis['technical_terms']) / benchmark.get('ideal_tech_terms', benchmark['min_tech_terms']), 1.0) * 25)
        if 'min_action_verbs' in benchmark:
            score_factors.append(min(len(analysis['action_verbs']) / benchmark['min_action_verbs'], 1.0) * 25)
        if 'min_metrics' in benchmark:
            score_factors.append(min(len(analysis['numbers_metrics']) / benchmark.get('ideal_metrics', benchmark['min_metrics']), 1.0) * 20)
    
    analysis['benchmark_score'] = sum(score_factors) if score_factors else 75
    
    return analysis

def calculate_comprehensive_ats_score(text, sections, job_matches):
    """Enhanced ATS scoring with detailed breakdown"""
    scores = {
        'technical_keywords': 0,
        'action_verbs': 0,
        'quantification': 0,
        'formatting': 0,
        'completeness': 0,
        'job_relevance': 0
    }
    
    text_lower = text.lower()
    
    # Technical keywords (25 points)
    all_tech_keywords = [kw for cat in TECH_CATEGORIES.values() for kw in cat]
    matched_tech = [kw for kw in all_tech_keywords if kw in text_lower]
    scores['technical_keywords'] = min(len(matched_tech) * 1.5, 25)
    
    # Action verbs (20 points)
    all_action_verbs = set()
    for profile in JOB_PROFILES.values():
        all_action_verbs.update(profile['action_verbs'])
    
    action_verb_count = sum(1 for verb in all_action_verbs if verb in text_lower)
    scores['action_verbs'] = min(action_verb_count * 2, 20)
    
    # Quantification (20 points)
    numbers_count = len(re.findall(r'\d+[%x+]?|\d+\.\d+[%]?', text))
    scores['quantification'] = min(numbers_count * 2, 20)
    
    # Formatting (15 points)
    bullet_count = len(re.findall(r'[•\-\*]', text))
    scores['formatting'] = min(bullet_count * 1, 15)
    
    # Completeness (10 points)
    required_sections = ['education', 'experience', 'skills']
    present_sections = [s for s in required_sections if s in sections and sections[s]]
    scores['completeness'] = len(present_sections) * 3 + (1 if 'contact' in sections else 0)
    
    # Job relevance (10 points) - based on best job match
    best_match = max(job_matches.values(), key=lambda x: x['score'])
    scores['job_relevance'] = min(best_match['score'] / 10, 10)
    
    total_score = sum(scores.values())
    return total_score, scores

def generate_comprehensive_report(resume_text, output_file):
    """Generate the ultimate detailed resume analysis report"""
    sections = parse_resume_sections(resume_text)
    tech_keywords = analyze_technical_keywords(resume_text)
    job_matches = calculate_job_profile_match(resume_text, sections)
    ats_score, score_breakdown = calculate_comprehensive_ats_score(resume_text, sections, job_matches)
    
    # Get best job matches
    sorted_matches = sorted(job_matches.items(), key=lambda x: x[1]['score'], reverse=True)
    best_match = sorted_matches[0]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🎯 ADVANCED RESUME INTELLIGENCE REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Executive Summary
        f.write("📊 EXECUTIVE SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Overall ATS Score: {ats_score:.1f}/100\n")
        f.write(f"Best Job Match: {best_match[1]['title']} ({best_match[1]['score']:.1f}%)\n")
        f.write(f"Technical Keywords Found: {sum(len(keywords) for keywords in tech_keywords.values())}\n")
        f.write(f"Sections Analyzed: {len(sections)}\n")
        f.write(f"Total Word Count: {len(resume_text.split())}\n\n")
        
        # Score Interpretation with detailed feedback
        if ats_score >= 90:
            f.write("🟢 OUTSTANDING - Your resume is exceptionally optimized and will pass most ATS systems\n")
            f.write("   💡 Focus on minor refinements and targeting specific job requirements\n")
        elif ats_score >= 80:
            f.write("🟢 EXCELLENT - Resume is highly optimized and ATS-friendly\n")
            f.write("   💡 Small improvements will make you a top candidate\n")
        elif ats_score >= 70:
            f.write("🟡 GOOD - Some improvements will significantly boost your success rate\n")
            f.write("   💡 Focus on technical keywords and quantifiable achievements\n")
        elif ats_score >= 55:
            f.write("🟠 FAIR - Significant improvements needed for better results\n")
            f.write("   💡 Major revision required in multiple areas\n")
        else:
            f.write("🔴 NEEDS MAJOR WORK - Comprehensive overhaul required for ATS compatibility\n")
            f.write("   💡 Consider professional resume review or complete rewrite\n")
        f.write("\n")
        
        # Detailed Score Breakdown with explanations
        f.write("📈 DETAILED ATS SCORE BREAKDOWN\n")
        f.write("-" * 50 + "\n")
        for category, score in score_breakdown.items():
            category_name = category.replace('_', ' ').title()
            percentage = (score / (25 if 'keywords' in category else 20 if category in ['action_verbs', 'quantification'] else 15 if 'formatting' in category else 10)) * 100
            
            f.write(f"  {category_name}: {score:.1f} points ({percentage:.0f}%)\n")
            
            # Add specific feedback for each category
            if category == 'technical_keywords':
                f.write("    💡 Boost by: Adding more relevant technical skills and tools\n")
            elif category == 'action_verbs':
                f.write("    💡 Boost by: Starting more bullets with strong action verbs\n")
            elif category == 'quantification':
                f.write("    💡 Boost by: Adding more numbers, percentages, and metrics\n")
            elif category == 'formatting':
                f.write("    💡 Boost by: Using consistent bullet points and clear structure\n")
            elif category == 'completeness':
                f.write("    💡 Boost by: Ensuring all key sections are present and detailed\n")
            elif category == 'job_relevance':
                f.write("    💡 Boost by: Better aligning content with target job requirements\n")
        f.write("\n")
        
        # Job Profile Analysis with detailed insights
        f.write("💼 COMPREHENSIVE JOB PROFILE COMPATIBILITY\n")
        f.write("-" * 60 + "\n")
        for i, (profile_id, match) in enumerate(sorted_matches, 1):
            f.write(f"{i}. {match['title']}: {match['score']:.1f}% compatibility\n")
            f.write(f"   ✅ Required keywords matched: {match['required_found']}/{match['required_total']} ({(match['required_found']/match['required_total']*100):.0f}%)\n")
            f.write(f"   ✅ Preferred keywords matched: {match['preferred_found']}/{match['preferred_total']} ({(match['preferred_found']/match['preferred_total']*100):.0f}%)\n")
            f.write(f"   ✅ Action verbs used: {match['action_verbs_found']} relevant\n")
            
            if match['missing_required']:
                f.write(f"   🚨 CRITICAL missing keywords: {', '.join(match['missing_required'][:5])}\n")
                if len(match['missing_required']) > 5:
                    f.write(f"   📝 Additional missing: {', '.join(match['missing_required'][5:])}\n")
            
            if match['missing_preferred']:
                f.write(f"   💡 Could strengthen by adding: {', '.join(match['missing_preferred'][:5])}\n")
                if len(match['missing_preferred']) > 5:
                    f.write(f"   💡 More suggestions: {', '.join(match['missing_preferred'][5:])}\n")
            
            # Add role-specific advice
            if i == 1:  # Best match
                f.write(f"   🎯 ROLE FOCUS: This is your strongest match - tailor applications for {match['title']} positions\n")
            elif match['score'] > 40:
                f.write(f"   🔄 POTENTIAL: With improvements, this could become a strong secondary target\n")
            
            f.write("\n")
        
        # Enhanced Technical Keywords by Category
        f.write("🔧 TECHNICAL KEYWORDS ANALYSIS BY CATEGORY\n")
        f.write("-" * 60 + "\n")
        for category, keywords in tech_keywords.items():
            category_name = category.replace('_', ' ').title()
            f.write(f"📂 {category_name} ({len(keywords)} found):\n")
            f.write(f"   ✅ Present: {', '.join(keywords)}\n")
            
            # Suggest missing keywords from the category
            all_category_keywords = TECH_CATEGORIES[category]
            missing = [kw for kw in all_category_keywords if kw not in [k.lower() for k in keywords]]
            if missing:
                f.write(f"   💡 Consider adding: {', '.join(missing[:5])}\n")
            f.write("\n")
        
        if not tech_keywords:
            f.write("⚠️ WARNING: No technical keywords detected! This is critical for technical roles.\n\n")
        
        # Section-by-Section Detailed Analysis
        f.write("📋 COMPREHENSIVE SECTION-BY-SECTION ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (section_name, content) in enumerate(sections.items(), 1):
            section_analysis = analyze_section_details(section_name, content)
            
            f.write(f"{i}. {section_name.upper()} SECTION DEEP DIVE\n")
            f.write("=" * (len(section_name) + 25) + "\n")
            
            # Core Metrics
            f.write("📊 CORE METRICS:\n")
            f.write(f"   • Word Count: {section_analysis['word_count']}\n")
            f.write(f"   • Sentence Count: {section_analysis['sentence_count']}\n")
            f.write(f"   • Technical Terms: {len(section_analysis['technical_terms'])}\n")
            f.write(f"   • Action Verbs: {len(set(section_analysis['action_verbs']))}\n")
            f.write(f"   • Metrics/Numbers: {len(section_analysis['numbers_metrics'])}\n")
            f.write(f"   • Benchmark Score: {section_analysis['benchmark_score']:.1f}/100\n")
            f.write(f"   • Improvement Priority: {section_analysis['improvement_priority']}\n\n")
            
            # Detailed Content Analysis
            if section_analysis['technical_terms']:
                f.write("🔧 TECHNICAL TERMS IDENTIFIED:\n")
                f.write(f"   {', '.join(section_analysis['technical_terms'])}\n\n")
            
            if section_analysis['action_verbs']:
                f.write("💪 ACTION VERBS FOUND:\n")
                f.write(f"   {', '.join(set(section_analysis['action_verbs']))}\n\n")
            
            if section_analysis['numbers_metrics']:
                f.write("📈 QUANTITATIVE DATA:\n")
                f.write(f"   {', '.join(section_analysis['numbers_metrics'])}\n\n")
            
            # Strengths
            if section_analysis['strengths']:
                f.write("✅ SECTION STRENGTHS:\n")
                for strength in section_analysis['strengths']:
                    f.write(f"   {strength}\n")
                f.write("\n")
            
            # Issues & Problems
            if section_analysis['issues']:
                f.write("⚠️ ISSUES REQUIRING ATTENTION:\n")
                for issue in section_analysis['issues']:
                    f.write(f"   {issue}\n")
                f.write("\n")
            
            # Specific Recommendations
            if section_analysis['recommendations']:
                f.write("💡 SPECIFIC IMPROVEMENT RECOMMENDATIONS:\n")
                for rec in section_analysis['recommendations']:
                    f.write(f"   {rec}\n")
                f.write("\n")
            
            # Industry Insights
            if section_analysis['industry_insights']:
                f.write("🏢 INDUSTRY INSIGHTS & BEST PRACTICES:\n")
                for insight in section_analysis['industry_insights']:
                    f.write(f"   {insight}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n\n")
        
        # Enhanced Final Verdict and Action Plan
        f.write("🏆 COMPREHENSIVE IMPROVEMENT ACTION PLAN\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"🎯 PRIMARY TARGET ROLE: {best_match[1]['title']}\n")
        f.write(f"🎯 CURRENT COMPATIBILITY: {best_match[1]['score']:.1f}%\n")
        f.write(f"🎯 POTENTIAL WITH IMPROVEMENTS: {min(best_match[1]['score'] + 20, 95):.1f}%\n\n")
        
        # Priority-based action items
        f.write("🚨 CRITICAL PRIORITY ACTIONS (Do First):\n")
        critical_actions = []
        if best_match[1]['missing_required']:
            critical_actions.append(f"Add missing critical keywords: {', '.join(best_match[1]['missing_required'][:3])}")
        
        # Check for critical section issues
        for section_name, content in sections.items():
            analysis = analyze_section_details(section_name, content)
            if analysis['improvement_priority'] == 'CRITICAL':
                critical_actions.append(f"Fix {section_name} section - {analysis['issues'][0]}")
        
        for i, action in enumerate(critical_actions[:5], 1):
            f.write(f"   {i}. {action}\n")
        f.write("\n")
        
        f.write("⚠️ HIGH PRIORITY ACTIONS (Do Next):\n")
        high_priority = [
            "Increase action verb usage throughout resume",
            "Add more quantifiable metrics and achievements",
            "Expand experience descriptions with technical details",
            f"Consider these additional keywords: {', '.join(best_match[1]['missing_preferred'][:3])}"
        ]
        for i, action in enumerate(high_priority, 1):
            f.write(f"   {i}. {action}\n")
        f.write("\n")
        
        f.write("💡 MEDIUM PRIORITY IMPROVEMENTS (Polish Phase):\n")
        medium_priority = [
            "Optimize formatting and visual consistency",
            "Add links to portfolio/GitHub if missing",
            "Include relevant certifications or courses",
            "Tailor summary/objective for specific roles"
        ]
        for i, action in enumerate(medium_priority, 1):
            f.write(f"   {i}. {action}\n")
        f.write("\n")
        
        # Success predictions
        f.write("📈 PREDICTED IMPROVEMENTS WITH CHANGES:\n")
        f.write(f"   🎯 ATS Score: {ats_score:.1f} → {min(ats_score + 15, 95):.1f} (+{min(15, 95-ats_score):.1f} points)\n")
        f.write(f"   💼 Job Match: {best_match[1]['score']:.1f}% → {min(best_match[1]['score'] + 20, 90):.1f}% (+{min(20, 90-best_match[1]['score']):.1f}%)\n")
        f.write(f"   📊 Interview Likelihood: +35% with critical fixes implemented\n\n")
        
        # Industry benchmarks comparison
        f.write("📊 HOW YOU COMPARE TO INDUSTRY STANDARDS:\n")
        total_words = len(resume_text.split())
        if total_words < 300:
            f.write("   📝 Resume Length: Below standard (aim for 400-600 words)\n")
        elif total_words > 800:
            f.write("   📝 Resume Length: Too long (aim for 400-600 words)\n")
        else:
            f.write("   📝 Resume Length: Good (within industry standards)\n")
        
        tech_count = sum(len(keywords) for keywords in tech_keywords.values())
        if tech_count < 10:
            f.write("   🔧 Technical Depth: Below average (aim for 15+ technical terms)\n")
        elif tech_count >= 20:
            f.write("   🔧 Technical Depth: Excellent (strong technical presence)\n")
        else:
            f.write("   🔧 Technical Depth: Good (solid technical foundation)\n")
        
        f.write("\n")
        f.write("✨ ANALYSIS COMPLETE - READY FOR OPTIMIZATION! ✨\n")
    
    return {
        'ats_score': ats_score,
        'best_job_match': best_match[1]['title'],
        'match_percentage': best_match[1]['score'],
        'sections_analyzed': len(sections),
        'tech_keywords_found': sum(len(keywords) for keywords in tech_keywords.values()),
        'total_words': len(resume_text.split()),
        'improvement_potential': min(ats_score + 15, 95)
    }

def generate_perfectly_formatted_resume(resume_text, output_file):
    """Generate perfectly formatted resume with proper spacing"""
    sections = parse_resume_sections(resume_text)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for section_name, content in sections.items():
            if section_name == 'header':
                # Header without title
                for line in content:
                    f.write(clean_and_fix_text(line) + "\n")
                f.write("\n")
            else:
                # Section with proper formatting
                f.write(f"{section_name.upper()}\n")
                f.write("=" * len(section_name) + "\n\n")
                
                for line in content:
                    cleaned_line = clean_and_fix_text(line)
                    
                    # Add bullets for appropriate sections
                    if section_name in ['experience', 'projects', 'achievements']:
                        if not cleaned_line.startswith(('•', '-', '*', '◦')):
                            cleaned_line = '• ' + cleaned_line
                    
                    f.write(cleaned_line + "\n")
                f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Advanced Resume Intelligence System")
    parser.add_argument("resume_file", help="Path to your resume (PDF or TXT)")
    parser.add_argument("-o", "--output", default="detailed_analysis", 
                       help="Output file prefix (default: detailed_analysis)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.resume_file):
        print(f"❌ Error: File '{args.resume_file}' not found.")
        sys.exit(1)
    
    print("🚀 Starting Advanced Resume Intelligence Analysis...")
    
    # Extract and clean text
    resume_text = extract_resume_text(args.resume_file)
    if not resume_text:
        print("❌ Error: Could not extract text from the file.")
        sys.exit(1)
    
    print("📖 Text extracted and cleaned successfully")
    
    # Generate comprehensive analysis
    analysis_file = f"{args.output}_intelligence_report.txt"
    
    print("🧠 Running comprehensive resume intelligence analysis...")
    result = generate_comprehensive_report(resume_text, analysis_file)
    
    print(f"\n🎯 COMPREHENSIVE ANALYSIS COMPLETE!")
    print(f"📊 ATS Score: {result['ats_score']:.1f}/100")
    print(f"💼 Best Job Match: {result['best_job_match']} ({result['match_percentage']:.1f}%)")
    print(f"🔧 Technical Keywords: {result['tech_keywords_found']} found")
    print(f"📝 Total Words: {result['total_words']}")
    print(f"📈 Improvement Potential: {result['improvement_potential']:.1f}/100")
    
    print(f"\n✅ Detailed Analysis Generated:")
    print(f"   📋 Comprehensive Report: {analysis_file}")
    
    # Final verdict with improvement potential
    current_score = result['ats_score']
    potential_score = result['improvement_potential']
    
    if current_score >= 85:
        print(f"\n🏆 VERDICT: OUTSTANDING! Your resume is ready for {result['best_job_match']} positions!")
    elif current_score >= 70:
        print(f"\n⭐ VERDICT: GOOD! With targeted improvements, you'll excel as a {result['best_job_match']}!")
        print(f"💡 Potential to reach {potential_score:.1f}/100 with recommended changes")
    else:
        print(f"\n🔧 VERDICT: NEEDS IMPROVEMENT! Focus on the critical actions to boost your {result['best_job_match']} profile!")
        print(f"💡 Strong potential to reach {potential_score:.1f}/100 with systematic improvements")

if __name__ == "__main__":
    main() 
