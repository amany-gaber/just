import os
import re
import pandas as pd
import PyPDF2
import docx
import nltk
from fastapi import UploadFile
from io import BytesIO

# Download NLTK data (punkt for tokenization)
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f"Warning: Failed to download NLTK punkt: {e}")

# Constants
STOPWORDS = set([
    "a", "the", "of", "and", "to", "up", "i", "com", "student", "education", "experience"
])

class JobMatcher:
    def __init__(self):
        # Resolve the path to job_data.csv relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = '/home/yaz/specific_job/api/src/static/job_data.csv'
        self.df, self.error = self.load_data()
        if self.error:
            raise ValueError(self.error)
        self.all_skills = self.get_all_skills()

    def load_data(self):
        try:
            if not os.path.exists(self.data_path):
                return pd.DataFrame(), f"File not found: {self.data_path}"
            df = pd.read_csv(self.data_path)
            required_columns = ['Job Title', 'skills', 'Governorate']
            for col in required_columns:
                if col not in df.columns:
                    return pd.DataFrame(), f"Missing column: {col}"
            level_col = 'professional level' if 'professional level' in df.columns else 'professional Level'
            if level_col not in df.columns:
                return pd.DataFrame(), "Missing professional level column"
            return df, None
        except Exception as e:
            return pd.DataFrame(), f"Error loading data: {e}"

    def extract_text_from_cv(self, file: UploadFile):
        text = ""
        ext = file.filename.split('.')[-1].lower()
        try:
            file_content = file.file.read()  # Read file content into memory
            if ext == 'pdf':
                reader = PyPDF2.PdfReader(BytesIO(file_content))
                for page in reader.pages:
                    text += page.extract_text() or ""
            elif ext == 'docx':
                doc = docx.Document(BytesIO(file_content))
                text = "\n".join([para.text for para in doc.paragraphs])
            elif ext == 'txt':
                text = file_content.decode('utf-8')
            else:
                return None, f"Unsupported file format: {ext}"
            return text, None
        except Exception as e:
            return None, str(e)

    def extract_skills(self, text, skills_list):
        if not text:
            return []
        text = text.lower()
        found = [s for s in skills_list if re.search(r'\b' + re.escape(s.lower()) + r'\b', text)]
        filtered = [s for s in found if s.lower() not in STOPWORDS and len(s) > 2]
        return list(set(filtered))

    def analyze_skills(self, user_skills, job_skills):
        user_lower = set(s.lower() for s in user_skills)
        matched = [s for s in job_skills if s.lower() in user_lower]
        missing = [s for s in job_skills if s.lower() not in user_lower]
        return matched, missing

    def get_all_skills(self):
        all_skills = []
        for skill_text in self.df['skills']:
            skills = [s.strip() for s in str(skill_text).split(',')]
            all_skills.extend(skills)
        return list(set(all_skills))

    def match_job(self, file: UploadFile, job_title: str, governorate: str, level: str):
        # Validate inputs
        job_title = job_title.strip().lower()
        governorate = governorate.strip().lower()
        level = level.strip().lower()
        if not all([job_title, governorate, level]):
            return {"error": "Job title, governorate, and level must not be empty."}

        # Extract text from CV
        text, error = self.extract_text_from_cv(file)
        if error:
            return {"error": error}

        # Extract user skills
        user_skills = self.extract_skills(text, self.all_skills)
        if not user_skills:
            return {"error": "No valid skills found in CV."}

        # Normalize DataFrame for matching
        level_col = 'professional level' if 'professional level' in df.columns else 'professional Level'
        df = self.df
        df['job_title_lower'] = df['Job Title'].str.strip().str.lower()
        df['governorate_lower'] = df['Governorate'].str.strip().str.lower()
        df['level_lower'] = df[level_col].str.strip().str.lower()

        # Find matching job
        job_row = df[
            (df['job_title_lower'] == job_title) &
            (df['governorate_lower'] == governorate) &
            (df['level_lower'] == level)
        ]

        if job_row.empty:
            job_row = df[df['job_title_lower'] == job_title]
            if job_row.empty:
                return {"error": f"No matching job found for title '{job_title}'."}

        # Extract job skills
        job_skills = [s.strip() for s in job_row.iloc[0]['skills'].split(',')]
        matched, missing = self.analyze_skills(user_skills, job_skills)
        percent = round((len(matched) / len(job_skills)) * 100, 2) if job_skills else 0
        top_missing = missing[:5] if len(missing) > 5 else missing

        return {
            "summary": f"You match {len(matched)} out of {len(job_skills)} required skills ({percent:.1f}%) for the job '{job_title.title()}' in {governorate.title()} ({level} level).",
            "cv_skills_found": user_skills,
            "matched_skills": {
                "count": len(matched),
                "skills": matched
            },
            "missing_skills": {
                "count": len(missing),
                "skills": missing
            },
            "top_missing_suggestions": top_missing,
            "recommendation": f"To improve your chances, consider learning or highlighting these skills in your CV: {', '.join(top_missing)}."
        }