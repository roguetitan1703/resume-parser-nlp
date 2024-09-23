### Workflow: Resume Parsing System

#### Step 1: **Bulk CV Upload & Text Extraction (Completed)**
- **Input:** Bulk resumes are uploaded by the recruiter via the front end.
- **Process:** 
  - CVs are uploaded in various formats (PDF, DOC, DOCX).
  - Your current system processes the CVs using `ResumeProcessor`, extracting text from each file and removing unwanted characters (e.g., `\n`).
- **Output:** Clean, extracted text from resumes is ready for further processing.

#### Step 2: **Named Entity Recognition (NER)**
- **Goal:** Extract structured data (personal info, education, work experience, skills) from the resumes using NER.
- **Tasks:**
  1. **Preprocess Text:**
     - Tokenize the text and clean it further (remove non-informative words).
     - You might need to create a pipeline for preprocessing steps (removing stopwords, stemming, lemmatization) if needed for NER.
     
  2. **Custom NER Model:**
     - Use **Spacy**'s pre-trained models for basic entity recognition (name, location, organizations, etc.).
     - Train a **custom NER model** to identify specific entities like `skills`, `education`, `work experience`, etc., since generic models may not identify them accurately.
       - Option 1: Use **Spacy** to annotate and train the model for `skills`, `job titles`, `companies`, and `education`.
       - Option 2: Use **predefined dictionaries** for common skills and job titles, combining them with NER results.
       
  3. **Data Structuring:**
     - Once entities are identified, structure the data into a JSON format with relevant fields (e.g., name, contact info, skills, education).
     - Example structured output:
       ```json
       {
         "name": "John Doe",
         "email": "john.doe@example.com",
         "education": ["B.Sc in Computer Science"],
         "skills": ["Python", "Machine Learning"],
         "experience": [
           {"company": "XYZ Corp", "position": "Data Scientist", "years": 3}
         ]
       }
       ```

  4. **Storing Data in MongoDB:**
     - Create MongoDB collections for resumes, storing the extracted information in a structured format for each candidate.
     - Each CV will be stored as a separate document in MongoDB for easy querying.
       - Example MongoDB document:
       ```json
       {
         "_id": "some_unique_id",
         "name": "John Doe",
         "email": "john.doe@example.com",
         "education": "B.Sc in Computer Science",
         "skills": ["Python", "Machine Learning"],
         "experience": [
           {"company": "XYZ Corp", "position": "Data Scientist", "years": 3}
         ]
       }
       ```

#### Step 3: **Resume Filtering**
- **Goal:** Allow recruiters to filter and search through candidates based on certain criteria (e.g., skills, experience).
- **Tasks:**
  1. **Filter UI on Frontend:**
     - Design a page using **Tailwind CSS** where recruiters can select filters such as:
       - Required skills (e.g., `Python`, `Machine Learning`)
       - Minimum or maximum years of experience.
       - Education level.
       
  2. **Backend Filtering Logic:**
     - Use **FastAPI** to create routes for filtering the MongoDB database.
     - Perform **queries on MongoDB** based on the recruiter’s selected filters:
       - E.g., filter candidates who have "Python" in their skills and more than 2 years of experience:
         ```python
         {"skills": {"$in": ["Python"]}, "experience.years": {"$gte": 2}}
         ```
     - Return the filtered results to the frontend for display.

  3. **Displaying Eligible Candidates:**
     - After the filtering, display the list of eligible candidates on the frontend.
     - Include a download or export option (e.g., CSV, Excel) for the recruiter to download the filtered resumes.

#### Step 4: **Future Enhancements (Optional)**
- **Sentiment Analysis:** Analyze the sentiment of resume descriptions or cover letters.
- **Resume Scoring:** Create a scoring mechanism to rank resumes based on relevance to the job description.
- **Integration with ATS:** Consider integrating the system with an Applicant Tracking System (ATS) to streamline the hiring process.
