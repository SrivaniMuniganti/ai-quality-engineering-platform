import traceback
import streamlit as st
from core.database import init_db
from services.requirement_service import get_requirement_by_id
from services.testcase_service import get_test_case_by_id, get_all_test_cases
from services.script_service import get_all_scripts, create_script_for_test_case

init_db()

if not st.session_state.get("authenticated"):
    st.warning("Please login first.")
    st.stop()

st.title("Scripts")
st.markdown("AI-generated Playwright + pytest automation scripts.")

all_tcs = get_all_test_cases()

if all_tcs:
    st.subheader("Generate Script")
    tc_options = {f"#{tc['id']} — {tc['title']} [{tc['feature']}]": tc for tc in all_tcs}
    selected_label = st.selectbox("Select Test Case", list(tc_options.keys()))
    selected_tc = tc_options[selected_label]

    if st.button("Generate Playwright Script with AI", type="primary"):
        req = get_requirement_by_id(selected_tc["requirement_id"])
        if not req:
            st.error("Associated requirement not found.")
        else:
            with st.spinner("Generating Playwright script..."):
                try:
                    script = create_script_for_test_case(req, selected_tc)
                    st.success(f"Script generated and saved to: `{script['script_path']}`")
                except ValueError as e:
                    st.error(f"Script validation failed: script must start with import statements.")
                except Exception as e:
                    st.error("Failed to generate script. Check your AI provider configuration.")
                    with st.expander("Error details", expanded=True):
                        st.code(traceback.format_exc())

st.divider()

scripts = get_all_scripts()
st.subheader(f"All Scripts ({len(scripts)})")

if not scripts:
    st.info("No scripts yet. Select a test case above and click 'Generate Playwright Script with AI'.")
else:
    feature_filter = st.selectbox(
        "Filter by Feature",
        ["All"] + sorted(set(s["feature"] for s in scripts if s["feature"])),
    )
    filtered = scripts if feature_filter == "All" else [s for s in scripts if s["feature"] == feature_filter]

    for script in filtered:
        with st.expander(f"[{script['feature']}] {script['title']} (ID: {script['id']})"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**Path:** `{script['script_path']}`")
                st.markdown(f"**Created:** {script['created_at']}")
            with col_b:
                st.download_button(
                    label="Download .py",
                    data=script["script_content"],
                    file_name=f"test_{script['id']}_{script['feature'].lower()}.py",
                    mime="text/x-python",
                    key=f"dl_{script['id']}",
                )
            st.code(script["script_content"], language="python")
