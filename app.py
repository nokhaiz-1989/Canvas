"""
OUTCOME DRAWING ICEBREAKER
--------------------------
A standalone warm-up exercise for demonstrating the importance of
clearly defined learning outcomes and alignment.

Participants are given a deliberately vague task.
The rubric is NOT shown until everyone has submitted.

Features:
- 6 teams
- 2-minute countdown
- Animated visual time bomb
- Bomb fuse gets progressively shorter as time runs out
- Team canvas for drawing
- Live facilitator gallery
- Rubric revealed only by facilitator
- Shared state across browser sessions

Run with:
    streamlit run outcome_drawing_icebreaker.py

Requirements:
    pip install "streamlit-drawable-canvas[image]"
    pip install streamlit-autorefresh

Requires:
    streamlit-drawable-canvas >= 0.10.0
    Streamlit >= 1.53
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import base64
import io

from streamlit_autorefresh import st_autorefresh
from streamlit_drawable_canvas import st_canvas
from PIL import Image


# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Team Challenge",
    page_icon="💣",
    layout="wide"
)


# --------------------------------------------------------------------------
# SETTINGS
# --------------------------------------------------------------------------

DEFAULT_TEAM_NAMES = {
    1: "Team Alpha",
    2: "Team Bravo",
    3: "Team Charlie",
    4: "Team Delta",
    5: "Team Echo",
    6: "Team Fifa",
}


# 2 MINUTES
DRAW_SECONDS = 120

CANVAS_HEIGHT = 380
CANVAS_WIDTH = 460


# --------------------------------------------------------------------------
# HIDDEN RUBRIC
# --------------------------------------------------------------------------

# Participants NEVER see this until the facilitator reveals it.

RUBRIC = [
    "Exactly 1 door",
    "Exactly 1 window",
    "Exactly 1 chimney",
]


# --------------------------------------------------------------------------
# HELPER
# --------------------------------------------------------------------------

def flat_html(s):
    """
    Flatten multiline HTML so Streamlit's Markdown parser
    does not interpret indented HTML as a code block.
    """
    return " ".join(
        line.strip()
        for line in s.strip().splitlines()
    )


# --------------------------------------------------------------------------
# SHARED STATE
# --------------------------------------------------------------------------

@st.cache_resource
def get_shared_state():

    return {
        "start_time": None,

        "rubric_revealed": False,

        "teams": {
            i: {
                "name": DEFAULT_TEAM_NAMES[i],
                "submitted": False,
                "image_b64": None,
                "marks": {
                    item: None
                    for item in RUBRIC
                },
            }
            for i in range(1, 7)
        },
    }


state = get_shared_state()
teams = state["teams"]


# --------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "team" not in st.session_state:
    st.session_state.team = None


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------

def inject_css():

    st.markdown(
        flat_html("""
        <style>

        .block-container {
            max-width: 100% !important;
            padding: 1.2rem 2rem !important;
        }

        /* --------------------------------------------------------------
           HEADER
        -------------------------------------------------------------- */

        .ib-header {
            background: #101534;
            border-radius: 16px;
            padding: 16px 24px;
            margin-bottom: 16px;
            text-align: center;
        }

        .ib-title {
            font-family: 'Trebuchet MS', sans-serif;
            font-size: 32px;
            font-weight: 800;
            color: #FFFFFF;
            margin: 0;
        }

        .ib-sub {
            font-size: 15px;
            color: #98A2D8;
            margin-top: 4px;
        }


        /* --------------------------------------------------------------
           TIME BOMB AREA
        -------------------------------------------------------------- */

        .bomb-wrapper {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 5px 0 18px 0;
        }

        .bomb-stage {
            position: relative;
            width: 360px;
            height: 145px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Bomb body */

        .bomb {
            position: absolute;
            left: 75px;
            top: 35px;
            width: 82px;
            height: 82px;
            background: #101534;
            border-radius: 50%;
            border: 5px solid #343A70;
            box-shadow:
                0 5px 0 #080B20,
                inset 0 0 0 4px #1B2250;
        }

        /* Bomb shine */

        .bomb:before {
            content: "";
            position: absolute;
            width: 17px;
            height: 17px;
            border-radius: 50%;
            background: #FFFFFF;
            opacity: 0.7;
            top: 14px;
            left: 17px;
        }

        /* Bomb neck */

        .bomb-neck {
            position: absolute;
            left: 137px;
            top: 24px;
            width: 27px;
            height: 25px;
            background: #343A70;
            border-radius: 6px 6px 2px 2px;
        }

        /* Fuse base */

        .fuse-base {
            position: absolute;
            left: 154px;
            top: 27px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #F59F00;
            z-index: 4;
        }

        /* Fuse */

        .fuse-track {
            position: absolute;
            left: 158px;
            top: 10px;
            width: 170px;
            height: 5px;
            background: #ADB5BD;
            border-radius: 10px;
            transform: rotate(-18deg);
            transform-origin: left center;
        }

        .fuse-burning {
            position: absolute;
            left: 0;
            top: 0;
            height: 5px;
            width: var(--fuse-width);
            background: #F59F00;
            border-radius: 10px;
            transition: width 1s linear;
        }

        /* Spark */

        .spark {
            position: absolute;
            left: calc(158px + var(--spark-position));
            top: 2px;
            font-size: 26px;
            line-height: 1;
            transition: left 1s linear;
        }

        /* Timer */

        .timer-number {
            font-family: 'Trebuchet MS', sans-serif;
            font-size: 48px;
            font-weight: 900;
            color: #101534;
            text-align: center;
            margin-top: 0;
            line-height: 1;
        }

        .timer-label {
            font-size: 14px;
            font-weight: 700;
            color: #868E96;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
            margin-top: 5px;
        }


        /* --------------------------------------------------------------
           TIME'S UP
        -------------------------------------------------------------- */

        .times-up {
            background: #FFE3E3;
            border: 4px solid #C92A2A;
            color: #C92A2A;
            border-radius: 18px;
            padding: 20px;
            text-align: center;
            font-size: 30px;
            font-weight: 900;
            margin-bottom: 18px;
        }


        /* --------------------------------------------------------------
           GALLERY
        -------------------------------------------------------------- */

        .gallery-card {
            background: #FFFFFF;
            border: 3px solid #101534;
            border-radius: 14px;
            padding: 10px;
            text-align: center;
            box-shadow: 0 5px 0 #101534;
            margin-bottom: 14px;
        }

        .gallery-name {
            font-weight: 800;
            font-size: 17px;
            color: #101534;
            margin-bottom: 6px;
        }

        .gallery-empty {
            color: #ADB5BD;
            font-style: italic;
            padding: 40px 0;
            font-size: 15px;
        }


        /* --------------------------------------------------------------
           RUBRIC
        -------------------------------------------------------------- */

        .rubric-box {
            background: #FFF3BF;
            border: 3px solid #F59F00;
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 16px;
        }

        .rubric-title {
            font-family: 'Trebuchet MS', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #8A6100;
            margin-bottom: 8px;
        }

        .rubric-item {
            font-size: 19px;
            color: #5C4500;
            margin: 4px 0;
        }


        /* --------------------------------------------------------------
           FINAL MESSAGE
        -------------------------------------------------------------- */

        .moral-box {
            background: #101534;
            color: #FFFFFF;
            border-radius: 16px;
            padding: 20px 26px;
            font-size: 20px;
            line-height: 1.55;
        }

        </style>
        """),
        unsafe_allow_html=True
    )


# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------

def header(subtitle):

    st.markdown(
        flat_html(f"""
        <div class="ib-header">
            <div class="ib-title">🎯 TEAM CHALLENGE</div>
            <div class="ib-sub">{subtitle}</div>
        </div>
        """),
        unsafe_allow_html=True
    )


# --------------------------------------------------------------------------
# IMAGE CONVERSION
# --------------------------------------------------------------------------

def image_from_canvas(image_data):

    img = Image.fromarray(
        image_data.astype("uint8"),
        "RGBA"
    )

    # Put transparent canvas onto white background
    bg = Image.new(
        "RGBA",
        img.size,
        (255, 255, 255, 255)
    )

    bg.paste(
        img,
        mask=img
    )

    buf = io.BytesIO()

    bg.convert("RGB").save(
        buf,
        format="PNG"
    )

    return base64.b64encode(
        buf.getvalue()
    ).decode()


# --------------------------------------------------------------------------
# CONFETTI
# --------------------------------------------------------------------------

def celebrate_submit():

    components.html(
        """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/canvas-confetti/1.9.2/confetti.browser.min.js"></script>

        <script>

        (function () {

            function fire() {

                if (typeof confetti === 'function') {

                    confetti({
                        particleCount: 90,
                        spread: 80,
                        origin: {y: 0.4}
                    });

                } else {

                    setTimeout(fire, 100);

                }

            }

            fire();

        })();

        </script>
        """,
        height=1,
    )


# --------------------------------------------------------------------------
# TIMER
# --------------------------------------------------------------------------

def time_left():

    if state["start_time"] is None:
        return None

    elapsed = time.time() - state["start_time"]

    return max(
        0,
        DRAW_SECONDS - elapsed
    )


# --------------------------------------------------------------------------
# TIME BOMB DISPLAY
# --------------------------------------------------------------------------

def render_time_bomb(remaining):

    if remaining is None:

        st.markdown(
            flat_html("""
            <div class="bomb-wrapper">

                <div class="bomb-stage">

                    <div class="bomb-neck"></div>

                    <div class="fuse-track">
                        <div class="fuse-burning"
                             style="--fuse-width:170px;">
                        </div>
                    </div>

                    <div class="fuse-base"></div>

                    <div class="bomb"></div>

                </div>

                <div class="timer-number">2:00</div>

                <div class="timer-label">
                    Waiting for the timer
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

        return


    # --------------------------------------------------------------
    # TIME IS UP
    # --------------------------------------------------------------

    if remaining <= 0:

        st.markdown(
            """
            <div class="times-up">
                💥 TIME'S UP!
            </div>
            """,
            unsafe_allow_html=True
        )

        return


    # --------------------------------------------------------------
    # CALCULATE FUSE LENGTH
    # --------------------------------------------------------------

    ratio = remaining / DRAW_SECONDS

    # Original fuse length = 170px
    fuse_width = max(
        0,
        int(170 * ratio)
    )

    # Spark travels from right to left
    spark_position = int(
        170 * ratio
    )

    mins, secs = divmod(
        int(remaining),
        60
    )

    timer_text = f"{mins:01d}:{secs:02d}"


    # --------------------------------------------------------------
    # COLOR CHANGES
    # --------------------------------------------------------------

    if remaining <= 30:

        timer_color = "#C92A2A"

    elif remaining <= 60:

        timer_color = "#F59F00"

    else:

        timer_color = "#101534"


    # --------------------------------------------------------------
    # RENDER
    # --------------------------------------------------------------

    st.markdown(
        flat_html(f"""
        <div class="bomb-wrapper">

            <div class="bomb-stage">

                <div class="bomb-neck"></div>

                <div class="fuse-track">

                    <div class="fuse-burning"
                         style="
                         --fuse-width:{fuse_width}px;
                         background:{timer_color};
                         ">
                    </div>

                </div>

                <div class="fuse-base"></div>

                <div class="spark"
                     style="
                     --spark-position:{spark_position}px;
                     ">
                    ✨
                </div>

                <div class="bomb"></div>

            </div>

            <div class="timer-number"
                 style="color:{timer_color};">

                {timer_text}

            </div>

            <div class="timer-label">

                TIME REMAINING

            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------

def home():

    inject_css()

    header(
        "Work with your team to complete the challenge."
    )

    st.info(
        "Further instructions will be revealed during the activity."
    )

    a, b = st.columns(2)

    with a:

        if st.button(
            "🎨 JOIN AS TEAM",
            use_container_width=True,
            type="primary"
        ):

            st.session_state.page = "join"

            st.rerun()


    with b:

        if st.button(
            "📺 FACILITATOR VIEW",
            use_container_width=True
        ):

            st.session_state.page = "facilitator"

            st.rerun()


# --------------------------------------------------------------------------
# JOIN
# --------------------------------------------------------------------------

def join():

    inject_css()

    header(
        "Select your team to enter the challenge."
    )

    team = st.selectbox(
        "Select your team",
        [
            t["name"]
            for t in teams.values()
        ]
    )

    team_id = next(
        i
        for i, tm in teams.items()
        if tm["name"] == team
    )


    if st.button(
        "ENTER",
        type="primary",
        use_container_width=True
    ):

        st.session_state.team = team_id
        st.session_state.page = "draw"

        st.rerun()


    if st.button("← Back"):

        st.session_state.page = "home"

        st.rerun()


# --------------------------------------------------------------------------
# DRAW PAGE
# --------------------------------------------------------------------------

def draw_page():

    inject_css()

    team_id = st.session_state.team

    t = teams[team_id]


    header(
        f"{t['name']} — complete the challenge!"
    )


    # Refresh every second
    st_autorefresh(
        interval=1000,
        key="draw_timer_refresh"
    )


    remaining = time_left()


    # --------------------------------------------------------------
    # TIME BOMB
    # --------------------------------------------------------------

    render_time_bomb(remaining)


    # --------------------------------------------------------------
    # SUBMITTED
    # --------------------------------------------------------------

    if t["submitted"]:

        st.success(
            "Your task is submitted. Sit tight for the reveal."
        )

        st.image(
            Image.open(
                io.BytesIO(
                    base64.b64decode(
                        t["image_b64"]
                    )
                )
            ),
            width=CANVAS_WIDTH
        )


        if st.button(
            "↺ Redraw"
        ):

            t["submitted"] = False
            t["image_b64"] = None

            st.rerun()


    # --------------------------------------------------------------
    # CANVAS
    # --------------------------------------------------------------

    else:

        canvas_result = st_canvas(

            fill_color="rgba(0,0,0,0)",

            stroke_width=4,

            stroke_color="#101534",

            background_color="#FFFFFF",

            height=CANVAS_HEIGHT,

            width=CANVAS_WIDTH,

            drawing_mode="freedraw",

            return_image_data=True,

            key=f"canvas_{team_id}",

        )


        if st.button(
            "🚀 Submit",
            type="primary",
            use_container_width=True
        ):

            if canvas_result.image_data is not None:

                t["image_b64"] = image_from_canvas(
                    canvas_result.image_data
                )

                t["submitted"] = True

                celebrate_submit()

                st.rerun()

            else:

                st.warning(
                    "Complete the task first!"
                )


    # --------------------------------------------------------------
    # LEAVE
    # --------------------------------------------------------------

    if st.button("← Leave"):

        st.session_state.page = "home"

        st.rerun()


# --------------------------------------------------------------------------
# FACILITATOR VIEW
# --------------------------------------------------------------------------

def facilitator():

    inject_css()

    st_autorefresh(
        interval=1000,
        key="facilitator_refresh"
    )


    header(
        "Facilitator view — live gallery and reveal"
    )


    remaining = time_left()


    # --------------------------------------------------------------
    # CONTROL BAR
    # --------------------------------------------------------------

    c1, c2, c3 = st.columns(3)


    with c1:

        if state["start_time"] is None:

            if st.button(
                "▶ Start 2-minute timer",
                type="primary",
                use_container_width=True
            ):

                state["start_time"] = time.time()

                st.rerun()


        else:

            if st.button(
                "↺ Reset timer",
                use_container_width=True
            ):

                state["start_time"] = None

                st.rerun()


    with c2:

        submitted_count = sum(
            1
            for tm in teams.values()
            if tm["submitted"]
        )

        st.metric(
            "Submitted",
            f"{submitted_count} / {len(teams)}"
        )


    with c3:

        if remaining is not None:

            if remaining > 0:

                mins, secs = divmod(
                    int(remaining),
                    60
                )

                label = f"{mins:01d}:{secs:02d}"

            else:

                label = "Time's up"

            st.metric(
                "Time left",
                label
            )

        else:

            st.metric(
                "Time left",
                "—"
            )


    st.divider()


    # --------------------------------------------------------------
    # FACILITATOR TIME BOMB
    # --------------------------------------------------------------

    render_time_bomb(remaining)


    st.divider()


    # --------------------------------------------------------------
    # LIVE GALLERY
    # --------------------------------------------------------------

    st.subheader(
        "🖼️ Live gallery"
    )


    cols = st.columns(3)


    for idx, (i, t) in enumerate(
        teams.items()
    ):

        with cols[idx % 3]:

            if t["submitted"]:

                st.markdown(
                    f"""
                    <div class='gallery-card'>
                        <div class='gallery-name'>
                            {t['name']}
                        </div>
                    """,
                    unsafe_allow_html=True
                )


                st.image(
                    Image.open(
                        io.BytesIO(
                            base64.b64decode(
                                t["image_b64"]
                            )
                        )
                    ),
                    use_container_width=True
                )


                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


            else:

                st.markdown(
                    flat_html(f"""
                    <div class="gallery-card">

                        <div class="gallery-name">
                            {t['name']}
                        </div>

                        <div class="gallery-empty">
                            Still working…
                        </div>

                    </div>
                    """),
                    unsafe_allow_html=True
                )


    st.divider()


    # --------------------------------------------------------------
    # RUBRIC REVEAL
    # --------------------------------------------------------------

    if not state["rubric_revealed"]:

        submitted_count = sum(
            1
            for tm in teams.values()
            if tm["submitted"]
        )


        if submitted_count < len(teams):

            st.caption(
                f"Waiting on "
                f"{len(teams) - submitted_count} "
                f"more team(s) before moving on."
            )


        else:

            if st.button(
                "▶ Move on to the next step",
                type="primary",
                use_container_width=True
            ):

                state["rubric_revealed"] = True

                st.rerun()


    else:

        st.subheader(
            "📋 The rubric nobody saw"
        )


        st.markdown(
            flat_html(f"""
            <div class="rubric-box">

                <div class="rubric-title">
                    The rubric was:
                </div>

                {"".join(
                    f"<div class='rubric-item'>✔ {item}</div>"
                    for item in RUBRIC
                )}

            </div>
            """),
            unsafe_allow_html=True
        )


        st.caption(
            "For each team's drawing, mark whether it happens "
            "to meet each rubric item. This is for discussion, "
            "judged by eye, not auto-graded."
        )


        full_match = 0
        judged = 0


        for i, t in teams.items():

            if not t["submitted"]:
                continue


            with st.expander(
                f"{t['name']}",
                expanded=False
            ):

                left, right = st.columns(
                    [1, 1]
                )


                with left:

                    st.image(
                        Image.open(
                            io.BytesIO(
                                base64.b64decode(
                                    t["image_b64"]
                                )
                            )
                        ),
                        use_container_width=True
                    )


                with right:

                    hits = 0
                    any_judged = False


                    for item in RUBRIC:

                        current = t["marks"][item]


                        choice = st.radio(

                            item,

                            [
                                "Not judged",
                                "✅ Meets it",
                                "❌ Misses it"
                            ],

                            index={
                                "Not judged": 0,
                                True: 1,
                                False: 2
                            }.get(
                                "Not judged"
                                if current is None
                                else current,
                                0
                            ),

                            key=f"mark_{i}_{item}",

                            horizontal=True,

                        )


                        if choice == "✅ Meets it":

                            t["marks"][item] = True

                            hits += 1

                            any_judged = True


                        elif choice == "❌ Misses it":

                            t["marks"][item] = False

                            any_judged = True


                        else:

                            t["marks"][item] = None


                    if any_judged:

                        judged += 1


                        if hits == len(RUBRIC):

                            full_match += 1


        # ----------------------------------------------------------
        # FINAL DISCUSSION MESSAGE
        # ----------------------------------------------------------

        if judged:

            st.markdown(
                flat_html(f"""
                <div class="moral-box">

                    <b>
                    {full_match} of {judged} judged teams
                    </b>
                    happened to satisfy every rubric item —
                    even though nobody knew the rubric while
                    completing the task.

                    <br><br>

                    Notice how different the results can be
                    when the expected outcome is not clearly
                    defined before the activity begins.

                    <br><br>

                    This is what happens when a learning outcome
                    isn't defined <i>before</i> the activity starts.

                    Aligning the <b>outcome</b>,
                    <b>activity</b>, and <b>assessment</b>
                    — in that order — is what the rest of
                    today's game is about.

                </div>
                """),
                unsafe_allow_html=True
            )


    st.divider()


    # --------------------------------------------------------------
    # BOTTOM CONTROLS
    # --------------------------------------------------------------

    c1, c2 = st.columns(2)


    with c1:

        if st.button(
            "🔄 Refresh",
            use_container_width=True
        ):

            st.rerun()


    with c2:

        if st.button(
            "🏠 Home",
            use_container_width=True
        ):

            st.session_state.page = "home"

            st.rerun()


# --------------------------------------------------------------------------
# RESET
# --------------------------------------------------------------------------

def reset_all():

    state["start_time"] = None

    state["rubric_revealed"] = False


    for i in range(1, 7):

        teams[i].update({

            "name": DEFAULT_TEAM_NAMES[i],

            "submitted": False,

            "image_b64": None,

            "marks": {
                item: None
                for item in RUBRIC
            },

        })


# --------------------------------------------------------------------------
# PAGE ROUTING
# --------------------------------------------------------------------------

if st.session_state.page == "home":

    home()


elif st.session_state.page == "join":

    join()


elif st.session_state.page == "draw":

    draw_page()


elif st.session_state.page == "facilitator":

    facilitator()
