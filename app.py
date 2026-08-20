import streamlit as st
from supabase import create_client
from scanner import scan
from datetime import datetime
import time

st.set_page_config(
    page_title="Nafees.Sarfraz BOT",
    page_icon="🚀",
    layout="wide"
)
# ==================================================
# SUPABASE AUTH
# ==================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

if "user" not in st.session_state:
    st.session_state.user = None


# ==================================================
# LOGIN / SIGN UP
# ==================================================

if st.session_state.user is None:

    st.title("🚀 Nafees.Sarfraz BOT")

    tab_login, tab_signup = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    with tab_login:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            key="login_button"
        ):

            try:

                response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.session_state.user = response.user

                st.success("Login successful!")
                st.rerun()

            except Exception as e:

                st.error(
                    f"Login failed: {e}"
                )


    with tab_signup:

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button(
            "📝 Create Account",
            key="signup_button"
        ):

            try:

                response = supabase.auth.sign_up(
                    {
                        "email": new_email,
                        "password": new_password
                    }
                )

                st.success(
                    "Account created successfully! "
                    "You can now login."
                )

            except Exception as e:

                st.error(
                    f"Sign Up failed: {e}"
                )


    st.stop()



# ==================================================
# SESSION STATE
# ==================================================

if "results" not in st.session_state:
    st.session_state.results = None

if "last_scan" not in st.session_state:
    st.session_state.last_scan = 0.0

if "scan_error" not in st.session_state:
    st.session_state.scan_error = None

if "history" not in st.session_state:
    st.session_state.history = []


# ==================================================
# SCANNER
# ==================================================

def run_scan():

    try:

        new_results = scan()

        st.session_state.results = new_results
        st.session_state.last_scan = time.time()
        st.session_state.scan_error = None

        snapshot = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "results": new_results
        }

        st.session_state.history.insert(
            0,
            snapshot
        )

        st.session_state.history = (
            st.session_state.history[:20]
        )

        return True

    except Exception as e:

        st.session_state.scan_error = str(e)

        return False


# ==================================================
# INITIAL SCAN
# ==================================================

if st.session_state.results is None:

    if not run_scan():

        st.error("Initial scanner error")
        st.error(st.session_state.scan_error)
        st.stop()


# ==================================================
# HEADER
# ==================================================

st.title("🚀 Nafees.Sarfraz BOT")

st.caption(
    "Signal-only mode — no automatic trades"
)
# ==================================================
# LOGGED-IN USER + LOGOUT
# ==================================================

if st.session_state.user:

    user_email = getattr(
        st.session_state.user,
        "email",
        None
    )

    if user_email:
        st.caption(f"👤 Logged in: {user_email}")

    if st.button("🚪 Sign Out"):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user = None
        st.rerun()

st.divider()


# ==================================================
# MANUAL REFRESH
# ==================================================

if st.button("🔄 Refresh Now"):

    if run_scan():
        st.rerun()


results = st.session_state.results


# ==================================================
# STRONGEST SIGNAL
# ==================================================

valid_results = [
    x for x in results
    if x.get("status") == "OK"
]

if valid_results:

    strongest = max(
        valid_results,
        key=lambda x: x["score"]
    )

    st.subheader("⭐ Strongest Signal")

    if strongest["signal"] == "UP":

        st.success(
            f"🟢 {strongest['pair']} | "
            f"UP | SCORE: {strongest['score']}"
        )

    elif strongest["signal"] == "DOWN":

        st.error(
            f"🔴 {strongest['pair']} | "
            f"DOWN | SCORE: {strongest['score']}"
        )

    else:

        st.info(
            f"⚪ {strongest['pair']} | "
            f"WAIT | SCORE: {strongest['score']}"
        )

else:

    st.warning("No valid signals available.")


st.divider()


# ==================================================
# LIVE SIGNALS
# ==================================================

st.subheader("📈 Live Forex Signals")

cols = st.columns(len(results))


for col, item in zip(cols, results):

    with col:

        pair = item.get("pair", "Unknown")
        signal = item.get("signal", "ERROR")
        score = item.get("score", 0)
        rsi = item.get("rsi")
        status = item.get("status", "ERROR")
        reasons = item.get("reasons", [])


        if signal == "UP":
            icon = "🟢"

        elif signal == "DOWN":
            icon = "🔴"

        else:
            icon = "⚪"


        st.markdown(f"### {pair}")

        st.markdown(
            f"# {icon} {signal}"
        )


        st.metric(
            "Score",
            score
        )


        if rsi is not None:

            st.metric(
                "RSI",
                f"{float(rsi):.2f}"
            )

        else:

            st.metric(
                "RSI",
                "N/A"
            )


        if status == "OK":

            st.success("● LIVE")

        else:

            st.error("● ERROR")


        st.markdown("**Signal Reasons**")


        if reasons:

            for reason in reasons:

                text = reason.lower()

                if (
                    "bullish" in text
                    or "positive" in text
                ):

                    st.write(
                        f"🟢 {reason}"
                    )

                elif (
                    "bearish" in text
                    or "negative" in text
                ):

                    st.write(
                        f"🔴 {reason}"
                    )

                else:

                    st.write(
                        f"⚪ {reason}"
                    )

        else:

            st.write(
                "No reasons available"
            )


# ==================================================
# LAST SCAN
# ==================================================

st.divider()

last_scan = datetime.fromtimestamp(
    st.session_state.last_scan
)

st.write(
    f"🕐 Last API scan: "
    f"**{last_scan.strftime('%H:%M:%S')}**"
)


# ==================================================
# AUTO COUNTDOWN + AUTO SCAN
# ==================================================

@st.fragment(run_every=1)
def countdown():

    elapsed = time.time() - st.session_state.last_scan

    seconds_left = max(
        0,
        60 - int(elapsed)
    )

    st.subheader(
        "⏱️ Next API Scan"
    )

    st.metric(
        "Refresh in",
        f"{seconds_left} seconds"
    )

    # ==============================================
    # AUTOMATIC SCAN AT 60 SECONDS
    # ==============================================

    if elapsed >= 60:

        if run_scan():

            st.rerun(scope="app")


countdown()


# ==================================================
# SIGNAL HISTORY
# ==================================================

st.divider()

st.subheader("📜 Signal History")

st.caption(
    "Last 20 completed scans — signal changes are highlighted."
)


if st.session_state.history:

    for index, entry in enumerate(
        st.session_state.history
    ):

        st.markdown(
            f"### 🕐 {entry['time']}"
        )

        history_cols = st.columns(5)


        previous_results = None

        if index + 1 < len(
            st.session_state.history
        ):

            previous_results = (
                st.session_state.history[
                    index + 1
                ]["results"]
            )


        for col, item in zip(
            history_cols,
            entry["results"]
        ):

            with col:

                pair = item.get(
                    "pair",
                    "Unknown"
                )

                signal = item.get(
                    "signal",
                    "ERROR"
                )

                score = item.get(
                    "score",
                    0
                )


                if signal == "UP":

                    icon = "🟢"

                elif signal == "DOWN":

                    icon = "🔴"

                else:

                    icon = "⚪"


                st.write(
                    f"{icon} **{pair}**"
                )

                st.write(
                    f"{signal} | {score}"
                )


                previous_signal = None


                if previous_results:

                    for old_item in previous_results:

                        if (
                            old_item.get("pair")
                            == pair
                        ):

                            previous_signal = (
                                old_item.get(
                                    "signal"
                                )
                            )

                            break


                if (
                    previous_signal is not None
                    and previous_signal != signal
                ):

                    st.warning(
                        f"🔄 {previous_signal} → {signal}"
                    )

                elif (
                    previous_signal is not None
                    and previous_signal == signal
                ):

                    st.caption(
                        "➡️ No signal change"
                    )

else:

    st.info(
        "No signal history yet."
    )


# ==================================================
# ERROR NOTICE
# ==================================================

if st.session_state.scan_error:

    st.warning(
        f"Last scan error: "
        f"{st.session_state.scan_error}"
    )


# ==================================================
# SAFETY NOTICE
# ==================================================

st.divider()

st.warning(
    "⚠️ This dashboard provides indicator-based "
    "signals only. A high score does not guarantee "
    "a profitable trade."
)

st.caption(
    "🔐 API key is loaded from .env and is never displayed."
)