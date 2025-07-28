import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --- Streamlit Setup ---
st.set_page_config(layout="wide", page_title="Economic Mobility Dashboard. This better work...")


# --- Load Data ---
@st.cache_data
def load_data(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Error: The file '{path}' was not found. Please ensure it's in the correct directory.")
        st.stop()


df = load_data('dream_92.csv')

# --- Shared Color Mapping (FIXED: Added definition here) ---
quintile_colors = {
    'top': '#9467bd',  # purple
    'fourth': '#1f77b4',  # blue
    'third': '#2ca02c',  # green
    'second': '#ff7f0e',  # orange
    'lowest': '#d62728'  # red
}

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


def get_next_n_available_years_strictly_after(person_years_sorted, start_after_year, n):
    """
    Returns the next 'n' available survey years from 'person_years_sorted'
    that are strictly after 'start_after_year'.
    """
    future_years = [y for y in person_years_sorted if y > start_after_year]
    return future_years[:n]


@st.cache_data
def calculate_robust_mobility(df, start_range, goal_range, time_horizon, consec_years, selected_start_year=None):
    """
    Calculates robust mobility: individuals who meet start criteria and
    then achieve and sustain goal quintile for `consec_years` after `time_horizon`.

    Returns:
        achiever_ids (list): List of person IDs who are robust achievers.
        n_achievers (int): Count of robust achievers.
        n_eligible_starters (int): Count of individuals eligible to start (denominator).
        achievers_details (dict): {pid: {'start_year': int, 'goal_years': list}}
                                  Stores the *first* valid achievement path for each PID.
    """
    df_sorted = df.sort_values(["family_person", "year"])

    # Dictionary to store the first valid achievement path for each PID
    achievers_details = {}

    # Set of PIDs who are eligible to be considered as starters
    eligible_starters = set()

    # Iterate through each person's data
    for pid, group in df_sorted.groupby("family_person"):
        person_years_sorted = np.sort(group['year'].values)
        person_quintiles = group.set_index('year')['quintile_label']

        # Find potential start points for this person
        potential_start_points = []
        if selected_start_year is not None:
            # If a specific start_year is selected, check only that year for this person
            if selected_start_year in person_years_sorted:
                if person_quintiles.loc[selected_start_year] in start_range:
                    potential_start_points.append(selected_start_year)
        else:
            # If 'All years' selected, any year where they are in start_range is a potential start
            for sy in person_years_sorted:
                if person_quintiles.loc[sy] in start_range:
                    potential_start_points.append(sy)

        if not potential_start_points:
            continue  # This person doesn't meet the initial start criteria

        # For the denominator, if they have *any* valid starting point, they're an eligible starter
        if any(person_quintiles.loc[sy] in start_range for sy in potential_start_points):
            eligible_starters.add(pid)

        # Now, check for achievement for this person based on potential start points
        # We want to find the *first* valid achievement path
        found_achievement_for_person = False
        for sy in potential_start_points:
            # Year from which to start looking for the goal period
            look_start_for_goal_period = sy + time_horizon

            # Get the next 'consec_years' available survey years *strictly after* this point
            goal_years_available = get_next_n_available_years_strictly_after(
                person_years_sorted, look_start_for_goal_period - 1, consec_years
            )

            # Check if we found exactly 'consec_years' available data points
            if len(goal_years_available) == consec_years:
                # Check if the person was in the goal_range for all these years
                all_in_goal = True
                for gy in goal_years_available:
                    if gy not in person_quintiles.index or person_quintiles.loc[gy] not in goal_range:
                        all_in_goal = False
                        break

                if all_in_goal:
                    # This person is a robust achiever, store the first valid path found
                    if pid not in achievers_details:  # Store only the first valid path
                        achievers_details[pid] = {'start_year': sy, 'goal_years': goal_years_available}
                        found_achievement_for_person = True
                        break  # Move to next person once their first achievement is found

    achiever_ids = list(achievers_details.keys())
    n_achievers = len(achiever_ids)
    n_eligible_starters = len(eligible_starters)  # This is the crucial denominator

    return achiever_ids, n_achievers, n_eligible_starters, achievers_details


# FIX: Re-adding the 'ever_reached_goal' function as it is used in Tab 4
def ever_reached_goal(df, start_range, goal_range):
    """
    Calculate the number of individuals who were ever in the start_range and
    ever reached the goal_range at least once (no time horizon or consecutive constraint).
    """
    reached = 0
    total = 0
    reached_ids = []

    df_filtered = df[df['quintile_label'].isin(quintile_options)]

    for pid, group in df_filtered.groupby("family_person"):
        quintiles = group.sort_values("year")['quintile_label'].values

        # Check if the person was ever in any of the start_range quintiles within the filtered dataframe (period)
        if any(q in start_range for q in quintiles):
            total += 1
            # Check if the person was ever in any of the goal_range quintiles within the filtered dataframe (period)
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
    "Ever Reached Comparison (Early vs Later Years)"
])

# ====================== TAB 1: Mobility Calculator ====================== #
with tabs[0]:
    st.title("The American Dream: An Economic Mobility Dashboard")

    start_range = get_quintile_range(start_quintile, start_quintile_comp)
    goal_range = get_quintile_range(goal_quintile, goal_quintile_comp)

    if start_year == "All years":
        achiever_ids, n_achievers, n_total_eligible, achievers_details = calculate_robust_mobility(
            df, start_range, goal_range, time_horizon, consec_years, selected_start_year=None
        )
    else:
        achiever_ids, n_achievers, n_total_eligible, achievers_details = calculate_robust_mobility(
            df, start_range, goal_range, time_horizon, consec_years, int(start_year)
        )

    if n_total_eligible == 0:
        st.warning("No individuals found who meet the initial starting criteria for the calculation.")
    else:
        st.success(f"Probability: {n_achievers / n_total_eligible:.2%} ({n_achievers}/{n_total_eligible})")
        st.info(f"Achiever IDs (first 20): {achiever_ids[:20]}")

    if achiever_ids:
        st.subheader("Individual Mobility Trajectory")
        plot_id = st.selectbox("Select an individual ID to plot trajectory:", achiever_ids, index=0)
        col1, col2 = st.columns([4, 1])

        with col2:
            plot_yaxis = st.radio("Plot y-axis:", ["Quintile (1–5)", "head_labor_income"], index=0)

        # Ensure person_data is correctly filtered and sorted
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

        # Retrieve the specific achievement path for the selected individual from achievers_details
        achiever_path = achievers_details.get(plot_id)

        if achiever_path:
            plot_start_year = achiever_path['start_year']
            plot_goal_years = achiever_path['goal_years']

            # Only plot data from the start year onwards for clarity
            person_data_for_plot = person_data[person_data['year'] >= plot_start_year].copy()

            # Re-create figure to only include data from the plot_start_year
            fig = px.line(person_data_for_plot, x="year", y=yvar,
                          title=f"Trajectory for ID {plot_id} from Start Year {plot_start_year}", markers=True)
            if yvar == "quintile_num":
                fig.update_yaxes(title=ytitle, tickmode='linear', dtick=1)
            else:
                fig.update_yaxes(title=ytitle, tickformat=",", rangemode="tozero", showgrid=True)

            # Add vertical lines for start and time horizon
            fig.add_vline(x=plot_start_year, line_dash="dash", line_color="green",
                          annotation_text=f"Start: {plot_start_year}", annotation_position="top left")

            # The time horizon line marks the beginning of the "check" period
            fig.add_vline(x=plot_start_year + time_horizon, line_dash="dash", line_color="orange",
                          annotation_text=f"Horizon: {plot_start_year + time_horizon}", annotation_position="top right")

            # Add markers for the consecutive goal years
            goal_year_data = person_data_for_plot[person_data_for_plot['year'].isin(plot_goal_years)]
            if not goal_year_data.empty:
                fig.add_scatter(
                    x=goal_year_data['year'],
                    y=goal_year_data[yvar],
                    mode="markers",
                    marker=dict(symbol='diamond', color="red", size=11),
                    name="Goal Years"
                )
            else:
                st.warning("No data found for goal years to plot, even though marked as achiever.")

        else:
            st.info("Selected individual does not have a robust achievement path matching the criteria for plotting.")

        with col1:
            st.plotly_chart(fig, use_container_width=True)

    # --- Debugging Section for Verification ---
    with st.expander("🔎 DEBUG: Verify Achiever Logic for Selected ID", expanded=False):
        if achiever_ids:
            selected_debug_id = st.selectbox("Select ID to verify logic:", achiever_ids, key="debug_id")

            debug_path_info = achievers_details.get(selected_debug_id)

            if debug_path_info:
                debug_start_year = debug_path_info['start_year']
                debug_goal_years = debug_path_info['goal_years']

                st.write("Full Quintile History (all years in dataset):")
                debug_data_full = df[df['family_person'] == selected_debug_id].sort_values("year")
                st.dataframe(debug_data_full[['year', 'quintile_label']])

                st.markdown(f"**Achiever's Found Start Year:** {debug_start_year}")
                st.markdown(f"**Configured Time Horizon:** {time_horizon}")
                st.markdown(f"**Goal Check Period Starts Calendar Year:** `{debug_start_year + time_horizon}`")
                st.markdown(f"**Configured Consecutive Years:** {consec_years}")

                st.markdown(f"**Actual Survey Years Used for Goal Check:** {debug_goal_years}")

                person_quintiles_debug = debug_data_full.set_index('year')['quintile_label']

                st.markdown("**Observed Quintiles in Goal Window:**")
                all_match = True
                for y in debug_goal_years:
                    q = person_quintiles_debug.get(y)
                    if q:
                        st.markdown(f"- {y}: {q} (In Goal Range: {q in goal_range})")
                        if q not in goal_range:
                            all_match = False
                    else:
                        st.markdown(
                            f"- {y}: (Data Missing for this year) - Should not happen if `get_next_n_available_years_strictly_after` is correct.")
                        all_match = False  # Treat missing data in required window as failure

                if all_match and len(debug_goal_years) == consec_years:
                    st.success(
                        "✅ Achiever logic confirmed: All goal years in required quintile and correct number of years found.")
                else:
                    st.error(
                        "❌ Achiever flagged, but verification failed. Check start quintile, goal quintiles, or available years.")
            else:
                st.info(
                    "No robust mobility details available for this selected ID. They might not be an achiever under the current criteria.")
        else:
            st.info("No achievers found to debug.")

    with st.expander("Explanation of how robust mobility probability is calculated (method/math)", expanded=False):
        st.markdown("""
**Robust Mobility Probability Calculation:**
- We identify "eligible starters" as individuals who are observed in the `Start Quintile (Childhood)` at the `Start Year (Childhood)` selected (or any year if 'All years' is chosen for start). These are the individuals who *could potentially* achieve mobility.
- For each eligible starter, we then look `Time Horizon` years into the future from their `Start Year`.
- From this future point, we identify the *next `Consecutive Years in Goal Quintile` available survey years* for that individual.
- An individual is counted as a "Robust Achiever" if they are observed in the `Goal Quintile` for *all* of these `Consecutive Years`.
- The probability is:
""")
        st.latex(
            r"P(\text{Robust Mobility}) = \frac{\text{Number of Robust Achievers}}{\text{Number of Eligible Starters}}")
        st.markdown("""
This is an **empirical estimate** of conditional probability using real PSID longitudinal data. This calculation precisely defines robust upward mobility, accounting for potential gaps in survey data and ensuring that individuals truly sustained their position in the target quintile.
       """)

# ========================== Tab 2: Matrix Check ========================== #
with tabs[1]:
    st.header("Mobility Matrix Check")

    # Set quintile order
    quintile_order = ['lowest', 'second', 'third', 'fourth', 'top']
    df['quintile_label'] = pd.Categorical(df['quintile_label'], categories=quintile_order, ordered=True)

    # Compute counts
    transition_counts = df.groupby(['year', 'quintile_label'])['family_person'].nunique().reset_index()

    # Plot
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

    # ==================== Animated Income Distribution ==================== #
    st.subheader("Income Quintile Distribution: 1968, 1993, 2022")

    # Data (assuming this is static for demonstration purposes)
    percents = {
        'lowest': [35.12, 40.70, 38.83],
        'second': [25.46, 21.60, 28.41],
        'third': [18.26, 18.45, 19.10],
        'fourth': [11.99, 12.77, 8.58],
        'top': [9.02, 6.48, 5.09]
    }

    # Create DataFrame
    df_animated = pd.DataFrame([
        {"Year": str(year), "Quintile": quintile, "Percentage": percents[quintile][i]}
        for i, year in enumerate(['1968', '1993', '2022'])
        for quintile in percents.keys()
    ])

    # Plot animated bar
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

    # === Static Side-by-Side Bar Chart for 1968, 1993, 2022 === #

    df_static = pd.DataFrame([
        {"Year": str(year), "Quintile": quintile, "Percentage": percents[quintile][i]}
        for i, year in enumerate(['1968', '1993', '2022'])
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

    # Display
    st.plotly_chart(fig_static, use_container_width=True)

# ========================== Tab 2: Income Quintile Thresholds over time ========================== #
with tabs[2]:
    st.header("Income Quintile Thresholds Over Time")

    quintile_cols = [
        'Lowest',
        'Second',
        'Third',
        'Fourth',
        'Lower.limit.of.top.5.percent..dollars.'
    ]

    existing_cols = [col for col in quintile_cols if col in df.columns]
    if not existing_cols:
        st.error("None of the expected quintile columns were found in the dataset.")
    else:
        quintiles_by_year = (
            df
            .groupby('year')[existing_cols]
            .mean()
            .reset_index()
        )

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
            melted,
            x='year',
            y='Threshold',
            color='Quintile',
            markers=True,
            title='Income Quintile and Top 5% Thresholds Over Time (Linear Scale)',
            labels={'year': 'Year', 'Threshold': 'Income Threshold ($)', 'Quintile': 'Income Group'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_original.update_layout(template='plotly_white')
        st.subheader("Linear Scale")
        st.plotly_chart(fig_original, use_container_width=True)

        # --- Log Chart ---
        melted_log = melted.copy()
        melted_log['Log Threshold'] = np.log(melted_log['Threshold'])

        fig_log = px.line(
            melted_log,
            x='year',
            y='Log Threshold',
            color='Quintile',
            markers=True,
            title='Log-Transformed Income Thresholds Over Time',
            labels={'year': 'Year', 'Log Threshold': 'Log(Income Threshold)', 'Quintile': 'Income Group'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_log.update_layout(template='plotly_white')
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
               Log transformation reveals that income growth has **not been evenly distributed** across quintiles. The gap between the top and bottom has widened in proportional terms — a strong sign of rising income inequality.
               """)

# ------- Tab 3 ----------------------- #
# ------ Income Trends Mean Median St Dev ----
with tabs[3]:
    st.header("Income Trends: Mean, Median, & Std Dev")

    income_stats = df.groupby('year')['head_labor_income'].agg(['mean', 'median', 'std']).reset_index()

    fig_income = go.Figure([
        go.Scatter(x=income_stats.year, y=income_stats['mean'], name='Mean', line_color='blue'),
        go.Scatter(x=income_stats.year, y=income_stats['median'], name='Median', line_color='green'),
        go.Scatter(x=income_stats.year, y=income_stats['mean'] + income_stats['std'], name='+1 Std Dev',
                   line=dict(width=0), marker_color='rgba(0,0,255,0)'),
        go.Scatter(x=income_stats.year, y=income_stats['mean'] - income_stats['std'], name='-1 Std Dev',
                   line=dict(width=0), fill='tonexty', fillcolor='rgba(0,0,255,0.2)')
    ])

    fig_income.update_layout(title="Head Labor Income Over Time",
                             xaxis_title="Year", yaxis_title="Income ($)",
                             template="plotly_white")
    st.plotly_chart(fig_income, use_container_width=True)

# ============= TAB 4: Robust Mobility Comparison (1968–1995 vs 1996–2002) ============= #
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

    early_period_years = (1968, 1995)
    late_period_years = (1996, 2022)

    # --- Calculation per method ---
    if ever_calc_mode == "Ever Reached (Plain)":
        # Filter dataframe for each period before passing to ever_reached_goal
        df_early = df[df['year'].between(*early_period_years)]
        df_late = df[df['year'].between(*late_period_years)]

        reached_early, total_early_starters, _ = ever_reached_goal(df_early, start_range, goal_range)
        reached_late, total_late_starters, _ = ever_reached_goal(df_late, start_range, goal_range)

        explanation = (
            "Counts anyone who was *ever* observed in the start range within the period, "
            "and at *any* point within that same period also observed in the goal range."
        )
    elif ever_calc_mode == "Robust Mobility (Consecutive Years & Horizon)":
        # For robust mobility, we need to apply the full logic to the filtered data
        _, n_achievers_early, n_total_early_starters, _ = calculate_robust_mobility(
            df[df['year'].between(*early_period_years)], start_range, goal_range,
            time_horizon, consec_years, selected_start_year=None)  # Always 'All years' for comparison

        _, n_achievers_late, n_total_late_starters, _ = calculate_robust_mobility(
            df[df['year'].between(*late_period_years)], start_range, goal_range,
            time_horizon, consec_years, selected_start_year=None)  # Always 'All years' for comparison

        reached_early, reached_late = n_achievers_early, n_achievers_late

        explanation = (
            f"Requires being in the start range, then reaching and remaining in the goal range "
            f"for **{consec_years} consecutive survey years** after a horizon of {time_horizon} years. "
            "Reflects robust mobility, not just one-time movement. Applies 'All years' for start year within each period."
        )
    else:
        # Should not happen with selectbox options
        reached_early = total_early_starters = reached_late = total_late_starters = 0
        explanation = "Invalid calculation method selected."

    # --- Metrics and Plotting ---
    if total_early_starters == 0 and total_late_starters == 0:
        st.warning("No valid individuals found to calculate mobility for in either period.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            early_prob = reached_early / total_early_starters if total_early_starters else 0
            st.metric(f"{early_period_years[0]}–{early_period_years[1]}", f"{early_prob:.2%}",
                      f"{reached_early}/{total_early_starters}")
        with col2:
            late_prob = reached_late / total_late_starters if total_late_starters else 0
            st.metric(f"{late_period_years[0]}–{late_period_years[1]}", f"{late_prob:.2%}",
                      f"{reached_late}/{total_late_starters}")

        results_df = pd.DataFrame({
            "Period": [f"{early_period_years[0]}–{early_period_years[1]}",
                       f"{late_period_years[0]}–{late_period_years[1]}"],
            "Reached Goal (%)": [
                early_prob * 100,
                late_prob * 100
            ]
        })

        fig = px.bar(
            results_df,
            x="Period",
            y="Reached Goal (%)",
            text="Reached Goal (%)",
            color="Period",
            color_discrete_map={
                f"{early_period_years[0]}–{early_period_years[1]}": "#1f77b4",
                f"{late_period_years[0]}–{late_period_years[1]}": "#d62728"
            },
            title="% Ever Reached Goal Quintile (Calculation Method: " + ever_calc_mode + ")",
            labels={"Reached Goal (%)": "% Reached Goal"},
            template="plotly_white",
            range_y=[0, 100]  # Ensure y-axis always goes to 100%
        )

        fig.update_traces(texttemplate='%{text:.2f}%', textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.info(f"**Calculation Explanation:** {explanation}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "**DISCLAIMER:** The information contained in this dashboard reflects average probabilities and should not be interpreted in absolute terms. Life is not always easy and hardwork will always improve your odds of success. Certainly, anything can happen 😊! However, in this pursuit it is imperative to maintain selfless community values to support and promote a society with high 'neighborhood quality' avoid rampant individualism that historical ensured inequalities persisted. One may define rampant individualism as a society's collective proclivity to pursue an undefinable, subjective, and continually-changing view of success—independent of help—fueled by the notion that America is rich in opportunity and success is limitless; the absence of opportunity combined with rampant individualism, however, ensures issues persist, and a large portion population is unable to compete in the capitalist system (Chetty, p ,2024). By and large, most Americans still believe that success is the product of individual effort. The myth that hard work will allow anyone to overcome even the most difficult circumstances has endured across the centuries—even in the face of evidence to the contrary. Though this ‘boot-strap’ mentality is not entirely false, this myth creates the idea that the poorest in America can work hard and achieve anything. The notion that the United States is a “mythical land of plenty” in which the individual is free to secure success is belied by the fact that success is shaped-and at times pre-conditioned by forces largely outside of individual control—class, race/ethnicity, and gender. A primary source of inspiration for this dashboard was the work completed by Dr. Raj Chetty's team at Opportunity Insights who identified a variable they call 'neighborhood quality' as the most impactful variables for upward mobility. ")
