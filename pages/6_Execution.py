import streamlit as st
import pandas as pd
from core.database import init_db
from services.script_service import get_all_scripts
from services.execution_service import execute_script, get_all_runs

init_db()

if not st.session_state.get("authenticated"):
    st.warning("Please login first.")
    st.stop()

st.title("Test Execution")
st.markdown("Execute Playwright scripts and view results.")

scripts = get_all_scripts()

if not scripts:
    st.info("No scripts available. Generate scripts first from the Scripts page.")
else:
    st.subheader("Run a Script")
    script_options = {f"#{s['id']} — {s['title']} [{s['feature']}]": s for s in scripts}
    selected_label = st.selectbox("Select Script to Execute", list(script_options.keys()))
    selected_script = script_options[selected_label]

    if st.button("Execute Test", type="primary"):
        with st.spinner("Running test... this may take up to 2 minutes."):
            try:
                run = execute_script(selected_script["id"])
                if run["status"] == "passed":
                    st.success(f"Test PASSED in {run['duration_seconds']}s")
                elif run["status"] == "failed":
                    st.error(f"Test FAILED after {run['duration_seconds']}s")
                    st.info("Go to Failure Analysis page to analyze this failure.")
                else:
                    st.warning(f"Test ERROR after {run['duration_seconds']}s")

                if run.get("output"):
                    with st.expander("Test Output", expanded=True):
                        st.code(run["output"], language="text")
                if run.get("error_message"):
                    with st.expander("Error Details"):
                        st.code(run["error_message"], language="text")
            except FileNotFoundError:
                st.error("Script file not found on disk. It may have been deleted.")
            except ValueError:
                st.error("Invalid script path detected.")
            except Exception as e:
                st.error("Execution failed unexpectedly. Check server logs.")

st.divider()

runs = get_all_runs()
st.subheader(f"Run History ({len(runs)})")

if not runs:
    st.info("No test runs yet.")
else:
    df = pd.DataFrame(runs)
    display_cols = ["id", "test_name", "feature", "status", "duration_seconds", "started_at"]
    df = df[[c for c in display_cols if c in df.columns]]

    def color_status(val):
        colors = {"passed": "color: green", "failed": "color: red", "error": "color: orange", "running": "color: blue"}
        return colors.get(val, "")

    styled = df.style.applymap(color_status, subset=["status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
