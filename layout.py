import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Economic Mobility Dashboard")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data('C:/Users/Mark Crisci/Downloads/dream_92.csv')

# --- Sidebar Configs ---
st.sidebar.header("Dashboard Controls")
years = sorted(df['year'].unique())
years_with_all = ['All years'] + years
quintile_options = ["lowest", "second", "third", "fourth", "top"]
comp_options = ["Exact", "No higher than", "No lower than"]

start_year = st.sidebar.selectbox("Start Year (Childhood):", years_with_all)
start_quintile_comp = st.sidebar.selectbox("Start Quintile Comparison:", comp_options)
start_quintile = st.sidebar.selectbox("Start Quintile (Childhood):", quintile_options)
goal_quintile_comp = st.sidebar.selectbox("Goal Quintile Comparison:", comp_options)
goal_quintile = st.sidebar.selectbox("Goal Quintile:", quintile_options, index=4)
time_horizon = st.sidebar.number_input("Time Horizon (years):", 1, 40, 10)
consec_years = st.sidebar.number_input("Consecutive Years in Goal Quintile:", 1, 25, 3)

# --- Helper Functions ---
def get_quintile_range(q, comp):
    idx = quintile_options.index(q)
    if comp == "Exact":
        return [q]
    elif comp == "No higher than":
        return quintile_options[:idx + 1]
    else:  # "No lower than"
        return quintile_options[idx:]

# === NEW: Correct survey year windowing function from Script 1 ===
def get_consecutive_available_years(start_from, consec, available_years):
    sorted_years = sorted(available_years)
    if start_from not in sorted_years:
        sorted_years.append(start_from)
        sorted_years = sorted(sorted_years)
    idx = sorted_years.index(start_from)
    next_years = sorted_years[idx + 1:idx + 1 + consec]
    return next_years

# === NEW: robust_achievers from Script 1 ===
@st.cache_data
def robust_achievers(df, start_range, goal_range, horizon, consec, start_year=None):
    df_filtered = df[df['quintile_label'].isin(quintile_options)].sort_values(["family_person", "year"])
    achievers_info = {}  # Stores {pid: first_achieving_sy_found}
    valid = set()  # Stores PIDs that are potential starters (denominator)

    for pid, group in df_filtered.groupby("family_person"):
        years = group['year'].values
        quintiles = group['quintile_label'].values

        # SPECIFIC START YEAR scenario:
        if start_year is not None:
            if start_year in years:
                idx = np.where(years == start_year)[0][0]
                if quintiles[idx] in start_range:
                    end_year = start_year + horizon + consec - 1
                    if years[-1] >= end_year:
                        valid.add(pid)  # Add to denominator if potential starter
                        goal_years = get_consecutive_available_years(start_year + horizon - 1, consec, years)
                        goal_mask = np.isin(years, goal_years)
                        if goal_mask.sum() == consec and all(q in goal_range for q in quintiles[goal_mask]):
                            achievers_info[pid] = start_year  # Store the specific start_year

        # ALL YEARS scenario:
        else:
            person_is_potential_starter_candidate = False

            for idx, sy in enumerate(years):
                if quintiles[idx] in start_range:
                    end_year = sy + horizon + consec - 1
                    if years[-1] >= end_year:
                        person_is_potential_starter_candidate = True  # Has at least one starting point with enough data
                        goal_years = get_consecutive_available_years(sy + horizon - 1, consec, years)
                        mask_goal_years_exist = np.isin(years, goal_years)
                        if mask_goal_years_exist.sum() == consec and all(q in goal_range for q in quintiles[mask_goal_years_exist]):
                            if pid not in achievers_info:
                                achievers_info[pid] = sy
            if person_is_potential_starter_candidate:
                valid.add(pid)
    return list(achievers_info.keys()), len(achievers_info), len(valid), achievers_info

# --- Everything else remains the same except for replacing calls/logic to use above robust functions. ---

def ever_reached_goal(df, start_range, goal_range):
    reached = 0
    total = 0
    reached_ids = []

    df_filtered = df[df['quintile_label'].isin(quintile_options)]
    for pid, group in df_filtered.groupby("family_person"):
        quintiles = group.sort_values("year")['quintile_label'].values
        if any(q in start_range for q in quintiles):
            total += 1
            if any(q in goal_range for q in quintiles):
                reached += 1
                reached_ids.append(pid)
    return reached, total, reached_ids

# --- Tab Layout ---
tabs = st.tabs([
    "Mobility Calculator",
    "Matrix Check",
    "Income Trends",
    "Income Trends: Mean, Median & Std Dev",
    "Ever Reached Comparison (Early vs Later Years)",
    "Multi-Person Income Trajectories"
])

# ====================== TAB 1: Mobility Calculator ====================== #
with tabs[0]:
    st.title("The American Dream: An Economic Mobility Dashboard")

    start_range = get_quintile_range(start_quintile, start_quintile_comp)
    goal_range = get_quintile_range(goal_quintile, goal_quintile_comp)

    if start_year == "All years":
        result = robust_achievers(df, start_range, goal_range, time_horizon, consec_years, start_year=None)
    else:
        result = robust_achievers(df, start_range, goal_range, time_horizon, consec_years, start_year=int(start_year))

    achiever_ids, n_achievers, n_total, achievers_map = result

    if n_total == 0:
        st.warning("No valid cases found for these criteria.")
    else:
        st.success(f"Probability: {n_achievers / n_total:.2%} ({n_achievers}/{n_total})")
        st.info(f"Achiever IDs (first 20): {achiever_ids[:20]}")

    if achiever_ids:
        st.subheader("Individual Mobility Trajectory")
        plot_id = st.selectbox("Select an individual ID to plot trajectory:", achiever_ids, index=0)
        col1, col2 = st.columns([4, 1])

        with col2:
            plot_yaxis = st.radio("Plot y-axis:", ["Quintile (1–5)", "head_labor_income"], index=0)

        person_data = df[(df['family_person'] == plot_id) & (df['head_labor_income'] > 0)].copy()
        person_data = person_data.sort_values("year")
        person_data['quintile_num'] = person_data['quintile_label'].map({
            'lowest': 1, 'second': 2, 'third': 3, 'fourth': 4, 'top': 5
        })

        yvar = 'quintile_num' if plot_yaxis == "Quintile (1–5)" else 'head_labor_income'
        ytitle = "Income Quintile (1=Lowest, 5=Top)" if yvar == "quintile_num" else "Head Labor Income ($)"

        fig = px.line(person_data, x="year", y=yvar,
                      title=f"Trajectory for ID {plot_id}", markers=True)
        if yvar == "quintile_num":
            fig.update_yaxes(title=ytitle, tickmode='linear', dtick=1)
        else:
            fig.update_yaxes(title=ytitle, tickformat=",", rangemode="tozero", showgrid=True)

        # --- Highlight Goal Window Years Only If Present ---
        sy_to_plot = achievers_map.get(plot_id)
        if sy_to_plot is not None:
            years_arr = person_data["year"].values
            quintiles_arr = person_data["quintile_label"].values
            goal_years = get_consecutive_available_years(sy_to_plot + time_horizon - 1, consec_years, years_arr)
            mask = np.isin(years_arr, goal_years)
            if mask.sum() == consec_years and np.all([q in goal_range for q in quintiles_arr[mask]]):
                fig.add_vline(x=sy_to_plot, line_dash="dash", line_color="green", annotation_text="Start", annotation_position="top left")
                fig.add_vline(x=sy_to_plot + time_horizon, line_dash="dash", line_color="orange", annotation_text="Time Horizon", annotation_position="top right")
                goal_vals = person_data[person_data['year'].isin(goal_years)][yvar]
                fig.add_scatter(
                    x=goal_years,
                    y=goal_vals,
                    mode="markers",
                    marker=dict(symbol='x', color="red", size=14),
                    name="Goal Years"
                )
            else:
                st.info(
                    f"Selected individual {plot_id} was identified as an achiever, but their specific achievement path starting in {sy_to_plot} could not be fully visualized with the current plotting criteria. This might occur due to subtle data gaps or if a different achievement path was the basis for their inclusion.")
        else:
            st.info("Selected individual does not have a trajectory that fits the chosen criteria.")

        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # --- Optional: Secondary Reach Probability ---
        reached, total_starting, reached_ids = ever_reached_goal(df, start_range, goal_range)
        if total_starting > 0:
            st.info(f"🔄 Ever Reached Goal (Even Once): {reached / total_starting:.2%} ({reached}/{total_starting})")
            with st.expander("IDs Who Ever Reached Goal (first 20)", expanded=False):
                st.write(reached_ids[:20])

    # --- Debugging Section for Verification ---
    with st.expander("🔎 DEBUG: Verify Achiever Logic for Selected ID", expanded=False):
        if achiever_ids:
            selected_debug_id = st.selectbox("Select ID to verify logic:", achiever_ids, key="debug_id")
            debug_data = df[df['family_person'] == selected_debug_id].sort_values("year")
            st.write("Full Quintile History:")
            st.dataframe(debug_data[['year', 'quintile_label']])

            debug_sy = achievers_map.get(selected_debug_id)
            st.markdown(f"**Start Year:** {debug_sy}  ")
            st.markdown(f"**Time Horizon:** {time_horizon}  → Checking from: `{debug_sy + time_horizon}`")

            person_years = debug_data['year'].values
            person_quintiles = debug_data['quintile_label'].values
            goal_years = get_consecutive_available_years(debug_sy + time_horizon - 1, consec_years, person_years)

            st.markdown(f"**Goal Years Window (Next {consec_years} available):** {goal_years}")

            if len(goal_years) >= consec_years:
                mask = np.isin(person_years, goal_years)
                q_slice = person_quintiles[mask]
                st.markdown("**Observed Quintiles in Goal Window:**")
                for y, q in zip(goal_years, q_slice):
                    st.markdown(f"- {y}: {q}")

                if all(q in goal_range for q in q_slice):
                    st.success("✅ Achiever logic confirmed — all goal years in required quintile.")
                else:
                    st.error("❌ Achiever flagged, but not all goal years match goal quintile.")
            else:
                st.warning("⚠️ Not enough available survey years after horizon to verify.")

    with st.expander("Explanation of how robust mobility probability is calculated (method/math)", expanded=False):
        st.markdown("""
**Robust Mobility Probability Calculation:**
- For a chosen starting quintile and year, we find all individuals in the dataset who were in that quintile and year.
- We track those same individuals to a future year (based on the selected time horizon) and require they remain in the target quintile for **consecutive years**, as defined by the **robustness window** parameter.
- The **robustness window** sets the number of consecutive years an individual must stay in the goal quintile for their transition to count as robust.

- The probability is:
""")
        st.latex(
            r"P(\text{Robust Mobility}) = \frac{\text{Achieved and sustained for N years}}{\text{Eligible starters}}")
        st.markdown("""
This is an **empirical estimate** of conditional probability using real PSID longitudinal data.
       """)

# --- Tabs 1, 2, 3 (Matrix Check, Income Trends, Mean/Median/Std Dev) remain as in your Script 2 ---

# ============= TAB 4: Ever Reached Comparison (Early vs Later Years) ============= #
with tabs[4]:
    st.header("Ever Reached Goal: Early vs. Later Periods (1968–1995 vs 1996–2022)")

    ever_calc_mode = st.selectbox(
        "Calculation Method:",
        [
            "Ever Reached (Plain)",
            "Robust Mobility (Consecutive Years & Horizon)"
        ]
    )

    start_range = get_quintile_range(start_quintile, start_quintile_comp)
    goal_range = get_quintile_range(goal_quintile, goal_quintile_comp)

    early_period = (1968, 1995)
    late_period = (1996, 2022)

    # --- Calculation per method ---
    if ever_calc_mode == "Ever Reached (Plain)":
        reached_early, total_early, _ = ever_reached_goal(df[df['year'].between(*early_period)], start_range, goal_range)
        reached_late, total_late, _ = ever_reached_goal(df[df['year'].between(*late_period)], start_range, goal_range)
        explanation = (
            "Counts anyone who was *ever* observed in the start range, "
            "and at *any* point also observed in the goal range."
        )
    elif ever_calc_mode == "Robust Mobility (Consecutive Years & Horizon)":
        # Use improved robust_achievers for each period
        _, n_achievers_early, n_total_early, _ = robust_achievers(
            df[df['year'].between(*early_period)], start_range, goal_range,
            time_horizon, consec_years)
        _, n_achievers_late, n_total_late, _ = robust_achievers(
            df[df['year'].between(*late_period)], start_range, goal_range,
            time_horizon, consec_years)
        reached_early, total_early = n_achievers_early, n_total_early
        reached_late, total_late = n_achievers_late, n_total_late
        explanation = (
            f"Requires being in the start range, then reaching and remaining in the goal range "
            f"for **{consec_years} consecutive survey years** after a horizon of {time_horizon} years. "
            "Reflects robust mobility, not just one-time movement."
        )
    else:
        reached_early = total_early = reached_late = total_late = 0
        explanation = "Invalid selection."

    # --- Metrics and Plotting ---
    if total_early == 0 and total_late == 0:
        st.warning("No valid individuals found in either period.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("1968–1995", f"{reached_early / total_early:.2%}" if total_early else "N/A", f"{reached_early}/{total_early}")
        with col2:
            st.metric("1996–2022", f"{reached_late / total_late:.2%}" if total_late else "N/A", f"{reached_late}/{total_late}")

        results_df = pd.DataFrame({
            "Period": ["1968–1995", "1996–2022"],
            "Reached Goal (%)": [
                reached_early / total_early * 100 if total_early else 0,
                reached_late / total_late * 100 if total_late else 0
            ]
        })

        fig = px.bar(
            results_df,
            x="Period",
            y="Reached Goal (%)",
            text="Reached Goal (%)",
            color="Period",
            color_discrete_map={
                "1968–1995": "#1f77b4",
                "1996–2022": "#d62728"
            },
            title="% Ever Reached Goal Quintile (Calculation Method: " + ever_calc_mode + ")",
            labels={"Reached Goal (%)": "% Reached Goal"},
            template="plotly_white"
        )
        fig.update_traces(texttemplate='%{text:.2f}%', textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.info(f"**Calculation Explanation:** {explanation}")



# ========== TAB 5: Multi-Person Income Trajectories ========== #
with tabs[5]:
    st.header("Multi-Person Income Trajectories")

    # Option to filter by year range, if desired:
    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider("Select year range to display:", min_value=year_min, max_value=year_max,
                           value=(year_min, year_max), step=1)

    # Filter the dataframe for the selected year range:
    df_range = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()

    # Multi-select box for up to 10 IDs:
    available_ids = df_range['family_person'].unique()
    default_ids = list(available_ids[:3])  # or random sample
    selected_ids = st.multiselect(
        "Select up to 10 individual IDs to visualize:",
        options=available_ids,
        default=default_ids,
        max_selections=10
    )

    if selected_ids:
        df_plot = df_range[df_range['family_person'].isin(selected_ids)].copy()
        fig = px.line(
            df_plot,
            x="year",
            y="head_labor_income",
            color="family_person",
            line_group="family_person",
            markers=True,
            title="Head Labor Income Trajectories",
            labels={"head_labor_income": "Head Labor Income ($)", "year": "Year", "family_person": "Individual ID"},
            template="plotly_white"
        )
        fig.update_layout(
            yaxis_title="Head Labor Income ($)",
            xaxis_title="Year",
            legend_title_text="ID",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one ID to display income trajectories.")

    with st.expander("How to use this tab"):
        st.markdown(
            "- **Select up to 10 people** to visualize their income journeys.\n"
            "- Use the slider to restrict the year range shown.\n"
            "- Useful for exploring heterogeneity in income dynamics."
        )


# --- Footer ---
st.markdown("---")
st.markdown(
    "**DISCLAIMER:** The information contained in this dashboard reflects average probabilities and should not be interpreted in absolute terms. Life is not always easy and hardwork will always improve your odds of success. Certainly, anything can happen 😊! However, in this pursuit it is imperative to maintain selfless community values to support and promote a society with high 'neighborhood quality' avoid rampant individualism that historical ensured inequalities persisted. One may define rampant individualism as a society's collective proclivity to pursue an undefinable, subjective, and continually-changing view of success—independent of help—fueled by the notion that America is rich in opportunity and success is limitless; the absence of opportunity combined with rampant individualism, however, ensures issues persist, and a large portion population is unable to compete in the capitalist system (Chetty, p ,2024). By and large, most Americans still believe that success is the product of individual effort. The myth that hard work will allow anyone to overcome even the most difficult circumstances has endured across the centuries—even in the face of evidence to the contrary. Though this ‘boot-strap’ mentality is not entirely false, this myth creates the idea that the poorest in America can work hard and achieve anything. The notion that the United States is a “mythical land of plenty” in which the individual is free to secure success is belied by the fact that success is shaped-and at times pre-conditioned by forces largely outside of individual control—class, race/ethnicity, and gender. A primary source of inspiration for this dashboard was the work completed by Dr. Raj Chetty's team at Opportunity Insights who identified a variable they call 'neighborhood quality' as the most impactful variables for upward mobility. ")
