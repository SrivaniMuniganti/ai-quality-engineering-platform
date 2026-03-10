import streamlit as st
import pandas as pd
from core.database import init_db
from services.execution_service import get_all_runs
from services.healing_service import attempt_self_heal, get_all_healing_attempts, get_healing_stats

init_db()

if not st.session_state.get("authenticated"):
    st.warning("Please login first.")
    st.stop()

st.title("Self-Healing Engine")
st.markdown("AI-powered test locator healing for failed Playwright tests.")

tab1, tab2, tab3 = st.tabs(["Heal a Failed Test", "Healing History", "Healing Stats"])

# ── Tab 1: Heal a Failed Test ──────────────────────────────────────────────
with tab1:
    st.subheader("Select a failed test run to heal")

    all_runs = get_all_runs()
    failed_runs = [r for r in all_runs if r["status"] in ("failed", "error")]

    if not failed_runs:
        st.info("No failed test runs found. Execute some scripts first.")
    else:
        options = {f"Run #{r['id']} — {r['test_name']} ({r['status']})": r["id"] for r in failed_runs}
        selected_label = st.selectbox("Failed Run", list(options.keys()))
        selected_run_id = options[selected_label]

        run_detail = next((r for r in failed_runs if r["id"] == selected_run_id), None)
        if run_detail:
            with st.expander("Failure Output", expanded=False):
                st.code(run_detail.get("output") or run_detail.get("error_message") or "No output", language="text")

        if st.button("Attempt Self-Heal", type="primary"):
            with st.spinner("Analysing DOM and generating healed locators..."):
                try:
                    result = attempt_self_heal(selected_run_id)

                    if result["status"] == "healed":
                        st.success(f"Successfully healed! New run status: {result.get('new_run', {}).get('status', 'unknown')}")
                    elif result["status"] == "skipped":
                        st.warning(f"Skipped: {result.get('reason', '')}")
                    else:
                        st.error("Healing attempt failed — could not produce a passing run.")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Locator", result.get("original_locator", "N/A"))
                    col2.metric("Confidence", f"{result.get('confidence', 0):.0%}")
                    col3.metric("Strategy", result.get("strategy", "N/A"))

                    if result.get("alternatives"):
                        st.markdown("**Suggested Alternatives:**")
                        for i, alt in enumerate(result["alternatives"], 1):
                            st.code(alt, language="css")

                    if result.get("explanation"):
                        st.info(result["explanation"])

                except Exception as e:
                    st.error(f"Self-healing error: {e}")
                    import traceback
                    with st.expander("Error details"):
                        st.code(traceback.format_exc())

# ── Tab 2: Healing History ─────────────────────────────────────────────────
with tab2:
    st.subheader("Healing Attempt History")
    attempts = get_all_healing_attempts()

    if not attempts:
        st.info("No healing attempts yet. Use the 'Heal a Failed Test' tab.")
    else:
        df = pd.DataFrame(attempts)
        display_cols = ["id", "run_id", "test_name", "original_locator", "healing_strategy", "status", "confidence_score", "created_at"]
        df = df[[c for c in display_cols if c in df.columns]]
        df.columns = [c.replace("_", " ").title() for c in df.columns]

        status_emoji = {"healed": "✅", "failed": "❌", "skipped": "⏭️"}
        if "Status" in df.columns:
            df["Status"] = df["Status"].map(lambda s: f"{status_emoji.get(s, '')} {s}")

        st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab 3: Healing Stats ───────────────────────────────────────────────────
with tab3:
    st.subheader("Self-Healing Statistics")
    stats = get_healing_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Attempts", stats["total"])
    col2.metric("Successfully Healed", stats["healed"])
    col3.metric("Success Rate", f"{stats['success_rate']}%")
    col4.metric("Avg Confidence", f"{stats['avg_confidence']:.0%}")

    if stats["total"] > 0:
        import plotly.express as px
        fig = px.pie(
            values=[stats["healed"], stats["failed"], stats["skipped"]],
            names=["Healed", "Failed", "Skipped"],
            color_discrete_map={"Healed": "#22c55e", "Failed": "#ef4444", "Skipped": "#f97316"},
            hole=0.4,
            title="Healing Outcome Distribution",
        )
        fig.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run some healing attempts to see statistics here.")
