# AI-Powered Task Planner & Smart Scheduler

An AI-assisted task planning application that transforms everyday task descriptions into structured, prioritized daily schedules using Large Language Models (LLMs).

## Overview

Managing multiple tasks with different priorities, deadlines and time requirements can become difficult when everything is planned manually.

This project explores how Generative AI can simplify that process. Users can describe their tasks in natural language, and the application uses Llama 3.2 to identify individual tasks, classify their priorities, estimate completion times and extract explicitly mentioned deadlines.

The extracted information is then processed by a Python-based scheduling engine, which assigns time slots within the user's available working hours. An interactive Streamlit interface allows users to view their schedules, track task completion and monitor productivity.

## Problem Statement

Traditional task planning often requires users to manually break down responsibilities, assign priorities, estimate durations and organize their daily schedules.

This becomes increasingly difficult when several tasks compete for limited working hours.

The objective of this project is to reduce that manual effort by developing an AI-assisted application that understands unstructured task descriptions and converts them into an organized daily plan.

## Key Objectives

- Convert natural-language descriptions into individual actionable tasks.
- Classify tasks according to their priority.
- Estimate the time required for each task.
- Extract deadlines explicitly mentioned by the user.
- Organize tasks within user-defined working hours.
- Store scheduled tasks and track their completion status.
- Present productivity statistics through an interactive dashboard.

## Key Features

### 1. Natural Language Task Processing

Accepts everyday task descriptions and uses Llama 3.2 to identify individual tasks and convert them into structured data.

### 2. AI-Based Priority Classification

Categorizes tasks into four priority levels:

- **P0 – Critical:** Urgent and critical responsibilities.
- **P1 – High:** Important tasks requiring attention.
- **P2 – Medium:** Regular tasks.
- **P3 – Low:** Lower-priority activities.

### 3. Time Estimation

Uses the language model to estimate the time required to complete individual tasks.

### 4. Deadline Extraction

Identifies deadlines explicitly mentioned in the user's input and converts them into a standardized date format.

### 5. Smart Daily Scheduling

Uses Python scheduling logic to arrange tasks according to priority, with deadlines used as a secondary sorting criterion. Tasks are assigned sequential time slots within the selected working hours.

### 6. Task Management

Stores scheduled tasks in an SQLite database and allows users to mark pending tasks as completed.

### 7. Productivity Dashboard

Displays total tasks, completed tasks, pending tasks, completion progress and priority distribution.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic and scheduling |
| Llama 3.2 | Natural-language understanding and task analysis |
| Ollama | Local LLM execution |
| Streamlit | Interactive web interface |
| SQLite | Persistent task storage |
| Pandas | Data handling and dashboard statistics |

## System Workflow

1. The user enters multiple tasks using natural language.
2. Streamlit collects the task descriptions, planning date and working hours.
3. Ollama sends the input to the locally running Llama 3.2 model.
4. The model extracts tasks, assigns priorities, estimates durations and identifies explicitly mentioned deadlines.
5. Python parses and validates the generated JSON response.
6. The scheduling engine sorts tasks by priority and deadline, then allocates available time slots.
7. Scheduled tasks are stored in the SQLite database.
8. The Streamlit interface displays the schedule and productivity statistics.

## System Architecture

```text
User Input
    |
    v
Streamlit Interface
    |
    v
Ollama + Llama 3.2
    |
    v
Task Extraction & Classification
    |
    v
JSON Parsing & Validation
    |
    v
Python Scheduling Engine
    |
    v
SQLite Database
    |
    v
Task Management & Dashboard
```

## Project Structure

```text
AI-Powered-Task-Planner/
│
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

**Note:** The `tasks.db` SQLite database is generated automatically when the application runs. It is intentionally excluded from version control.

## Installation and Execution

### Prerequisites

- Python 3.9 or later
- Ollama installed and running
- Llama 3.2 model

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-powered-task-planner.git
```

### 2. Navigate to the Project Directory

```bash
cd ai-powered-task-planner
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the Language Model

```bash
ollama pull llama3.2
```

Make sure the Ollama application or service is running before proceeding.

### 5. Launch the Application

```bash
streamlit run app.py
```

### 6. Access the Application

Open the following address in your browser:

```text
http://localhost:8501
```

## Design Approach

A key design decision in this project is separating AI-based task interpretation from the actual scheduling logic.

The language model handles natural-language understanding, task extraction, priority classification, duration estimation and deadline extraction.

Python handles response parsing and validation, time allocation, database operations and application logic.

This approach combines the flexibility of Generative AI with the consistency of traditional programming logic, making the overall workflow easier to understand and maintain.

## Possible Limitations

- Task priorities and estimated durations depend on the language model and may not always reflect actual requirements.
- Extracted deadlines may be inaccurate and should be reviewed by the user.
- The current scheduling engine uses sequential time allocation without accounting for breaks, existing calendar events or task dependencies.
- Priority is considered before deadline when arranging tasks, so the earliest deadline is not necessarily scheduled first.
- Tasks that do not fit within the selected working hours are displayed separately rather than automatically rescheduled.
- Unscheduled tasks are not currently saved to the database.
- The application relies on a locally running language model, so response speed and performance depend on available system resources.
- External calendar synchronization and multi-user support are not currently implemented.

## Future Enhancements

- **Deadline-Aware Scheduling:** Improve scheduling logic to consider approaching deadlines, overdue tasks and time-sensitive responsibilities.
- **Break Management:** Introduce configurable breaks, lunch intervals and personal availability.
- **Dynamic Rescheduling:** Automatically reorganize pending tasks when priorities or available working hours change.
- **Task Dependencies:** Support tasks that must be completed in a particular order.
- **Task Editing and Deletion:** Allow users to edit, delete and update previously saved tasks.
- **Unscheduled Task Management:** Persist tasks that cannot fit into the current schedule and suggest alternative time slots.
- **Calendar Integration:** Explore synchronization with Google Calendar and other calendar platforms.
- **Improved AI Capabilities:** Explore agentic workflows that can review task progress, evaluate schedules and recommend adjustments.
- **Cloud Deployment:** Make the application accessible through a hosted environment with appropriate data protection.

## Learning Outcomes

Working on this project provided practical experience in:

- Integrating locally hosted Large Language Models into Python applications.
- Designing prompts for structured LLM responses.
- Parsing and validating JSON generated by an LLM.
- Combining Generative AI with traditional programming logic.
- Building interactive applications using Streamlit.
- Managing persistent data using SQLite.
- Developing a basic scheduling engine.
- Structuring an end-to-end AI-assisted application.

## Project Status

**Working Prototype**

The current implementation supports natural-language task extraction, AI-based priority classification, duration estimation, deadline extraction, basic daily scheduling, SQLite task storage and productivity tracking.

Additional scheduling capabilities and improvements are planned.

## Author

**Borugula Muzzammil Alisha**

AI/ML Graduate | Python | Generative AI | Machine Learning

---

*This project was developed to explore practical applications of Generative AI in everyday productivity and intelligent task management.*
