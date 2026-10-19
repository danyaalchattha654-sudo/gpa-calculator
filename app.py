"""
GPA Calculator - Streamlit edition

Run locally:  streamlit run app.py
"""

from dataclasses import dataclass

import pandas as pd
import streamlit as st


# =====================================================================
# 1. CORE LOGIC (no UI code)
# =====================================================================

# US 4.0 grading scale. Edit this to match your school's scale.
GRADE_POINTS: dict[str, float] = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}

MAX_CREDITS_PER_COURSE = 10.0


@dataclass(frozen=True)
class Course:
    name: str
    credits: float
    grade: str

    @property
    def quality_points(self) -> float:
        return GRADE_POINTS[self.grade] * self.credits


def calculate_gpa(courses: list[Course]) -> float:
    """Credit-weighted GPA: total quality points divided by total credits."""
    total = sum(c.credits for c in courses)
    if total == 0:
        return 0.0
    return sum(c.quality_points for c in courses) / total


def validate_course(name: str, credits: float) -> str | None:
    """Return an error message, or None if the input is valid."""
    if not name.strip():
        return "Please enter a course name."
    if not 0 < credits <= MAX_CREDITS_PER_COURSE:
        return f"Credits must be greater than 0 and at most {MAX_CREDITS_PER_COURSE:g}."
    return None


def gpa_status(gpa: float) -> tuple[str, str]:
    """Return a (label, color) pair for a GPA value."""
    if gpa >= 3.5:
        return "Excellent", "#059669"
    if gpa >= 2.0:
        return "Good standing", "#D97706"
    return "Needs attention", "#DC2626"


# =====================================================================
# 2. PAGE SETUP AND STYLING
# =====================================================================

st.set_page_config(page_title="GPA Calculator", page_icon="🎓", layout="centered")

st.markdown(
    """
    <style>
    .block-container { max-width: 820px; padding-top: 2rem; }
    .app-title { font-size: 2rem; font-weight: 700; color: #1F2937; margin-bottom: 0; }
    .app-sub { color: #6B7280; margin-top: 0.25rem; margin-bottom: 1.5rem; }
    .gpa-card {
        background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 16px;
        padding: 24px 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .gpa-label { font-size: 0.8rem; letter-spacing: 0.08em; color: #6B7280; text-transform: uppercase; }
    .gpa-value { font-size: 3.5rem; font-weight: 800; line-height: 1.1; }
    .gpa-status { font-size: 0.95rem; font-weight: 600; margin-top: 4px; }
    .gpa-of { color: #6B7280; font-size: 0.85rem; }
    .stat-value { font-size: 1.4rem; font-weight: 700; color: #1F2937; }
    .stat-label { font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.06em; }
    .bar-track { background: #E5E7EB; border-radius: 999px; height: 10px; margin-top: 18px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 999px; transition: width 0.4s ease; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# 3. SESSION STATE
# =====================================================================

if "courses" not in st.session_state:
    st.session_state.courses = []  # list of Course objects


# =====================================================================
# 4. INTERFACE
# =====================================================================

st.markdown('<div class="app-title">GPA Calculator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Add your courses to see your credit-weighted grade point average.</div>',
    unsafe_allow_html=True,
)

# ----- Input form -----
with st.form("add_course", clear_on_submit=True):
    col_name, col_credits, col_grade = st.columns([3, 1.2, 1.2])
    with col_name:
        name = st.text_input("Course name", placeholder="e.g. Calculus I")
    with col_credits:
        credits = st.number_input("Credits", min_value=0.5, max_value=MAX_CREDITS_PER_COURSE,
                                  value=3.0, step=0.5)
    with col_grade:
        grade = st.selectbox("Grade", options=list(GRADE_POINTS), index=1)

    submitted = st.form_submit_button("+ Add course", type="primary", use_container_width=True)

if submitted:
    error = validate_course(name, credits)
    if error:
        st.error(error)
    else:
        st.session_state.courses.append(Course(name.strip(), float(credits), grade))
        st.rerun()

courses: list[Course] = st.session_state.courses

# ----- Course table -----
st.subheader("Your courses")

if courses:
    table = pd.DataFrame(
        {
            "Course": [c.name for c in courses],
            "Credits": [c.credits for c in courses],
            "Grade": [c.grade for c in courses],
            "Quality points": [round(c.quality_points, 2) for c in courses],
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    col_delete, col_clear = st.columns(2)
    with col_delete:
        to_delete = st.selectbox(
            "Remove a course",
            options=range(len(courses)),
            format_func=lambda i: f"{courses[i].name} ({courses[i].grade})",
        )
        if st.button("Delete selected", use_container_width=True):
            del st.session_state.courses[to_delete]
            st.rerun()
    with col_clear:
        st.write("")  # spacing to align with the select box
        if st.button("Clear all courses", use_container_width=True):
            st.session_state.courses = []
            st.rerun()
else:
    st.info("No courses yet. Add one above to get started.")

# ----- Summary -----
st.subheader("Summary")

gpa = calculate_gpa(courses)
total_credits = sum(c.credits for c in courses)
total_points = sum(c.quality_points for c in courses)
label, color = gpa_status(gpa)
progress_pct = min(gpa / 4.0 * 100, 100)

st.markdown(
    f"""
    <div class="gpa-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:16px;">
            <div>
                <div class="gpa-label">Cumulative GPA</div>
                <div class="gpa-value" style="color:{color};">{gpa:.2f}</div>
                <div class="gpa-status" style="color:{color};">{label}</div>
                <div class="gpa-of">out of 4.00</div>
            </div>
            <div style="display:flex; gap:28px;">
                <div><div class="stat-value">{len(courses)}</div><div class="stat-label">Courses</div></div>
                <div><div class="stat-value">{total_credits:g}</div><div class="stat-label">Credits</div></div>
                <div><div class="stat-value">{total_points:.2f}</div><div class="stat-label">Quality points</div></div>
            </div>
        </div>
        <div class="bar-track">
            <div class="bar-fill" style="width:{progress_pct:.1f}%; background:{color};"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----- Footer -----
st.caption("Grade scale: standard US 4.0. Edit GRADE_POINTS in app.py to match your school.")