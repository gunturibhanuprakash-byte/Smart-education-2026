-- Smart Education Platform Database Schema

PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    student_code TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    semester TEXT NOT NULL,
    learning_streak INTEGER DEFAULT 1,
    overall_percentage REAL DEFAULT 0.0,
    overall_performance_band TEXT DEFAULT 'Average',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Teachers Table
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT DEFAULT 'fa-book',
    color_theme TEXT DEFAULT '#4361ee'
);

-- 5. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    difficulty_weight REAL DEFAULT 1.0,
    order_index INTEGER DEFAULT 0,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- 6. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
    difficulty TEXT NOT NULL CHECK(difficulty IN ('easy', 'medium', 'hard')),
    explanation TEXT NOT NULL,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 7. Learning Materials Table
CREATE TABLE IF NOT EXISTS learning_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    resource_type TEXT NOT NULL CHECK(resource_type IN ('notes', 'video', 'example', 'exercise')),
    difficulty TEXT NOT NULL CHECK(difficulty IN ('beginner', 'intermediate', 'advanced')),
    description TEXT,
    content TEXT,
    link_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- 8. Student Marks Table
CREATE TABLE IF NOT EXISTS student_marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    internal_marks REAL DEFAULT 0.0,
    quiz_marks REAL DEFAULT 0.0,
    assignment_marks REAL DEFAULT 0.0,
    max_marks REAL DEFAULT 100.0,
    grade TEXT DEFAULT 'B',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(student_id, subject_id)
);

-- 9. Quiz Attempts Table
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    topic_id INTEGER,
    total_questions INTEGER NOT NULL,
    score INTEGER NOT NULL,
    percentage REAL NOT NULL,
    performance_band TEXT NOT NULL,
    difficulty_progression TEXT, -- JSON string e.g. ["easy","medium","hard"]
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
);

-- 10. Quiz Answers Table
CREATE TABLE IF NOT EXISTS quiz_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    student_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    difficulty_at_time TEXT NOT NULL,
    time_taken_seconds INTEGER DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- 11. Student Topic Mastery Table
CREATE TABLE IF NOT EXISTS student_topic_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    total_attempted INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    mastery_percentage REAL DEFAULT 50.0,
    status_band TEXT DEFAULT 'Average', -- 'Very Weak', 'Needs Improvement', 'Average', 'Good', 'Excellent'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    UNIQUE(student_id, topic_id)
);

-- 12. AI Chat History Table
CREATE TABLE IF NOT EXISTS ai_chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    message TEXT NOT NULL,
    topic TEXT,
    difficulty_level TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Indices for rapid querying
CREATE INDEX IF NOT EXISTS idx_questions_topic_diff ON questions(topic_id, difficulty);
CREATE INDEX IF NOT EXISTS idx_mastery_student ON student_topic_mastery(student_id);
CREATE INDEX IF NOT EXISTS idx_marks_student ON student_marks(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON quiz_attempts(student_id);
