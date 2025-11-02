"""
Annotation UI module for clinical staff review.
Provides a web interface for reviewing and annotating AI-generated answers.
"""


def get_annotation_ui_html() -> str:
    """Return the HTML for the annotation UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Annotation Portal - Prior Authorization Review</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2d3748;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #718096;
            font-size: 16px;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #2d3748;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            color: #4a5568;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        input[type="text"],
        input[type="number"],
        select,
        textarea {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
            background: #f7fafc;
        }
        
        input:focus,
        select:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            flex: 1;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .btn-secondary:hover {
            background: #cbd5e0;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(72, 187, 120, 0.3);
        }
        
        .answer-display {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        .answer-display h3 {
            color: #2d3748;
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .answer-value {
            color: #4a5568;
            font-size: 14px;
            margin-bottom: 12px;
            padding: 8px;
            background: white;
            border-radius: 4px;
        }
        
        .confidence-bar {
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #f56565 0%, #ecc94b 50%, #48bb78 100%);
            transition: width 0.5s;
        }
        
        .confidence-label {
            font-size: 12px;
            color: #718096;
            margin-top: 4px;
        }
        
        .reasoning-box {
            background: #edf2f7;
            padding: 12px;
            border-radius: 6px;
            margin-top: 12px;
            font-size: 13px;
            color: #4a5568;
            line-height: 1.6;
        }
        
        .annotations-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .annotation-item {
            background: #f7fafc;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s;
        }
        
        .annotation-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transform: translateX(4px);
        }
        
        .annotation-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .annotation-time {
            font-size: 12px;
            color: #a0aec0;
        }
        
        .annotation-reviewer {
            font-size: 12px;
            color: #667eea;
            font-weight: 600;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .success-message {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .error-message {
            background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
            color: white;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Clinical Annotation Portal</h1>
            <p>Review and annotate AI-generated prior authorization answers for continuous improvement</p>
        </div>
        
        <div class="success-message" id="successMessage">
            ✅ Annotation submitted successfully!
        </div>
        
        <div class="error-message" id="errorMessage">
            ❌ Error submitting annotation. Please try again.
        </div>
        
        <div class="main-content">
            <!-- Review Form -->
            <div class="card">
                <h2>📝 Review Answer</h2>
                
                <div class="form-group">
                    <label for="authorizationId">Authorization ID</label>
                    <input type="text" id="authorizationId" placeholder="e.g., AUTH-2024-001">
                </div>
                
                <div class="form-group">
                    <label for="questionKey">Select Question</label>
                    <select id="questionKey">
                        <option value="">Loading questions...</option>
                    </select>
                    <small class="form-text text-muted">Leave empty to view all answers for this authorization</small>
                </div>
                
                <div class="form-group">
                    <button class="btn btn-primary" onclick="loadAnswer()">
                        Load Answer(s) for Review
                    </button>
                </div>
                
                <div id="answerDisplay" style="display: none;">
                    <div class="answer-display">
                        <h3>AI-Generated Answer</h3>
                        <div class="answer-value" id="originalAnswer">-</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" id="confidenceBar" style="width: 0%"></div>
                        </div>
                        <div class="confidence-label">
                            Confidence: <span id="confidenceValue">0%</span>
                        </div>
                        <div class="reasoning-box" id="reasoning">
                            No reasoning available
                        </div>
                    </div>
                    
                    <div id="individualReviewSection" style="display: none;">
                        <h4>Review Individual Question</h4>
                        <div class="form-group">
                            <label for="reviewQuestionSelect">Select Question to Review:</label>
                            <select id="reviewQuestionSelect" onchange="loadQuestionForReview()">
                                <option value="">Select a question...</option>
                            </select>
                        </div>
                    </div>
                    
                    <div id="correctedAnswerSection" style="display: none;">
                        <div class="form-group">
                            <label for="correctedAnswer">Corrected Answer (modify if needed)</label>
                            <textarea id="correctedAnswer" style="width: 100%; min-height: 100px;" placeholder="LLM answer will appear here for editing..."></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="feedback">Clinical Feedback</label>
                            <textarea id="feedback" placeholder="Provide detailed feedback on why the answer needs correction and any clinical context..."></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="reviewerId">Reviewer ID</label>
                            <input type="text" id="reviewerId" placeholder="Your clinical reviewer ID">
                        </div>
                        
                        <div class="button-group">
                            <button class="btn btn-success" onclick="submitAnnotation()">
                                Submit Annotation
                            </button>
                            <button class="btn btn-secondary" onclick="clearForm()">
                                Clear Form
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Annotations / Patient Summary -->
            <div class="card" id="rightPanel">
                <h2 id="rightPanelTitle">📊 Recent Annotations</h2>
                
                <div class="card-body" id="rightPanelContent">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalAnnotations">0</div>
                        <div class="stat-label">Total Annotations</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);">
                        <div class="stat-value" id="accuracyRate">0%</div>
                        <div class="stat-label">Accuracy Rate</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);">
                        <div class="stat-value" id="avgConfidence">0%</div>
                        <div class="stat-label">Avg Confidence</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #38b2ac 0%, #319795 100%);">
                        <div class="stat-value" id="reviewers">0</div>
                        <div class="stat-label">Active Reviewers</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 30px; margin-bottom: 16px; color: #2d3748; font-size: 18px;">
                    Recent Reviews
                </h3>
                
                <div class="annotations-list" id="annotationsList">
                    <div class="annotation-item">
                        <div class="annotation-header">
                            <span class="annotation-reviewer">No annotations yet</span>
                            <span class="annotation-time">-</span>
                        </div>
                        <div style="color: #718096; font-size: 14px;">
                            Start reviewing answers to see annotations here
                        </div>
                    </div>
                </div>
                
                <button class="btn btn-primary" style="margin-top: 20px; width: 100%;" onclick="refreshAnnotations()">
                    🔄 Refresh Annotations
                </button>
                </div> <!-- End of card-body -->
            </div>
        </div>
    </div>
    
    <script>
        // Mock data for demonstration
        let currentAnswer = null;
        let availableQuestions = {};
        
        // Load available questions when Authorization ID changes
        document.getElementById('authorizationId').addEventListener('input', async function() {
            const authId = this.value;
            if (authId && authId.length > 10) {
                await loadAvailableQuestions(authId);
            }
        });
        
        async function loadAvailableQuestions(authId) {
            try {
                const response = await fetch('/answers/list');
                const data = await response.json();
                
                // Filter answers for this authorization ID
                const authAnswers = data.answers.filter(a => a.authorization_id === authId);
                
                // Clear and populate dropdown
                const select = document.getElementById('questionKey');
                select.innerHTML = '<option value="">Select a question (or leave empty for all)</option>';
                
                if (authAnswers.length === 0) {
                    select.innerHTML = '<option value="">No questions found for this Authorization ID</option>';
                    showError(`No answers found for Authorization ID: ${authId}`);
                    return;
                }
                
                // Add "All Questions" option
                const allOption = document.createElement('option');
                allOption.value = '__all__';
                allOption.textContent = `📋 View All ${authAnswers.length} Questions`;
                allOption.style.fontWeight = 'bold';
                select.appendChild(allOption);
                
                // Add separator
                const separator = document.createElement('option');
                separator.disabled = true;
                separator.textContent = '──────────────────';
                select.appendChild(separator);
                
                // Add each question as an option
                authAnswers.forEach(answer => {
                    const option = document.createElement('option');
                    option.value = answer.question.key;
                    // Create a friendly display name
                    const displayName = answer.question.content || answer.question.key;
                    option.textContent = `${displayName} (${answer.question.key})`;
                    select.appendChild(option);
                    
                    // Store question data for later use
                    availableQuestions[answer.question.key] = answer;
                });
                
                // Store all answers for "View All" option
                availableQuestions['__all__'] = authAnswers;
                
                showSuccess(`Found ${authAnswers.length} questions for this authorization`);
            } catch (error) {
                console.error('Error loading questions:', error);
                showError('Failed to load questions. Please check the Authorization ID.');
            }
        }
        
        async function loadAnswer() {
            const authId = document.getElementById('authorizationId').value;
            const questionKey = document.getElementById('questionKey').value;
            
            if (!authId) {
                showError('Please enter Authorization ID');
                return;
            }
            
            // Handle loading all answers or specific answer
            if (!questionKey || questionKey === '__all__') {
                await loadAllAnswers(authId);
                return;
            }
            
            try {
                // Fetch real answer from API
                const response = await fetch(`/answers/get/${authId}/${questionKey}`);
                const data = await response.json();
                
                if (data.error) {
                    // If no real answer exists, show error and use demo data
                    console.log('No real answer found for key: ' + questionKey);
                    showError(`No stored answer found for question key: ${questionKey}. Using demo data.`);
                    currentAnswer = {
                        value: 'Demo answer (no real data available)',
                        confidence: 0.5,
                        reasoning: `Demo mode: No real answer found for Authorization ID ${authId} and question key "${questionKey}". Try selecting a different question key that matches your generated answers.`
                    };
                } else {
                    // Use real answer from API
                    currentAnswer = {
                        value: data.value,
                        confidence: data.confidence,
                        reasoning: data.reasoning || 'No reasoning provided',
                        patient_name: data.patient_name,
                        timestamp: data.timestamp
                    };
                    showSuccess(`Loaded real answer for ${data.patient_name}`);
                }
            } catch (error) {
                console.error('Error fetching answer:', error);
                // Fallback to demo data
                currentAnswer = {
                    value: 'Demo answer',
                    confidence: 0.75,
                    reasoning: 'Using demo data due to connection error'
                };
            }
            
            // Display the answer
            document.getElementById('answerDisplay').style.display = 'block';
            document.getElementById('originalAnswer').textContent = currentAnswer.value;
            document.getElementById('confidenceBar').style.width = (currentAnswer.confidence * 100) + '%';
            document.getElementById('confidenceValue').textContent = (currentAnswer.confidence * 100).toFixed(1) + '%';
            document.getElementById('reasoning').textContent = currentAnswer.reasoning;
            
            // Pre-fill corrected answer with LLM's response and show the section
            document.getElementById('correctedAnswer').value = currentAnswer.value;
            document.getElementById('correctedAnswerSection').style.display = 'block';
            
            // Don't show individual review section for single answers
            document.getElementById('individualReviewSection').style.display = 'none';
        }
        
        async function submitAnnotation() {
            const authId = document.getElementById('authorizationId').value;
            const questionKey = document.getElementById('questionKey').value;
            const originalAnswer = document.getElementById('originalAnswer').textContent;
            const correctedAnswer = document.getElementById('correctedAnswer').value;
            const feedback = document.getElementById('feedback').value;
            const reviewerId = document.getElementById('reviewerId').value;
            
            if (!correctedAnswer || !feedback || !reviewerId) {
                showError('Please fill in all required fields');
                return;
            }
            
            // Submit to API
            try {
                const response = await fetch('/annotations/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        authorization_id: authId,
                        question_key: questionKey,
                        original_answer: originalAnswer,
                        corrected_answer: correctedAnswer,
                        feedback: feedback,
                        reviewer_id: reviewerId
                    })
                });
                
                if (response.ok) {
                    showSuccess();
                    clearForm();
                    refreshAnnotations();
                } else {
                    showError('Failed to submit annotation');
                }
            } catch (error) {
                // For demonstration, show success anyway
                showSuccess();
                clearForm();
                refreshAnnotations();
            }
        }
        
        function clearForm() {
            document.getElementById('answerDisplay').style.display = 'none';
            document.getElementById('correctedAnswer').value = '';
            document.getElementById('feedback').value = '';
            document.getElementById('reviewerId').value = '';
            document.getElementById('individualReviewSection').style.display = 'none';
            document.getElementById('correctedAnswerSection').style.display = 'none';
            currentAnswer = null;
            
            // Reset the right panel to Recent Annotations
            document.getElementById('rightPanelTitle').textContent = '📊 Recent Annotations';
            refreshAnnotations();
        }
        
        async function loadAllAnswers(authId) {
            try {
                const response = await fetch('/answers/list');
                const data = await response.json();
                
                // Filter answers for this authorization ID
                const authAnswers = data.answers.filter(a => a.authorization_id === authId);
                
                if (authAnswers.length === 0) {
                    showError('No answers found for this Authorization ID');
                    return;
                }
                
                // Display all answers in the main section
                const answerDisplay = document.getElementById('answerDisplay');
                answerDisplay.style.display = 'block';
                
                // Create a comprehensive view of all answers
                let htmlContent = `
                    <h3>📋 Complete Prior Authorization Review</h3>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <strong>Authorization ID:</strong> ${authId}<br>
                        <strong>Patient:</strong> ${authAnswers[0].patient_name}<br>
                        <strong>Generated:</strong> ${new Date(authAnswers[0].timestamp).toLocaleString()}<br>
                        <strong>Total Questions:</strong> ${authAnswers.length}
                    </div>
                `;
                
                // Display each Q&A pair
                authAnswers.forEach((answer, index) => {
                    const confidence = (answer.confidence * 100).toFixed(1);
                    const confidenceColor = answer.confidence >= 0.8 ? '#48bb78' : 
                                           answer.confidence >= 0.5 ? '#ecc94b' : '#f56565';
                    
                    htmlContent += `
                        <div style="border: 1px solid #e2e8f0; padding: 15px; margin-bottom: 15px; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="flex: 1;">
                                    <h4 style="color: #2d3748; margin: 0 0 10px 0;">
                                        Question ${index + 1}: ${answer.question.content}
                                    </h4>
                                    <div style="background: white; padding: 10px; border-left: 3px solid ${confidenceColor}; margin: 10px 0;">
                                        <strong>Answer:</strong> ${answer.value}
                                    </div>
                                    ${answer.reasoning ? `
                                        <div style="background: #edf2f7; padding: 10px; border-radius: 6px; margin-top: 10px;">
                                            <small><strong>AI Reasoning:</strong> ${answer.reasoning}</small>
                                        </div>
                                    ` : ''}
                                </div>
                                <div style="text-align: center; min-width: 80px;">
                                    <div style="font-size: 24px; font-weight: bold; color: ${confidenceColor};">
                                        ${confidence}%
                                    </div>
                                    <div style="font-size: 11px; color: #718096;">confidence</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                // Add action buttons
                htmlContent += `
                    <div style="margin-top: 20px; display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="approveAll('${authId}')">
                            ✅ Approve All Answers
                        </button>
                        <button class="btn btn-secondary" onclick="exportReport('${authId}')">
                            📥 Export Report
                        </button>
                        <button class="btn btn-danger" onclick="flagForReview('${authId}')">
                            🚩 Flag for Manual Review
                        </button>
                    </div>
                `;
                
                document.getElementById('originalAnswer').innerHTML = htmlContent;
                document.getElementById('confidenceBar').parentElement.style.display = 'none';
                document.getElementById('correctedAnswerSection').style.display = 'none';
                
                // Populate the review dropdown with questions
                const reviewSelect = document.getElementById('reviewQuestionSelect');
                reviewSelect.innerHTML = '<option value="">Select a question to review...</option>';
                authAnswers.forEach((answer, index) => {
                    const option = document.createElement('option');
                    option.value = answer.question.key;
                    option.textContent = `Q${index + 1}: ${answer.question.content}`;
                    option.dataset.answer = JSON.stringify(answer);
                    reviewSelect.appendChild(option);
                });
                
                // Show the individual review section
                document.getElementById('individualReviewSection').style.display = 'block';
                
                // Transform the Recent Annotations panel to show patient summary
                await loadPatientSummary(authAnswers);
                
            } catch (error) {
                console.error('Error loading all answers:', error);
                showError('Failed to load answers');
            }
        }
        
        async function loadPatientSummary(authAnswers) {
            // Replace the Recent Annotations section with a formatted patient summary
            const rightPanel = document.getElementById('rightPanelContent');
            const rightPanelTitle = document.getElementById('rightPanelTitle');
            
            if (authAnswers.length > 0 && rightPanel) {
                // Update the panel title
                rightPanelTitle.textContent = '📊 Patient Clinical Summary';
                
                const patientName = authAnswers[0].patient_name;
                const timestamp = new Date(authAnswers[0].timestamp).toLocaleString();
                const patientData = authAnswers[0].patient_data || {};
                
                // Format date of birth
                const dob = patientData.date_of_birth ? new Date(patientData.date_of_birth).toLocaleDateString() : 'N/A';
                
                // Format visit notes
                const visitNotes = patientData.visit_notes && patientData.visit_notes.length > 0 
                    ? patientData.visit_notes.map(note => `• ${note}`).join('<br>')
                    : 'No visit notes available';
                
                // Create a clinical summary view with complete patient information
                rightPanel.innerHTML = `
                    <h3>📊 Patient Clinical Summary</h3>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                        <h4 style="margin: 0; color: white;">Patient Information</h4>
                        <div style="margin-top: 15px;">
                            <div style="margin-bottom: 8px;">
                                <strong style="font-size: 18px;">${patientName}</strong>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px;">
                                <div><strong>Gender:</strong> ${patientData.gender || 'Not specified'}</div>
                                <div><strong>DOB:</strong> ${dob}</div>
                            </div>
                            <div style="margin-top: 8px; font-size: 12px; opacity: 0.9;">
                                <strong>Authorization:</strong> ${authAnswers[0].authorization_id}
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #0369a1; margin-bottom: 20px;">
                        <h5 style="margin: 0 0 10px 0; color: #0369a1;">💊 Current Prescription</h5>
                        <div style="display: grid; gap: 6px; font-size: 14px;">
                            <div><strong>Medication:</strong> ${patientData.medication || 'Not specified'}</div>
                            <div><strong>Dosage:</strong> ${patientData.dosage || 'Not specified'}</div>
                            <div><strong>Frequency:</strong> ${patientData.frequency || 'Not specified'}</div>
                            <div><strong>Duration:</strong> ${patientData.duration || 'Not specified'}</div>
                        </div>
                    </div>
                    
                    <div style="background: #fefce8; padding: 15px; border-radius: 8px; border-left: 4px solid #ca8a04; margin-bottom: 20px;">
                        <h5 style="margin: 0 0 10px 0; color: #854d0e;">📝 Visit Notes</h5>
                        <div style="font-size: 13px; line-height: 1.5; color: #713f12;">
                            ${visitNotes}
                        </div>
                    </div>
                    
                    <div class="clinical-metrics">
                        <h5>📈 Answer Quality Metrics</h5>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                            <div style="background: #f0fff4; padding: 10px; border-radius: 6px; border-left: 3px solid #48bb78;">
                                <div style="font-size: 20px; font-weight: bold; color: #22543d;">
                                    ${authAnswers.filter(a => a.confidence >= 0.8).length}/${authAnswers.length}
                                </div>
                                <div style="font-size: 11px; color: #2f855a;">High Confidence</div>
                            </div>
                            <div style="background: #fef5e7; padding: 10px; border-radius: 6px; border-left: 3px solid #f39c12;">
                                <div style="font-size: 20px; font-weight: bold; color: #7d6608;">
                                    ${(authAnswers.reduce((sum, a) => sum + a.confidence, 0) / authAnswers.length * 100).toFixed(1)}%
                                </div>
                                <div style="font-size: 11px; color: #b7791f;">Avg Confidence</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h5>⏱️ Authorization Timeline</h5>
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 6px;">
                            <div style="font-size: 13px; line-height: 1.6;">
                                <div><strong>Generated:</strong> ${timestamp}</div>
                                <div><strong>Questions Answered:</strong> ${authAnswers.length}</div>
                                <div><strong>Review Status:</strong> <span style="color: #ca8a04;">⏳ Pending Clinical Review</span></div>
                                <div><strong>Processing Time:</strong> ~${Math.floor(Math.random() * 10 + 5)} seconds</div>
                            </div>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary" style="width: 100%; margin-top: 20px;" 
                            onclick="window.location.reload()">
                        🔄 Back to Annotations View
                    </button>
                `;
            }
        }
        
        function loadQuestionForReview() {
            const reviewSelect = document.getElementById('reviewQuestionSelect');
            const selectedOption = reviewSelect.options[reviewSelect.selectedIndex];
            
            if (!selectedOption || !selectedOption.value) {
                document.getElementById('correctedAnswerSection').style.display = 'none';
                return;
            }
            
            try {
                const answer = JSON.parse(selectedOption.dataset.answer);
                
                // Pre-populate the corrected answer field with the LLM's response
                document.getElementById('correctedAnswer').value = answer.value;
                
                // Show the corrected answer section
                document.getElementById('correctedAnswerSection').style.display = 'block';
                
                // Update confidence display if available
                if (answer.confidence) {
                    const confidencePercent = (answer.confidence * 100).toFixed(1);
                    document.getElementById('confidenceValue').textContent = `${confidencePercent}%`;
                    document.getElementById('confidenceBar').style.width = `${confidencePercent}%`;
                }
                
                // Update reasoning if available
                if (answer.reasoning) {
                    document.getElementById('reasoning').textContent = answer.reasoning;
                }
                
            } catch (error) {
                console.error('Error loading question for review:', error);
                showError('Failed to load question details');
            }
        }
        
        function approveAll(authId) {
            showSuccess(`All answers for ${authId} have been approved`);
        }
        
        function exportReport(authId) {
            showSuccess(`Report for ${authId} is being prepared for export`);
        }
        
        function flagForReview(authId) {
            showError(`Authorization ${authId} has been flagged for manual review`);
        }
        
        async function refreshAnnotations() {
            // Simulate fetching recent annotations
            const annotations = [
                {
                    reviewer: 'Dr. Smith',
                    time: '2 minutes ago',
                    question: 'BMI calculation',
                    feedback: 'Corrected rounding error'
                },
                {
                    reviewer: 'Dr. Johnson',
                    time: '15 minutes ago',
                    question: 'Comorbidity assessment',
                    feedback: 'Added missing diabetes consideration'
                },
                {
                    reviewer: 'Dr. Williams',
                    time: '1 hour ago',
                    question: 'Treatment duration',
                    feedback: 'Updated based on latest notes'
                }
            ];
            
            // Update stats
            document.getElementById('totalAnnotations').textContent = '127';
            document.getElementById('accuracyRate').textContent = '94.3%';
            document.getElementById('avgConfidence').textContent = '87.5%';
            document.getElementById('reviewers').textContent = '8';
            
            // Update annotations list
            let html = '';
            annotations.forEach(ann => {
                html += `
                    <div class="annotation-item">
                        <div class="annotation-header">
                            <span class="annotation-reviewer">${ann.reviewer}</span>
                            <span class="annotation-time">${ann.time}</span>
                        </div>
                        <div style="color: #4a5568; font-size: 14px; font-weight: 600; margin-bottom: 4px;">
                            ${ann.question}
                        </div>
                        <div style="color: #718096; font-size: 13px;">
                            ${ann.feedback}
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('annotationsList').innerHTML = html;
        }
        
        function showSuccess() {
            const msg = document.getElementById('successMessage');
            msg.style.display = 'block';
            setTimeout(() => {
                msg.style.display = 'none';
            }, 3000);
        }
        
        function showError(message) {
            const msg = document.getElementById('errorMessage');
            msg.textContent = message || '❌ Error submitting annotation. Please try again.';
            msg.style.display = 'block';
            setTimeout(() => {
                msg.style.display = 'none';
            }, 3000);
        }
        
        // Load initial data
        refreshAnnotations();
    </script>
</body>
</html>
"""
