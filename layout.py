import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# --- Streamlit Page Setup ---
st.set_page_config(layout="wide", page_title="Dream: An Economic Mobility Dashboard")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

DATA_PATH = "C:/Users/Mark Crisci/Downloads/dream_92.csv"
df = load_data(DATA_PATH)

# --- Sidebar Inputs ---
st.sidebar.header("Mobility Calculator Options")
years = sorted(df['year'].unique())
years_with_all = ['All years'] + years
quintile_options = ["lowest", "second", "third", "fourth", "top"]
comp_options = ["Exact", "No higher than", "No lower than"]

start_year = st.sidebar.selectbox("Select A Start Year (childhood):", years_with_all, index=0)
start_quintile_comp = st.sidebar.selectbox("Start Quintile Comparison:", comp_options, index=0)
start_quintile = st.sidebar.selectbox("Select A Start Quintile (childhood):", quintile_options, index=0)
time_horizon = st.sidebar.number_input("Time horizon (years):", min_value=1, max_value=40, value=10)
consec_years = st.sidebar.number_input("Robustness Window: Consecutive years in goal quintile (robust mobility):", min_value=1, max_value=15, value=3)
goal_quintile_comp = st.sidebar.selectbox("GOAL Quintile Comparison:", comp_options, index=0)
goal_quintile = st.sidebar.selectbox("Select A GOAL Quintile:", quintile_options, index=4)

# --- Helper Functions ---
def quintile_num(q):
    try:
        return quintile_options.index(q) + 1
    except Exception:
        return np.nan

def get_quintile_range(q, comp, q_opts):
    idx = q_opts.index(q)
    if comp == "Exact":
        return [q]
    elif comp == "No higher than":
        return q_opts[:idx+1]
    elif comp == "No lower than":
        return q_opts[idx:]
    else:
        return [q]

@st.cache_data(show_spinner="Finding robust achievers (revised logic)...")
# def robust_achievers_corrected(df, start_quintile_range, goal_quintile_range, time_horizon, consec_years, quintile_options, restrict_start_year=None):
#     df = df[df['quintile_label'].isin(quintile_options)].copy()
#     df = df.sort_values(["family_person", "year"])
#     robust_set = set()
#     valid_denominator = set()
#     for pid, group in df.groupby("family_person"):
#         years = group['year'].values
#         quintiles = group['quintile_label'].values
#         # Find all possible start years
#         start_years = years[np.isin(quintiles, start_quintile_range)]
#         if restrict_start_year is not None:
#             # Only look at the *specific* start year
#             start_years = [y for y in start_years if y == restrict_start_year]
#         for sy in start_years:
#             idx = np.where(years == sy)[0][0]
#             horizon_idx = np.where(years >= sy + time_horizon)[0]
#             if len(horizon_idx) == 0:
#                 continue
#             start_goal_idx = horizon_idx[0]
#             window_idx = np.arange(start_goal_idx, start_goal_idx + consec_years)
#             if window_idx[-1] >= len(years):
#                 continue
#             valid_denominator.add(pid)
#             window_quints = [quintiles[i] for i in window_idx]
#             if all(q in goal_quintile_range for q in window_quints):
#                 robust_set.add(pid)
#                 break
#     n_achievers = len(robust_set)
#     n_total = len(valid_denominator)
#     return list(robust_set), n_achievers, n_total

def robust_achievers_corrected(df, start_quintile_range, goal_quintile_range, time_horizon, consec_years, quintile_options,restrict_start_year=None):
    df = df[df['quintile_label'].isin(quintile_options)].copy()
    df = df.sort_values(["family_person", "year"])
    robust_set = set()
    valid_denominator = set()
    for pid, group in df.groupby("family_person"):
        years = group['year'].values
        quintiles = group['quintile_label'].values
        start_years = years[np.isin(quintiles, start_quintile_range)]
        # Only allow start_years to be the restrict_start_year if set:
        if restrict_start_year is not None:
            start_years = [y for y in start_years if y == restrict_start_year]
        if len(start_years) == 0:
            continue
        for start_year in start_years:
            end_year = start_year + time_horizon + consec_years - 1
            if years[-1] < end_year:
                continue
            valid_denominator.add(pid)
            target_years = np.arange(start_year + time_horizon, start_year + time_horizon + consec_years)
            if not np.all(np.isin(target_years, years)):
                continue
            mask = np.isin(years, target_years)
            if np.all([q in goal_quintile_range for q in quintiles[mask]]):
                robust_set.add(pid)
                break
    n_achievers = len(robust_set)
    n_total = len(valid_denominator)
    return list(robust_set), n_achievers, n_total

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

# --- Shared Color Mapping ---
quintile_colors = {
    'top': '#9467bd',
    'fourth': '#1f77b4',
    'third': '#2ca02c',
    'second': '#ff7f0e',
    'lowest': '#d62728'
}

tab_titles = [
    "Mobility Calculator",
    "Matrix Check",
    "Income Trends",
    "Income Trends: Mean, Median & Std Dev",
    "Ever Reached Comparison",
    "Multi-Person Income Trajectories"
]
tabs = st.tabs(tab_titles)

# =================== TAB 0: Mobility Calculator =================== #
with tabs[0]:
    st.title("Dream: An Economic Mobility Dashboard")
    st.markdown("""
    **Data Source:** PSID — Processed and cleaned.  
    **Definition of Mobility:** "Household Head" refers to the person recorded as the household head in the PSID for a given year.  
    This dashboard estimates the probability of moving between income quintiles over time, using robust (multi-year) definitions of mobility.
    """)
    start_quintile_range = get_quintile_range(start_quintile, start_quintile_comp, quintile_options)
    goal_quintile_range = get_quintile_range(goal_quintile, goal_quintile_comp, quintile_options)
    goal_covers_all = (goal_quintile_range == quintile_options)

    if goal_covers_all:
        st.error("⚠️ The selected GOAL quintile comparison includes **all quintiles**, which makes the result meaningless.")
        st.stop()

    if start_year == "All years":
        achiever_ids, n_achievers, n_total = robust_achievers_corrected(
            df, start_quintile_range, goal_quintile_range, time_horizon, consec_years, quintile_options)
    else:
        sy = int(start_year)
        # Identify those who are in the start quintile in the specific start year
        eligible_ids = df[(df['year'] == sy) & (df['quintile_label'].isin(start_quintile_range))][
            'family_person'].unique()
        # Only pass all years for those people to the function!
        df_cohort = df[df['family_person'].isin(eligible_ids)].copy()
        # But, inside robust_achievers_corrected, restrict valid start windows to ONLY the specific year
        achiever_ids, n_achievers, n_total = robust_achievers_corrected(
            df_cohort, start_quintile_range, goal_quintile_range, time_horizon, consec_years, quintile_options,
            restrict_start_year=sy)

    if n_total == 0:
        st.warning("No valid cases found for these criteria.")
    else:
        probability = n_achievers / n_total if n_total > 0 else 0
        st.info(
            f"IDs of individuals who meet criteria ({n_achievers}): {', '.join(str(x) for x in achiever_ids[:30])}" +
            ("..." if n_achievers > 30 else ""))
        st.success(f"Probability: {probability:.1%} ({n_achievers} out of {n_total} people)")

    if n_achievers > 0:
        st.subheader("Individual Mobility Trajectory")
        plot_id = st.selectbox("Select an individual ID to plot trajectory:", achiever_ids, index=0)
        col1, col2 = st.columns([4, 1])
        with col2:
            plot_yaxis = st.radio("Plot y-axis:", ["Quintile (1–5)", "head_labor_income"], index=0,
                                  key="plot_yaxis_side")

        # Use the correct data source for this individual!
        if start_year == "All years":
            # Find this individual's full trajectory from the full df
            person_data = df[(df['family_person'] == plot_id) & (df['head_labor_income'] > 0)].copy()
        else:
            # Only consider cohort for this start_year and restrict years >= start_year (optional)
            person_data = df_cohort[
                (df_cohort['family_person'] == plot_id) & (df_cohort['head_labor_income'] > 0)
                ].copy()
            person_data = person_data[person_data['year'] >= int(start_year)]

        if person_data.empty:
            st.warning("No income records for this person.")
        else:
            person_data = person_data.sort_values("year")
            person_data['quintile_num'] = person_data['quintile_label'].map(quintile_num)
            yvar = 'quintile_num' if plot_yaxis == "Quintile (1–5)" else 'head_labor_income'
            ytitle = "Income Quintile (1=Lowest, 5=Top)" if yvar == "quintile_num" else "Head Labor Income ($)"
            fig = px.line(person_data, x="year", y=yvar, title=f"Trajectory for ID {plot_id}", markers=True)
            if yvar == "quintile_num":
                fig.update_yaxes(title=ytitle, tickmode='linear', dtick=1)
            else:
                fig.update_yaxes(title=ytitle, tickformat=",", rangemode="tozero", showgrid=True)

            # ------- NEW LOGIC FOR WINDOW HIGHLIGHTING --------
            # This person only qualifies as an achiever by meeting robust mobility at least once
            # We'll plot/highlight ONLY the first window (for visual clarity)
            years_arr = person_data["year"].values
            quintiles_arr = person_data["quintile_label"].values

            found = False
            if start_year == "All years":
                # All valid start years for this person
                start_years = person_data[person_data["quintile_label"].isin(start_quintile_range)]["year"].values
            else:
                sy = int(start_year)
                if sy in person_data[person_data["quintile_label"].isin(start_quintile_range)]["year"].values:
                    start_years = np.array([sy])
                else:
                    start_years = np.array([])

            for sy in start_years:
                # Get the N *actual* next available survey years, not just calendar years!
                possible_goal_years = years_arr[years_arr > sy + time_horizon - 1]  # survey years after horizon
                # You need to get the first N years after the time horizon
                window_start_idx = np.where(years_arr == sy + time_horizon)[0]
                if len(window_start_idx) == 0:
                    continue
                idx = window_start_idx[0]
                goal_years = years_arr[idx:idx + consec_years]
                if len(goal_years) < consec_years:
                    continue
                # Check if all those years are present and in goal range
                mask = np.isin(years_arr, goal_years)
                if np.all([q in goal_quintile_range for q in quintiles_arr[mask]]):
                    fig.add_vline(x=sy, line_dash="dash", line_color="green", annotation_text="Start",
                                  annotation_position="top left")
                    fig.add_vline(x=goal_years[0], line_dash="dash", line_color="orange",
                                  annotation_text="Time Horizon", annotation_position="top right")
                    goal_vals = person_data[person_data['year'].isin(goal_years)][yvar]
                    fig.add_scatter(x=goal_years, y=goal_vals, mode="markers",
                                    marker=dict(symbol='x', color="red", size=14), name="Goal Years")
                    found = True
                    break  # Only show the first window they succeeded in

            if not found:
                st.info(
                    "Selected individual does not have a trajectory that fits the chosen criteria in any year window.")
            with col1:
                st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show: How robust mobility probability is calculated (method/math)", expanded=False):
        st.markdown("""
        **Robust Mobility Probability Calculation:**  
        - For a chosen starting quintile and year, we find all individuals in the dataset who were in that quintile and year.
        - We track those same individuals to a future year (based on the selected time horizon) and require they remain in the target quintile for **consecutive years**, as defined by the **robustness window** parameter.
        - The probability is:
        """)
        st.latex(r"P(\text{Robust Mobility}) = \frac{\text{Number who reach/stay in goal quintile for N years}}{\text{Number who started in start quintile}}")
        st.markdown("This uses observed longitudinal transitions in the PSID, not a simulation or model.")

# ========== TAB 1: Matrix Check ========== #
with tabs[1]:
    st.header("Mobility Matrix Check")
    quintile_order = ['lowest', 'second', 'third', 'fourth', 'top']
    df['quintile_label'] = pd.Categorical(df['quintile_label'], categories=quintile_order, ordered=True)
    transition_counts = df.groupby(['year', 'quintile_label'])['family_person'].nunique().reset_index()
    fig_matrix = px.bar(
        transition_counts,
        x='year',
        y='family_person',
        color='quintile_label',
        category_orders={'quintile_label': quintile_order},
        color_discrete_map=quintile_colors,
        title="Number of People in Each Quintile by Year",
        labels={'family_person': 'Unique Individuals', 'quintile_label': 'Quintile'},
        template='plotly_white'
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

    # === Animated Income Distribution & Static Side-by-Side === #
    st.subheader("Income Quintile Distribution: 1968, 1993, 2022")
    percents = {
        'lowest': [35.12, 40.70, 38.83],
        'second': [25.46, 21.60, 28.41],
        'third': [18.26, 18.45, 19.10],
        'fourth': [11.99, 12.77, 8.58],
        'top': [9.02, 6.48, 5.09]
    }
    years_ = ['1968', '1993', '2022']
    df_animated = pd.DataFrame([
        {"Year": str(year), "Quintile": quintile, "Percentage": percents[quintile][i]}
        for i, year in enumerate(years_)
        for quintile in percents.keys()
    ])
    fig_animated = px.bar(
        df_animated,
        x='Quintile',
        y='Percentage',
        color='Quintile',
        animation_frame='Year',
        text='Percentage',
        title='Animated Income Distribution by Quintile (1968 → 1993 → 2022)',
        range_y=[0, 45],
        template='plotly_white',
        color_discrete_map=quintile_colors
    )
    fig_animated.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_animated.update_layout(
        showlegend=False,
        yaxis_title='Percentage (%)',
        xaxis_title='Income Quintile',
        height=500,
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": 2500, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 3000, "easing": "cubic-in-out"}
                    }]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                }
            ]
        }],
        sliders=[{
            "active": 0,
            "steps": [
                {
                    "label": year,
                    "method": "animate",
                    "args": [[year], {
                        "mode": "immediate",
                        "frame": {"duration": 2500, "redraw": True},
                        "transition": {"duration": 1000}
                    }]
                } for year in df_animated["Year"].unique()
            ]
        }]
    )
    with st.expander("▶ Show Animated Quintile Distribution", expanded=False):
        st.plotly_chart(fig_animated, use_container_width=True)

    df_static = pd.DataFrame([
        {"Year": str(year), "Quintile": quintile, "Percentage": percents[quintile][i]}
        for i, year in enumerate(years_)
        for quintile in percents.keys()
    ])
    fig_static = px.bar(
        df_static,
        x='Quintile',
        y='Percentage',
        color='Year',
        barmode='group',
        text='Percentage',
        title='Distribution of Income by Quintile (1968 vs 1993 vs 2022)',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig_static.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_static.update_layout(
        yaxis_title='Percentage (%)',
        xaxis_title='Income Quintile',
        height=500,
        legend_title_text='Survey Year',
    )

    with st.expander("▶ Show Distribution of Income by Quintile (1968 vs 1993 vs 2022)", expanded=False):
        st.plotly_chart(fig_static, use_container_width=True)

# ========== TAB 2: Income Trends (Quintile Thresholds Linear & Log) ========== #
with tabs[2]:
    st.header("Income Quintile Thresholds Over Time")
    quintile_cols = ['Lowest', 'Second', 'Third', 'Fourth', 'Lower.limit.of.top.5.percent..dollars.']
    existing_cols = [col for col in quintile_cols if col in df.columns]
    if not existing_cols:
        st.error("None of the expected quintile columns were found in the dataset.")
    else:
        quintiles_by_year = df.groupby('year')[existing_cols].mean().reset_index()
        melted = quintiles_by_year.melt(id_vars='year', var_name='Quintile', value_name='Threshold')
        label_map = {
            'Lowest': '1st Quintile (Lowest)',
            'Second': '2nd Quintile',
            'Third': '3rd Quintile',
            'Fourth': '4th Quintile',
            'Lower.limit.of.top.5.percent..dollars.': 'Top 5% Threshold'
        }
        melted['Quintile'] = melted['Quintile'].map(label_map)
        # --- Linear Chart ---
        fig_original = px.line(
            melted, x='year', y='Threshold', color='Quintile', markers=True,
            title='Income Quintile and Top 5% Thresholds Over Time (Linear Scale)',
            labels={'year': 'Year', 'Threshold': 'Income Threshold ($)', 'Quintile': 'Income Group'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.subheader("Linear Scale")
        st.plotly_chart(fig_original, use_container_width=True)
        # --- Log Chart ---
        melted_log = melted.copy()
        melted_log['Log Threshold'] = np.log(melted_log['Threshold'])
        fig_log = px.line(
            melted_log, x='year', y='Log Threshold', color='Quintile', markers=True,
            title='Log-Transformed Income Thresholds Over Time',
            labels={'year': 'Year', 'Log Threshold': 'Log(Income Threshold)', 'Quintile': 'Income Group'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.subheader("Log-Transformed Scale")
        st.plotly_chart(fig_log, use_container_width=True)
        with st.expander("What does the log-transformation show?"):
            st.markdown("""
                The **original chart** shows rapid increases in income thresholds for higher quintiles, especially the **Top 5%**, which grows exponentially.
                The **log-transformed chart** rescales this so we can compare **proportional growth rates**:
                - A straight line on the log plot implies **constant exponential growth**
                - Steeper slope = faster proportional increase
                - Lower quintiles exhibit flatter slopes, indicating slower relative growth over time
                **Conclusion:**
                Log transformation reveals that income growth has **not been evenly distributed** across quintiles.
                """)

# ========== TAB 3: Income Trends (Mean, Median, Std Dev, with log plot) ========== #
with tabs[3]:
    st.header("Income Trends: Mean, Median, & Std Dev (Linear & Log Scales)")
    income_stats = df.groupby('year')['head_labor_income'].agg(['mean', 'median', 'std']).reset_index()
    # Linear plot as before...
    fig_income = go.Figure([
        go.Scatter(x=income_stats.year, y=income_stats['mean'], name='Mean', line_color='blue'),
        go.Scatter(x=income_stats.year, y=income_stats['median'], name='Median', line_color='green'),
        go.Scatter(x=income_stats.year, y=income_stats['mean'] + income_stats['std'], name='+1 Std Dev',
                   line=dict(width=0), marker_color='rgba(0,0,255,0)'),
        go.Scatter(x=income_stats.year, y=income_stats['mean'] - income_stats['std'], name='-1 Std Dev',
                   line=dict(width=0), fill='tonexty', fillcolor='rgba(0,0,255,0.2)')
    ])
    fig_income.update_layout(title="Head Labor Income Over Time (Linear)", xaxis_title="Year", yaxis_title="Income ($)", template="plotly_white")
    st.subheader("Linear Scale")
    st.plotly_chart(fig_income, use_container_width=True)

    # Log plot with correct std dev in log space
    yearly = []
    for year, group in df.groupby('year'):
        incomes = group['head_labor_income']
        log_incomes = np.log(incomes[incomes > 0])
        yearly.append({
            'year': year,
            'log_mean': log_incomes.mean(),
            'log_median': np.median(log_incomes),
            'log_std': log_incomes.std()
        })
    income_stats_log = pd.DataFrame(yearly).sort_values('year')

    fig_income_log = go.Figure([
        go.Scatter(x=income_stats_log.year, y=income_stats_log['log_mean'], name='Log(Mean)', line_color='blue'),
        go.Scatter(x=income_stats_log.year, y=income_stats_log['log_median'], name='Log(Median)', line_color='green'),
        go.Scatter(x=income_stats_log.year, y=income_stats_log['log_mean'] + income_stats_log['log_std'], name='+1 Std Dev (log)',
                   line=dict(width=0), marker_color='rgba(0,0,255,0)'),
        go.Scatter(x=income_stats_log.year, y=income_stats_log['log_mean'] - income_stats_log['log_std'], name='-1 Std Dev (log)',
                   line=dict(width=0), fill='tonexty', fillcolor='rgba(0,0,255,0.2)')
    ])
    fig_income_log.update_layout(title="Head Labor Income Over Time (Log-Transformed)", xaxis_title="Year", yaxis_title="Log(Income)", template="plotly_white")
    st.subheader("Log-Transformed Scale")
    st.plotly_chart(fig_income_log, use_container_width=True)

# ========== TAB 4: Ever Reached Comparison (Early vs Later) ========== #
with tabs[4]:
    st.header("Ever Reached Goal: Early vs. Later Periods (1968–1995 vs 1996–2022)")
    ever_calc_mode = st.selectbox(
        "Calculation Method:",
        [
            "Ever Reached (Plain)",
            "Robust Mobility (Consecutive Years & Horizon)"
        ]
    )
    start_range = get_quintile_range(start_quintile, start_quintile_comp, quintile_options)
    goal_range = get_quintile_range(goal_quintile, goal_quintile_comp, quintile_options)
    early_period = (1968, 1995)
    late_period = (1996, 2022)
    if ever_calc_mode == "Ever Reached (Plain)":
        reached_early, total_early, _ = ever_reached_goal(df[df['year'].between(*early_period)], start_range, goal_range)
        reached_late, total_late, _ = ever_reached_goal(df[df['year'].between(*late_period)], start_range, goal_range)
        explanation = (
            "Counts anyone who was *ever* observed in the start range, "
            "and at *any* point also observed in the goal range."
        )
    elif ever_calc_mode == "Robust Mobility (Consecutive Years & Horizon)":
        _, n_achievers_early, n_total_early = robust_achievers_corrected(
            df[df['year'].between(*early_period)], start_range, goal_range,
            time_horizon, consec_years, quintile_options)
        _, n_achievers_late, n_total_late = robust_achievers_corrected(
            df[df['year'].between(*late_period)], start_range, goal_range,
            time_horizon, consec_years, quintile_options)
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
# ========== TAB 5: Multi-Person Income Trajectories ========== #
with tabs[5]:
    st.header("Multi-Person Income Trajectories")

    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider("Select year range to display:", min_value=year_min, max_value=year_max,
                           value=(year_min, year_max), step=1)

    df_range = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()
    available_ids = df_range['family_person'].unique()
    default_ids = list(available_ids[:3])
    selected_ids = st.multiselect(
        "Select up to 10 individual IDs to visualize:",
        options=available_ids,
        default=default_ids,
        max_selections=10
    )

    if selected_ids:
        df_plot = df_range[df_range['family_person'].isin(selected_ids)].copy()
        # Map quintile to number for plotting
        df_plot['quintile_num'] = df_plot['quintile_label'].map(lambda q: quintile_options.index(q) + 1 if q in quintile_options else np.nan)

        col1, col2 = st.columns([4, 1])
        with col2:
            plot_yaxis_multi = st.radio(
                "Plot y-axis:",
                ["head_labor_income", "Quintile (1–5)"],
                index=0,
                key="plot_yaxis_multi"
            )

        with col1:
            if plot_yaxis_multi == "head_labor_income":
                yvar = "head_labor_income"
                ytitle = "Head Labor Income ($)"
                fig = px.line(
                    df_plot, x="year", y=yvar, color="family_person", line_group="family_person",
                    markers=True, title="Head Labor Income Trajectories",
                    labels={"head_labor_income": "Head Labor Income ($)", "year": "Year", "family_person": "Individual ID"},
                    template="plotly_white"
                )
                fig.update_layout(
                    yaxis_title=ytitle,
                    xaxis_title="Year",
                    legend_title_text="ID",
                    height=500
                )
                fig.update_yaxes(tickformat=",")
            else:
                yvar = "quintile_num"
                ytitle = "Income Quintile (1=Lowest, 5=Top)"
                fig = px.line(
                    df_plot, x="year", y=yvar, color="family_person", line_group="family_person",
                    markers=True, title="Income Quintile Trajectories",
                    labels={"quintile_num": ytitle, "year": "Year", "family_person": "Individual ID"},
                    template="plotly_white"
                )
                fig.update_layout(
                    yaxis_title=ytitle,
                    xaxis_title="Year",
                    legend_title_text="ID",
                    height=500
                )
                fig.update_yaxes(tickmode='linear', dtick=1, range=[0.9, 5.1])

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Select at least one ID to display income trajectories.")

    with st.expander("How to use this tab"):
        st.markdown(
            "- **Select up to 10 people** to visualize their income journeys.\n"
            "- **Toggle the y-axis** between Head Labor Income and Income Quintile.\n"
            "- Use the slider to restrict the year range shown.\n"
            "- Useful for exploring heterogeneity in income dynamics."
        )


# --- Footer ---
st.markdown("---")
st.markdown(
"**DISCLAIMER:** The information contained in this dashboard reflects average probabilities and should not be interpreted in absolute terms. Life is not always easy and hardwork will always improve your odds of success. Certainly, anything can happen 😊! However, in this pursuit it is imperative to maintain selfless community values to support and promote a society with high 'neighborhood quality' avoid rampant individualism that historical ensured inequalities persisted. One may define rampant individualism as a society's collective proclivity to pursue an undefinable, subjective, and continually-changing view of success—independent of help—fueled by the notion that America is rich in opportunity and success is limitless; the absence of opportunity combined with rampant individualism, however, ensures issues persist, and a large portion population is unable to compete in the capitalist system (Chetty, p ,2024). By and large, most Americans still believe that success is the product of individual effort. The myth that hard work will allow anyone to overcome even the most difficult circumstances has endured across the centuries—even in the face of evidence to the contrary. Though this ‘boot-strap’ mentality is not entirely false, this myth creates the idea that the poorest in America can work hard and achieve anything. The notion that the United States is a “mythical land of plenty” in which the individual is free to secure success is belied by the fact that success is shaped-and at times pre-conditioned by forces largely outside of individual control—class, race/ethnicity, and gender. A primary source of inspiration for this dashboard was the work completed by Dr. Raj Chetty's team at Opportunity Insights who identified a variable they call 'neighborhood quality' as the most impactful variables for upward mobility.")

