import os
import json
import requests
from database.db import query_db

# Built-in Domain Knowledge Base for Offline / Zero-API Key Fallback
KNOWLEDGE_BASE = {
    'pointers': {
        'beginner': "💡 **Pointers Made Simple (Analogy):**\n\nImagine memory as a huge row of lockers in a school. Each locker has a **unique number (Memory Address)**, and inside the locker is the **actual item (Value)**.\n\n- Normal variable: `int a = 10;` (A locker named `a` holding the number 10).\n- Address-of operator `&`: `&a` gives the locker number (e.g., `0x7ffee`).\n- Pointer variable: `int *ptr = &a;` (A sticky note holding locker number `0x7ffee`).\n- Dereferencing operator `*`: `*ptr` means 'Go to that locker number and fetch the value inside' (which gives 10!).\n\n**Quick Example:**\n```c\nint x = 42;\nint *p = &x; // p stores the address of x\nprintf(\"Value of x = %d\\n\", *p); // prints 42\n```",
        'advanced': "⚡ **Deep Dive: Pointers, Memory Model & Pointer Arithmetic:**\n\nIn C, a pointer is a primitive variable that holds a virtual memory address pointing into the program's address space (Stack, Heap, Data segment).\n\n1. **Pointer Arithmetic:** `p + 1` does NOT increment by 1 byte; it increments by `sizeof(*p)` bytes (e.g. 4 bytes for `int32_t`, 8 bytes for `double`).\n2. **Dynamic Allocation & Dangling Pointers:**\n```c\nint *arr = (int*)malloc(10 * sizeof(int));\nif (!arr) return -1; // Allocation failure check\n// Use arr...\nfree(arr);\narr = NULL; // Crucial: Prevents dangling pointer dereference!\n```\n3. **Double Pointers (`**`)**: Used for 2D dynamic arrays, modifying pointer targets inside functions, or jagged memory tables."
    },
    'recursion': {
        'beginner': "🔁 **Recursion Explained Simply (Russian Nesting Dolls):**\n\nRecursion is when a function solves a problem by calling **a smaller version of itself** until it reaches the simplest possible case (the **Base Case**).\n\n**The Two Golden Rules:**\n1. **Base Case:** When should the function stop? Without this, it will repeat forever (Stack Overflow).\n2. **Recursive Step:** How do we shrink the problem towards the base case?\n\n**Example: Factorial (5! = 5 * 4 * 3 * 2 * 1)**\n```c\nint factorial(int n) {\n    if (n <= 1) return 1; // 1. Base Case\n    return n * factorial(n - 1); // 2. Recursive step\n}\n```",
        'advanced': "⚡ **Advanced Recursion, Call Stacks & Tail Call Optimization:**\n\nEach recursive invocation pushes a new **Stack Frame** (local variables, parameters, return address) onto the call stack.\n\n- **Stack Depth:** If recursion depth is $O(N)$, space complexity is $O(N)$ stack memory.\n- **Tail Recursion:** When the recursive call is the final evaluation step, compilers can optimize the stack frame into an iterative loop with $O(1)$ auxiliary stack overhead.\n```c\n// Tail Recursive Accumulator:\nint fact_tail(int n, int acc) {\n    if (n <= 1) return acc;\n    return fact_tail(n - 1, n * acc);\n}\n```"
    },
    'arrays': {
        'beginner': "📦 **Arrays in Plain English:**\n\nAn array is a collection of items of the **same type** stored side-by-side in continuous memory slots.\n\n- Think of an egg carton with numbered slots starting from **0** up to **size - 1**.\n- Fast lookups: You can jump directly to any slot instantly using its index in $O(1)$ time (e.g. `scores[0]`, `scores[1]`).",
        'advanced': "⚡ **Arrays, Cache Locality & Memory Layout:**\n\nIn C, 1D and 2D arrays (`arr[R][C]`) are contiguous in Row-Major order.\n\n- Element address formula: $\\text{Address}(arr[i][j]) = \\text{Base} + (i \\times C + j) \\times \\text{sizeof}(T)$.\n- **CPU Cache Locality:** Iterating row-by-row utilizes spatial locality and L1/L2 cache prefetching; iterating column-by-column causes frequent cache misses."
    },
    'linked_lists': {
        'beginner': "🔗 **Linked Lists vs Arrays:**\n\nUnlike arrays which need a continuous block of memory, a Linked List is like a **scavenger hunt**:\n- Each item is a 'Node' containing data and a clue (**pointer**) pointing to where the next node lives in memory.\n- Adding a new item at the beginning is super fast: you just create the node and point it to the current head.",
        'advanced': "⚡ **Linked List Engineering & Invariants:**\n\n- **Cycle Detection:** Floyd's Cycle Detection (Tortoise and Hare) uses two pointers ($v_1 = 1, v_2 = 2$) to detect loops in $O(N)$ time and $O(1)$ memory.\n- **In-place Reversal:** Requires 3 pointers (`prev`, `curr`, `next`) to flip pointers without extra memory."
    }
}

def ask_ai_tutor(student_id, question_text, topic_hint=None, user_level='beginner'):
    """
    Returns an educational response tailored to student's ability level.
    Uses Gemini/OpenAI if API keys exist, otherwise delivers an accurate, structured educational response.
    """
    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    openai_key = os.environ.get('OPENAI_API_KEY', '').strip()
    
    q_lower = question_text.lower()
    
    # Try calling Google Gemini API if configured
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini
                                                                                                                  _key}"
            prompt = f"""
You are a friendly, encouraging Smart AI Tutor on an educational platform.
Student mastery level: {user_level}.
Student Question: {question_text}

Rules:
1. If level is 'beginner', use relatable analogies, simple everyday comparisons, and clear short code snippets.
2. If level is 'advanced', provide rigorous technical depth, time/space complexities, and best practices.
3. Keep the format clean with markdown headings, bullet points, and code blocks.
"""
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                answer = data['candidates'][0]['content']['parts'][0]['text']
                return answer
        except Exception as e:
            print(f"Gemini API error, falling back to built-in knowledge base: {e}")

    # Fallback to Built-in Knowledge Base & Heuristic Tutor
    for key, responses in KNOWLEDGE_BASE.items():
        if key in q_lower or (topic_hint and key in topic_hint.lower()):
            return responses.get(user_level, responses.get('beginner'))
            
    # Universal fallback for various subjects
    if 'c program' in q_lower or 'c language' in q_lower or 'malloc' in q_lower:
        return """📚 **C Programming Core Concept:**
In C, memory is divided into:
1. **Stack**: Fast automatic memory for local variables and function calls.
2. **Heap**: Dynamic memory managed by the programmer using `malloc()`, `calloc()`, and `free()`.
3. **Data Segment**: Holds global and static variables.
4. **Code Segment**: Stores compiled machine instructions."""
    elif 'tree' in q_lower or 'bst' in q_lower:
        return """🌲 **Binary Search Trees (BST):**
A Binary Search Tree is a hierarchical node structure where:
- Left child values are strictly **smaller** than the parent.
- Right child values are strictly **greater** than the parent.
- **In-order Traversal** (Left -> Root -> Right) always yields sorted values in ascending order!"""
    elif 'matrix' in q_lower or 'determinant' in q_lower or 'math' in q_lower:
        return """📐 **Mathematics: Matrix & Determinant Essentials:**
- For a 2x2 matrix $\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$, the determinant is $|A| = ad - bc$.
- If $\\det(A) = 0$, the matrix is **singular** and cannot be inverted.
- Eigenvalues satisfy the characteristic equation $\\det(A - \\lambda I) = 0$."""
    elif 'physics' in q_lower or 'force' in q_lower or 'motion' in q_lower or 'newton' in q_lower:
        return """⚛️ **Physics: Laws of Motion & Energy:**
1. **Newton's 1st Law**: An object remains in uniform motion unless acted upon by a net external force.
2. **Newton's 2nd Law**: $\\vec{F} = m \\vec{a}$ (Net force equals mass times acceleration).
3. **Newton's 3rd Law**: For every action, there is an equal and opposite reaction."""
    else:
        return f"""🎓 **Smart AI Tutor Assistant:**

Here is a structured explanation for **"{question_text}"**:

1. **Core Concept:** Understanding the foundational definitions and working principles.
2. **Step-by-Step Breakdown:** Break complex problems into smaller, manageable pieces.
3. **Best Practice / Tip:** Try testing this with an adaptive quiz or interactive code example to reinforce your learning!

*Feel free to ask for specific code examples, analogies, or practice questions on any topic!*"""


def generate_questions_ai(subject_name, topic_name, difficulty, num_questions=3):
    """
    Generates structured multiple-choice questions for teachers.
    Uses Gemini if key exists, otherwise returns curated high quality questions.
    """
    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            prompt = f"""
Generate exactly {num_questions} multiple choice questions for Subject: '{subject_name}', Topic: '{topic_name}', Difficulty: '{difficulty}'.
Return ONLY a valid JSON array of objects with keys:
"question_text", "option_a", "option_b", "option_c", "option_d", "correct_option" (must be "A", "B", "C", or "D"), "explanation".
"""
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code == 200:
                raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                if '```json' in raw_text:
                    raw_text = raw_text.split('```json')[1].split('```')[0].strip()
                elif '```' in raw_text:
                    raw_text = raw_text.split('```')[1].split('```')[0].strip()
                return json.loads(raw_text)
        except Exception as e:
            print(f"AI generation failed, using rule-based generator: {e}")

    # Fallback Curated Generated Questions
    sample_pool = [
        {
            "question_text": f"What is a primary characteristic of {topic_name} at the {difficulty} level in {subject_name}?",
            "option_a": f"It requires understanding memory allocation and fundamental data types.",
            "option_b": f"It is only applicable in interpreted script languages.",
            "option_c": f"It removes the need for boundary checks.",
            "option_d": f"It is completely deprecated in modern standards.",
            "correct_option": "A",
            "explanation": f"Understanding fundamentals and memory behavior is essential for {topic_name} in {subject_name}."
        },
        {
            "question_text": f"Which time or space complexity standard typically applies to basic operations in {topic_name}?",
            "option_a": "O(1) or O(log n) for optimal balanced cases",
            "option_b": "O(n^4) in all common cases",
            "option_c": "O(n!) for sequential traversals",
            "option_d": "Undefined complexity",
            "correct_option": "A",
            "explanation": f"Most efficient algorithms in {topic_name} strive for constant O(1) or logarithmic O(log n) efficiency."
        },
        {
            "question_text": f"What is the recommended best practice when handling edge cases in {topic_name}?",
            "option_a": "Ignore NULL or boundary inputs",
            "option_b": "Always validate inputs, check null/empty conditions, and free allocated resources",
            "option_c": "Rely entirely on default compiler optimization",
            "option_d": "Use infinite loops without base conditions",
            "correct_option": "B",
            "explanation": "Defensive programming and resource deallocation are paramount in software engineering."
        }
    ]
    return sample_pool[:num_questions]
