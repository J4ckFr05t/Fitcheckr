# Resume Editor & ATS Analyzer

A comprehensive Streamlit application for editing resume JSON data and analyzing ATS (Applicant Tracking System) compatibility with job descriptions.

## Features

### 📄 Resume Editor
- **JSON Editor**: Edit all resume sections (Personal Info, Experience, Education, Projects) with real-time validation
- **Formatted Preview**: View how your data will appear in a formatted layout
- **Data Validation**: Built-in JSON validation to ensure data integrity
- **Auto-save**: Save changes directly to your JSON files

### 🎯 ATS Score Analyzer
- **Keyword Matching**: Analyze how well your resume matches job descriptions
- **Score Calculation**: Get a 0-100 ATS compatibility score
- **Keyword Analysis**: See which keywords are matched and which are missing
- **Visual Analytics**: Interactive charts showing keyword frequency comparison
- **Recommendations**: Get actionable suggestions to improve your resume

### 📊 Analytics & Insights
- **Resume Statistics**: Word count, unique keywords, and frequency analysis
- **Keyword Frequency Charts**: Compare keyword usage between job descriptions and your resume
- **Performance Metrics**: Track your resume's effectiveness across different positions

## Installation

1. **Clone or download** this repository to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run resume_editor.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## Usage

### Editing Resume Data

1. **Navigate to a section** using the sidebar (Personal Information, Experience, Education, or Projects)
2. **Edit the JSON** in the text area
3. **Validate** your JSON format using the "Validate JSON" button
4. **Save changes** using the "Save Changes" button
5. **Preview** your formatted data in the preview section

### ATS Analysis

1. **Go to "ATS Score Analyzer"** in the sidebar
2. **Paste a job description** in the left text area
3. **Click "Analyze ATS Score"** to get your compatibility score
4. **Review the results**:
   - Overall ATS score (0-100)
   - Matched and missing keywords
   - Keyword frequency comparison chart
   - Personalized recommendations

### Understanding Your ATS Score

- **80-100**: Excellent match - your resume is well-aligned with the job description
- **60-79**: Good match - consider adding a few more relevant keywords
- **Below 60**: Needs improvement - significant keyword gaps identified

## File Structure

```
Resumes/
├── _data/
│   ├── personal.json    # Personal information, skills, certifications
│   ├── exp.json         # Work experience and achievements
│   ├── edu.json         # Education history
│   └── proj.json        # Projects and portfolio
├── resume_editor.py     # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## JSON Data Format

### Personal Information (`personal.json`)
```json
[
  {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1234567890",
    "website": "https://yourwebsite.com",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "languages": [
      {"language": "Python"},
      {"language": "SQL"}
    ],
    "technologies": [
      {"technology": "Machine Learning"},
      {"technology": "Data Analysis"}
    ],
    "certifications": [
      {"certification": "AWS Certified"},
      {"certification": "Google Cloud Professional"}
    ]
  }
]
```

### Experience (`exp.json`)
```json
[
  {
    "company": "Company Name",
    "company_location": "City, Country",
    "role": "Job Title",
    "team": "Team/Department",
    "time_duration": "Jan 2023 - Present",
    "details": [
      {
        "title": "Achievement Title",
        "description": "Detailed description of your achievement"
      }
    ]
  }
]
```

### Education (`edu.json`)
```json
[
  {
    "school": "University Name",
    "school_location": "City, Country",
    "degree": "Degree Name with GPA",
    "time_period": "2019 - 2023"
  }
]
```

### Projects (`proj.json`)
```json
[
  {
    "title": "Project Title",
    "description": "Detailed project description with technologies used and outcomes"
  }
]
```

## Tips for Better ATS Scores

1. **Use Relevant Keywords**: Include industry-specific terms from the job description
2. **Quantify Achievements**: Use numbers and percentages to demonstrate impact
3. **Match Job Requirements**: Align your skills and experience with the job requirements
4. **Use Standard Job Titles**: Avoid creative titles that ATS systems might not recognize
5. **Include Certifications**: Add relevant certifications and credentials
6. **Optimize Skills Section**: List technical skills and tools mentioned in the job description

## Troubleshooting

### Common Issues

1. **JSON Validation Errors**: Ensure proper JSON syntax with correct brackets, commas, and quotes
2. **File Not Found**: Make sure your `_data` folder contains the required JSON files
3. **Low ATS Score**: Review missing keywords and consider adding relevant experience or skills

### Getting Help

If you encounter any issues:
1. Check that all JSON files are properly formatted
2. Ensure all required dependencies are installed
3. Verify that the `_data` folder structure matches the expected format

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## License

This project is open source and available under the MIT License. 