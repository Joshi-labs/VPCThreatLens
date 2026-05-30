import streamlit as st
import subprocess

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(

    page_title="AI SOC Analyst",

    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------

st.title("🛡️ AI SOC Analyst")

st.markdown(
    "Natural Language Security Investigation System"
)

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Example Queries")

examples = [

    "show high severity ssh attacks",

    "what happened between 12:10 and 12:20",

    "find suspicious traffic",

    "show rejected activity",

    "find port scanning activity"
]

for ex in examples:

    st.sidebar.code(ex)

# -----------------------------
# INPUT
# -----------------------------

query = st.text_input(
    "Enter Investigation Query"
)

# -----------------------------
# BUTTON
# -----------------------------

if st.button("Run Investigation"):

    if query.strip() == "":

        st.warning(
            "Please enter query"
        )

    else:

        with st.spinner(
            "Running investigation..."
        ):

            result = subprocess.run(

                [
                    r".\.venv\Scripts\python.exe",
                    "agentic_query.py"
                ],

                input=query,

                text=True,

                capture_output=True
            )

        # -----------------------------
        # STDOUT
        # -----------------------------

        st.subheader("STDOUT")

        st.code(
            result.stdout,
            language="text"
        )

        # -----------------------------
        # STDERR
        # -----------------------------

        if result.stderr:

            st.subheader("ERRORS")

            st.code(
                result.stderr,
                language="text"
            )

        # -----------------------------
        # RETURN CODE
        # -----------------------------

        st.subheader("RETURN CODE")

        st.write(
            result.returncode
        )