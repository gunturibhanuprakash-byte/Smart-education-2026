import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from werkzeug.security import generate_password_hash
from database.db import get_db, init_db


def seed_database():
    """Populates the database with realistic sample data for demo and hackathon presentation."""
    with get_db() as conn:
        conn.executescript("""
            DROP TABLE IF EXISTS ai_chat_history;
            DROP TABLE IF EXISTS quiz_answers;
            DROP TABLE IF EXISTS quiz_attempts;
            DROP TABLE IF EXISTS student_topic_mastery;
            DROP TABLE IF EXISTS student_marks;
            DROP TABLE IF EXISTS learning_materials;
            DROP TABLE IF EXISTS questions;
            DROP TABLE IF EXISTS topics;
            DROP TABLE IF EXISTS subjects;
            DROP TABLE IF EXISTS teachers;
            DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS users;
        """)
    init_db()
    
    with get_db() as conn:

        
        print("Seeding Users...")
        # 1. Teachers
        teacher_pw = generate_password_hash('teacher123')
        conn.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email, avatar_url)
            VALUES (?, ?, 'teacher', ?, ?, ?)
        """, ('teacher1', teacher_pw, 'Prof. Arvind Swaminathan', 'arvind.prof@smartedu.org', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'))
        teacher_user_id = conn.execute("SELECT id FROM users WHERE username='teacher1'").fetchone()[0]
        
        conn.execute("""
            INSERT INTO teachers (user_id, department, designation)
            VALUES (?, 'Computer Science & Engineering', 'Associate Professor')
        """, (teacher_user_id,))
        
        # 2. Students
        student_pw = generate_password_hash('student123')
        student_users = [
            ('student1', 'Rahul Sharma', 'rahul.s@smartedu.org', 'STU202601', 'CSE', 'Semester 2', 7, 76.0, 'Good'),
            ('student2', 'Priya Patel', 'priya.p@smartedu.org', 'STU202602', 'EEE', 'Semester 1', 12, 92.5, 'Excellent'),
            ('student3', 'Ankit Verma', 'ankit.v@smartedu.org', 'STU202603', 'ECE', 'Semester 5', 3, 54.0, 'Needs Improvement'),
            ('student4', 'Sneha Reddy', 'sneha.r@smartedu.org', 'STU202604', 'IT', 'Semester 3', 5, 68.5, 'Average'),
            ('student5', 'Vikram Singh', 'vikram.s@smartedu.org', 'STU202605', 'MECH', 'Semester 4', 1, 38.0, 'Very Weak'),
            ('student20', 'Priya Patel', 'priya.p@smartedu.org', 'STU202602', 'CIVIL', 'Semester 2', 12, 92.5, 'Excellent'),
        ]
        
        student_id_map = {}
        for username, full_name, email, code, branch, sem, streak, pct, band in student_users:
            conn.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, 'student', ?, ?)
            """, (username, student_pw, full_name, email))
            uid = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
            
            conn.execute("""
                INSERT INTO students (user_id, student_code, branch, semester, learning_streak, overall_percentage, overall_performance_band)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uid, code, branch, sem, streak, pct, band))
            sid = conn.execute("SELECT id FROM students WHERE user_id=?", (uid,)).fetchone()[0]
            student_id_map[username] = sid

        print("Seeding Subjects and Topics...")
        # 3. Subjects
        subjects_data = [
            ('CS101', 'C Programming', 'Foundations of structured programming, pointers, memory management, and file systems.', 'fa-code', '#4361ee'),
            ('CS201', 'Data Structures', 'Abstract data types, linear and non-linear data structures, algorithms, and complexity.', 'fa-sitemap', '#3a0ca3'),
            ('MA101', 'Mathematics', 'Linear algebra, matrix operations, multivariable calculus, and probability distributions.', 'fa-calculator', '#7209b7'),
            ('PH101', 'Engineering Physics', 'Classical mechanics, electromagnetism, wave optics, and introductory quantum mechanics.', 'fa-atom', '#00b4d8'),
        ]
        
        subject_id_map = {}
        for code, name, desc, icon, color in subjects_data:
            conn.execute("""
                INSERT INTO subjects (code, name, description, icon, color_theme)
                VALUES (?, ?, ?, ?, ?)
            """, (code, name, desc, icon, color))
            sub_id = conn.execute("SELECT id FROM subjects WHERE code=?", (code,)).fetchone()[0]
            subject_id_map[code] = sub_id

        # 4. Topics
        topics_data = {
            'CS101': [
                ('Arrays', 'Single and multidimensional array operations and memory layout.', 1.0, 1),
                ('Functions', 'Modular programming, parameter passing by value and reference.', 1.1, 2),
                ('Strings', 'Character array manipulation, null terminators, and string functions.', 1.1, 3),
                ('Structures', 'User-defined composite types, nested structures, and unions.', 1.2, 4),
                ('Pointers', 'Memory addresses, dereferencing, pointer arithmetic, and double pointers.', 1.5, 5),
                ('Recursion', 'Base cases, recursive call stacks, and recursive problem solving.', 1.4, 6),
            ],
            'CS201': [
                ('Linked Lists', 'Singly, doubly, and circular linked lists with pointer operations.', 1.2, 1),
                ('Stacks & Queues', 'LIFO & FIFO data structures, array and list implementations.', 1.1, 2),
                ('Trees & BST', 'Binary trees, traversals (inorder, preorder, postorder), and binary search trees.', 1.4, 3),
                ('Graph Algorithms', 'Adjacency representation, BFS, DFS, and shortest path basics.', 1.6, 4),
            ],
            'MA101': [
                ('Linear Algebra & Matrices', 'Matrix determinants, rank, inverse, and eigenvalues.', 1.2, 1),
                ('Calculus & Derivatives', 'Limits, continuity, partial derivatives, and optimization.', 1.3, 2),
                ('Probability & Statistics', 'Random variables, Bayes theorem, normal distributions.', 1.2, 3),
            ],
            'PH101': [
                ('Mechanics & Motion', "Newton's laws, rotational dynamics, work-energy theorem.", 1.1, 1),
                ('Electromagnetism', "Coulomb's law, Gauss law, magnetic fields, and Maxwell equations.", 1.4, 2),
                ('Wave Optics & Lasers', 'Interference, diffraction, polarization, and laser physics.', 1.3, 3),
            ]
        }
        
        topic_id_map = {}
        for sub_code, topics in topics_data.items():
            sub_id = subject_id_map[sub_code]
            for t_name, t_desc, weight, order in topics:
                conn.execute("""
                    INSERT INTO topics (subject_id, name, description, difficulty_weight, order_index)
                    VALUES (?, ?, ?, ?, ?)
                """, (sub_id, t_name, t_desc, weight, order))
                tid = conn.execute("SELECT id FROM topics WHERE subject_id=? AND name=?", (sub_id, t_name)).fetchone()[0]
                topic_id_map[t_name] = tid

        print("Seeding Questions Bank...")
        # 5. Questions (60+ comprehensive questions with Easy, Medium, Hard tiers)
        questions_list = [
            # C Programming - Arrays
            ('CS101', 'Arrays', 'What is the index of the first element in a C array?', '1', '0', '-1', 'Undefined', 'B', 'easy', 'In C programming language, arrays are zero-indexed, meaning the first element is at index 0.'),
            ('CS101', 'Arrays', 'What happens if you access an array element beyond its defined bounds in C?', 'Compile-time error', 'Array automatically resizes', 'Undefined behavior (can access junk memory or crash)', 'Returns 0', 'C', 'medium', 'C does not perform boundary checks at runtime; accessing out of bounds causes undefined behavior.'),
            ('CS101', 'Arrays', 'If `int arr[3][4]` is stored in row-major order, what is the formula to find the offset of `arr[i][j]` from the base address?', '(i * 3 + j) * sizeof(int)', '(i * 4 + j) * sizeof(int)', '(j * 4 + i) * sizeof(int)', '(i + j) * sizeof(int)', 'B', 'hard', 'In row-major 2D array arr[R][C], offset for (i, j) is (i * C + j) * element_size. Here C=4.'),
            
            # C Programming - Functions
            ('CS101', 'Functions', 'Which keyword is used in C to define a function that does not return any value?', 'null', 'empty', 'void', 'static', 'C', 'easy', 'The `void` keyword indicates that a function has no return value.'),
            ('CS101', 'Functions', 'In C, arguments to a function are by default passed by:', 'Value', 'Reference', 'Pointer', 'Address', 'A', 'medium', 'C functions use pass-by-value by default. To simulate pass-by-reference, pointers must be explicitly passed.'),
            ('CS101', 'Functions', 'What is a function pointer in C and how is it invoked?', 'A pointer to the return value', 'A variable that stores the memory address of executable code in a function', 'A function that returns a pointer', 'An array of function names', 'B', 'hard', 'A function pointer holds the entry address of a function and can be used for callbacks and dynamic function dispatch.'),
            
            # C Programming - Strings
            ('CS101', 'Strings', 'Which character marks the termination of a string in C?', '\\n', '\\t', '\\0', '\\s', 'C', 'easy', 'Strings in C are null-terminated character arrays ending with the null character `\\0`.'),
            ('CS101', 'Strings', 'Which standard library function is used to compare two strings lexicographically in C?', 'strcmp()', 'strcmpi()', 'strcat()', 'strlen()', 'A', 'medium', '`strcmp(str1, str2)` from `<string.h>` returns 0 if strings are identical, negative if str1 < str2, and positive if str1 > str2.'),
            ('CS101', 'Strings', 'What is the risk of using `gets()` function in C?', 'Slow execution', 'Causes buffer overflow vulnerability because it does not limit input size', 'Does not support uppercase letters', 'Memory leaks automatically', 'B', 'hard', '`gets()` reads input until a newline without checking buffer size, making it a critical security hazard replaced by `fgets()`.'),
            
            # C Programming - Pointers
            ('CS101', 'Pointers', 'Which operator is used to get the memory address of a variable in C?', '*', '&', '->', '%', 'B', 'easy', 'The address-of operator `&` yields the memory location of a variable.'),
            ('CS101', 'Pointers', 'What is a "dangling pointer" in C?', 'A pointer pointing to NULL', 'A pointer that points to a memory location that has been deallocated or freed', 'A pointer that has never been initialized', 'A pointer to constant data', 'B', 'medium', 'A dangling pointer points to memory that was freed or went out of scope, causing errors if dereferenced.'),
            ('CS101', 'Pointers', 'If `int *p = (int*)malloc(sizeof(int)); *p = 10; free(p);`, what is the state of `p` immediately after `free(p)`?', '`p` automatically becomes NULL', '`p` still holds the old address and is now a dangling pointer', 'Memory at `p` is set to 0', 'Compile error', 'B', 'hard', '`free(p)` deallocates the memory heap block but does not alter `p` itself; `p` retains the old address until set to NULL explicitly.'),
            ('CS101', 'Pointers', 'What does `int *arr[10]` declare in C?', 'An array of 10 pointers to integers', 'A pointer to an array of 10 integers', 'A pointer to a function returning 10 integers', 'A dynamically sized integer matrix', 'A', 'medium', '`int *arr[10]` is an array holding 10 integer pointer elements.'),
            
            # C Programming - Recursion
            ('CS101', 'Recursion', 'What is the crucial condition in any recursive function to prevent infinite loops?', 'Step condition', 'Base case', 'Loop counter', 'Return type', 'B', 'easy', 'The base case specifies the condition under which recursion stops and unwinds the call stack.'),
            ('CS101', 'Recursion', 'What error occurs when a recursive function exceeds system stack capacity?', 'Segmentation Fault / Stack Overflow', 'Division by Zero', 'Heap Out of Memory', 'Syntax Error', 'A', 'medium', 'Infinite recursion consumes stack frames until the program exceeds memory limits, triggering a Stack Overflow.'),
            ('CS101', 'Recursion', 'What is Tail Recursion?', 'Recursion where the recursive call is the very last operation performed by the function', 'Recursion with multiple recursive branches', 'Recursion where parameters decrease by 2', 'A function calling itself from a loop', 'A', 'hard', 'In tail recursion, the recursive call is the final statement, allowing compilers to optimize stack frames into iterations.'),
            
            # C Programming - Structures
            ('CS101', 'Structures', 'Which operator is used to access structure members through a structure pointer?', '.', '->', '::', '&', 'B', 'easy', 'The arrow operator `->` is syntactic sugar for `(*ptr).member`.'),
            ('CS101', 'Structures', 'What is structure padding / alignment in C?', 'Adding zeros to numerical fields', 'Compiler inserting unused bytes between members to align data on word boundaries for fast memory access', 'Encrypting structure contents', 'Allocating memory in reverse order', 'B', 'medium', 'CPUs read memory more efficiently in aligned word chunks (e.g. 4 or 8 bytes), so compilers add padding bytes.'),

            # Data Structures - Linked Lists
            ('CS201', 'Linked Lists', 'What is the time complexity to insert an element at the beginning of a singly linked list with a head pointer?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)', 'A', 'easy', 'Inserting at head only requires creating the node, setting its next to head, and updating head pointer in constant time O(1).'),
            ('CS201', 'Linked Lists', 'Which algorithm is standard for detecting a cycle in a linked list in O(n) time and O(1) space?', "Floyd's Cycle-Finding Algorithm (Tortoise and Hare)", "Dijkstra's Algorithm", "Binary Search", "Kruskal's Algorithm", 'A', 'medium', "Floyd's algorithm uses two pointers moving at different speeds (1 step and 2 steps) to detect loops."),
            ('CS201', 'Linked Lists', 'How do you reverse a singly linked list iteratively in O(n) time and O(1) space?', 'By using an auxiliary array', 'By maintaining prev, current, and next pointers while reversing next pointers', 'By recursively calling head', 'By swapping data in all nodes', 'B', 'hard', 'Using three pointers (prev, curr, next), you can invert links sequentially without extra memory allocation.'),

            # Data Structures - Stacks & Queues
            ('CS201', 'Stacks & Queues', 'A Stack follows which order of element processing?', 'FIFO (First In First Out)', 'LIFO (Last In First Out)', 'Priority Order', 'Random Access', 'B', 'easy', 'Stack operates on LIFO (Last-In, First-Out), where the last item pushed is the first popped.'),
            ('CS201', 'Stacks & Queues', 'Which data structure is primarily used in Breadth-First Search (BFS) graph traversal?', 'Stack', 'Queue', 'Priority Queue', 'Binary Tree', 'B', 'medium', 'BFS visits nodes level by level, requiring a FIFO Queue to maintain traversal order.'),
            ('CS201', 'Stacks & Queues', 'How many regular FIFO Queues are minimally required to implement a LIFO Stack?', '1', '2', '3', '4', 'B', 'hard', 'A stack can be implemented using two queues by either making push operation costly O(n) or pop operation costly O(n).'),

            # Data Structures - Trees & BST
            ('CS201', 'Trees & BST', 'What traversal on a Binary Search Tree (BST) visits nodes in non-decreasing sorted order?', 'Pre-order', 'In-order', 'Post-order', 'Level-order', 'B', 'easy', 'In-order traversal (Left, Root, Right) of a BST outputs elements in strictly increasing sorted order.'),
            ('CS201', 'Trees & BST', 'What is the worst-case search time complexity in a skewed Binary Search Tree of N nodes?', 'O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'C', 'medium', 'When a BST becomes completely degenerate/skewed into a linked list, searching degrades to O(n). Self-balancing trees (AVL, Red-Black) maintain O(log n).'),
            ('CS201', 'Trees & BST', 'In an AVL tree, what is the maximum permissible absolute difference in height (balance factor) between left and right subtrees of any node?', '0', '1', '2', 'log(n)', 'B', 'hard', 'AVL trees enforce the balance factor `|height(left) - height(right)| <= 1`. When balance exceeds 1, rotations are performed.'),

            # Mathematics - Linear Algebra
            ('MA101', 'Linear Algebra & Matrices', 'What is the determinant of a 2x2 matrix [[a, b], [c, d]]?', 'ad + bc', 'ad - bc', 'ac - bd', 'ab - cd', 'B', 'easy', 'Determinant of 2x2 matrix is computed as (a*d - b*c).'),
            ('MA101', 'Linear Algebra & Matrices', 'If a square matrix A has determinant det(A) = 0, what does it signify?', 'Matrix is invertible', 'Matrix is singular (no inverse exists)', 'Matrix has only positive eigenvalues', 'Matrix is diagonal', 'B', 'medium', 'A determinant of zero means columns/rows are linearly dependent and the matrix cannot be inverted.'),
            ('MA101', 'Linear Algebra & Matrices', 'If lambda is an eigenvalue of matrix A with eigenvector v, what fundamental equation holds?', 'A * v = lambda * v', 'A + v = lambda', 'A * lambda = v', 'det(A) = lambda * v', 'A', 'hard', 'The characteristic eigenvalue equation is A*v = lambda*v where v is non-zero eigenvector.'),

            # Mathematics - Calculus
            ('MA101', 'Calculus & Derivatives', 'What is the derivative of f(x) = x^3 with respect to x?', '3x', '3x^2', 'x^2', '6x', 'B', 'easy', 'By the power rule d/dx(x^n) = n*x^(n-1), d/dx(x^3) = 3x^2.'),
            ('MA101', 'Calculus & Derivatives', 'What is the value of the limit: lim (x->0) [sin(x) / x]?', '0', '1', 'Infinity', 'Undefined', 'B', 'medium', 'The standard trigonometric limit lim (x->0) sin(x)/x equals 1, demonstrable by L\'Hopital rule.'),
            ('MA101', 'Calculus & Derivatives', 'What condition on second derivative f\'\'(x) confirms a local minimum at a critical point where f\'(x)=0?', 'f\'\'(x) < 0', 'f\'\'(x) > 0', 'f\'\'(x) = 0', 'f\'\'(x) is undefined', 'B', 'hard', 'By the second derivative test, f\'(c)=0 and f\'\'(c)>0 indicates a concave-up local minimum.'),

            # Physics - Mechanics
            ('PH101', 'Mechanics & Motion', "What is Newton's Second Law of Motion formula?", 'F = m / a', 'F = m * a', 'F = m * v', 'F = 0.5 * m * v^2', 'B', 'easy', 'Force equals mass multiplied by acceleration (F = ma).'),
            ('PH101', 'Mechanics & Motion', 'What is the work done by a force when the displacement is perpendicular to the force direction?', 'Maximum positive work', 'Zero', 'Negative work', 'Infinite', 'B', 'medium', 'Work is W = F * d * cos(theta). When theta = 90 deg, cos(90 deg) = 0, so work is 0.'),
            ('PH101', 'Mechanics & Motion', 'A sphere and a solid cylinder of equal mass and radius roll down an incline without slipping. Which reaches the bottom first?', 'Solid sphere', 'Solid cylinder', 'Both reach together', 'Depends on incline angle', 'A', 'hard', 'Solid sphere has lower moment of inertia (2/5 MR^2 vs 1/2 MR^2), converting more potential energy into linear kinetic energy.'),

            # Physics - Electromagnetism
            ('PH101', 'Electromagnetism', 'What is the SI unit of electric capacitance?', 'Ohm', 'Volt', 'Farad', 'Henry', 'C', 'easy', 'The SI unit of capacitance is Farad (F), defined as 1 Coulomb per Volt.'),
            ('PH101', 'Electromagnetism', "Which of Maxwell's equations establishes that magnetic monopoles do not exist?", "Gauss's Law for Electricity", "Gauss's Law for Magnetism (div B = 0)", "Faraday's Law of Induction", "Ampere-Maxwell Law", 'B', 'medium', 'Gauss\'s law for magnetism states del . B = 0, proving magnetic field lines are continuous closed loops with no isolated magnetic poles.'),
            ('PH101', 'Electromagnetism', "What phenomenon is described by Faraday's law of electromagnetic induction?", 'Magnetic force on static charge', 'An electromotive force (EMF) is induced across a conductor experiencing changing magnetic flux', 'Heating in resistors', 'Electric polarization', 'B', 'hard', 'EMF = - d(Phi_B)/dt, showing a time-varying magnetic field induces an electric field.')
        ]
        
        for sub_code, top_name, q_text, opt_a, opt_b, opt_c, opt_d, corr, diff, expl in questions_list:
            sub_id = subject_id_map[sub_code]
            top_id = topic_id_map[top_name]
            conn.execute("""
                INSERT INTO questions (subject_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sub_id, top_id, q_text, opt_a, opt_b, opt_c, opt_d, corr, diff, expl, teacher_user_id))

        print("Seeding Learning Materials...")
        # 6. Learning Materials (Notes, Videos, Examples, Exercises)
        materials_data = [
            # C Programming
            ('CS101', 'Arrays', 'Array Basics & Memory Representation', 'notes', 'beginner', 'Comprehensive guide explaining contiguous memory layout, index calculations, and multidimensional arrays.', 'Arrays are contiguous memory blocks allocated for homogeneous data types. In C, arr[i] is internally evaluated as *(arr + i).', 'https://en.wikipedia.org/wiki/Array_(data_structure)'),
            ('CS101', 'Arrays', 'Visualizing 2D Arrays in C', 'video', 'intermediate', 'Watch dynamic visual animations showing row-major vs column-major array allocations.', 'https://www.youtube.com/watch?v=1uR4tJwiZ5o', 'https://www.youtube.com/watch?v=1uR4tJwiZ5o'),
            ('CS101', 'Pointers', 'Pointers Demystified: Addresses & Dereferencing', 'notes', 'beginner', 'Clear analogies explaining memory addresses, the & operator, and pointer dereferencing with *.', 'Think of memory like a series of numbered houses. A variable is the resident inside, and a pointer is a piece of paper holding the house number.', 'https://en.wikipedia.org/wiki/Pointer_(computer_programming)'),
            ('CS101', 'Pointers', 'Deep Dive: Pointer Arithmetic & Double Pointers', 'example', 'advanced', 'Step-by-step code walkthrough showing dynamic 2D array allocation using `int **` and pointer arithmetic.', 'int **matrix = (int**)malloc(rows * sizeof(int*)); for(int i=0; i<rows; i++) matrix[i] = (int*)malloc(cols * sizeof(int));', '#'),
            ('CS101', 'Recursion', 'Recursion & The Call Stack in Depth', 'notes', 'beginner', 'Understanding how stack frames are pushed and popped during recursive invocations.', 'Every recursive call creates a new stack frame containing local variables and return address. Always ensure your base case is reachable.', '#'),
            ('CS101', 'Recursion', 'Mastering Recursive Backtracking (N-Queens, Maze)', 'exercise', 'advanced', 'Practice problem set solving classic backtracking problems using recursion with interactive hints.', 'Problem 1: Implement Tower of Hanoi with N disks.\nProblem 2: Print all permutations of a string recursively.', '#'),
            
            # Data Structures
            ('CS201', 'Linked Lists', 'Singly & Doubly Linked Lists Explained', 'notes', 'beginner', 'Detailed notes on node structures, pointer manipulation, insertion, and deletion algorithms.', 'A linked list stores data in discrete nodes connected via pointer links, providing O(1) insertions at known nodes.', '#'),
            ('CS201', 'Linked Lists', 'Animated Linked List Operations', 'video', 'intermediate', 'Interactive visual breakdown of head insertion, tail insertion, deletion, and cycle detection.', 'https://www.youtube.com/watch?v=njTh_OwMljA', 'https://www.youtube.com/watch?v=njTh_OwMljA'),
            ('CS201', 'Trees & BST', 'Binary Search Tree Implementations', 'notes', 'intermediate', 'In-depth guide on BST properties, insertion, searching, and in-order traversals.', 'A Binary Search Tree satisfies: Left child < Node < Right child for every subtree.', '#'),
            
            # Mathematics
            ('MA101', 'Linear Algebra & Matrices', 'Matrices, Determinants & Eigenvalues', 'notes', 'intermediate', 'Clear theoretical summary and worked examples for calculating matrix rank and eigenvalues.', 'Eigenvalues satisfy det(A - lambda*I) = 0. Eigenvectors indicate directional invariance under linear transformation.', '#'),
            ('MA101', 'Calculus & Derivatives', 'Calculus Optimization & Partial Derivatives', 'example', 'advanced', 'Step-by-step optimization examples for engineering and machine learning cost functions.', 'To optimize f(x), solve for f\'(x)=0 and examine f\'\'(x) to classify extrema.', '#'),
            
            # Physics
            ('PH101', 'Mechanics & Motion', 'Rotational Mechanics & Conservation of Angular Momentum', 'notes', 'intermediate', 'Conceptual clarity on torque, moment of inertia, and angular momentum conservation.', 'Torque tau = I * alpha. Total angular momentum remains conserved when external torque is zero.', '#'),
            ('PH101', 'Electromagnetism', "Maxwell's Equations Simplified", 'video', 'advanced', 'Intuitive visual explanation of the 4 fundamental equations of electrodynamics.', 'https://www.youtube.com/watch?v=K40lVnwhPz4', 'https://www.youtube.com/watch?v=K40lVnwhPz4')
        ]
        
        for sub_code, top_name, title, r_type, diff, desc, content, link in materials_data:
            sub_id = subject_id_map[sub_code]
            top_id = topic_id_map[top_name]
            conn.execute("""
                INSERT INTO learning_materials (subject_id, topic_id, title, resource_type, difficulty, description, content, link_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sub_id, top_id, title, r_type, diff, desc, content, link))

        print("Seeding Student Marks & Topic Masteries...")
        # 7. Student Marks
        # student1 marks
        s1_id = student_id_map['student1']
        marks_data = [
            (s1_id, subject_id_map['CS101'], 24.0, 26.0, 32.0, 100.0, 'A'),   # 82%
            (s1_id, subject_id_map['CS201'], 23.0, 25.0, 32.0, 100.0, 'A'),   # 80%
            (s1_id, subject_id_map['MA101'], 22.0, 23.0, 30.0, 100.0, 'B+'),  # 75%
            (s1_id, subject_id_map['PH101'], 19.0, 21.0, 27.0, 100.0, 'B'),   # 67%
            
            # student2 (top student)
            (student_id_map['student2'], subject_id_map['CS101'], 28.0, 29.0, 38.0, 100.0, 'A+'),
            (student_id_map['student2'], subject_id_map['CS201'], 27.0, 28.0, 37.0, 100.0, 'A+'),
            (student_id_map['student2'], subject_id_map['MA101'], 29.0, 28.0, 38.0, 100.0, 'A+'),
            (student_id_map['student2'], subject_id_map['PH101'], 26.0, 27.0, 36.0, 100.0, 'A'),
            
            # student5 (at-risk student)
            (student_id_map['student5'], subject_id_map['CS101'], 10.0, 12.0, 16.0, 100.0, 'F'),
            (student_id_map['student5'], subject_id_map['CS201'], 9.0, 11.0, 15.0, 100.0, 'F'),
            (student_id_map['student5'], subject_id_map['MA101'], 12.0, 14.0, 18.0, 100.0, 'F'),
            (student_id_map['student5'], subject_id_map['PH101'], 14.0, 15.0, 19.0, 100.0, 'C'),
        ]
        
        for sid, subid, internal, quiz_m, assign_m, max_m, gr in marks_data:
            conn.execute("""
                INSERT INTO student_marks (student_id, subject_id, internal_marks, quiz_marks, assignment_marks, max_marks, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (sid, subid, internal, quiz_m, assign_m, max_m, gr))

        # 8. Student Topic Mastery (Detailed topic strengths/weaknesses)
        # student1: Strong in Arrays(90%), Functions(85%), Strings(78%), Structures(72%), Weak in Pointers(42%), Recursion(48%)
        s1_mastery = [
            (s1_id, topic_id_map['Arrays'], 10, 9, 90.0, 'Excellent'),
            (s1_id, topic_id_map['Functions'], 12, 10, 83.3, 'Good'),
            (s1_id, topic_id_map['Strings'], 8, 6, 75.0, 'Good'),
            (s1_id, topic_id_map['Structures'], 6, 4, 66.7, 'Average'),
            (s1_id, topic_id_map['Pointers'], 15, 6, 40.0, 'Needs Improvement'),
            (s1_id, topic_id_map['Recursion'], 10, 4, 40.0, 'Needs Improvement'),
            (s1_id, topic_id_map['Linked Lists'], 10, 8, 80.0, 'Good'),
            (s1_id, topic_id_map['Stacks & Queues'], 8, 7, 87.5, 'Good'),
            (s1_id, topic_id_map['Trees & BST'], 10, 6, 60.0, 'Average'),
            (s1_id, topic_id_map['Linear Algebra & Matrices'], 10, 8, 80.0, 'Good'),
            (s1_id, topic_id_map['Calculus & Derivatives'], 10, 7, 70.0, 'Average'),
            (s1_id, topic_id_map['Mechanics & Motion'], 10, 7, 70.0, 'Average'),
            (s1_id, topic_id_map['Electromagnetism'], 8, 5, 62.5, 'Average'),
        ]
        
        for sid, tid, att, corr, pct, band in s1_mastery:
            conn.execute("""
                INSERT INTO student_topic_mastery (student_id, topic_id, total_attempted, total_correct, mastery_percentage, status_band)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sid, tid, att, corr, pct, band))

        # Seed realistic past quiz attempt for student1
        attempt_id = conn.execute("""
            INSERT INTO quiz_attempts (student_id, subject_id, topic_id, total_questions, score, percentage, performance_band, difficulty_progression, completed_at)
            VALUES (?, ?, ?, 5, 4, 80.0, 'Good', ?, CURRENT_TIMESTAMP)
        """, (s1_id, subject_id_map['CS101'], topic_id_map['Arrays'], json.dumps(['easy', 'medium', 'medium', 'hard', 'medium']))).lastrowid

        print("Database seeded successfully with realistic data!")

if __name__ == '__main__':
    seed_database()
