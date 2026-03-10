import traceback
import streamlit as st
from core.database import init_db
from services.requirement_service import get_all_requirements, create_requirements_from_text
from services.testcase_service import create_test_cases_for_requirement, get_test_cases_by_requirement
from services.script_service import create_script_for_test_case, get_all_scripts
from services.execution_service import execute_script

init_db()

if not st.session_state.get("authenticated"):
    st.warning("Please login first.")
    st.stop()

st.title("AI Pipeline")
st.markdown("Run the full AI pipeline: Requirements → Test Cases → Scripts → Execution")

FEATURES = ["Login", "Inventory", "ProductDetail", "Cart", "Checkout", "Navigation"]

feature = st.selectbox("Select Feature to Pipeline", FEATURES)

FEATURE_REQUIREMENTS = {
    "Login": "Users must be able to login with valid and invalid credentials. Locked out users should see error messages.",
    "Inventory": "Products page should display all items with sorting by name and price. Users can add and remove cart items.",
    "ProductDetail": "Individual product pages should show name, description, price, and image. Users can add to cart from detail page.",
    "Cart": "Cart should show all added items, allow removal, and display correct totals. Cart badge count should update.",
    "Checkout": "Checkout requires first name, last name, and zip code. Order summary should show correct items and totals.",
    "Navigation": "Navigation menu should allow logout, reset app state. Navigation between pages should work correctly.",
}

if st.button("Run Full Pipeline", type="primary"):
    req_text = FEATURE_REQUIREMENTS.get(feature, f"Test the {feature} feature of SauceDemo.")

    log_container = st.container()

    with log_container:
        # Step 1: Parse Requirements
        with st.status(f"Step 1/5: Parsing requirements for {feature}...", expanded=True) as status:
            try:
                reqs = create_requirements_from_text(req_text)
                status.update(label=f"Step 1/5: Requirements parsed ({len(reqs)} found)", state="complete")
                st.write(f"Created {len(reqs)} requirement(s)")
            except Exception as e:
                status.update(label="Step 1/5: Failed to parse requirements", state="error")
                st.error(f"Requirement parsing failed: {type(e).__name__}")
                st.code(traceback.format_exc())
                st.stop()

        req = reqs[0] if reqs else None
        if not req:
            st.error("No requirements generated.")
            st.stop()

        # Step 2: Generate Test Cases
        with st.status("Step 2/5: Generating test cases...", expanded=True) as status:
            try:
                tcs = create_test_cases_for_requirement(req)
                status.update(label=f"Step 2/5: Test cases generated ({len(tcs)} found)", state="complete")
                st.write(f"Created {len(tcs)} test case(s)")
            except Exception as e:
                status.update(label="Step 2/5: Failed to generate test cases", state="error")
                st.error(f"Test case generation failed: {type(e).__name__}")
                st.code(traceback.format_exc())
                st.stop()

        tc = tcs[0] if tcs else None
        if not tc:
            st.error("No test cases generated.")
            st.stop()

        # Step 3: Generate Script
        with st.status("Step 3/5: Generating Playwright script...", expanded=True) as status:
            try:
                script = create_script_for_test_case(req, tc)
                status.update(label="Step 3/5: Script generated", state="complete")
                st.write(f"Script saved: {script['script_path']}")
            except Exception as e:
                status.update(label="Step 3/5: Failed to generate script", state="error")
                st.error(f"Script generation failed: {type(e).__name__}")
                st.code(traceback.format_exc())
                st.stop()

        # Step 4: Execute Script
        with st.status("Step 4/5: Executing test...", expanded=True) as status:
            try:
                run = execute_script(script["id"])
                state = "complete" if run["status"] == "passed" else "error"
                status.update(label=f"Step 4/5: Execution {run['status']} ({run['duration_seconds']}s)", state=state)
                st.write(f"Status: **{run['status']}**")
                if run.get("output"):
                    st.code(run["output"][:2000], language="text")
            except Exception as e:
                status.update(label="Step 4/5: Execution error", state="error")
                st.error(f"Execution failed: {type(e).__name__}")
                st.code(traceback.format_exc())
                run = None

        # Step 5: Summary
        with st.status("Step 5/5: Pipeline complete", expanded=False) as status:
            status.update(label="Step 5/5: Pipeline complete", state="complete")

    st.success(f"Pipeline finished for **{feature}** feature!")
    st.markdown(f"""
**Results:**
- Requirements: {len(reqs)}
- Test Cases: {len(tcs)}
- Script: `{script['title']}`
- Execution: {run['status'] if run else 'N/A'}
""")

    if run and run["status"] != "passed":
        st.info("Go to **Failure Analysis** page to analyze this test failure.")
