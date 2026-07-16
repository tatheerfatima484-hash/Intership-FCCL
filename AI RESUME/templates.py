"""
templates.py
------------
Houses every resume layout used by the AI Resume Builder.

Each template is a self-contained HTML5 string with an embedded <style> block
(pure CSS3 - Flexbox/Grid, no external stylesheets, so WeasyPrint can render
it without extra network calls). Templates use Jinja2 syntax so that:

  - {{ variable }}            -> simple value injection
  - {% if variable %} ... {% endif %}   -> optional-field / section skipping
  - {% for item in list %} ... {% endfor %}  -> repeating sections
    (education, experience, skills, projects)

This means any field the user leaves blank simply disappears from the
rendered PDF instead of leaving an empty heading or awkward gap.

Expected context dict (all keys optional except name & email):
{
    "name": str,
    "job_title": str,
    "email": str,
    "phone": str,
    "linkedin": str,
    "github": str,
    "address": str,
    "about_me": str,
    "education": [{"degree": "", "institution": "", "year": "", "gpa": ""}, ...],
    "experience": [{"role": "", "company": "", "duration": "", "description": ""}, ...],
    "skills": ["Python", "SQL", ...],
    "projects": [{"title": "", "description": "", "link": ""}, ...],
}
"""

# ---------------------------------------------------------------------------
# 1. MODERN TECH  (dark sidebar, accent-blue, great for developers/PMs)
# ---------------------------------------------------------------------------
MODERN_TECH = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page { size: A4; margin: 0; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #24292e;
        font-size: 10.5pt;
    }
    .page { display: flex; width: 100%; min-height: 100%; }

    /* ---------- Sidebar ---------- */
    .sidebar {
        width: 34%;
        background: #101828;
        color: #f2f4f7;
        padding: 28px 22px;
    }
    .sidebar .name { font-size: 20pt; font-weight: 700; line-height: 1.15; }
    .sidebar .job-title { font-size: 11pt; color: #4fd1c5; margin-top: 4px; font-weight: 500; }

    .sidebar h3 {
        font-size: 9.5pt; text-transform: uppercase; letter-spacing: 1.2px;
        color: #4fd1c5; margin-top: 22px; margin-bottom: 8px;
        border-bottom: 1px solid #344054; padding-bottom: 4px;
    }
    .contact-item { font-size: 9pt; margin-bottom: 6px; word-break: break-word; color: #d0d5dd; }
    .skill-pill {
        display: inline-block; background: #1d2939; color: #4fd1c5;
        border: 1px solid #344054; border-radius: 12px;
        padding: 3px 10px; margin: 3px 4px 0 0; font-size: 8.5pt;
    }
    .sidebar .edu-item { margin-bottom: 10px; }
    .sidebar .edu-degree { font-weight: 600; font-size: 9.5pt; }
    .sidebar .edu-meta { font-size: 8.5pt; color: #98a2b3; }

    /* ---------- Main column ---------- */
    .main { width: 66%; padding: 28px 30px; }
    .main h3 {
        font-size: 11pt; text-transform: uppercase; letter-spacing: 1px;
        color: #101828; border-bottom: 2px solid #4fd1c5;
        padding-bottom: 4px; margin-bottom: 10px; margin-top: 18px;
    }
    .main h3:first-child { margin-top: 0; }
    .about-text { font-size: 9.8pt; line-height: 1.5; color: #344054; }

    .exp-item, .proj-item { margin-bottom: 12px; }
    .exp-role { font-weight: 700; font-size: 10.2pt; color: #101828; }
    .exp-meta { font-size: 8.8pt; color: #667085; font-style: italic; margin-bottom: 3px; }
    .exp-desc, .proj-desc { font-size: 9.5pt; color: #344054; line-height: 1.45; }
    .proj-title { font-weight: 700; font-size: 10pt; }
    .proj-link { font-size: 8.5pt; color: #0e7490; }
</style>
</head>
<body>
<div class="page">
    <div class="sidebar">
        <div class="name">{{ name }}</div>
        {% if job_title %}<div class="job-title">{{ job_title }}</div>{% endif %}

        <h3>Contact</h3>
        <div class="contact-item">{{ email }}</div>
        {% if phone %}<div class="contact-item">{{ phone }}</div>{% endif %}
        {% if linkedin %}<div class="contact-item">{{ linkedin }}</div>{% endif %}
        {% if github %}<div class="contact-item">{{ github }}</div>{% endif %}
        {% if address %}<div class="contact-item">{{ address }}</div>{% endif %}

        {% if skills %}
        <h3>Skills</h3>
        <div>
        {% for s in skills %}<span class="skill-pill">{{ s }}</span>{% endfor %}
        </div>
        {% endif %}

        {% if education %}
        <h3>Education</h3>
        {% for edu in education %}
        <div class="edu-item">
            <div class="edu-degree">{{ edu.degree }}</div>
            <div class="edu-meta">{{ edu.institution }}{% if edu.year %} &middot; {{ edu.year }}{% endif %}</div>
            {% if edu.gpa %}<div class="edu-meta">GPA: {{ edu.gpa }}</div>{% endif %}
        </div>
        {% endfor %}
        {% endif %}
    </div>

    <div class="main">
        {% if about_me %}
        <h3>Profile</h3>
        <div class="about-text">{{ about_me }}</div>
        {% endif %}

        {% if experience %}
        <h3>Experience</h3>
        {% for exp in experience %}
        <div class="exp-item">
            <div class="exp-role">{{ exp.role }}{% if exp.company %} — {{ exp.company }}{% endif %}</div>
            {% if exp.duration %}<div class="exp-meta">{{ exp.duration }}</div>{% endif %}
            {% if exp.description %}<div class="exp-desc">{{ exp.description }}</div>{% endif %}
        </div>
        {% endfor %}
        {% endif %}

        {% if projects %}
        <h3>Projects</h3>
        {% for p in projects %}
        <div class="proj-item">
            <div class="proj-title">{{ p.title }}</div>
            {% if p.link %}<div class="proj-link">{{ p.link }}</div>{% endif %}
            {% if p.description %}<div class="proj-desc">{{ p.description }}</div>{% endif %}
        </div>
        {% endfor %}
        {% endif %}
    </div>
</div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 2. CLASSIC CORPORATE (single column, serif headings, traditional & ATS safe)
# ---------------------------------------------------------------------------
CLASSIC_CORPORATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page { size: A4; margin: 26px 34px; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Georgia', 'Times New Roman', serif; color: #1a1a1a; font-size: 10.5pt; }

    .header { text-align: center; border-bottom: 3px double #1a1a1a; padding-bottom: 10px; margin-bottom: 14px; }
    .header .name { font-size: 22pt; font-weight: 700; letter-spacing: 1px; }
    .header .job-title { font-size: 11pt; color: #444; margin-top: 3px; font-style: italic; }
    .contact-line { font-size: 9pt; color: #333; margin-top: 8px; }
    .contact-line span:not(:last-child)::after { content: "  |  "; color: #999; }

    h3 {
        font-size: 11.5pt; text-transform: uppercase; letter-spacing: 1.5px;
        border-bottom: 1px solid #1a1a1a; margin-top: 16px; margin-bottom: 8px; padding-bottom: 2px;
    }
    .about-text { font-size: 10pt; line-height: 1.55; text-align: justify; }

    .row-flex { display: flex; justify-content: space-between; }
    .exp-item, .edu-item, .proj-item { margin-bottom: 11px; }
    .exp-role, .edu-degree, .proj-title { font-weight: 700; font-size: 10.3pt; }
    .exp-meta, .edu-meta { font-size: 9pt; color: #555; font-style: italic; }
    .exp-desc, .proj-desc { font-size: 9.8pt; margin-top: 3px; line-height: 1.45; }

    .skills-line { font-size: 9.8pt; line-height: 1.6; }
    .skills-line .skill-pill { font-weight: 600; }
    .skills-line .skill-pill:not(:last-child)::after { content: "  •  "; font-weight: 400; color: #888; }
</style>
</head>
<body>
    <div class="header">
        <div class="name">{{ name }}</div>
        {% if job_title %}<div class="job-title">{{ job_title }}</div>{% endif %}
        <div class="contact-line">
            <span>{{ email }}</span>
            {% if phone %}<span>{{ phone }}</span>{% endif %}
            {% if linkedin %}<span>{{ linkedin }}</span>{% endif %}
            {% if github %}<span>{{ github }}</span>{% endif %}
            {% if address %}<span>{{ address }}</span>{% endif %}
        </div>
    </div>

    {% if about_me %}
    <h3>Professional Summary</h3>
    <div class="about-text">{{ about_me }}</div>
    {% endif %}

    {% if experience %}
    <h3>Work Experience</h3>
    {% for exp in experience %}
    <div class="exp-item">
        <div class="row-flex">
            <div class="exp-role">{{ exp.role }}{% if exp.company %}, {{ exp.company }}{% endif %}</div>
            {% if exp.duration %}<div class="exp-meta">{{ exp.duration }}</div>{% endif %}
        </div>
        {% if exp.description %}<div class="exp-desc">{{ exp.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if education %}
    <h3>Education</h3>
    {% for edu in education %}
    <div class="edu-item">
        <div class="row-flex">
            <div class="edu-degree">{{ edu.degree }}{% if edu.institution %}, {{ edu.institution }}{% endif %}</div>
            {% if edu.year %}<div class="edu-meta">{{ edu.year }}</div>{% endif %}
        </div>
        {% if edu.gpa %}<div class="exp-meta">GPA: {{ edu.gpa }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if projects %}
    <h3>Projects</h3>
    {% for p in projects %}
    <div class="proj-item">
        <div class="proj-title">{{ p.title }}{% if p.link %} ({{ p.link }}){% endif %}</div>
        {% if p.description %}<div class="proj-desc">{{ p.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if skills %}
    <h3>Skills</h3>
    <div class="skills-line">
        {% for s in skills %}<span class="skill-pill">{{ s }}</span>{% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 3. ELEGANT MINIMALIST (lots of whitespace, thin rules, light grey accents)
# ---------------------------------------------------------------------------
ELEGANT_MINIMALIST = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page { size: A4; margin: 40px 46px; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #2b2b2b; font-size: 10pt; }

    .name { font-size: 24pt; font-weight: 300; letter-spacing: 2px; }
    .job-title { font-size: 10.5pt; letter-spacing: 3px; text-transform: uppercase; color: #9a9a9a; margin-top: 4px; }
    hr { border: none; border-top: 1px solid #ddd; margin: 14px 0; }

    .contact-grid { display: flex; flex-wrap: wrap; gap: 14px; font-size: 8.8pt; color: #666; margin-top: 10px; }

    h3 {
        font-size: 9pt; letter-spacing: 2.5px; text-transform: uppercase;
        color: #9a9a9a; margin-top: 20px; margin-bottom: 8px; font-weight: 600;
    }
    .about-text { font-size: 10pt; line-height: 1.7; color: #333; font-weight: 300; }

    .exp-item, .edu-item, .proj-item { margin-bottom: 14px; }
    .row-flex { display: flex; justify-content: space-between; align-items: baseline; }
    .exp-role, .edu-degree, .proj-title { font-weight: 600; font-size: 10.5pt; color: #1a1a1a; }
    .exp-meta, .edu-meta { font-size: 8.5pt; color: #a0a0a0; letter-spacing: 0.5px; }
    .exp-desc, .proj-desc { font-size: 9.5pt; color: #555; line-height: 1.6; margin-top: 3px; font-weight: 300; }

    .skills-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
    .skill-pill { font-size: 8.8pt; border: 1px solid #ddd; padding: 4px 12px; border-radius: 2px; color: #555; }
</style>
</head>
<body>
    <div class="name">{{ name }}</div>
    {% if job_title %}<div class="job-title">{{ job_title }}</div>{% endif %}
    <div class="contact-grid">
        <span>{{ email }}</span>
        {% if phone %}<span>{{ phone }}</span>{% endif %}
        {% if linkedin %}<span>{{ linkedin }}</span>{% endif %}
        {% if github %}<span>{{ github }}</span>{% endif %}
        {% if address %}<span>{{ address }}</span>{% endif %}
    </div>
    <hr>

    {% if about_me %}
    <h3>About</h3>
    <div class="about-text">{{ about_me }}</div>
    {% endif %}

    {% if experience %}
    <h3>Experience</h3>
    {% for exp in experience %}
    <div class="exp-item">
        <div class="row-flex">
            <div class="exp-role">{{ exp.role }}{% if exp.company %} · {{ exp.company }}{% endif %}</div>
            {% if exp.duration %}<div class="exp-meta">{{ exp.duration }}</div>{% endif %}
        </div>
        {% if exp.description %}<div class="exp-desc">{{ exp.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if projects %}
    <h3>Projects</h3>
    {% for p in projects %}
    <div class="proj-item">
        <div class="row-flex">
            <div class="proj-title">{{ p.title }}</div>
            {% if p.link %}<div class="exp-meta">{{ p.link }}</div>{% endif %}
        </div>
        {% if p.description %}<div class="proj-desc">{{ p.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if education %}
    <h3>Education</h3>
    {% for edu in education %}
    <div class="edu-item">
        <div class="row-flex">
            <div class="edu-degree">{{ edu.degree }}{% if edu.institution %} · {{ edu.institution }}{% endif %}</div>
            {% if edu.year %}<div class="edu-meta">{{ edu.year }}</div>{% endif %}
        </div>
        {% if edu.gpa %}<div class="exp-meta">GPA: {{ edu.gpa }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if skills %}
    <h3>Skills</h3>
    <div class="skills-wrap">
        {% for s in skills %}<span class="skill-pill">{{ s }}</span>{% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 4. CREATIVE EXECUTIVE (bold color block header, two-column body, for design/leadership roles)
# ---------------------------------------------------------------------------
CREATIVE_EXECUTIVE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page { size: A4; margin: 0; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #2d2d2d; font-size: 10pt; }

    .header-block {
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
        color: #fff; padding: 26px 34px;
    }
    .header-block .name { font-size: 24pt; font-weight: 800; }
    .header-block .job-title { font-size: 11.5pt; font-weight: 400; opacity: 0.92; margin-top: 2px; }
    .header-block .contact-line { font-size: 8.8pt; margin-top: 10px; opacity: 0.9; }
    .header-block .contact-line span:not(:last-child)::after { content: "   /   "; opacity: 0.6; }

    .body-grid { display: flex; padding: 22px 34px; gap: 26px; }
    .col-left { width: 62%; }
    .col-right { width: 38%; }

    h3 {
        font-size: 10.5pt; text-transform: uppercase; letter-spacing: 1px;
        color: #7c3aed; margin-bottom: 8px; margin-top: 16px;
        border-left: 4px solid #db2777; padding-left: 8px;
    }
    h3:first-child { margin-top: 0; }
    .about-text { font-size: 9.7pt; line-height: 1.55; }

    .exp-item, .proj-item, .edu-item { margin-bottom: 12px; }
    .exp-role, .proj-title, .edu-degree { font-weight: 700; font-size: 10.2pt; }
    .exp-meta, .edu-meta { font-size: 8.5pt; color: #7c3aed; font-weight: 600; }
    .exp-desc, .proj-desc { font-size: 9.3pt; line-height: 1.5; color: #444; margin-top: 2px; }

    .skill-pill {
        display: inline-block; background: #f3e8ff; color: #7c3aed; font-weight: 600;
        border-radius: 10px; padding: 3px 10px; margin: 3px 4px 0 0; font-size: 8.3pt;
    }
    .side-box { background: #faf5ff; border-radius: 6px; padding: 10px 12px; margin-bottom: 10px; }
</style>
</head>
<body>
    <div class="header-block">
        <div class="name">{{ name }}</div>
        {% if job_title %}<div class="job-title">{{ job_title }}</div>{% endif %}
        <div class="contact-line">
            <span>{{ email }}</span>
            {% if phone %}<span>{{ phone }}</span>{% endif %}
            {% if linkedin %}<span>{{ linkedin }}</span>{% endif %}
            {% if github %}<span>{{ github }}</span>{% endif %}
            {% if address %}<span>{{ address }}</span>{% endif %}
        </div>
    </div>

    <div class="body-grid">
        <div class="col-left">
            {% if about_me %}
            <h3>Executive Summary</h3>
            <div class="about-text">{{ about_me }}</div>
            {% endif %}

            {% if experience %}
            <h3>Experience</h3>
            {% for exp in experience %}
            <div class="exp-item">
                <div class="exp-role">{{ exp.role }}{% if exp.company %} — {{ exp.company }}{% endif %}</div>
                {% if exp.duration %}<div class="exp-meta">{{ exp.duration }}</div>{% endif %}
                {% if exp.description %}<div class="exp-desc">{{ exp.description }}</div>{% endif %}
            </div>
            {% endfor %}
            {% endif %}

            {% if projects %}
            <h3>Projects</h3>
            {% for p in projects %}
            <div class="proj-item">
                <div class="proj-title">{{ p.title }}</div>
                {% if p.link %}<div class="exp-meta">{{ p.link }}</div>{% endif %}
                {% if p.description %}<div class="proj-desc">{{ p.description }}</div>{% endif %}
            </div>
            {% endfor %}
            {% endif %}
        </div>

        <div class="col-right">
            {% if education %}
            <h3>Education</h3>
            {% for edu in education %}
            <div class="edu-item">
                <div class="edu-degree">{{ edu.degree }}</div>
                <div class="edu-meta">{{ edu.institution }}{% if edu.year %} · {{ edu.year }}{% endif %}</div>
                {% if edu.gpa %}<div class="exp-desc">GPA: {{ edu.gpa }}</div>{% endif %}
            </div>
            {% endfor %}
            {% endif %}

            {% if skills %}
            <h3>Skills</h3>
            <div>
            {% for s in skills %}<span class="skill-pill">{{ s }}</span>{% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# 5. COMPACT ATS (single column, no tables/graphics — maximum ATS parseability)
# ---------------------------------------------------------------------------
COMPACT_ATS = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page { size: A4; margin: 30px 40px; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Arial', sans-serif; color: #000; font-size: 10.5pt; line-height: 1.4; }

    .name { font-size: 18pt; font-weight: 700; }
    .job-title { font-size: 11pt; color: #333; margin-top: 2px; }
    .contact-line { font-size: 9.5pt; color: #222; margin-top: 6px; }
    .contact-line span:not(:last-child)::after { content: " | "; }

    h3 {
        font-size: 11pt; text-transform: uppercase; font-weight: 700;
        margin-top: 14px; margin-bottom: 6px; border-bottom: 1px solid #000; padding-bottom: 2px;
    }
    .about-text { font-size: 10.2pt; }

    .exp-item, .edu-item, .proj-item { margin-bottom: 9px; }
    .exp-role, .edu-degree, .proj-title { font-weight: 700; }
    .exp-meta, .edu-meta { font-size: 9.5pt; color: #333; }
    .exp-desc, .proj-desc { font-size: 10pt; margin-top: 2px; }
    ul.skills-list { margin-left: 18px; font-size: 10pt; }
</style>
</head>
<body>
    <div class="name">{{ name }}</div>
    {% if job_title %}<div class="job-title">{{ job_title }}</div>{% endif %}
    <div class="contact-line">
        <span>{{ email }}</span>
        {% if phone %}<span>{{ phone }}</span>{% endif %}
        {% if linkedin %}<span>{{ linkedin }}</span>{% endif %}
        {% if github %}<span>{{ github }}</span>{% endif %}
        {% if address %}<span>{{ address }}</span>{% endif %}
    </div>

    {% if about_me %}
    <h3>Summary</h3>
    <div class="about-text">{{ about_me }}</div>
    {% endif %}

    {% if experience %}
    <h3>Experience</h3>
    {% for exp in experience %}
    <div class="exp-item">
        <div class="exp-role">{{ exp.role }}{% if exp.company %}, {{ exp.company }}{% endif %}</div>
        {% if exp.duration %}<div class="exp-meta">{{ exp.duration }}</div>{% endif %}
        {% if exp.description %}<div class="exp-desc">{{ exp.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if education %}
    <h3>Education</h3>
    {% for edu in education %}
    <div class="edu-item">
        <div class="edu-degree">{{ edu.degree }}{% if edu.institution %}, {{ edu.institution }}{% endif %}</div>
        <div class="edu-meta">
            {% if edu.year %}{{ edu.year }}{% endif %}{% if edu.gpa %} | GPA: {{ edu.gpa }}{% endif %}
        </div>
    </div>
    {% endfor %}
    {% endif %}

    {% if projects %}
    <h3>Projects</h3>
    {% for p in projects %}
    <div class="proj-item">
        <div class="proj-title">{{ p.title }}{% if p.link %} — {{ p.link }}{% endif %}</div>
        {% if p.description %}<div class="proj-desc">{{ p.description }}</div>{% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if skills %}
    <h3>Skills</h3>
    <ul class="skills-list">
        {% for s in skills %}<li>{{ s }}</li>{% endfor %}
    </ul>
    {% endif %}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Registry — used by app.py to populate the template-selection dropdown
# ---------------------------------------------------------------------------
TEMPLATES = {
    "modern_tech": {
        "label": "▣ Modern Tech (dark sidebar)",
        "html": MODERN_TECH,
    },
    "classic_corporate": {
        "label": "▤ Classic Corporate (serif, traditional)",
        "html": CLASSIC_CORPORATE,
    },
    "elegant_minimalist": {
        "label": "▢ Elegant Minimalist (whitespace-first)",
        "html": ELEGANT_MINIMALIST,
    },
    "creative_executive": {
        "label": "◈ Creative Executive (gradient header)",
        "html": CREATIVE_EXECUTIVE,
    },
    "compact_ats": {
        "label": "▥ Compact ATS-Safe (plain single column)",
        "html": COMPACT_ATS,
    },
}


def get_template_html(template_key: str) -> str:
    """Return the raw Jinja2 HTML string for a given template key."""
    return TEMPLATES.get(template_key, COMPACT_ATS)["html"]


def list_template_choices():
    """Return [(key, label), ...] for use in a Streamlit selectbox."""
    return [(key, meta["label"]) for key, meta in TEMPLATES.items()]