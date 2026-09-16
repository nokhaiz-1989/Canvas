"""
OUTCOME DRAWING ICEBREAKER
--------------------------
A standalone warm-up exercise, separate from the OBE Level-Up pyramid game.

Teams draw a house with deliberately vague instructions and NO rubric.
When every team has submitted, the facilitator reveals a simple rubric
(1 door, 1 window, 1 chimney) live on the projector. Because teams never
saw the rubric while drawing, their houses vary wildly and rarely satisfy
it cleanly — which is the whole point: this is what happens when a
learning outcome isn't defined before the task begins.

Run with:
    streamlit run outcome_drawing_icebreaker.py

Needs one extra package beyond the base game:
    pip install "streamlit-drawable-canvas[image]"

Requires streamlit-drawable-canvas >= 0.10.0 and Streamlit >= 1.53. That
version made image_data opt-in on st_canvas() -- reading it without passing
return_image_data=True raises a RuntimeError, which is why the flag is set
explicitly below.
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import base64
import io

from streamlit_autorefresh import st_autorefresh
from streamlit_drawable_canvas import st_canvas
from PIL import Image

st.set_page_config(page_title="Draw the House", page_icon="🏠", layout="wide")

DEFAULT_TEAM_NAMES = {
    1: "Team Alpha",
    2: "Team Bravo",
    3: "Team Charlie",
    4: "Team Delta",
    5: "Team Echo",
    6: "Team Fifa",
}

# The rubric is intentionally never shown to teams before they draw.
# Change these freely — the exercise works with any short checklist.
RUBRIC = [
    "Exactly 1 door",
    "Exactly 1 window",
    "Exactly 1 chimney",
]

DRAW_SECONDS = 180  # 3-minute default drawing window
CANVAS_HEIGHT = 380
CANVAS_WIDTH = 460


def flat_html(s):
    """Collapse a pretty-printed, indented multi-line HTML string down to a
    single line with no leading whitespace on any part.

    st.markdown renders unsafe_allow_html content through a Markdown parser
    first, and Markdown treats a line indented 4+ spaces as a code block —
    a naturally-indented Python f-string trips that rule and prints raw
    HTML tags as literal text instead of rendering them. Flattening avoids
    it entirely.
    """
    return " ".join(line.strip() for line in s.strip().splitlines())


@st.cache_resource
def get_shared_state():
    """One object shared by every browser session, the same trick used in
    the pyramid game: st.session_state is per-device, so a team's drawing
    would never reach the facilitator's screen without this."""
    return {
        "start_time": None,      # set when facilitator starts the timer
        "rubric_revealed": False,
        "teams": {
            i: {
                "name": DEFAULT_TEAM_NAMES[i],
                "submitted": False,
                "image_b64": None,
                "marks": {item: None for item in RUBRIC},  # facilitator-judged
            }
            for i in range(1, 7)
        },
    }


state = get_shared_state()
teams = state["teams"]

if "page" not in st.session_state:
    st.session_state.page = "home"

if "team" not in st.session_state:
    st.session_state.team = None


def inject_css():
    st.markdown(
        flat_html("""
        <style>
        .block-container { max-width:100% !important; padding:1.2rem 2rem !important; }
        .ib-header {
            background:#101534; border-radius:16px; padding:16px 24px;
            margin-bottom:16px; text-align:center;
        }
        .ib-title {
            font-family:'Trebuchet MS', sans-serif; font-size:32px;
            font-weight:800; color:#FFFFFF; margin:0;
        }
        .ib-sub { font-size:15px; color:#98A2D8; margin-top:4px; }
        .timer-big {
            font-family:'Trebuchet MS', sans-serif; font-size:54px;
            font-weight:800; text-align:center; border-radius:16px;
            padding:10px; margin-bottom:14px;
        }
        .gallery-card {
            background:#FFFFFF; border:3px solid #101534; border-radius:14px;
            padding:10px; text-align:center; box-shadow:0 5px 0 #101534;
            margin-bottom:14px;
        }
        .gallery-name { font-weight:800; font-size:17px; color:#101534; margin-bottom:6px; }
        .gallery-empty {
            color:#ADB5BD; font-style:italic; padding:40px 0; font-size:15px;
        }
        .rubric-box {
            background:#FFF3BF; border:3px solid #F59F00; border-radius:16px;
            padding:18px 22px; margin-bottom:16px;
        }
        .rubric-title {
            font-family:'Trebuchet MS', sans-serif; font-size:22px;
            font-weight:800; color:#8A6100; margin-bottom:8px;
        }
        .rubric-item { font-size:19px; color:#5C4500; margin:4px 0; }
        .moral-box {
            background:#101534; color:#FFFFFF; border-radius:16px;
            padding:20px 26px; font-size:20px; line-height:1.55;
        }
        .tally-pill {
            display:inline-block; padding:4px 12px; border-radius:999px;
            font-size:14px; font-weight:800; margin:3px 4px 0 0;
        }
        </style>
        """),
        unsafe_allow_html=True
    )


def header(subtitle):
    st.markdown(
        flat_html(f"""
        <div class="ib-header">
            <div class="ib-title">🏠 DRAW THE HOUSE</div>
            <div class="ib-sub">{subtitle}</div>
        </div>
        """),
        unsafe_allow_html=True
    )


def image_from_canvas(image_data):
    """Convert the canvas RGBA numpy array to a base64 PNG for storage in
    the shared dict, so every browser (including the facilitator's) can
    display it without re-running any drawing code."""
    img = Image.fromarray(image_data.astype("uint8"), "RGBA")

    # Flatten onto white so transparent canvas background doesn't turn black
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img)

    buf = io.BytesIO()
    bg.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def celebrate_submit():
    components.html(
        """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/canvas-confetti/1.9.2/confetti.browser.min.js"></script>
        <script>
        (function () {
            function fire() {
                if (typeof confetti === 'function') {
                    confetti({particleCount: 90, spread: 80, origin: {y: 0.4}});
                } else { setTimeout(fire, 100); }
            }
            fire();
        })();
        </script>
        """,
        height=1,
    )


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def home():
    inject_css()
    header("A warm-up before we talk about learning outcomes")

    st.info(
        "Every team will draw a house. That's the only instruction you'll get "
        "right now. Once everyone submits, we'll reveal something you didn't "
        "know while drawing."
    )

    a, b = st.columns(2)

    with a:
        if st.button("🎨 JOIN AS TEAM", use_container_width=True, type="primary"):
            st.session_state.page = "join"
            st.rerun()

    with b:
        if st.button("📺 FACILITATOR VIEW", use_container_width=True):
            st.session_state.page = "facilitator"
            st.rerun()


def join():
    inject_css()
    header("Join the warm-up")

    team = st.selectbox("Select your team", [t["name"] for t in teams.values()])
    team_id = next(i for i, tm in teams.items() if tm["name"] == team)

    if st.button("ENTER", type="primary", use_container_width=True):
        st.session_state.team = team_id
        st.session_state.page = "draw"
        st.rerun()

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()


def time_left():
    if state["start_time"] is None:
        return None
    elapsed = time.time() - state["start_time"]
    return max(0, DRAW_SECONDS - elapsed)


def draw_page():
    inject_css()

    team_id = st.session_state.team
    t = teams[team_id]

    header(f"{t['name']} — draw a house. Go with your own style.")

    st_autorefresh(interval=1000, key="draw_timer_refresh")

    remaining = time_left()

    if remaining is None:
        st.markdown(
            flat_html("""
            <div class="timer-big" style="background:#E9ECEF;color:#868E96;">
                Waiting for the facilitator to start the timer
            </div>
            """),
            unsafe_allow_html=True
        )
    elif remaining > 0:
        mins, secs = divmod(int(remaining), 60)
        color = "#FFF3BF" if remaining > 30 else "#FFE3E3"
        text_color = "#8A6100" if remaining > 30 else "#C92A2A"
        st.markdown(
            flat_html(f"""
            <div class="timer-big" style="background:{color};color:{text_color};">
                ⏱ {mins:01d}:{secs:02d}
            </div>
            """),
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            flat_html("""
            <div class="timer-big" style="background:#FFE3E3;color:#C92A2A;">
                ⏱ TIME'S UP — submit what you have
            </div>
            """),
            unsafe_allow_html=True
        )

    if t["submitted"]:
        st.success("Your house is submitted. Sit tight for the reveal.")
        st.image(
            Image.open(io.BytesIO(base64.b64decode(t["image_b64"]))),
            width=CANVAS_WIDTH
        )

        if st.button("↺ Redraw (clears your submission)"):
            t["submitted"] = False
            t["image_b64"] = None
            st.rerun()

    else:
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=4,
            stroke_color="#101534",
            background_color="#FFFFFF",
            height=CANVAS_HEIGHT,
            width=CANVAS_WIDTH,
            drawing_mode="freedraw",
            return_image_data=True,  # required since streamlit-drawable-canvas 0.10.0,
                                      # otherwise reading .image_data raises RuntimeError
            key=f"canvas_{team_id}",
        )

        if st.button("🚀 Submit my house", type="primary", use_container_width=True):

            if canvas_result.image_data is not None:
                t["image_b64"] = image_from_canvas(canvas_result.image_data)
                t["submitted"] = True
                celebrate_submit()
                st.rerun()
            else:
                st.warning("Draw something first!")

    if st.button("← Leave"):
        st.session_state.page = "home"
        st.rerun()


def facilitator():
    inject_css()
    st_autorefresh(interval=2000, key="facilitator_refresh")

    header("Facilitator view — live gallery and rubric reveal")

    remaining = time_left()

    c1, c2, c3 = st.columns(3)

    with c1:
        if state["start_time"] is None:
            if st.button("▶ Start 3-minute timer", type="primary", use_container_width=True):
                state["start_time"] = time.time()
                st.rerun()
        else:
            if st.button("↺ Reset timer", use_container_width=True):
                state["start_time"] = None
                st.rerun()

    with c2:
        submitted_count = sum(1 for tm in teams.values() if tm["submitted"])
        st.metric("Submitted", f"{submitted_count} / {len(teams)}")

    with c3:
        if remaining is not None:
            mins, secs = divmod(int(remaining), 60)
            label = f"{mins:01d}:{secs:02d}" if remaining > 0 else "Time's up"
            st.metric("Time left", label)
        else:
            st.metric("Time left", "—")

    st.divider()

    # ---- Live gallery ----
    st.subheader("🖼️ Live gallery")

    cols = st.columns(3)

    for idx, (i, t) in enumerate(teams.items()):
        with cols[idx % 3]:
            if t["submitted"]:
                st.markdown(
                    f"<div class='gallery-card'><div class='gallery-name'>{t['name']}</div>",
                    unsafe_allow_html=True
                )
                st.image(
                    Image.open(io.BytesIO(base64.b64decode(t["image_b64"]))),
                    use_container_width=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    flat_html(f"""
                    <div class="gallery-card">
                        <div class="gallery-name">{t['name']}</div>
                        <div class="gallery-empty">Still drawing…</div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

    st.divider()

    # ---- Rubric reveal ----
    # Nothing here names "rubric" or hints one exists until the facilitator
    # actually clicks reveal -- this section stays projector-safe.

    if not state["rubric_revealed"]:

        submitted_count = sum(1 for tm in teams.values() if tm["submitted"])

        if submitted_count < len(teams):
            st.caption(
                f"Waiting on {len(teams) - submitted_count} more team(s) "
                "before moving on."
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
        st.subheader("📋 The rubric nobody saw")
        st.markdown(
            flat_html(f"""
            <div class="rubric-box">
                <div class="rubric-title">The rubric was:</div>
                {"".join(f"<div class='rubric-item'>✔ {item}</div>" for item in RUBRIC)}
            </div>
            """),
            unsafe_allow_html=True
        )

        st.caption(
            "For each team's drawing, mark whether it happens to meet each "
            "rubric item — this is for discussion, judged by eye, not auto-graded."
        )

        full_match = 0
        judged = 0

        for i, t in teams.items():

            if not t["submitted"]:
                continue

            with st.expander(f"{t['name']}", expanded=False):

                left, right = st.columns([1, 1])

                with left:
                    st.image(
                        Image.open(io.BytesIO(base64.b64decode(t["image_b64"]))),
                        use_container_width=True
                    )

                with right:
                    hits = 0
                    any_judged = False

                    for item in RUBRIC:
                        current = t["marks"][item]
                        choice = st.radio(
                            item,
                            ["Not judged", "✅ Meets it", "❌ Misses it"],
                            index={"Not judged": 0, True: 1, False: 2}.get(
                                "Not judged" if current is None else current, 0
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

        if judged:
            st.markdown(
                flat_html(f"""
                <div class="moral-box">
                    <b>{full_match} of {judged} judged teams</b> happened to satisfy
                    every rubric item — purely by chance, since nobody knew the
                    rubric while drawing. Notice how different the houses look
                    even though every team heard the exact same instruction.
                    <br><br>
                    This is what happens when a learning outcome isn't defined
                    <i>before</i> the activity starts: effort and creativity go
                    into the task, but not necessarily toward the thing that
                    will actually be assessed. Aligning the outcome, the
                    activity, and the assessment — in that order — is what the
                    rest of today's game is about.
                </div>
                """),
                unsafe_allow_html=True
            )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with c2:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


def reset_all():
    state["start_time"] = None
    state["rubric_revealed"] = False

    for i in range(1, 7):
        teams[i].update({
            "name": DEFAULT_TEAM_NAMES[i],
            "submitted": False,
            "image_b64": None,
            "marks": {item: None for item in RUBRIC},
        })


if st.session_state.page == "home":
    home()

elif st.session_state.page == "join":
    join()

elif st.session_state.page == "draw":
    draw_page()

elif st.session_state.page == "facilitator":
    facilitator()
