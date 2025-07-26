import streamlit as st
import json
import os
from typing import Dict, List, Any
import re
from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Resume Editor & ATS Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .score-high { color: #27ae60; font-weight: bold; }
    .score-medium { color: #f39c12; font-weight: bold; }
    .score-low { color: #e74c3c; font-weight: bold; }
    .keyword-match { background-color: #d5f4e6; padding: 2px 4px; border-radius: 3px; }
    .keyword-missing { background-color: #fadbd8; padding: 2px 4px; border-radius: 3px; }
    .form-container { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 10px; 
        margin: 10px 0; 
        border: 1px solid #dee2e6;
    }
    .add-button { 
        background-color: #28a745; 
        color: white; 
        border: none; 
        padding: 8px 16px; 
        border-radius: 5px; 
        cursor: pointer; 
    }
    .remove-button { 
        background-color: #dc3545; 
        color: white; 
        border: none; 
        padding: 4px 8px; 
        border-radius: 3px; 
        cursor: pointer; 
        font-size: 12px; 
    }
    .dynamic-list-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    .input-container {
        flex: 1;
        margin-right: 10px;
    }
    .button-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 80px;
    }
    .add-button-container {
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 10px 0;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        min-height: 50px;
    }
    .chip {
        display: inline-flex;
        align-items: center;
        background-color: #007bff;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .chip:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .chip-remove {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        margin-left: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        transition: background-color 0.2s ease;
    }
    .chip-remove:hover {
        background: rgba(255,255,255,0.3);
    }
    .add-chip-input {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
    }
    .add-chip-input input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #ced4da;
        border-radius: 20px;
        font-size: 14px;
    }
    .add-chip-button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }
    .add-chip-button:hover {
        background-color: #218838;
    }
    .empty-chips {
        color: #6c757d;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

class ResumeEditor:
    def __init__(self):
        self.sections = [
            "Personal Information",
            "Experience",
            "Education",
            "Projects"
        ]
        self.files = {
            "Personal Information": "personal.json",
            "Experience": "exp.json",
            "Education": "edu.json",
            "Projects": "proj.json"
        }
        
    def load_json_from_session(self, section: str) -> List[Dict]:
        key = f"{section.lower().replace(' ', '_')}_data"
        return st.session_state.get(key, [])

    def save_json_to_session(self, section: str, data: List[Dict]):
        key = f"{section.lower().replace(' ', '_')}_data"
        st.session_state[key] = data

    def export_json(self, section: str):
        data = self.load_json_from_session(section)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label=f"Export {section} as JSON",
            data=json_str,
            file_name=self.files[section],
            mime="application/json"
        )

    def upload_page(self):
        st.markdown('<h2 class="section-header">⬆️ Upload Resume Data (JSON)</h2>', unsafe_allow_html=True)
        
        # Upload option selection
        upload_option = st.radio(
            "Choose upload method:",
            ["Upload Combined Resume JSON", "Upload Individual Section JSONs"],
            help="Select whether to upload a single combined resume file or individual section files"
        )
        
        if upload_option == "Upload Combined Resume JSON":
            st.subheader("Upload Combined Resume JSON")
            st.info("Upload a single JSON file containing all sections (personal, experience, education, projects)")
            
            combined_file = st.file_uploader(
                "Upload combined resume JSON file", 
                type=["json"], 
                key="upload_combined",
                help="JSON file should have keys: personal, experience, education, projects"
            )
            
            if combined_file:
                try:
                    combined_data = json.load(combined_file)
                    if not isinstance(combined_data, dict):
                        st.error("Combined JSON must be an object with section keys.")
                    else:
                        # Extract and save each section
                        sections_uploaded = []
                        for section in self.sections:
                            section_key = section.lower().replace(' ', '_')
                            # Special handling for Personal Information: support both 'personal' and 'personal_information'
                            if section == "Personal Information":
                                personal_data = None
                                if "personal_information" in combined_data:
                                    personal_data = combined_data["personal_information"]
                                elif "personal" in combined_data:
                                    personal_data = combined_data["personal"]
                                if personal_data is not None:
                                    self.save_json_to_session(section, personal_data)
                                    sections_uploaded.append(section)
                            else:
                                if section_key in combined_data:
                                    self.save_json_to_session(section, combined_data[section_key])
                                    sections_uploaded.append(section)
                        
                        if sections_uploaded:
                            st.success(f"✅ Successfully uploaded sections: {', '.join(sections_uploaded)}")
                        else:
                            st.warning("No valid sections found in the combined JSON file.")
                            
                except Exception as e:
                    st.error(f"Error reading combined JSON: {str(e)}")
        
        else:  # Upload Individual Section JSONs
            st.subheader("Upload Individual Section JSONs")
            st.info("Upload JSON files for each section separately")
            
            for section in self.sections:
                st.write(f"**{section}**")
                uploaded_file = st.file_uploader(
                    f"Upload {section} JSON file", 
                    type=["json"], 
                    key=f"upload_{section}",
                    help=f"Upload JSON file for {section} section"
                )
                
                if uploaded_file:
                    try:
                        data = json.load(uploaded_file)
                        if not isinstance(data, list):
                            st.error(f"{section} JSON must be a list of objects.")
                        else:
                            self.save_json_to_session(section, data)
                            st.success(f"✅ {section} data uploaded successfully!")
                    except Exception as e:
                        st.error(f"Error reading {section} JSON: {str(e)}")
        
        # Show current session state summary
        st.markdown("---")
        st.subheader("📊 Current Data Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            for section in self.sections[:2]:
                data = self.load_json_from_session(section)
                count = len(data) if isinstance(data, list) else 0
                st.write(f"**{section}:** {count} item(s)")
        
        with col2:
            for section in self.sections[2:]:
                data = self.load_json_from_session(section)
                count = len(data) if isinstance(data, list) else 0
                st.write(f"**{section}:** {count} item(s)")
        
        st.info("Uploaded data will be available for manual editing and ATS analysis.")

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine',
            'yours', 'his', 'hers', 'ours', 'theirs', 'am', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def calculate_ats_score(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate ATS score based on keyword matching"""
        resume_keywords = self.extract_keywords(resume_text)
        job_keywords = self.extract_keywords(job_description)
        
        if not job_keywords:
            return {
                'score': 0,
                'matched_keywords': [],
                'missing_keywords': job_keywords,
                'match_percentage': 0
            }
        
        # Count keyword frequencies
        resume_keyword_counts = Counter(resume_keywords)
        job_keyword_counts = Counter(job_keywords)
        
        # Find matched and missing keywords
        matched_keywords = []
        missing_keywords = []
        
        for keyword, count in job_keyword_counts.items():
            if keyword in resume_keyword_counts:
                matched_keywords.extend([keyword] * min(count, resume_keyword_counts[keyword]))
            else:
                missing_keywords.extend([keyword] * count)
        
        # Calculate score
        total_job_keywords = len(job_keywords)
        matched_count = len(matched_keywords)
        match_percentage = (matched_count / total_job_keywords) * 100
        
        # Score calculation (0-100)
        score = min(100, match_percentage)
        
        return {
            'score': round(score, 1),
            'matched_keywords': list(set(matched_keywords)),
            'missing_keywords': list(set(missing_keywords)),
            'match_percentage': round(match_percentage, 1),
            'total_job_keywords': total_job_keywords,
            'matched_count': matched_count
        }
    
    def get_resume_text(self) -> str:
        """Extract all text from resume data"""
        text_parts = []
        
        # Personal info
        personal_data = self.load_json_from_session("Personal Information")
        if personal_data:
            personal = personal_data[0]
            text_parts.append(f"{personal.get('name', '')} {personal.get('email', '')}")
            
            # Languages
            languages = [lang.get('language', '') for lang in personal.get('languages', [])]
            text_parts.append(' '.join(languages))
            
            # Technologies
            technologies = [tech.get('technology', '') for tech in personal.get('technologies', [])]
            text_parts.append(' '.join(technologies))
            
            # Certifications
            certifications = [cert.get('certification', '') for cert in personal.get('certifications', [])]
            text_parts.append(' '.join(certifications))
        
        # Experience
        exp_data = self.load_json_from_session("Experience")
        for exp in exp_data:
            text_parts.append(f"{exp.get('role', '')} {exp.get('company', '')}")
            for detail in exp.get('details', []):
                text_parts.append(f"{detail.get('title', '')} {detail.get('description', '')}")
        
        # Education
        edu_data = self.load_json_from_session("Education")
        for edu in edu_data:
            text_parts.append(f"{edu.get('degree', '')} {edu.get('school', '')}")
        
        # Projects
        proj_data = self.load_json_from_session("Projects")
        for proj in proj_data:
            text_parts.append(f"{proj.get('title', '')} {proj.get('description', '')}")
        
        return ' '.join(text_parts)
    
    def run(self):
        """Main application"""
        st.markdown('<h1 class="main-header">📄 Resume Editor & ATS Analyzer</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["Upload Data"] + ["ATS Score Analyzer"] + self.sections
        )
        
        if page == "Upload Data":
            self.upload_page()
        elif page == "ATS Score Analyzer":
            self.ats_analyzer_page()
        else:
            self.form_editor_page(page)
    
    def ats_analyzer_page(self):
        """ATS Score Analyzer page"""
        st.markdown('<h2 class="section-header">🎯 ATS Score Analyzer</h2>', unsafe_allow_html=True)
        
        # Export full JSON data button
        if st.button("Export Full Resume JSON"):
            combined_data = {
                "personal_information": self.load_json_from_session("Personal Information"),
                "experience": self.load_json_from_session("Experience"),
                "education": self.load_json_from_session("Education"),
                "projects": self.load_json_from_session("Projects")
            }
            st.download_button(
                label="Download Combined Resume JSON",
                data=json.dumps(combined_data, indent=2, ensure_ascii=False),
                file_name="combined_resume.json",
                mime="application/json"
            )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Job Description")
            job_description = st.text_area(
                "Paste the job description here:",
                height=400,
                placeholder="Enter the job description to analyze against your resume..."
            )
            
            if st.button("Analyze ATS Score", type="primary"):
                if job_description.strip():
                    st.session_state['analyze_ats'] = True
                    st.session_state['job_description'] = job_description
                    st.rerun()
                else:
                    st.warning("Please enter a job description to analyze.")
        
        with col2:
            st.subheader("Resume Preview")
            resume_text = self.get_resume_text()
            st.text_area(
                "Your resume content (read-only):",
                value=resume_text,
                height=400,
                disabled=True
            )
        
        # Render ATS Analysis Results in a full-width container if requested
        if st.session_state.get('analyze_ats') and st.session_state.get('job_description'):
            with st.container():
                self.perform_ats_analysis(st.session_state['job_description'])
                # Do NOT reset analyze_ats here; only reset when a new analysis is triggered

    def perform_ats_analysis(self, job_description: str):
        """Perform ATS analysis and display results"""
        resume_text = self.get_resume_text()
        ats_results = self.calculate_ats_score(resume_text, job_description)
        
        # Custom CSS for full width
        st.markdown("""
        <style>
        .full-width-section {
            width: 100vw !important;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
            padding-left: 5vw;
            padding-right: 5vw;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="full-width-section">', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<h3 class="section-header">📊 ATS Analysis Results</h3>', unsafe_allow_html=True)
        
        # Score display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score = ats_results['score']
            if score >= 80:
                score_class = "score-high"
            elif score >= 60:
                score_class = "score-medium"
            else:
                score_class = "score-low"
            
            st.markdown(f'<div class="{score_class}">ATS Score: {score}/100</div>', unsafe_allow_html=True)
        
        with col2:
            st.metric("Keywords Matched", ats_results['matched_count'])
        
        with col3:
            st.metric("Match Percentage", f"{ats_results['match_percentage']}%")
        
        # Matched and Missing Keywords as horizontal chips with show more
        st.markdown("<style>\n.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }\n.chip { padding: 6px 14px; border-radius: 16px; font-size: 1rem; font-weight: 500; background: #e0f7fa; color: #006064; border: none; }\n.chip-missing { background: #ffebee; color: #b71c1c; }\n@media (prefers-color-scheme: dark) { .chip { background: #263238; color: #80deea; } .chip-missing { background: #311111; color: #ff8a80; } }\n</style>", unsafe_allow_html=True)
        
        # Matched Keywords
        matched_keywords = ats_results['matched_keywords']
        missing_keywords = ats_results['missing_keywords']
        show_count = 10
        show_more_matched = st.session_state.get('show_more_matched', False)
        show_more_missing = st.session_state.get('show_more_missing', False)
        
        st.subheader("✅ Matched Keywords")
        if matched_keywords:
            display_matched = matched_keywords if show_more_matched or len(matched_keywords) <= show_count else matched_keywords[:show_count]
            st.markdown('<div class="chip-row">' + ''.join([f'<span class="chip">{kw}</span>' for kw in display_matched]) + '</div>', unsafe_allow_html=True)
            if len(matched_keywords) > show_count:
                if not show_more_matched:
                    if st.button("Show more matched keywords"):
                        st.session_state['show_more_matched'] = True
                        st.rerun()
                else:
                    if st.button("Show less matched keywords"):
                        st.session_state['show_more_matched'] = False
                        st.rerun()
        else:
            st.info("No keywords matched")
        
        st.subheader("❌ Missing Keywords")
        if missing_keywords:
            display_missing = missing_keywords if show_more_missing or len(missing_keywords) <= show_count else missing_keywords[:show_count]
            st.markdown('<div class="chip-row">' + ''.join([f'<span class="chip chip-missing">{kw}</span>' for kw in display_missing]) + '</div>', unsafe_allow_html=True)
            if len(missing_keywords) > show_count:
                if not show_more_missing:
                    if st.button("Show more missing keywords"):
                        st.session_state['show_more_missing'] = True
                        st.rerun()
                else:
                    if st.button("Show less missing keywords"):
                        st.session_state['show_more_missing'] = False
                        st.rerun()
        else:
            st.success("All keywords found!")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        if ats_results['score'] < 60:
            st.warning("Your resume needs significant improvement for this position.")
            st.write("Consider adding these missing keywords to your resume:")
            missing_keywords = ats_results['missing_keywords'][:10]  # Top 10
            if missing_keywords:
                st.markdown('<div class="chip-row">' + ''.join([f'<span class="chip">{kw}</span>' for kw in missing_keywords]) + '</div>', unsafe_allow_html=True)
        elif ats_results['score'] < 80:
            st.info("Your resume is moderately aligned with the job description.")
            st.write("Consider adding a few more relevant keywords to improve your score.")
        else:
            st.success("Excellent! Your resume is well-aligned with the job description.")
        
        # Keyword frequency analysis
        st.subheader("📈 Keyword Frequency Analysis")
        resume_keywords = self.extract_keywords(resume_text)
        job_keywords = self.extract_keywords(job_description)
        
        if resume_keywords and job_keywords:
            # Create frequency data
            resume_freq = Counter(resume_keywords)
            job_freq = Counter(job_keywords)
            
            # Get top keywords from job description
            top_job_keywords = dict(job_freq.most_common(10))
            
            # Create comparison data
            comparison_data = []
            for keyword, job_count in top_job_keywords.items():
                resume_count = resume_freq.get(keyword, 0)
                comparison_data.append({
                    'Keyword': keyword,
                    'Job Description': job_count,
                    'Resume': resume_count
                })
            
            if comparison_data:
                df = pd.DataFrame(comparison_data)
                fig = px.bar(df, x='Keyword', y=['Job Description', 'Resume'], 
                           title="Keyword Frequency Comparison",
                           barmode='group')
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def form_editor_page(self, section_name: str):
        """Form-based editor page for each section"""
        st.markdown(f'<h2 class="section-header">✏️ {section_name} Editor</h2>', unsafe_allow_html=True)
        
        data = self.load_json_from_session(section_name)
        
        # Debug information
        st.write(f"Debug: Loaded {len(data) if isinstance(data, list) else 'invalid'} items from session for {section_name}")
        
        if not data:
            st.info(f"No data found for {section_name}. You can start adding your information below.")
        
        # There are no stray st.text_input or st.text_area calls with empty labels here.
        # All input fields are inside the respective edit_* functions and have proper labels.
        # If a white bar persists, it may be a Streamlit theme or CSS issue.
        
        # Form-based editing based on section
        if section_name == "Personal Information":
            self.edit_personal_info(data, section_name)
        elif section_name == "Experience":
            self.edit_experience(data, section_name)
        elif section_name == "Education":
            self.edit_education(data, section_name)
        elif section_name == "Projects":
            self.edit_projects(data, section_name)
        self.export_json(section_name)
    
    def edit_personal_info(self, data: List[Dict], filename: str):
        """Edit personal information with forms"""
        # Initialize with empty data if none exists
        if not data or len(data) == 0:
            personal = {}
        else:
            personal = data[0] if isinstance(data[0], dict) else {}
        
        st.subheader("Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=personal.get('name', ''))
            email = st.text_input("Email", value=personal.get('email', ''))
            phone = st.text_input("Phone", value=personal.get('phone', ''))
        
        with col2:
            website = st.text_input("Website", value=personal.get('website', ''))
            linkedin = st.text_input("LinkedIn", value=personal.get('linkedin', ''))
        
        # Initialize session state for dynamic lists
        if 'languages' not in st.session_state:
            st.session_state['languages'] = personal.get('languages', [])
        if 'technologies' not in st.session_state:
            st.session_state['technologies'] = personal.get('technologies', [])
        if 'certifications' not in st.session_state:
            st.session_state['certifications'] = personal.get('certifications', [])
        
        # Languages
        st.subheader("Languages & Skills")
        
        languages = st.session_state['languages']
        if not isinstance(languages, list):
            languages = []
        
        st.write("Languages:")
        
        # Initialize remove_lang_idx to avoid UnboundLocalError
        remove_lang_idx = None
        # Display languages as chips with clickable remove
        if languages:
            # Create columns for chips (3 chips per row)
            chip_cols = st.columns(3)
            
            for i, lang in enumerate(languages):
                if isinstance(lang, dict) and lang.get('language', '').strip():
                    col_idx = i % 3
                    with chip_cols[col_idx]:
                        # Create a chip-like appearance with clickable remove
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="
                                background-color: rgba(0, 123, 255, 0.1); 
                                color: #007bff; 
                                padding: 8px 12px; 
                                border-radius: 20px; 
                                font-size: 14px; 
                                font-weight: 500; 
                                margin: 2px 0;
                                display: inline-block;
                                border: 1px solid rgba(0, 123, 255, 0.3);
                                cursor: pointer;
                                transition: all 0.2s ease;
                            " 
                            onmouseover="this.style.transform='scale(1.05)'; this.style.background='rgba(0, 123, 255, 0.2)'; this.style.boxShadow='0 4px 8px rgba(0, 123, 255, 0.2)';"
                            onmouseout="this.style.transform='scale(1)'; this.style.background='rgba(0, 123, 255, 0.1)'; this.style.boxShadow='none';"
                            title="Click the X button to remove">
                                {lang.get('language', '')}
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("×", key=f"remove_lang_{i}", help="Remove this language"):
                                remove_lang_idx = i
        else:
            st.info("No languages added yet")
        
        if remove_lang_idx is not None:
            languages.pop(remove_lang_idx)
            st.session_state['languages'] = languages
            st.rerun()
        
        # Add new language input (Enter key to add)
        new_language = st.text_input("Add Language (Press Enter to add)", key="new_language_input", placeholder="Enter a language and press Enter...")
        
        # Handle Enter key press for language
        if new_language.strip():
            # Check if this is a new entry (not just page reload)
            if 'last_language' not in st.session_state or st.session_state['last_language'] != new_language:
                languages.append({"language": new_language.strip()})
                st.session_state['languages'] = languages
                st.session_state['last_language'] = new_language
                st.rerun()
        
        # Technologies
        technologies = st.session_state['technologies']
        if not isinstance(technologies, list):
            technologies = []
        
        st.write("Technologies:")
        
        # Initialize remove_tech_idx to avoid UnboundLocalError
        remove_tech_idx = None
        # Display technologies as chips with clickable remove
        if technologies:
            # Create columns for chips (3 chips per row)
            tech_chip_cols = st.columns(3)
            
            for i, tech in enumerate(technologies):
                if isinstance(tech, dict) and tech.get('technology', '').strip():
                    col_idx = i % 3
                    with tech_chip_cols[col_idx]:
                        # Create a chip-like appearance with clickable remove
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="
                                background-color: rgba(40, 167, 69, 0.1); 
                                color: #28a745; 
                                padding: 8px 12px; 
                                border-radius: 20px; 
                                font-size: 14px; 
                                font-weight: 500; 
                                margin: 2px 0;
                                display: inline-block;
                                border: 1px solid rgba(40, 167, 69, 0.3);
                                cursor: pointer;
                                transition: all 0.2s ease;
                            " 
                            onmouseover="this.style.transform='scale(1.05)'; this.style.background='rgba(40, 167, 69, 0.2)'; this.style.boxShadow='0 4px 8px rgba(40, 167, 69, 0.2)';"
                            onmouseout="this.style.transform='scale(1)'; this.style.background='rgba(40, 167, 69, 0.1)'; this.style.boxShadow='none';"
                            title="Click the X button to remove">
                                {tech.get('technology', '')}
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("×", key=f"remove_tech_{i}", help="Remove this technology"):
                                remove_tech_idx = i
        else:
            st.info("No technologies added yet")
        
        if remove_tech_idx is not None:
            technologies.pop(remove_tech_idx)
            st.session_state['technologies'] = technologies
            st.rerun()
        
        # Add new technology input (Enter key to add)
        new_technology = st.text_input("Add Technology (Press Enter to add)", key="new_tech_input", placeholder="Enter a technology and press Enter...")
        
        # Handle Enter key press for technology
        if new_technology.strip():
            # Check if this is a new entry (not just page reload)
            if 'last_technology' not in st.session_state or st.session_state['last_technology'] != new_technology:
                technologies.append({"technology": new_technology.strip()})
                st.session_state['technologies'] = technologies
                st.session_state['last_technology'] = new_technology
                st.rerun()
        
        # Certifications
        st.subheader("Certifications")
        
        certifications = st.session_state['certifications']
        if not isinstance(certifications, list):
            certifications = []
        
        # Initialize remove_cert_idx to avoid UnboundLocalError
        remove_cert_idx = None
        # Display certifications as chips with clickable remove
        if certifications:
            # Create columns for chips (3 chips per row)
            cert_chip_cols = st.columns(3)
            
            for i, cert in enumerate(certifications):
                if isinstance(cert, dict) and cert.get('certification', '').strip():
                    col_idx = i % 3
                    with cert_chip_cols[col_idx]:
                        # Create a chip-like appearance with clickable remove
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="
                                background-color: rgba(255, 193, 7, 0.1); 
                                color: #856404; 
                                padding: 8px 12px; 
                                border-radius: 20px; 
                                font-size: 14px; 
                                font-weight: 500; 
                                margin: 2px 0;
                                display: inline-block;
                                border: 1px solid rgba(255, 193, 7, 0.3);
                                cursor: pointer;
                                transition: all 0.2s ease;
                            " 
                            onmouseover="this.style.transform='scale(1.05)'; this.style.background='rgba(255, 193, 7, 0.2)'; this.style.boxShadow='0 4px 8px rgba(255, 193, 7, 0.2)';"
                            onmouseout="this.style.transform='scale(1)'; this.style.background='rgba(255, 193, 7, 0.1)'; this.style.boxShadow='none';"
                            title="Click the X button to remove">
                                {cert.get('certification', '')}
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("×", key=f"remove_cert_{i}", help="Remove this certification"):
                                remove_cert_idx = i
        else:
            st.info("No certifications added yet")
        
        if remove_cert_idx is not None:
            certifications.pop(remove_cert_idx)
            st.session_state['certifications'] = certifications
            st.rerun()
        
        # Add new certification input (Enter key to add)
        new_certification = st.text_input("Add Certification (Press Enter to add)", key="new_cert_input", placeholder="Enter a certification and press Enter...")
        
        # Handle Enter key press for certification
        if new_certification.strip():
            # Check if this is a new entry (not just page reload)
            if 'last_certification' not in st.session_state or st.session_state['last_certification'] != new_certification:
                certifications.append({"certification": new_certification.strip()})
                st.session_state['certifications'] = certifications
                st.session_state['last_certification'] = new_certification
                st.rerun()
        
        # Save button
        # (Remove the following block for Personal Information)
        # if st.button("Save Personal Information", type="primary"):
        #     # Filter out empty entries
        #     new_languages = [lang for lang in languages if lang.get('language', '').strip()]
        #     new_technologies = [tech for tech in technologies if tech.get('technology', '').strip()]
        #     new_certifications = [cert for cert in certifications if cert.get('certification', '').strip()]
        #     updated_data = [{
        #         "name": name,
        #         "email": email,
        #         "phone": phone,
        #         "website": website,
        #         "linkedin": linkedin,
        #         "languages": new_languages,
        #         "technologies": new_technologies,
        #         "certifications": new_certifications
        #     }]
        #     self.save_json_to_session(filename, updated_data)
        #     st.success("✅ Personal information saved successfully!")
        #     # After saving, update session state lists from saved data
        #     st.session_state['languages'] = new_languages
        #     st.session_state['technologies'] = new_technologies
        #     st.session_state['certifications'] = new_certifications
        #     st.rerun()
    
    def edit_experience(self, data: List[Dict], filename: str):
        """Edit experience with forms"""
        # Initialize session state for experience
        if 'experiences' not in st.session_state:
            st.session_state['experiences'] = data if isinstance(data, list) else []
        
        experiences = st.session_state['experiences']
        if not isinstance(experiences, list):
            experiences = []
        
        st.subheader("Work Experience")
        
        # Handle experience removal
        remove_exp_idx = None
        for i, exp in enumerate(experiences):
            if not isinstance(exp, dict):
                continue
            
            # Create a row with expander and remove button
            col1, col2 = st.columns([20, 1])
            
            with col1:
                with st.expander(f"Experience {i+1}: {exp.get('role', 'New Role')} at {exp.get('company', 'New Company')}"):
                    # Use different column names to avoid conflict with outer columns
                    exp_col1, exp_col2 = st.columns(2)
                    
                    with exp_col1:
                        company = st.text_input("Company", value=exp.get('company', ''), key=f"company_{i}")
                        role = st.text_input("Role/Title", value=exp.get('role', ''), key=f"role_{i}")
                        team = st.text_input("Team/Department", value=exp.get('team', ''), key=f"team_{i}")
                    
                    with exp_col2:
                        company_location = st.text_input("Company Location", value=exp.get('company_location', ''), key=f"loc_{i}")
                        time_duration = st.text_input("Time Duration", value=exp.get('time_duration', ''), key=f"time_{i}")
                    
                    # Update experience data
                    experiences[i] = {
                        "company": company,
                        "company_location": company_location,
                        "role": role,
                        "team": team,
                        "time_duration": time_duration,
                        "details": exp.get('details', [])
                    }
                    
                    # Experience details
                    st.write("**Experience Details:**")
                    details = exp.get('details', [])
                    if not isinstance(details, list):
                        details = []
                    
                    # Handle detail removal
                    remove_detail_idx = None
                    
                    for j, detail in enumerate(details):
                        if isinstance(detail, dict):
                            st.write(f"Detail {j+1}:")
                            # Title and Remove button in the same row
                            title_col, btn_col = st.columns([5, 1])
                            with title_col:
                                title = st.text_input("Title", value=detail.get('title', ''), key=f"detail_title_{i}_{j}")
                            with btn_col:
                                st.markdown("<div style='height: 1.7em'></div>", unsafe_allow_html=True)  # vertical align
                                if st.button("Remove Detail", key=f"remove_detail_{i}_{j}"):
                                    remove_detail_idx = j
                            # Description in the same width as title input
                            desc_col, _ = st.columns([5, 1])
                            with desc_col:
                                description = st.text_area("Description", value=detail.get('description', ''), key=f"detail_desc_{i}_{j}")
                            # Update the detail in the list
                            details[j] = {
                                "title": title,
                                "description": description
                            }
                    
                    # Remove detail if requested
                    if remove_detail_idx is not None:
                        details.pop(remove_detail_idx)
                        experiences[i]["details"] = details
                        st.session_state['experiences'] = experiences
                        st.rerun()
                    
                    if st.button("Add Detail", key=f"add_detail_{i}"):
                        details.append({"title": "", "description": ""})
                        experiences[i]["details"] = details
                        st.session_state['experiences'] = experiences
                        st.rerun()
            
            with col2:
                # Remove experience button aligned with expander
                if st.button("×", key=f"remove_exp_{i}", help="Remove this experience"):
                    remove_exp_idx = i
        
        # Remove experience if requested
        if remove_exp_idx is not None:
            experiences.pop(remove_exp_idx)
            st.session_state['experiences'] = experiences
            st.rerun()
        
        if st.button("Add New Experience"):
            experiences.append({
                "company": "",
                "company_location": "",
                "role": "",
                "team": "",
                "time_duration": "",
                "details": []
            })
            st.session_state['experiences'] = experiences
            st.rerun()
        
        # Save button
        # (Remove the following block for Experience)
        # if st.button("Save Experience", type="primary"):
        #     # Filter out empty experiences and details
        #     valid_experiences = []
        #     for exp in experiences:
        #         if exp.get('company', '').strip() or exp.get('role', '').strip():
        #             # Filter out empty details
        #             valid_details = []
        #             for detail in exp.get('details', []):
        #                 if detail.get('title', '').strip() and detail.get('description', '').strip():
        #                     valid_details.append(detail)
                    
        #             # Create experience with filtered details
        #             valid_exp = {
        #                 "company": exp.get('company', ''),
        #                 "company_location": exp.get('company_location', ''),
        #                 "role": exp.get('role', ''),
        #                 "team": exp.get('team', ''),
        #                 "time_duration": exp.get('time_duration', ''),
        #                 "details": valid_details
        #             }
        #             valid_experiences.append(valid_exp)
            
        #     self.save_json_to_session(filename, valid_experiences)
        #     st.success("✅ Experience saved successfully!")
        #     # Clear session state after successful save
        #     if 'experiences' in st.session_state:
        #         del st.session_state['experiences']
        #     st.rerun()
    
    def edit_education(self, data: List[Dict], filename: str):
        """Edit education with forms"""
        # Initialize session state for education
        if 'education' not in st.session_state:
            st.session_state['education'] = data if isinstance(data, list) else []
        
        education = st.session_state['education']
        if not isinstance(education, list):
            education = []
        
        st.subheader("Education")
        
        # Handle education removal
        remove_edu_idx = None
        for i, edu in enumerate(education):
            if not isinstance(edu, dict):
                continue
            
            # Create a row with expander and remove button
            col1, col2 = st.columns([20, 1])
            
            with col1:
                with st.expander(f"Education {i+1}: {edu.get('degree', 'New Degree')}"):
                    # Use different column names to avoid conflict with outer columns
                    edu_col1, edu_col2 = st.columns(2)
                    
                    with edu_col1:
                        school = st.text_input("School/University", value=edu.get('school', ''), key=f"school_{i}")
                        degree = st.text_input("Degree", value=edu.get('degree', ''), key=f"degree_{i}")
                    
                    with edu_col2:
                        school_location = st.text_input("School Location", value=edu.get('school_location', ''), key=f"school_loc_{i}")
                        time_period = st.text_input("Time Period", value=edu.get('time_period', ''), key=f"edu_time_{i}")
                    
                    # Update education data
                    education[i] = {
                        "school": school,
                        "school_location": school_location,
                        "degree": degree,
                        "time_period": time_period
                    }
            
            with col2:
                # Remove education button aligned with expander
                if st.button("×", key=f"remove_edu_{i}", help="Remove this education"):
                    remove_edu_idx = i
        
        # Remove education if requested
        if remove_edu_idx is not None:
            education.pop(remove_edu_idx)
            st.session_state['education'] = education
            st.rerun()
        
        if st.button("Add New Education"):
            education.append({
                "school": "",
                "school_location": "",
                "degree": "",
                "time_period": ""
            })
            st.session_state['education'] = education
            st.rerun()
        
        # Save button
        # (Remove the following block for Education)
        # if st.button("Save Education", type="primary"):
        #     # Filter out empty education entries
        #     valid_education = []
        #     for edu in education:
        #         if edu.get('school', '').strip() or edu.get('degree', '').strip():
        #             valid_education.append(edu)
            
        #     self.save_json_to_session(filename, valid_education)
        #     st.success("✅ Education saved successfully!")
        #     # Clear session state after successful save
        #     if 'education' in st.session_state:
        #         del st.session_state['education']
        #     st.rerun()
    
    def edit_projects(self, data: List[Dict], filename: str):
        """Edit projects with forms"""
        # Initialize session state for projects
        if 'projects' not in st.session_state:
            st.session_state['projects'] = data if isinstance(data, list) else []
        
        projects = st.session_state['projects']
        if not isinstance(projects, list):
            projects = []
        
        st.subheader("Projects")
        
        # Handle project removal
        remove_proj_idx = None
        for i, proj in enumerate(projects):
            if not isinstance(proj, dict):
                continue
            
            # Create a row with expander and remove button
            col1, col2 = st.columns([20, 1])
            
            with col1:
                with st.expander(f"Project {i+1}: {proj.get('title', 'New Project')}"):
                    title = st.text_input("Project Title", value=proj.get('title', ''), key=f"proj_title_{i}")
                    description = st.text_area("Project Description", value=proj.get('description', ''), key=f"proj_desc_{i}")
                    
                    # Update project data
                    projects[i] = {
                        "title": title,
                        "description": description
                    }
            
            with col2:
                # Remove project button aligned with expander
                if st.button("×", key=f"remove_proj_{i}", help="Remove this project"):
                    remove_proj_idx = i
        
        # Remove project if requested
        if remove_proj_idx is not None:
            projects.pop(remove_proj_idx)
            st.session_state['projects'] = projects
            st.rerun()
        
        if st.button("Add New Project"):
            projects.append({
                "title": "",
                "description": ""
            })
            st.session_state['projects'] = projects
            st.rerun()
        
        # Save button
        # (Remove the following block for Projects)
        # if st.button("Save Projects", type="primary"):
        #     # Filter out empty project entries
        #     valid_projects = []
        #     for proj in projects:
        #         if proj.get('title', '').strip() or proj.get('description', '').strip():
        #             valid_projects.append(proj)
            
        #     self.save_json_to_session(filename, valid_projects)
        #     st.success("✅ Projects saved successfully!")
        #     # Clear session state after successful save
        #     if 'projects' in st.session_state:
        #         del st.session_state['projects']
        #     st.rerun()
    

    
    def display_formatted_data(self, section_name: str, data: List[Dict]):
        """Display formatted data based on section"""
        if section_name == "Personal Information" and data:
            personal = data[0]
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {personal.get('name', 'N/A')}")
                st.write(f"**Email:** {personal.get('email', 'N/A')}")
                st.write(f"**Phone:** {personal.get('phone', 'N/A')}")
                st.write(f"**Website:** {personal.get('website', 'N/A')}")
                st.write(f"**LinkedIn:** {personal.get('linkedin', 'N/A')}")
            
            with col2:
                st.write("**Languages:**")
                for lang in personal.get('languages', []):
                    st.write(f"• {lang.get('language', '')}")
                
                st.write("**Technologies:**")
                for tech in personal.get('technologies', []):
                    st.write(f"• {tech.get('technology', '')}")
                
                st.write("**Certifications:**")
                for cert in personal.get('certifications', []):
                    st.write(f"• {cert.get('certification', '')}")
        
        elif section_name == "Experience":
            for i, exp in enumerate(data):
                with st.expander(f"{exp.get('role', 'N/A')} at {exp.get('company', 'N/A')}"):
                    st.write(f"**Company:** {exp.get('company', 'N/A')}")
                    st.write(f"**Location:** {exp.get('company_location', 'N/A')}")
                    st.write(f"**Role:** {exp.get('role', 'N/A')}")
                    st.write(f"**Team:** {exp.get('team', 'N/A')}")
                    st.write(f"**Duration:** {exp.get('time_duration', 'N/A')}")
                    
                    st.write("**Details:**")
                    for detail in exp.get('details', []):
                        st.write(f"**{detail.get('title', 'N/A')}:**")
                        st.write(f"{detail.get('description', 'N/A')}")
                        st.write("---")
        
        elif section_name == "Education":
            for edu in data:
                st.write(f"**School:** {edu.get('school', 'N/A')}")
                st.write(f"**Location:** {edu.get('school_location', 'N/A')}")
                st.write(f"**Degree:** {edu.get('degree', 'N/A')}")
                st.write(f"**Period:** {edu.get('time_period', 'N/A')}")
                st.write("---")
        
        elif section_name == "Projects":
            for proj in data:
                with st.expander(proj.get('title', 'N/A')):
                    st.write(f"**Title:** {proj.get('title', 'N/A')}")
                    st.write(f"**Description:** {proj.get('description', 'N/A')}")

if __name__ == "__main__":
    editor = ResumeEditor()
    editor.run() 