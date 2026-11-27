

import streamlit as st
import ollama
import sqlite3
import json
from datetime import datetime, date, time, timedelta

# ==========================================
# 1. CONFIGURATION
# ==========================================

MODEL = "llama3.2"
DB_NAME = "tasks.db"

st.set_page_config(
    page_title="AI Task Planner",
    page_icon="📅",
    layout="wide"
)

# ==========================================
# 2. DATABASE SETUP
# ==========================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            priority TEXT NOT NULL,
            estimated_minutes INTEGER NOT NULL,
            reasoning TEXT,
            due_date TEXT,
            start_time TEXT,
            end_time TEXT,
            plan_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# 3. AI TASK EXTRACTION
# ==========================================


SYSTEM_PROMPT = """
You are an intelligent AI task planning assistant.

Analyze the user's tasks and return structured JSON.

The user message will include a planning date.
Use that date as the reference when interpreting relative deadlines.

Assign priorities:

P0 = Critical and genuinely urgent tasks.
P1 = Important tasks and approaching deadlines.
P2 = Normal routine tasks.
P3 = Low urgency and long-term learning.

Extract:
1. Task name.
2. Priority.
3. Estimated duration in minutes.
4. Reason for priority.
5. Deadline, if explicitly mentioned.

Deadline rules:
- Interpret today, tomorrow, and relative dates using the supplied planning date.
- Convert relative deadlines into YYYY-MM-DD.
- Do not invent deadlines.
- If no deadline is explicitly mentioned, use null.
- Never use an arbitrary or historical date.

Return ONLY valid JSON in this format:

{
  "schedule": [
    {
      "task": "Complete Python assignment",
      "priority": "P1",
      "estimated_minutes": 60,
      "reasoning": "Important assignment",
      "due_date": "2026-11-28"
    }
  ]
}
"""



def validate_tasks(data):

    if not isinstance(data, dict):
        raise ValueError("Invalid AI response.")

    if not isinstance(data.get("schedule"), list):
        raise ValueError("Schedule must be a list.")

    for task in data["schedule"]:

        required = [
            "task",
            "priority",
            "estimated_minutes",
            "reasoning",
            "due_date"
        ]

        if not isinstance(task, dict):
            raise ValueError("Invalid task object.")

        for field in required:
            if field not in task:
                raise ValueError(f"Missing field: {field}")

        if not isinstance(task["task"], str) or not task["task"].strip():
            raise ValueError("Invalid task name.")

        if task["priority"] not in ["P0", "P1", "P2", "P3"]:
            raise ValueError("Invalid priority.")

        
        minutes = task["estimated_minutes"]

        if isinstance(minutes, bool):
            raise ValueError("Invalid estimated duration.")

        try:
            minutes = float(minutes)
        except (ValueError, TypeError):
            raise ValueError("Invalid estimated duration.")

        if not minutes.is_integer() or minutes <= 0:
            raise ValueError("Invalid estimated duration.")

        task["estimated_minutes"] = int(minutes)

        if not isinstance(task["reasoning"], str):
            raise ValueError("Invalid reasoning.")

        due = task["due_date"]

        if due is not None:
            if not isinstance(due, str):
                raise ValueError("Invalid deadline.")

            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Deadline must use YYYY-MM-DD.")

    return data



def generate_tasks(user_input, plan_date):

    planning_date = plan_date.isoformat()

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Planning date: {planning_date}\n\n"
                    f"User tasks:\n{user_input}"
                )
            }
        ],
        format="json",
        options={"temperature": 0.1}
    )

    result = json.loads(response.message.content)

    return validate_tasks(result)



# ==========================================
# 4. SMART SCHEDULING ENGINE
# ==========================================

def create_schedule(
    tasks,
    plan_date,
    start_time,
    end_time
):

    priority_order = {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3
    }

    tasks = sorted(
        tasks,
        key=lambda task: (
            priority_order[task["priority"]],
            task["due_date"] or "9999-12-31"
        )
    )

    current_time = datetime.combine(
        plan_date, start_time
    )

    closing_time = datetime.combine(
        plan_date, end_time
    )

    scheduled = []
    unscheduled = []

    for task in tasks:

        duration = task["estimated_minutes"]

        task_end = current_time + timedelta(
            minutes=duration
        )

        # Check whether the task fits in working hours
        if task_end > closing_time:
            unscheduled.append(task)
            continue

        scheduled.append({
            **task,
            "start_time": current_time.strftime("%H:%M"),
            "end_time": task_end.strftime("%H:%M")
        })

        current_time = task_end

    return scheduled, unscheduled


# ==========================================
# 5. SAVE TASKS TO SQLITE
# ==========================================

def save_tasks(tasks, plan_date):

    conn = get_connection()

    for task in tasks:

        conn.execute("""
            INSERT INTO tasks (
                task,
                priority,
                estimated_minutes,
                reasoning,
                due_date,
                start_time,
                end_time,
                plan_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task["task"],
            task["priority"],
            task["estimated_minutes"],
            task["reasoning"],
            task["due_date"],
            task["start_time"],
            task["end_time"],
            plan_date.isoformat()
        ))

    conn.commit()
    conn.close()


# 6. DISPLAY SAVED TASKS

def get_tasks():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, task, priority,
               estimated_minutes, reasoning,
               due_date, start_time, end_time,
               status
        FROM tasks
        ORDER BY plan_date DESC, start_time ASC
    """).fetchall()

    conn.close()

    columns = [
        "ID", "Task", "Priority", "Minutes",
        "Reason", "Deadline", "Start", "End", "Status"
    ]

    import pandas as pd

    return pd.DataFrame(rows, columns=columns)


def mark_completed(task_id):

    conn = get_connection()

    conn.execute("""
        UPDATE tasks
        SET status = 'Completed'
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()


# 7. MAIN APPLICATION

initialize_database()

st.title("📅 AI Task Planner")
st.caption(
    "Your personal AI-powered task prioritization "
    "and scheduling assistant."
)

tab1, tab2, tab3 = st.tabs([
    "Create Schedule",
    "My Tasks",
    "Dashboard"
])


# TAB 1: CREATE SCHEDULE

with tab1:

    st.subheader("Plan your day")

    with st.form("task_form"):

        user_input = st.text_area(
            "Enter your tasks",
            placeholder=(
                "Complete Python assignment by tomorrow.\n"
                "Prepare for AI Engineer interview.\n"
                "Revise SQL for 45 minutes."
            ),
            height=160
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            plan_date = st.date_input("Planning date (DD/MM/YYYY)",value=date.today(),format="DD/MM/YYYY")

        with col2:
            start_time = st.time_input(
                "Working hours start",
                value=time(9, 0)
            )

        with col3:
            end_time = st.time_input(
                "Working hours end",
                value=time(18, 0)
            )

        submit = st.form_submit_button(
            "Generate Smart Schedule",
            use_container_width=True
        )

    if submit:

        if not user_input.strip():
            st.error("Please enter your tasks.")

        elif start_time >= end_time:
            st.error("End time must be after start time.")

        else:

            try:
                with st.spinner("AI is analyzing your tasks..."):

                    result = generate_tasks(user_input, plan_date)

                    if not result["schedule"]:
                        st.warning("No tasks were identified.")

                    else:

                        scheduled, unscheduled = create_schedule(
                            result["schedule"],
                            plan_date,
                            start_time,
                            end_time
                        )

                        save_tasks(scheduled, plan_date)

                        st.session_state["scheduled"] = scheduled
                        st.session_state["unscheduled"] = unscheduled

                        st.success("Schedule generated and saved!")

            except ollama.ResponseError as error:
                st.error(f"Ollama error: {error.error}")

            except json.JSONDecodeError:
                st.error("AI returned invalid JSON.")

            except ValueError as error:
                st.error(f"Validation error: {error}")

            except Exception as error:
                st.error(f"Error: {error}")


    if "scheduled" in st.session_state:

        st.subheader("Your Daily Schedule")

        for index, task in enumerate(
            st.session_state["scheduled"], start=1
        ):

            with st.container(border=True):

                st.markdown(
                    f"**{index}. {task['task']}**"
                )

                col1, col2, col3 = st.columns(3)

                col1.write(f"Priority: {task['priority']}")
                col2.write(
                    f"Time: {task['start_time']} - "
                    f"{task['end_time']}"
                )
                col3.write(
                    f"Duration: {task['estimated_minutes']} min"
                )

                st.caption(task["reasoning"])

        if st.session_state.get("unscheduled"):

            st.warning("Some tasks could not fit into your working hours.")

            for task in st.session_state["unscheduled"]:
                st.write(
                    f"- {task['task']} "
                    f"({task['estimated_minutes']} minutes)"
                )


# TAB 2: MY TASKS

with tab2:

    st.subheader("Manage your tasks")

    df = get_tasks()

    if df.empty:

        st.info("No saved tasks yet.")

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        pending = df[df["Status"] == "Pending"]

        if not pending.empty:

            selected_id = st.selectbox(
                "Select a task to mark as completed",
                pending["ID"].tolist()
            )

            if st.button("Mark as Completed"):

                mark_completed(int(selected_id))

                st.success("Task marked as completed!")

                st.rerun()


# TAB 3: DASHBOARD


with tab3:

    st.subheader("Productivity Dashboard")

    df = get_tasks()

    if df.empty:

        st.info("Create your first schedule to see statistics.")

    else:

        total = len(df)

        completed = len(
            df[df["Status"] == "Completed"]
        )

        pending = total - completed

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tasks", total)
        col2.metric("Completed", completed)
        col3.metric("Pending", pending)

        progress = completed / total

        st.write("Overall Completion Progress")

        st.progress(progress)

        st.write(
            f"{progress * 100:.1f}% tasks completed"
        )

        st.subheader("Priority Distribution")

        st.bar_chart(
            df["Priority"].value_counts()
        )
