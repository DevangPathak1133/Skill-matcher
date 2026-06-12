from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import tempfile
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdfminer.high_level import extract_text
import docx

app = Flask(__name__)

# Curated technical skills keywords
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'js', 'typescript', 'ts', 'csharp', 'c#', 'cpp', 'c++',
    'go', 'rust', 'kotlin', 'scala', 'r', 'php', 'ruby', 'swift', 'objc', 'objective-c',
    'perl', 'haskell', 'erlang', 'elixir', 'clojure', 'julia',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'cassandra', 'redis', 'elasticsearch',
    'dynamodb', 'firestore', 'mariadb', 'sqlserver', 'neo4j', 'couchdb', 'memcached',
    
    # Web Frameworks
    'django', 'flask', 'fastapi', 'spring', 'springboot', 'react', 'vue', 'angular',
    'nextjs', 'nuxt', 'express', 'nodejs', 'node.js', 'asp.net', 'aspnet', 'rails', 'ruby on rails',
    
    # Cloud Platforms
    'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'linode', 'kubernetes', 'k8s',
    'docker', 'jenkins', 'gitlab', 'github', 'bitbucket',
    
    # Big Data & Analytics
    'hadoop', 'spark', 'hive', 'pig', 'kafka', 'airflow', 'etl', 'tableau', 'powerbi',
    'looker', 'qlik', 'datawarehouse', 'snowflake', 'bigquery',
    
    # ML & AI
    'tensorflow', 'pytorch', 'keras', 'sklearn', 'scikit-learn', 'nlp', 'cv', 'openai',
    'deep learning', 'machine learning', 'ai', 'mlops', 'huggingface',
    
    # DevOps & Tools
    'linux', 'windows', 'git', 'svn', 'maven', 'gradle', 'npm', 'pip', 'terraform',
    'ansible', 'puppet', 'vagrant', 'ci/cd', 'junit', 'pytest', 'selenium', 'jira',
    
    # APIs & Protocols
    'rest', 'graphql', 'grpc', 'soap', 'json', 'xml', 'http', 'https', 'api', 'oauth',
    
    # Other Tools
    'git', 'svn', 'vim', 'vscode', 'intellij', 'eclipse', 'postman', 'swagger',
    'junit', 'pytest', 'mocha', 'jasmine'
}


def extract_text_from_file(fp, filename):
    name = filename.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(name)[1]) as tmp:
        tmp.write(fp.read())
        tmp.flush()
        tmp_path = tmp.name

    text = ""
    try:
        if name.endswith('.pdf'):
            text = extract_text(tmp_path)
        elif name.endswith('.docx'):
            doc = docx.Document(tmp_path)
            paragraphs = [p.text for p in doc.paragraphs]
            text = '\n'.join(paragraphs)
        else:
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return text


def extract_keywords(text):
    """Extract technical keywords from text."""
    text_lower = text.lower()
    # Normalize common variations
    text_lower = text_lower.replace('c++', 'cpp').replace('c#', 'csharp')
    text_lower = text_lower.replace('node.js', 'nodejs').replace('ruby on rails', 'rails')
    
    found_keywords = set()
    for skill in TECHNICAL_SKILLS:
        # Match whole words only
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_keywords.add(skill)
    
    return sorted(list(found_keywords))


def get_top_n_words(tfidf, feature_names, doc_index, n=10):
    row = tfidf[doc_index].toarray().ravel()
    topn_ids = row.argsort()[-n:][::-1]
    return [feature_names[i] for i in topn_ids if row[i] > 0]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/match', methods=['POST'])
def match():
    # Accept multiple job descriptions and multiple resumes
    jds = request.files.getlist('jds')
    resumes = request.files.getlist('resumes')

    if not jds or not resumes:
        return jsonify({'error': 'Please upload at least one JD and one resume.'}), 400

    jd_texts = []
    jd_names = []
    jd_keywords_list = []
    for f in jds:
        jd_names.append(secure_filename(f.filename))
        text = extract_text_from_file(f.stream, f.filename)
        jd_texts.append(text)
        jd_keywords_list.append(extract_keywords(text))

    resume_texts = []
    resume_names = []
    resume_keywords_list = []
    for f in resumes:
        resume_names.append(secure_filename(f.filename))
        text = extract_text_from_file(f.stream, f.filename)
        resume_texts.append(text)
        resume_keywords_list.append(extract_keywords(text))

    results = []
    for i, jd_keywords in enumerate(jd_keywords_list):
        scores = []
        jd_set = set(jd_keywords)
        
        for j, resume_keywords in enumerate(resume_keywords_list):
            resume_set = set(resume_keywords)
            
            # Calculate overlap
            overlap = list(jd_set & resume_set)
            
            # Calculate match score: (overlap / jd_required) * 100
            if len(jd_set) > 0:
                match_score = (len(overlap) / len(jd_set)) * 100
            else:
                match_score = 0
            
            # Calculate coverage: how many JD skills are in resume
            coverage = len(overlap)
            
            # Calculate missing skills
            missing = list(jd_set - resume_set)
            
            # Calculate extra skills in resume (bonus)
            extra = list(resume_set - jd_set)
            
            scores.append({
                'resume': resume_names[j],
                'match_percentage': round(match_score, 2),
                'coverage': coverage,
                'total_required': len(jd_set),
                'matched_skills': overlap,
                'missing_skills': missing,
                'extra_skills': extra,
                'resume_total_skills': len(resume_set)
            })
        
        # sort by match_percentage desc
        scores = sorted(scores, key=lambda x: x['match_percentage'], reverse=True)
        results.append({
            'jd': jd_names[i],
            'required_skills': jd_keywords,
            'matches': scores
        })

    return jsonify({'results': results})


if __name__ == '__main__':
    import os
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)
