import sqlite3
import requests
import os
import json
import time
import random

def get_db_connection():
    db_path = os.path.abspath("database.db")
    print(f"Using database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        grade TEXT NOT NULL,
        board TEXT NOT NULL,
        activity TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    
    return conn

def generate_complexity_instructions(grade, board):
    """Generate complexity instructions based on grade and board."""
    complexity_map = {
        '1-3': {
            'CBSE': "Use simple language, focus on basic concepts, include lots of visual aids and hands-on activities.",
            'ICSE': "Emphasize foundational understanding with interactive and playful learning approaches.",
            'State': "Use local context and simple, concrete examples that students can easily relate to."
        },
        '4-6': {
            'CBSE': "Introduce more structured learning, include basic analytical thinking, use step-by-step explanations.",
            'ICSE': "Encourage critical thinking, provide slightly more complex explanations with real-world connections.",
            'State': "Balance between local context and broader understanding, use engaging visual representations."
        },
        '7-10': {
            'CBSE': "Focus on in-depth understanding, include advanced concepts, encourage scientific reasoning and research.",
            'ICSE': "Promote advanced analytical skills, include complex problem-solving and interdisciplinary connections.",
            'State': "Provide comprehensive understanding with advanced local and global perspectives."
        }
    }
    
    # Determine grade range
    grade_range = '1-3' if int(grade) <= 3 else '4-6' if int(grade) <= 6 else '7-10'
    
    return complexity_map.get(grade_range, {}).get(board, "Create an engaging and age-appropriate educational activity.")

def generate_classroom_activity(topic, grade, board):
    """Generate a fun classroom activity using a Hugging Face model."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if activity exists in the database
    cursor.execute(
        "SELECT activity FROM activities WHERE topic = ? AND grade = ? AND board = ?", 
        (topic.lower(), grade, board)
    )
    cached_result = cursor.fetchone()

    if cached_result:
        print(f"Found cached activity for '{topic}' in grade {grade}, {board} board")
        conn.close()
        return cached_result[0]

    print(f"Generating new activity for '{topic}' in grade {grade}, {board} board")
    
    # Get complexity instructions
    complexity_instructions = generate_complexity_instructions(grade, board)
    
    # Call Hugging Face API with more specific prompt
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer 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"}

    # Better prompt for the model
    prompt = f"""
    Create an engaging, educational classroom activity about "{topic}" for {grade}th grade students following {board} board curriculum.

    Complexity Guidelines: {complexity_instructions}

    Activity Requirements:
    - Align with {grade}th grade learning capabilities
    - Match {board} board educational standards
    - Interactive and hands-on
    - 20-30 minutes in length
    - Include clear steps for the teacher to follow
    
    Format your response to include:
    1. A creative title for the activity
    2. Learning objectives specific to the grade and board
    3. Materials needed
    4. Detailed step-by-step instructions
    5. Assessment or reflection component
    """

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True
        }
    }
    
    try:
        # Make API request with retry
        for attempt in range(3):
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                break
            elif response.status_code == 503:  # Model still loading
                time.sleep(10)  # Wait 10 seconds before retry
            else:
                break
        
        result = response.json()
        
        # Handle different response formats
        activity = ""
        if isinstance(result, list) and len(result) > 0:
            if 'generated_text' in result[0]:
                activity = result[0]['generated_text']
        elif isinstance(result, dict):
            if 'generated_text' in result:
                activity = result['generated_text']
        
        # If we still don't have content, create a varied fallback
        if not activity:
            activities = [
                f"Collaborative {topic.title()} Exploration: Students in {grade}th grade work in teams to create a comprehensive project about {topic}, tailored to {board} board curriculum.",
                f"Interactive {topic.title()} Workshop: Students research and present different aspects of {topic}, demonstrating understanding appropriate for {grade}th grade level.",
                f"Creative {topic.title()} Challenge: Teams design innovative ways to explain {topic} using visual aids and presentations suitable for {board} educational standards."
            ]
            activity = random.choice(activities)
    
    except Exception as e:
        print(f"Exception during API call: {str(e)}")
        activity = f"Interactive {topic.title()} Workshop for {grade}th Grade: Students work in pairs to research {topic}, create visual aids, and teach their findings to the rest of the class."
    
    # Store in database only if it's a valid activity (not an error message)
    cursor.execute(
        "INSERT INTO activities (topic, grade, board, activity) VALUES (?, ?, ?, ?)", 
        (topic.lower(), grade, board, activity)
    )
    conn.commit()
    conn.close()
    return activity