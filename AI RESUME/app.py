"""
app.py
------
AI Resume Builder — Streamlit front-end.

Flow:
1. User fills in personal info + optional sections (education, experience,
   skills, projects) using dynamic add/remove entry widgets.
2. About Me: user can type their own summary, then either
   "Write with AI" (AI writes it from scratch in a chosen tone) or
   "Enhance with AI" (AI polishes/improves what the user already wrote).
3. User picks a template layout (5 choices from templates.py).
4. User clicks "Download PDF" -> Jinja2 renders the chosen HTML template with
   the collected data -> WeasyPrint converts that HTML/CSS straight to a PDF
   -> a download button appears.

Run with:  streamlit run app.py
"""

import io
import os

import streamlit as st
from dotenv import load_dotenv
from jinja2 import Template
from weasyprint import HTML

# Official 2026 Google GenAI SDK (replaces the older google-generativeai package)
from google import genai
from google.genai import types

from templates import get_template_html, list_template_choices
from database import init_db, save_resume

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv(override=True)

init_db()  # creates resume_data.db (and its tables) on first run, safe to call every time

st.set_page_config(page_title="AI Resume Builder", page_icon="📄", layout="wide")

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

TONE_LABELS = {
    "professional": "🧑‍💼 Professional",
    "creative": "🎨 Creative",
    "catchy": "⚡ Catchy",
    "detailed": "📊 Detailed",
}
TONE_INSTRUCTIONS = {
    "professional": "a formal, polished, corporate tone (~3 sentences)",
    "creative": "a modern, energetic, personality-driven tone (~3 sentences)",
    "catchy": "a punchy, memorable tone (one or two sentences maximum)",
    "detailed": "an achievement-focused, leadership-oriented tone (4-5 sentences)",
}


def get_gemini_client():
    """Build and return a genai.Client, or None if no API key is available."""
    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("manual_api_key")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def init_state():
    defaults = {
        "education": [],       # list[dict]
        "experience": [],      # list[dict]
        "projects": [],        # list[dict]
        "about_me_text": "",   # user-written or AI-written summary (single source of truth)
        "about_me_pending": None,  # holds AI result until it's safe to apply before widget creation
        "manual_api_key": "",
        "dark_mode": False,
        "attempted_submit": False,  # set True once user tries Preview/Generate PDF, to trigger validation UI
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_state()


# ---------------------------------------------------------------------------
# Global layout fix: prevent the sticky tab bar from overlapping Streamlit's
# top header / toolbar (Deploy button etc.) when the page is scrolled.
# ---------------------------------------------------------------------------
def apply_layout_fix():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] { z-index: 999; }
        .stTabs [data-baseweb="tab-list"] {
            position: sticky;
            top: 0;
            z-index: 1;
            background: inherit;
            padding-top: 0.25rem;
        }
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Theming: lightweight dark-mode CSS override
# ---------------------------------------------------------------------------
def apply_theme():
    if st.session_state["dark_mode"]:
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"], [data-testid="stHeader"],
            [data-testid="stSidebar"], [data-testid="stSidebarContent"],
            .stTabs, [data-testid="stMarkdownContainer"] {
                background-color: #0e1117 !important;
                color: #fafafa !important;
            }
            [data-testid="stSidebar"] { border-right: 1px solid #2b2f38; }
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
                background-color: #1c1f26 !important;
                color: #fafafa !important;
                border-color: #3a3f4b !important;
            }
            .stButton button { background-color: #262a33; color: #fafafa; border: 1px solid #3a3f4b; }
            .stButton button[kind="primary"] { background-color: #6c63ff; border: none; }
            [data-testid="stExpander"] { background-color: #171a21 !important; border-color: #2b2f38; }
            hr { border-color: #2b2f38 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Best-effort "Enter" key -> move to next field
# (Streamlit has no native focus-management API, so this injects a small
#  script that walks text inputs in DOM order and focuses the next one.)
# ---------------------------------------------------------------------------
def enable_enter_key_navigation():
    st.components.v1.html(
        """
        <script>
        setTimeout(function () {
            const doc = window.parent.document;
            const fields = doc.querySelectorAll(
                'input[type="text"], input[type="password"], textarea'
            );
            fields.forEach((el, idx) => {
                el.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' && el.tagName === 'INPUT') {
                        e.preventDefault();
                        const next = fields[idx + 1];
                        if (next) { next.focus(); }
                    }
                });
            });
        }, 600);
        </script>
        """,
        height=0,
    )

# ---------------------------------------------------------------------------
# Helpers: dynamic repeatable-section editors
# ---------------------------------------------------------------------------
def dynamic_section_editor(section_key: str, field_defs: list, add_label: str):
    """
    Renders an "add entry" button plus one expander per existing entry with
    the fields described in field_defs = [(field_name, display_label, widget_type), ...]
    widget_type is "text" or "textarea".
    """
    entries = st.session_state[section_key]

    for idx, entry in enumerate(entries):
        with st.expander(f"{add_label} #{idx + 1}", expanded=True):
            cols = st.columns([1] * (len(field_defs) - 1) + [1]) if len(field_defs) > 1 else [st]
            for f_idx, (fname, flabel, wtype) in enumerate(field_defs):
                widget_key = f"{section_key}_{idx}_{fname}"
                if wtype == "textarea":
                    entry[fname] = st.text_area(
                        flabel, value=entry.get(fname, ""), key=widget_key, height=80
                    )
                else:
                    entry[fname] = st.text_input(
                        flabel, value=entry.get(fname, ""), key=widget_key
                    )
            if st.button(f"🗑️ Remove {add_label} #{idx + 1}", key=f"remove_{section_key}_{idx}"):
                entries.pop(idx)
                st.rerun()

    if st.button(f"➕ Add {add_label}", key=f"add_{section_key}"):
        entries.append({fname: "" for fname, _, _ in field_defs})
        st.rerun()


def clean_entries(entries: list) -> list:
    """Drop entries where every field is blank, so empty rows never reach the PDF."""
    return [e for e in entries if any(str(v).strip() for v in e.values())]


# ---------------------------------------------------------------------------
# Gemini: write a fresh summary, or enhance an existing draft, in one tone
# ---------------------------------------------------------------------------
def generate_about_me(profile: dict, tone: str, existing_text: str = "") -> str | None:
    client = get_gemini_client()
    if client is None:
        st.error(
            "No AI API key found. Add GEMINI_API_KEY to your .env file, "
            "or enter one in the sidebar."
        )
        return None

    skills_str = ", ".join(profile.get("skills", [])) or "Not specified"
    exp_str = "; ".join(
        f"{e.get('role', '')} at {e.get('company', '')}" for e in profile.get("experience", [])
    ) or "Not specified"
    edu_str = "; ".join(
        f"{e.get('degree', '')} - {e.get('institution', '')}" for e in profile.get("education", [])
    ) or "Not specified"

    tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["professional"])

    if existing_text.strip():
        task = (
            f"Improve and polish the candidate's own draft below. Keep the core "
            f"meaning and any specific facts, but rewrite it to be more compelling, "
            f"using {tone_instruction}.\n\nCandidate's draft:\n\"\"\"{existing_text.strip()}\"\"\""
        )
    else:
        task = f"Write a brand-new 'About Me' resume summary from scratch, using {tone_instruction}."

    prompt = f"""
You are an expert AI Resume Writer.

Candidate details:
- Name: {profile.get('name', 'N/A')}
- Target job title: {profile.get('job_title', 'Not specified')}
- Experience: {exp_str}
- Skills: {skills_str}
- Education: {edu_str}

{task}

Return ONLY the summary text itself. No labels, no markdown, no quotation
marks, no commentary before or after.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8),
        )
        return response.text.strip().strip('"')
    except Exception as exc:  # noqa: BLE001
        st.error(f"AI Generation Error: {exc}")
        return None


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------
def build_context() -> dict:
    return {
        "name": st.session_state.get("name", "").strip(),
        "job_title": st.session_state.get("job_title", "").strip(),
        "email": st.session_state.get("email", "").strip(),
        "phone": st.session_state.get("phone", "").strip(),
        "linkedin": st.session_state.get("linkedin", "").strip(),
        "github": st.session_state.get("github", "").strip(),
        "address": st.session_state.get("address", "").strip(),
        "about_me": st.session_state.get("about_me_text", "").strip(),
        "education": clean_entries(st.session_state["education"]),
        "experience": clean_entries(st.session_state["experience"]),
        "projects": clean_entries(st.session_state["projects"]),
        "skills": [s.strip() for s in st.session_state.get("skills_raw", "").split(",") if s.strip()],
    }


def render_resume_html(template_key: str, context: dict) -> str:
    template_str = get_template_html(template_key)
    return Template(template_str).render(**context)


def html_to_pdf_bytes(html_content: str) -> bytes:
    buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(buffer)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Sidebar — API key + theme + quick help
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    theme_label = "☀️ Light Mode" if st.session_state["dark_mode"] else "🌙 Dark Mode"
    st.session_state["dark_mode"] = st.toggle(theme_label, value=st.session_state["dark_mode"])
    if not os.getenv("GEMINI_API_KEY"):
        st.session_state["manual_api_key"] = st.text_input(
            "AI API Key", type="password", help="Or set GEMINI_API_KEY in a .env file."
        )
    st.divider()
    st.markdown(
        "**How it works**\n"
        "1. Fill in your details\n"
        "2. Write your own About Me, or let AI write/enhance it\n"
        "3. Pick a template\n"
        "4. Download your PDF resume"
    )

apply_layout_fix()
apply_theme()

# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
st.title("📄 AI Resume Builder")
st.caption("Fill in your details, let AI polish your summary, and export a premium PDF resume.")

tab_personal, tab_edu, tab_exp, tab_skills, tab_projects = st.tabs(
    ["👤 Personal Info", "🎓 Education", "💼 Experience", "🛠️ Skills", "🚀 Projects"]
)

with tab_personal:
    name_error = st.session_state.get("attempted_submit") and not st.session_state.get("name", "").strip()
    email_error = st.session_state.get("attempted_submit") and not st.session_state.get("email", "").strip()

    if name_error or email_error:
        st.markdown(
            f"""
            <style>
            {'input[aria-label="Full Name *"] { border: 2px solid #e53e3e !important; }' if name_error else ''}
            {'input[aria-label="Email *"] { border: 2px solid #e53e3e !important; }' if email_error else ''}
            </style>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full Name *", key="name")
        if name_error:
            st.caption(":red[⚠️ Full Name is required]")
        st.text_input("Job Title / Target Role", key="job_title")
        st.text_input("Email *", key="email")
        if email_error:
            st.caption(":red[⚠️ Email is required]")
        st.text_input("Phone", key="phone")
    with c2:
        st.text_input("LinkedIn URL", key="linkedin")
        st.text_input("GitHub URL", key="github")
        st.text_input("Address / City", key="address")
    enable_enter_key_navigation()

with tab_edu:
    st.caption("Add as many education entries as you need. Leave blank to skip entirely.")
    dynamic_section_editor(
        "education",
        [
            ("degree", "Degree / Qualification", "text"),
            ("institution", "Institution", "text"),
            ("year", "Year", "text"),
            ("gpa", "GPA / Grade (optional)", "text"),
        ],
        "Education Entry",
    )

with tab_exp:
    st.caption("Add your work experience, most recent first.")
    dynamic_section_editor(
        "experience",
        [
            ("role", "Job Title / Role", "text"),
            ("company", "Company", "text"),
            ("duration", "Duration (e.g. Jan 2022 - Present)", "text"),
            ("description", "Description / Achievements", "textarea"),
        ],
        "Experience Entry",
    )

with tab_skills:
    st.caption("Enter skills separated by commas, e.g. Python, SQL, Project Management")
    st.text_area("Skills", key="skills_raw", height=100)

with tab_projects:
    st.caption("Showcase notable projects (optional).")
    dynamic_section_editor(
        "projects",
        [
            ("title", "Project Title", "text"),
            ("link", "Link (optional)", "text"),
            ("description", "Description", "textarea"),
        ],
        "Project Entry",
    )

st.divider()

# ---------------------------------------------------------------------------
# About Me — write it yourself, or let AI write / enhance it
# ---------------------------------------------------------------------------
st.subheader("✨ About Me")
st.caption("Write your own summary below, or leave it blank and let AI write one for you.")

# Apply any pending AI-generated result BEFORE the widget is instantiated —
# Streamlit forbids writing to session_state[key] after that key's widget
# has already been created in the same run.
if st.session_state.get("about_me_pending") is not None:
    st.session_state["about_me_text"] = st.session_state.pop("about_me_pending")

st.text_area(
    "About Me (optional)",
    key="about_me_text",
    height=140,
    placeholder="e.g. A backend developer who loves solving hard problems with clean code...",
)

has_draft = bool(st.session_state.get("about_me_text", "").strip())

tone_col, action_col = st.columns([2, 1])
with tone_col:
    tone_choice = st.selectbox(
        "AI tone",
        options=list(TONE_LABELS.keys()),
        format_func=lambda t: TONE_LABELS[t],
        key="about_me_tone",
    )
with action_col:
    st.write("")  # vertical spacer to align button with selectbox
    if has_draft:
        action_clicked = st.button("🚀 Enhance with AI", type="primary", use_container_width=True)
        write_clicked, enhance_clicked = False, action_clicked
    else:
        action_clicked = st.button("✍️ Write with AI", type="primary", use_container_width=True)
        write_clicked, enhance_clicked = action_clicked, False

if write_clicked or enhance_clicked:
    if not st.session_state.get("name") or not st.session_state.get("email"):
        st.warning("Please fill in at least your Name and Email before using AI.")
    else:
        profile = build_context()
        existing = st.session_state.get("about_me_text", "") if enhance_clicked else ""
        spinner_msg = "Enhancing your summary..." if enhance_clicked else "Writing your summary..."
        with st.spinner(spinner_msg):
            result = generate_about_me(profile, tone_choice, existing_text=existing)
        if result:
            st.session_state["about_me_pending"] = result
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Template selection + PDF export
# ---------------------------------------------------------------------------
st.subheader("🎨 Choose a Template & Export")

template_choices = list_template_choices()
template_labels = [label for _, label in template_choices]
template_keys = [key for key, _ in template_choices]

selected_label = st.radio("Resume Template", template_labels, horizontal=False)
selected_key = template_keys[template_labels.index(selected_label)]

preview_col, download_col = st.columns([2, 1])

with preview_col:
    if st.button("👁️ Preview Resume"):
        st.session_state["attempted_submit"] = True
        if not st.session_state.get("name", "").strip() or not st.session_state.get("email", "").strip():
            st.warning("Please fill in the required fields (Full Name, Email) on the Personal Info tab first.")
            st.rerun()
        else:
            context = build_context()
            save_resume(context, template_key=selected_key)
            html_out = render_resume_html(selected_key, context)
            st.components.v1.html(html_out, height=800, scrolling=True)

with download_col:
    if st.button("⬇️ Generate PDF", type="primary", use_container_width=True):
        st.session_state["attempted_submit"] = True
        if not st.session_state.get("name", "").strip() or not st.session_state.get("email", "").strip():
            st.warning("Please fill in the required fields (Full Name, Email) on the Personal Info tab first.")
            st.rerun()
        else:
            with st.spinner("Rendering your PDF..."):
                context = build_context()
                save_resume(context, template_key=selected_key)
                html_out = render_resume_html(selected_key, context)
                pdf_bytes = html_to_pdf_bytes(html_out)
            file_name = f"{context['name'].replace(' ', '_') or 'resume'}_resume.pdf"
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
            )
            st.success("Your resume is ready!")