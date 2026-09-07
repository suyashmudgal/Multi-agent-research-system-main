import streamlit as st
import time
import re
from agents import (
    build_reader_agent,
    build_search_agent,
    build_writer_chain,
    build_critic_chain,
    writer_chain,
    critic_chain
)

def clean_text(text: str) -> str:
    """Clean redundant blank lines and whitespace."""
    if not text:
        return ""
    return re.sub(r'\n{3,}', '\n\n', text).strip()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Khoj AI · Autonomous Research Agent",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;600;700;900&family=Baloo+2:wght@500;600;700&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ═══════════════ PALETTE ═══════════════
   Indigo night  : #0e0b1f / #14102b
   Saffron       : #ff9933
   Marigold gold : #ffb84d / #e8b64f
   Deep maroon   : #8c2f39
   Success green : #3fae6a (Indian flag green, muted)
   Parchment text: #f3ead9
════════════════════════════════════════ */

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #f3ead9;
}

.stApp {
    background: #0e0b1f;
    background-image:
        radial-gradient(ellipse 70% 45% at 15% -8%, rgba(255,153,51,0.16) 0%, transparent 58%),
        radial-gradient(ellipse 55% 40% at 90% 8%, rgba(232,182,79,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 60% 45% at 50% 115%, rgba(140,47,57,0.18) 0%, transparent 60%),
        repeating-linear-gradient(115deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px, transparent 1px, transparent 46px);
    background-attachment: fixed;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1240px; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes diyaFlicker {
    0%, 100% { opacity: 1; filter: drop-shadow(0 0 6px rgba(255,153,51,0.55)); }
    50%      { opacity: 0.82; filter: drop-shadow(0 0 10px rgba(255,153,51,0.8)); }
}
@keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(255,153,51,0.35); }
    70%  { box-shadow: 0 0 0 10px rgba(255,153,51,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,153,51,0); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes spinSlow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

.block-container { animation: fadeInUp 0.55s ease-out; }

/* ── Hero ── */
.hero {
    text-align: center !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 2.8rem 1rem 1.6rem !important;
    position: relative;
    width: 100% !important;
    margin: 0 auto !important;
}
.hero * {
    text-align: center !important;
}
.hero-mark { font-size: 2.2rem; display: inline-block; margin-bottom: 0.6rem; animation: diyaFlicker 2.4s ease-in-out infinite; }
.hero-eyebrow {
    display: inline-flex; align-items: center; justify-content: center; gap: 0.55rem;
    font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 500;
    letter-spacing: 0.28em; text-transform: uppercase; color: #ffb84d;
    margin: 0 auto 1rem !important; padding: 0.4rem 1rem;
    border: 1px solid rgba(255,153,51,0.3); border-radius: 999px;
    background: rgba(255,153,51,0.07);
}
.hero-eyebrow::before {
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: #ff9933; box-shadow: 0 0 8px 2px rgba(255,153,51,0.65);
}
.hero-devanagari {
    font-family: 'Baloo 2', sans-serif;
    font-size: 1.35rem;
    color: #e8b64f;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
    opacity: 0.9;
    text-align: center !important;
}
.hero h1 {
    font-family: 'Fraunces', serif;
    font-size: clamp(2.9rem, 6.2vw, 5.4rem);
    font-weight: 900;
    line-height: 1.02;
    letter-spacing: -0.02em;
    color: #f6efe1;
    margin: 0 0 1rem;
    text-align: center !important;
}
.hero h1 span {
    background: linear-gradient(120deg, #ff9933 0%, #e8b64f 45%, #ffcf7a 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub,
p.hero-sub,
.hero p,
[data-testid="stMarkdownContainer"] .hero-sub,
[data-testid="stMarkdownContainer"] .hero p {
    font-size: 1.08rem !important;
    font-weight: 300 !important;
    color: #b8ac9a !important;
    max-width: 620px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-top: 0 !important;
    margin-bottom: 0.2rem !important;
    line-height: 1.75 !important;
    text-align: center !important;
    display: block !important;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,153,51,0.4), rgba(232,182,79,0.25), transparent);
    margin: 2.2rem 0;
}

/* ── Input card (native bordered container) ── */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.card-anchor) {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,153,51,0.22) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 24px 60px -22px rgba(0,0,0,0.6);
    position: relative;
    overflow: hidden;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.card-anchor)::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #ff9933, #e8b64f, #8c2f39, #ff9933);
    background-size: 300% 100%;
    animation: shimmer 5s linear infinite;
    z-index: 3;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.card-anchor) > div { padding: 0.3rem 0.4rem; }

.card-anchor { display: none; }
.card-header-row { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.3rem; }
.card-icon {
    width: 2.4rem; height: 2.4rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem;
    background: rgba(255,153,51,0.14);
    border: 1px solid rgba(255,153,51,0.3);
    flex-shrink: 0;
}
.card-title { font-family: 'Fraunces', serif; font-size: 1.25rem; font-weight: 700; color: #f6efe1; line-height: 1.2; }
.card-sub { font-size: 0.8rem; color: #8b8172; margin-top: 0.1rem; }
.card-inner-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(255,153,51,0.22), transparent);
    margin: 1.1rem 0 1.2rem;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,153,51,0.28) !important;
    border-radius: 12px !important;
    color: #f6efe1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.05rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff9933 !important;
    box-shadow: 0 0 0 3px rgba(255,153,51,0.15) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    color: #ffb84d !important; font-weight: 500 !important;
}

div[role="radiogroup"] { gap: 0.6rem !important; }
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 999px !important; padding: 0.35rem 1rem !important;
    transition: border-color 0.2s, background 0.2s !important;
}
div[role="radiogroup"] label:hover {
    border-color: rgba(255,153,51,0.4) !important;
    background: rgba(255,153,51,0.08) !important;
}
.stRadio > label {
    font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    color: #ffb84d !important; font-weight: 500 !important;
}

/* Primary CTA button */
.stButton > button[kind="primary"] {
    background: linear-gradient(120deg, #ff9933 0%, #e86a2a 55%, #8c2f39 130%) !important;
    color: #14102b !important;
    font-family: 'Baloo 2', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; letter-spacing: 0.02em !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.8rem 2.2rem !important; cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 6px 24px rgba(255,153,51,0.35) !important;
    width: 100%;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 34px rgba(255,153,51,0.48) !important;
    opacity: 0.97 !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* Secondary / chip buttons (example topics) */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.045) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 999px !important;
    color: #c9bfae !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 0.6rem !important;
    box-shadow: none !important;
    transition: border-color 0.2s, color 0.2s, background 0.2s, transform 0.15s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(255,153,51,0.5) !important;
    color: #ffb84d !important;
    background: rgba(255,153,51,0.08) !important;
    transform: translateY(-1px) !important;
}

.chip-label {
    font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #6b6258;
    letter-spacing: 0.12em; padding-top: 0.5rem; display: block; margin-bottom: 0.4rem;
}

/* ── Progress rail ── */
.progress-rail {
    height: 6px; width: 100%;
    background: rgba(255,255,255,0.06); border-radius: 999px;
    overflow: hidden; margin: 0 0 1.5rem;
}
.progress-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #ff9933, #8c2f39, #e8b64f, #ff9933);
    background-size: 300% 100%;
    animation: shimmer 2.2s linear infinite;
    transition: width 0.5s ease;
}

/* ── Timeline pipeline ── */
.timeline { position: relative; padding-left: 2.4rem; }
.timeline::before {
    content: '';
    position: absolute; left: 0.95rem; top: 0.4rem; bottom: 0.4rem;
    width: 2px;
    background: linear-gradient(180deg, rgba(255,153,51,0.5), rgba(232,182,79,0.15));
}
.tl-item { position: relative; margin-bottom: 1.15rem; }
.tl-node {
    position: absolute; left: -2.4rem; top: 0.15rem;
    width: 1.9rem; height: 1.9rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    background: rgba(255,255,255,0.05);
    border: 1.5px solid rgba(255,255,255,0.12);
    transition: border-color 0.3s, background 0.3s;
    z-index: 2;
}
.tl-item.active .tl-node {
    border-color: #ff9933; background: rgba(255,153,51,0.18);
    animation: pulseRing 1.6s ease-out infinite;
}
.tl-item.done .tl-node { border-color: #3fae6a; background: rgba(63,174,106,0.16); }

.tl-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.05rem 1.4rem;
    transition: border-color 0.3s, background 0.3s, transform 0.2s;
}
.tl-card:hover { transform: translateX(2px); }
.tl-item.active .tl-card { border-color: rgba(255,153,51,0.4); background: rgba(255,153,51,0.045); }
.tl-item.done .tl-card { border-color: rgba(63,174,106,0.3); background: rgba(63,174,106,0.035); }

.tl-header { display: flex; align-items: center; gap: 0.7rem; }
.tl-num { font-family: 'DM Mono', monospace; font-size: 0.66rem; letter-spacing: 0.15em; color: #ffb84d; opacity: 0.75; }
.tl-title { font-family: 'Baloo 2', sans-serif; font-size: 0.98rem; font-weight: 700; color: #f3ead9; }
.tl-status { margin-left: auto; font-family: 'DM Mono', monospace; font-size: 0.66rem; letter-spacing: 0.1em; display: inline-flex; align-items: center; gap: 0.35rem; }
.status-waiting { color: #665f56; }
.status-running { color: #ff9933; }
.status-done { color: #3fae6a; }
.dot-pulse {
    width: 6px; height: 6px; border-radius: 50%;
    background: #ff9933; box-shadow: 0 0 6px 1px rgba(255,153,51,0.6);
    animation: pulseRing 1.4s ease-in-out infinite;
}
.tl-desc { font-size: 0.8rem; color: #857b6e; margin-top: 0.25rem; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 0.6rem; margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.2em; text-transform: uppercase; color: #ffb84d;
    margin-bottom: 1rem; padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,153,51,0.18);
}
.result-content {
    font-size: 0.92rem; line-height: 1.8; color: #d9d0c1;
    white-space: pre-wrap; font-family: 'DM Sans', sans-serif;
}

.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,153,51,0.26);
    border-radius: 20px; padding: 2.2rem 2.6rem; margin-top: 1rem;
    box-shadow: 0 24px 55px -25px rgba(255,153,51,0.28);
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(63,174,106,0.26);
    border-radius: 20px; padding: 2.2rem 2.6rem; margin-top: 1.4rem;
    box-shadow: 0 24px 55px -25px rgba(63,174,106,0.22);
}
.panel-label {
    font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.2em;
    text-transform: uppercase; margin-bottom: 1.2rem; padding-bottom: 0.7rem;
}
.panel-label.orange { color: #ffb84d; border-bottom: 1px solid rgba(255,153,51,0.18); }
.panel-label.green { color: #3fae6a; border-bottom: 1px solid rgba(63,174,106,0.18); }

.stSpinner > div { color: #ff9933 !important; }

details {
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.02) !important;
}
details summary {
    font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important;
    color: #b8ac9a !important; letter-spacing: 0.1em !important; cursor: pointer;
}

.section-heading {
    font-family: 'Fraunces', serif; font-size: 1.4rem; font-weight: 700;
    color: #f6efe1; margin: 0 0 1.1rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.section-heading::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(255,153,51,0.3), transparent);
}
.count-badge {
    font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 500;
    letter-spacing: 0.05em; color: #ffb84d;
    background: rgba(255,153,51,0.1); border: 1px solid rgba(255,153,51,0.25);
    border-radius: 999px; padding: 0.2rem 0.7rem;
}

.stDownloadButton > button {
    background: rgba(255,153,51,0.1) !important; color: #ffb84d !important;
    border: 1px solid rgba(255,153,51,0.4) !important; border-radius: 12px !important;
    font-family: 'DM Mono', monospace !important; font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: background 0.2s, transform 0.15s !important;
}
.stDownloadButton > button:hover { background: rgba(255,153,51,0.2) !important; transform: translateY(-1px) !important; }

.notice {
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #6b6258;
    text-align: center; margin-top: 3.5rem; letter-spacing: 0.08em;
}
.notice span { color: #ffb84d; }
</style>
""", unsafe_allow_html=True)


# ── Helper: render a timeline step ────────────────────────────────────────────
STEP_ICONS = {
    "search": "🔍",
    "reader": "📄",
    "writer": "🖋️",
    "critic": "🧭",
}

def step_card(num: str, key: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting", ""),
        "running": ("RUNNING", "status-running", "<span class='dot-pulse'></span>"),
        "done":    ("DONE",    "status-done", "✓"),
    }
    label, cls, prefix = status_map.get(state, ("", "", ""))
    item_cls = {"running": "active", "done": "done"}.get(state, "")
    icon = STEP_ICONS.get(key, "•")
    st.markdown(f"""
    <div class="tl-item {item_cls}">
        <div class="tl-node">{icon}</div>
        <div class="tl-card">
            <div class="tl-header">
                <span class="tl-num">{num}</span>
                <span class="tl-title">{title}</span>
                <span class="tl-status {cls}">{prefix} {label}</span>
            </div>
            {"<div class='tl-desc'>"+desc+"</div>" if desc else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-mark">🪔</div>
    <div class="hero-eyebrow">Multi-Agent Research System</div>
    <div class="hero-devanagari">अन्वेषक</div>
    <h1>Anve<span>shak</span></h1>
    <p class="hero-sub">
        Four specialized AI agents work in harmony — searching, reading,
        writing, and critiquing — to bring you a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5.2, 0.5, 4.3])

# Example topics — clicking one fills the Research Topic field
EXAMPLES = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]

def _set_topic(value):
    st.session_state.topic_input = value

with col_input:
    with st.container(border=True):
        st.markdown('<div class="card-anchor"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header-row">
            <div class="card-icon">🪔</div>
            <div>
                <div class="card-title">New Research</div>
                <div class="card-sub">Point Anveshak at a topic and let the agents take over</div>
            </div>
        </div>
        <div class="card-inner-divider"></div>
        """, unsafe_allow_html=True)

        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Quantum computing breakthroughs in 2025",
            key="topic_input",
            label_visibility="visible",
        )

        st.markdown('<span class="chip-label">OR TRY ONE OF THESE →</span>', unsafe_allow_html=True)
        chip_cols = st.columns(len(EXAMPLES))
        for i, ex in enumerate(EXAMPLES):
            with chip_cols[i]:
                st.button(
                    ex, key=f"chip_{i}", use_container_width=True,
                    on_click=_set_topic, args=(ex,),
                )

        model_mode = st.radio(
            "Performance Mode",
            options=["⚡ Turbo Fast (~20s)", "🧠 Deep Research (~60s)"],
            index=0,
            horizontal=True,
            help="Turbo Fast uses lightweight GPT-OSS-20B for ultra fast results. Deep Research uses GPT-OSS-120B for maximum detail."
        )
        chosen_model = "openai/gpt-oss-20b" if "Turbo" in model_mode else "openai/gpt-oss-120b"

        run_btn = st.button("🪔  Begin Anveshan (Run Pipeline)", use_container_width=True, type="primary")

with col_pipeline:
    r = st.session_state.results
    done = st.session_state.done
    steps_order = ["search", "reader", "writer", "critic"]
    completed_count = sum(1 for k in steps_order if k in r)

    st.markdown(
        f'<div class="section-heading">Pipeline '
        f'<span class="count-badge">{completed_count}/{len(steps_order)} done</span></div>',
        unsafe_allow_html=True,
    )

    def s(step):
        if not r:
            return "waiting"
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps_order:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    # Overall progress bar
    pct = int((completed_count / len(steps_order)) * 100) if (r or st.session_state.running) else 0
    st.markdown(f"""
    <div class="progress-rail">
        <div class="progress-fill" style="width:{pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    step_card("01", "search", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "reader", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "writer", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "critic", "Critic Chain",  s("critic"), "Reviews & scores the report")
    st.markdown('</div>', unsafe_allow_html=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.chosen_model = chosen_model
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input
    active_model = getattr(st.session_state, "chosen_model", "openai/gpt-oss-20b")

    try:
        # ── Step 1: Search ──
        with st.spinner("🔍  Search Agent is gathering web sources…"):
            search_agent = build_search_agent(active_model)
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent and reliable information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 2: Reader ──
        with st.spinner("📄  Reader Agent is extracting deep page content…"):
            reader_agent = build_reader_agent(active_model)
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:1000]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 3: Writer ──
        with st.spinner("🖋️  Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search'][:3000]}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader'][:3000]}"
            )
            writer = build_writer_chain(active_model)
            results["writer"] = writer.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)

        # ── Step 4: Critic ──
        with st.spinner("🧭  Critic is reviewing the report…"):
            critic = build_critic_chain(active_model)
            results["critic"] = critic.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        st.session_state.done = False
        st.error(f"⚠️ An error occurred during the research process: {e}")


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍  Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄  Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])   # render markdown natively
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"anveshak_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧭 Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    <span>अन्वेषक</span> · Anveshak · Multi-agent LangChain pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)