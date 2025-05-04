import pandas as pd
import os
import docx
import PyPDF2
import re
from fastapi import UploadFile
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

STOPWORDS = {
    "com", "www", "edu", "the", "and", "for", "are", "can", "etc", "of", "in", "to", "a", "is",
    "with", "on", "as", "by", "an", "be", "from", "that", "at", "or", "this", "it", "up", "your", "you",
    "we", "us", "our", "about", "into", "their", "they", "will", "all", "also" , "." , "student" , "edu" , "education", "learning", "microsoft", "alexandria"
}

LOW_VALUE_TERMS = {
    "student", "education", "experience", "training", "learning"
}

class CVMatcher:
    def __init__(self):
        self.data_path = os.path.join("static", "job_data.csv")
        self.df, self.error = self.load_data()
        if self.error:
            raise ValueError(self.error)
        self.all_skills = self.get_all_skills()

    def load_data(self):
        if not os.path.exists(self.data_path):
            return pd.DataFrame(), f"File not found: {self.data_path}"

        df = pd.read_csv(self.data_path)

        required_columns = ['Job Title', 'skills', 'Governorate']
        for col in required_columns:
            if col not in df.columns:
                return pd.DataFrame(), f"Missing column: {col}"

        level_column = 'professional level' if 'professional level' in df.columns else 'professional Level'
        if level_column not in df.columns:
            return pd.DataFrame(), "Missing professional level column"

        return df, None

    def extract_text_from_cv(self, file: UploadFile):
        text = ""
        ext = file.filename.split('.')[-1].lower()
        try:
            if ext == 'pdf':
                reader = PyPDF2.PdfReader(file.file)
                for page in reader.pages:
                    text += page.extract_text() or ""
            elif ext == 'docx':
                doc = docx.Document(file.file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif ext == 'txt':
                text = file.file.read().decode("utf-8")
            else:
                return None, f"Unsupported file type: {ext}"
            return text, None
        except Exception as e:
            return None, str(e)

    def extract_skills(self, text):
        if not text:
            return []
        text_lower = text.lower()
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text_lower)
        words = clean_text.split()
        clean_words = [w for w in words if len(w) > 2 and w not in STOPWORDS and not any(char.isdigit() for char in w)]
        found_skills = []
        for skill in self.all_skills:
            skill_lower = skill.lower()
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', text_lower):
                found_skills.append(skill)
        return list(set(found_skills))

    def calculate_similarity(self, user_skills, job_skills):
        if not user_skills or not job_skills:
            return 0.0
        vectorizer = CountVectorizer().fit([' '.join(user_skills + job_skills)])
        skill_vectors = vectorizer.transform([' '.join(user_skills), ' '.join(job_skills)])
        similarity = cosine_similarity(skill_vectors)[0][1]
        return round(similarity * 100, 1)

    def analyze_skills(self, user_skills, job_skills):
        user_set = set([s.lower() for s in user_skills])
        matched = [s for s in job_skills if s.lower() in user_set and s.lower() not in LOW_VALUE_TERMS]
        missing = [s for s in job_skills if s.lower() not in user_set]
        total = len(matched) + len(missing)
        return matched, missing, round(len(matched)/total*100, 1) if total else 0.0, round(len(missing)/total*100, 1) if total else 0.0

    def get_all_skills(self):
        all_skills = []
        for skill_text in self.df['skills']:
            skills = [s.strip() for s in str(skill_text).split(',')]
            all_skills.extend(skills)
        return list(set(all_skills))

    def process_cv(self, file: UploadFile):
        cv_text, error = self.extract_text_from_cv(file)
        if error:
            return {"error": error}

        user_skills = self.extract_skills(cv_text)
        if not user_skills:
            return {"cv_skills": [], "top_matches": [], "bar_chart_data": []}

        all_matches = []
        seen_combinations = set()

        for _, row in self.df.iterrows():
            job_skills = [s.strip() for s in str(row['skills']).split(',') if s.strip()]
            similarity = self.calculate_similarity(user_skills, job_skills)
            matched, missing, match_pct, miss_pct = self.analyze_skills(user_skills, job_skills)
            key = (frozenset(matched), frozenset(missing))
            if key in seen_combinations:
                continue
            seen_combinations.add(key)

            all_matches.append({
                "job_title": row['Job Title'],
                "governorate": row['Governorate'],
                "professional_level": row.get('professional level', row.get('professional Level')),
                "similarity_percentage": similarity,
                "matched_skills": matched,
                "missing_skills": missing,
                "pie_chart_data": {
                    "matched": len(matched),
                    "missing": len(missing),
                    "matched_percentage": match_pct,
                    "missing_percentage": miss_pct
                }
            })

        top_matches = sorted(all_matches, key=lambda x: x['similarity_percentage'], reverse=True)[:3]
        bar_chart_data = {
            "job_titles": [match['job_title'] for match in top_matches],
            "similarities": [match['similarity_percentage'] for match in top_matches]
        }

        return {
            "cv_skills": user_skills,
            "top_matches": top_matches,
            "bar_chart_data": bar_chart_data
        }
