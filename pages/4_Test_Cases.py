import traceback
import streamlit as st
from core.database import init_db
from services.requirement_service import get_all_requirements
from services.testcase_service import (
    get_all_test_cases,
    create_test_cases_for_requirement,
    get_test_cases_by_requirement,
)

init_db()

if not st.session_state.get("authenticated"):
    st.warning("Please login first.")
    st.stop()

st.title("Test Cases")
st.markdown("AI-generated test cases from requirements.")

reqs = get_all_requirements()

if reqs:
    st.subheader("Generate Test Cases")
    req_options = {f"#{r['id']} — {r['title']} [{r['feature']}]": r for r in reqs}
    selected_label = st.selectbox("Select Requirement", list(req_options.keys()))
    selected_req = req_options[selected_label]

    if st.button("Generate Test Cases with AI", type="primary"):
        with st.spinner("Generating test cases..."):
            try:
                new_tcs = create_test_cases_for_requirement(selected_req)
                st.success(f"Generated {len(new_tcs)} test case(s)!")
            except Exception as e:
                st.error("Failed to generate test cases. Check your AI provider configuration.")
                with st.expander("Error details", expanded=True):
                    st.code(traceback.format_exc())

st.divider()

all_tcs = get_all_test_cases()
st.subheader(f"All Test Cases ({len(all_tcs)})")

if not all_tcs:
    st.info("No test cases yet. Select a requirement above and click 'Generate Test Cases with AI'.")
else:
    feature_filter = st.selectbox(
        "Filter by Feature",
        ["All"] + sorted(set(tc["feature"] for tc in all_tcs if tc["feature"])),
    )
    filtered = all_tcs if feature_filter == "All" else [tc for tc in all_tcs if tc["feature"] == feature_filter]

    for tc in filtered:
        type_icons = {"Functional": "✅", "Negative": "❌", "UI": "🖥️", "Performance": "⚡", "Security": "🔒"}
        icon = type_icons.get(tc["test_type"], "📋")
        with st.expander(f"{icon} [{tc['test_type']}] {tc['title']}"):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Priority:** {tc['priority']}")
            col_b.markdown(f"**Type:** {tc['test_type']}")
            col_c.markdown(f"**Req #:** {tc['requirement_id']}")
            if tc.get("preconditions"):
                st.markdown(f"**Preconditions:** {tc['preconditions']}")
            if tc.get("steps"):
                st.markdown(f"**Steps:**\n{tc['steps']}")
            if tc.get("expected_result"):
                st.markdown(f"**Expected Result:** {tc['expected_result']}")
            if tc.get("test_data"):
                st.markdown(f"**Test Data:** `{tc['test_data']}`")
