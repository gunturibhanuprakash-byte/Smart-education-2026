/**
 * Adaptive Quiz Runner & Client-side Evaluation
 */

let selectedOption = null;
let currentQuestionId = null;
let isAnswerSubmitted = false;
let timerSeconds = 0;
let timerInterval = null;

function initQuiz(questionId) {
  currentQuestionId = questionId;
  selectedOption = null;
  isAnswerSubmitted = false;
  
  // Setup option selection listeners
  document.querySelectorAll('.option-tile').forEach(tile => {
    tile.addEventListener('click', function() {
      if (isAnswerSubmitted) return;
      
      document.querySelectorAll('.option-tile').forEach(t => t.classList.remove('selected'));
      this.classList.add('selected');
      selectedOption = this.getAttribute('data-option');
      
      const submitBtn = document.getElementById('btnSubmitAnswer');
      if (submitBtn) submitBtn.disabled = false;
    });
  });

  // Start question timer
  startTimer();
}

function startTimer() {
  timerSeconds = 0;
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timerSeconds++;
    const timerEl = document.getElementById('quizTimer');
    if (timerEl) {
      const mins = Math.floor(timerSeconds / 60);
      const secs = timerSeconds % 60;
      timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
  }, 1000);
}

function submitCurrentAnswer() {
  if (!selectedOption || !currentQuestionId || isAnswerSubmitted) return;
  
  isAnswerSubmitted = true;
  if (timerInterval) clearInterval(timerInterval);

  const submitBtn = document.getElementById('btnSubmitAnswer');
  if (submitBtn) submitBtn.style.display = 'none';

  // Send answer to server for adaptive evaluation
  fetch('/quiz/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question_id: currentQuestionId,
      student_answer: selectedOption,
      time_taken: timerSeconds
    })
  })
  .then(res => res.json())
  .then(data => {
    // Highlight tiles
    document.querySelectorAll('.option-tile').forEach(tile => {
      const opt = tile.getAttribute('data-option');
      if (opt === data.correct_option) {
        tile.classList.add('correct');
      } else if (opt === selectedOption && !data.is_correct) {
        tile.classList.add('incorrect');
      }
    });

    // Display Explanation Box
    const feedbackBox = document.getElementById('feedbackBox');
    const feedbackTitle = document.getElementById('feedbackTitle');
    const feedbackExpl = document.getElementById('feedbackExplanation');
    const nextBtn = document.getElementById('btnNextQuestion');
    const finishBtn = document.getElementById('btnFinishQuiz');

    if (feedbackBox) {
      feedbackBox.className = `feedback-box show ${data.is_correct ? 'correct' : 'incorrect'}`;
      feedbackTitle.innerHTML = data.is_correct 
        ? '<i class="fas fa-check-circle"></i> Correct Answer!' 
        : '<i class="fas fa-times-circle"></i> Incorrect Answer';
      feedbackExpl.textContent = data.explanation;
    }

    // Update Difficulty Badge for upcoming question
    const diffBadge = document.getElementById('currentDiffBadge');
    if (diffBadge && data.next_difficulty) {
      diffBadge.className = `difficulty-badge difficulty-${data.next_difficulty}`;
      diffBadge.innerHTML = `<i class="fas fa-bolt"></i> Difficulty: ${data.next_difficulty.toUpperCase()}`;
    }

    // Toggle Next vs Finish button
    if (data.is_finished) {
      if (finishBtn) finishBtn.style.display = 'inline-flex';
    } else {
      if (nextBtn) nextBtn.style.display = 'inline-flex';
    }
  })
  .catch(err => {
    console.error('Quiz submission error:', err);
    alert('Failed to evaluate answer. Please try again.');
  });
}

function proceedToNextQuestion() {
  window.location.reload();
}

function finishQuizAttempt() {
  fetch('/quiz/finish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    }
  });
}
