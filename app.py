import io
import random
import time
from datetime import datetime

import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="OBE Icebreaker — Draw & Share",
    page_icon="🎨",
    layout="wide",
)

# -----------------------------
# Shared multiplayer state
# -----------------------------
TEAM_NAMES = {
    1: "Team Alpha",
    2: "Team Bravo",
    3: "Team Charlie",
    4: "Team Delta",
    5: "Team Echo",
    6: "Team Fifa",
}

PROMPT = "Draw a house in 10 seconds."
INSTRUCTION = "Do not discuss with other teams. Everyone receives exactly the same instruction."
CANVAS_WIDTH = 650
CANVAS_HEIGHT = 430


@st.cache_resource
def get_shared_state():
    return {
        i: {
            "name": TEAM_NAMES[i],
            "drawing": None,
            "submitted": False,
            "submitted_at": None,
        }
        for i in range(1, 7)
    }


teams = get_shared_state()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "team_id" not in st.session_state:
    st.session_state.team_id = None

# -----------------------------
# Styling helpers
# -----------------------------
def inject_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 1rem;}
        .hero {
            text-align:center; padding: 8px 10px 16px;
        }
        .hero h1 {
            font-size: 46px; margin:0; font-weight:900; letter-spacing:-1px;
        }
        .hero p {
            font-size:20px; color:#666; margin:8px 0 0;
        }
        .prompt-box {
            border:3px solid #4C6EF5; border-radius:22px;
            padding:22px 24px; background:#F8F9FA; text-align:center;
            box-shadow:0 8px 24px rgba(0,0,0,.08); margin:8px 0 18px;
        }
        .prompt-main {font-size:34px; font-weight:900;}
        .prompt-sub {font-size:17px; color:#555; margin-top:7px;}
        .timer {
            font-size:42px; font-weight:900; text-align:center;
            padding:8px; border-radius:16px; background:#FFF4E6;
            border:2px solid #FFD8A8;
        }
        .team-card {
            border:2px solid #DEE2E6; border-radius:18px; padding:12px;
            background:#FFF; box-shadow:0 4px 12px rgba(0,0,0,.06);
        }
        .team-card.done {border-color:#40C057; background:#F4FCE3;}
        .team-name {font-size:20px; font-weight:900;}
        .team-status {font-size:14px; font-weight:800; margin-top:4px;}
        .reveal-title {
            text-align:center; font-size:38px; font-weight:900; margin:12px 0 4px;
        }
        .reveal-sub {text-align:center; color:#666; font-size:18px; margin-bottom:15px;}
        .connection {
            text-align:center; font-size:26px; font-weight:900;
            padding:15px 20px; border-radius:18px; background:#E7F5FF;
            border:2px solid #74C0FC; margin-top:18px;
        }
        .step-card {
            text-align:center; padding:18px; border-radius:16px;
            border:2px solid #DEE2E6; background:#F8F9FA;
            min-height:135px;
        }
        .step-number {font-size:28px; font-weight:900;}
        .step-title {font-size:18px; font-weight:900; margin-top:4px;}
        .step-desc {font-size:14px; color:#666; margin-top:5px; line-height:1.3;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def drawing_to_png_bytes(image_data):
    if image_data is None:
        return None
    image = Image.fromarray(image_data.astype("uint8"), mode="RGBA")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def reset_all():
    for team in teams.values():
        team["drawing"] = None
        team["submitted"] = False
        team["submitted_at"] = None


# -----------------------------
# Pages
# -----------------------------
def home():
    st.markdown(
        """
        <div class="hero">
            <h1>🎨 DRAW & SHARE</h1>
            <p>A 3-minute OBE icebreaker for teams</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="prompt-box">
            <div class="prompt-main">🏠 {PROMPT}</div>
            <div class="prompt-sub">{INSTRUCTION}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎨 JOIN AS A TEAM", type="primary", use_container_width=True):
            st.session_state.page = "join"
            st.rerun()
    with col2:
        if st.button("📺 PRESENTER / SHARE SCREEN", use_container_width=True):
            st.session_state.page = "presenter"
            st.rerun()

    st.divider()
    st.markdown("### How the activity works")
    cols = st.columns(3)
    steps = [
        ("1", "DRAW", "Each team draws its own version of the house."),
        ("2", "SUBMIT", "The team's drawing is saved centrally."),
        ("3", "REVEAL", "You show every team's drawing together on the projector."),
    ]
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="step-card">
                    <div class="step-number">{num}</div>
                    <div class="step-title">{title}</div>
                    <div class="step-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def join():
    st.markdown("## 👥 Choose Your Team")
    st.caption("Use one device per team. Team members can collaborate on the same device.")

    team_id = st.selectbox(
        "Team",
        list(TEAM_NAMES.keys()),
        format_func=lambda i: TEAM_NAMES[i],
    )

    team = teams[team_id]
    if team["submitted"]:
        st.success(f"✅ {team['name']} has already submitted a drawing. You can reopen it below.")
    else:
        st.info(f"{team['name']} is ready to draw!")

    if st.button("ENTER DRAWING ROOM", type="primary", use_container_width=True):
        st.session_state.team_id = team_id
        st.session_state.page = "draw"
        st.rerun()

    if st.button("← Home"):
        st.session_state.page = "home"
        st.rerun()


def draw_room():
    team_id = st.session_state.team_id
    team = teams[team_id]

    st.markdown(
        f"<div class='hero'><h1>🎨 {team['name']}</h1><p>Get ready. Think fast. Draw!</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="prompt-box">
            <div class="prompt-main">🏠 {PROMPT}</div>
            <div class="prompt-sub">{INSTRUCTION}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning("⏱️ Suggested facilitator countdown: 10 seconds. Start when everyone is ready.")

    stroke_width = st.slider("Pen size", 2, 12, 5)
    drawing_color = st.color_picker("Pen color", "#111111")

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=drawing_color,
        background_color="#FFFFFF",
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH,
        drawing_mode="freedraw",
        return_image_data=True,
        key=f"canvas_{team_id}",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ SUBMIT TEAM DRAWING", type="primary", use_container_width=True):
            png_bytes = drawing_to_png_bytes(canvas_result.image_data)
            if png_bytes:
                team["drawing"] = png_bytes
                team["submitted"] = True
                team["submitted_at"] = datetime.now().strftime("%H:%M:%S")
                st.success("🎉 Drawing submitted! Check the presenter screen.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Please draw something before submitting.")
    with c2:
        if st.button("📺 Go to Presenter Screen", use_container_width=True):
            st.session_state.page = "presenter"
            st.rerun()

    if team["submitted"]:
        st.info(f"Your drawing was submitted at {team['submitted_at']}. You may draw again and resubmit to replace it.")


def presenter():
    # Refresh automatically so drawings appear as teams submit them.
    st_autorefresh(interval=2000, key="icebreaker_presenter_refresh")

    submitted_count = sum(t["submitted"] for t in teams.values())

    st.markdown(
        """
        <div class="hero">
            <h1>📺 TEAM DRAWING REVEAL</h1>
            <p>Watch the teams' interpretations appear live.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='reveal-sub'><b>{submitted_count}/6 teams</b> have submitted</div>",
        unsafe_allow_html=True,
    )

    if submitted_count == 0:
        st.info("Waiting for the teams to submit their drawings…")
    else:
        # Six-team projector layout: 3 x 2.
        for row in range(2):
            cols = st.columns(3)
            for col, team_id in zip(cols, range(row * 3 + 1, row * 3 + 4)):
                team = teams[team_id]
                with col:
                    card_class = "team-card done" if team["submitted"] else "team-card"
                    status = "✅ SUBMITTED" if team["submitted"] else "⏳ WAITING"
                    st.markdown(
                        f"""
                        <div class="{card_class}">
                            <div class="team-name">{team['name']}</div>
                            <div class="team-status">{status}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if team["drawing"]:
                        st.image(team["drawing"], use_container_width=True)
                    else:
                        st.markdown("<div style='height:300px;display:flex;align-items:center;justify-content:center;border:2px dashed #DEE2E6;border-radius:14px;color:#999;'>Waiting for drawing…</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="connection">
            Same instruction → different results → <b>WHY?</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 💡 Debrief: connect it to OBE")
    st.write(
        "Ask: “I gave every team the same instruction. Why are the results different? "
        "What was missing from the instruction? What would make the expected result clearer?"
    )
    st.markdown(
        "**Transition:** Clear expectations lead to clearer learning outcomes, better-designed activities, and assessments that actually measure the intended learning."
    )

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
    with b2:
        if st.button("🗑️ Reset All Drawings", use_container_width=True):
            reset_all()
            st.rerun()
    with b3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


inject_css()

if st.session_state.page == "home":
    home()
elif st.session_state.page == "join":
    join()
elif st.session_state.page == "draw":
    draw_room()
elif st.session_state.page == "presenter":
    presenter()
