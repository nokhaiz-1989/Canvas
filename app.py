import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_autorefresh import st_autorefresh
from PIL import Image, ImageDraw
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Team Challenge",
    page_icon="⏱️",
    layout="wide"
)

# ============================================================
# SETTINGS
# ============================================================

DRAW_SECONDS = 120  # 2 minutes

TEAM_NAMES = [
    "Team Alpha",
    "Team Bravo",
    "Team Charlie",
    "Team Delta",
    "Team Echo",
    "Team Fifa"
]

# ============================================================
# SHARED STATE
# ============================================================

@st.cache_resource
def get_shared_state():

    return {
        "teams": {
            name: {
                "submitted": False,
                "image": None,
                "timestamp": None
            }
            for name in TEAM_NAMES
        },
        "timer_started": False,
        "timer_start": None,
        "rubric_revealed": False
    }


state = get_shared_state()

# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_remaining_time():

    if not state["timer_started"]:
        return DRAW_SECONDS

    elapsed = time.time() - state["timer_start"]

    remaining = max(0, DRAW_SECONDS - int(elapsed))

    return remaining


def format_time(seconds):

    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}:{seconds:02d}"


# ============================================================
# TIME BAR
# ============================================================

def render_time_bar(remaining):

    progress = remaining / DRAW_SECONDS

    # --------------------------------------------------------
    # Colour changes as time decreases
    # --------------------------------------------------------

    if progress > 0.60:
        bar_color = "#40C057"       # Green
        status_text = "TIME REMAINING"
    elif progress > 0.35:
        bar_color = "#F59F00"       # Yellow / Orange
        status_text = "TIME IS RUNNING"
    elif progress > 0.15:
        bar_color = "#F76707"       # Orange
        status_text = "HURRY!"
    else:
        bar_color = "#F03E3E"       # Red
        status_text = "ALMOST OUT!"

    if remaining == 0:

        st.markdown(
            """
            <div style="
                text-align:center;
                margin:15px 0 25px 0;
            ">
                <div style="
                    font-size:42px;
                    font-weight:800;
                    color:#F03E3E;
                    margin-bottom:12px;
                ">
                    TIME'S UP!
                </div>

                <div style="
                    width:100%;
                    height:28px;
                    background:#F03E3E;
                    border-radius:20px;
                ">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    st.markdown(
        f"""
        <div style="
            width:100%;
            max-width:850px;
            margin:10px auto 25px auto;
            text-align:center;
        ">

            <div style="
                font-size:16px;
                font-weight:700;
                color:{bar_color};
                margin-bottom:4px;
                letter-spacing:1px;
            ">
                {status_text}
            </div>

            <div style="
                font-size:42px;
                font-weight:800;
                color:{bar_color};
                margin-bottom:12px;
            ">
                {format_time(remaining)}
            </div>

            <div style="
                width:100%;
                height:30px;
                background:#E9ECEF;
                border-radius:20px;
                overflow:hidden;
                border:2px solid #DEE2E6;
            ">

                <div style="
                    width:{progress * 100}%;
                    height:100%;
                    background:{bar_color};
                    border-radius:18px;
                    transition:width 0.8s linear, background 0.8s ease;
                ">
                </div>

            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                font-size:13px;
                color:#868E96;
                margin-top:5px;
            ">
                <span>START</span>
                <span>2:00</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HOME PAGE
# ============================================================

def home():

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:35px 10px 20px 10px;
        ">

            <h1 style="
                font-size:42px;
                margin-bottom:10px;
            ">
                🎯 TEAM CHALLENGE
            </h1>

            <p style="
                font-size:20px;
                color:#666;
            ">
                Work with your team to complete the challenge.
            </p>

            <p style="
                font-size:18px;
                color:#888;
            ">
                Further instructions will be revealed during the activity.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Select your team")

    cols = st.columns(3)

    for i, team in enumerate(TEAM_NAMES):

        with cols[i % 3]:

            if st.button(
                team,
                use_container_width=True,
                key=f"home_{team}"
            ):

                st.session_state.selected_team = team
                st.session_state.page = "draw"
                st.rerun()


# ============================================================
# DRAW / TASK PAGE
# ============================================================

def draw_page():

    team = st.session_state.selected_team

    if not team:
        st.session_state.page = "home"
        st.rerun()

    # --------------------------------------------------------
    # Refresh every second
    # --------------------------------------------------------

    st_autorefresh(
        interval=1000,
        key="participant_timer_refresh"
    )

    remaining = get_remaining_time()

    # --------------------------------------------------------
    # TEAM HEADER
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            text-align:center;
            margin-bottom:5px;
        ">

            <h1 style="margin-bottom:5px;">
                {team}
            </h1>

            <p style="
                font-size:19px;
                color:#666;
            ">
                Complete the challenge!
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TIME BAR
    # --------------------------------------------------------

    render_time_bar(remaining)

    # --------------------------------------------------------
    # START TIMER AUTOMATICALLY
    # --------------------------------------------------------

    if not state["timer_started"]:

        state["timer_started"] = True
        state["timer_start"] = time.time()

        st.rerun()

    # --------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=4,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=500,
        width=900,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.canvas_key}",
        display_toolbar=True
    )

    # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------

    if st.button(
        "🚀 Submit",
        use_container_width=True,
        type="primary"
    ):

        if canvas_result.image_data is not None:

            image = Image.fromarray(
                canvas_result.image_data.astype("uint8")
            )

            state["teams"][team]["image"] = image
            state["teams"][team]["submitted"] = True
            state["teams"][team]["timestamp"] = time.time()

            st.success(
                "Your task is submitted. Sit tight for the reveal."
            )

        else:

            st.warning(
                "Please complete the challenge before submitting."
            )

    # --------------------------------------------------------
    # TIME UP
    # --------------------------------------------------------

    if remaining == 0:

        st.error(
            "⏰ Time is up! No more changes can be made."
        )


# ============================================================
# FACILITATOR PAGE
# ============================================================

def facilitator():

    st.title("🎯 Facilitator View")

    # --------------------------------------------------------
    # TIMER
    # --------------------------------------------------------

    if state["timer_started"]:

        st_autorefresh(
            interval=1000,
            key="facilitator_timer_refresh"
        )

        remaining = get_remaining_time()

        render_time_bar(remaining)

    else:

        st.info(
            "The timer has not started yet."
        )

        if st.button(
            "▶ Start 2-minute timer",
            use_container_width=True
        ):

            state["timer_started"] = True
            state["timer_start"] = time.time()

            st.rerun()

    st.divider()

    # --------------------------------------------------------
    # TEAM STATUS
    # --------------------------------------------------------

    st.subheader("Team Status")

    cols = st.columns(3)

    for i, team in enumerate(TEAM_NAMES):

        with cols[i % 3]:

            submitted = state["teams"][team]["submitted"]

            if submitted:

                st.success(
                    f"✅ {team}\n\nSubmitted"
                )

            else:

                st.warning(
                    f"⏳ {team}\n\nNot submitted"
                )

    st.divider()

    # --------------------------------------------------------
    # LIVE GALLERY
    # --------------------------------------------------------

    st.subheader("Live Gallery")

    submitted_teams = [
        team
        for team in TEAM_NAMES
        if state["teams"][team]["submitted"]
    ]

    if submitted_teams:

        gallery_cols = st.columns(3)

        for i, team in enumerate(submitted_teams):

            with gallery_cols[i % 3]:

                st.markdown(
                    f"### {team}"
                )

                image = state["teams"][team]["image"]

                if image is not None:

                    st.image(
                        image,
                        use_container_width=True
                    )

    else:

        st.info(
            "No team has submitted yet."
        )

    st.divider()

    # --------------------------------------------------------
    # RUBRIC
    # --------------------------------------------------------

    st.subheader("🔐 Reveal the Rubric")

    if not state["rubric_revealed"]:

        st.write(
            "Keep this hidden until the activity is complete."
        )

        if st.button(
            "🔓 Reveal Rubric",
            use_container_width=True
        ):

            state["rubric_revealed"] = True

            st.rerun()

    else:

        st.success("Rubric Revealed")

        st.markdown(
            """
            ### Assessment Criteria

            - Exactly **1 door**
            - Exactly **1 window**
            - Exactly **1 chimney**

            ---

            **Discussion point:**

            The participants completed the activity without seeing
            these assessment criteria beforehand.

            This demonstrates why the **learning outcome,
            activity, and assessment criteria must be aligned
            in OBE.**
            """
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎯 Team Challenge")

    st.divider()

    if st.button(
        "🏠 Participant View",
        use_container_width=True
    ):

        st.session_state.page = "home"
        st.rerun()

    if st.button(
        "👩‍🏫 Facilitator View",
        use_container_width=True
    ):

        st.session_state.page = "facilitator"
        st.rerun()

    st.divider()

    st.caption(
        "Facilitator controls are intended for the workshop presenter."
    )


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == "home":

    home()

elif st.session_state.page == "draw":

    draw_page()

elif st.session_state.page == "facilitator":

    facilitator()
