# import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
# from matplotlib import pyplot as plt
# from sklearn.cluster import KMeans
# from statsmodels.tsa.arima.model import ARIMA
# from sklearn.metrics import silhouette_score

# --- Streamlit Setup ---
st.set_page_config(layout="wide", page_title="Economic Mobility Dashboard. This better work...")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data('dream_92.csv')

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

# --- Robust Achievers Function ---
def get_next_n_available_years(years_arr, start_year, n):
    return [y for y in years_arr if y >= start_year][:n]

def robust_achievers(df, start_range, goal_range, horizon, consec, start_year=None):
    df_filtered = df[df['quintile_label'].isin(quintile_options)].sort_values(["family_person", "year"])
    achievers_map = {}
    valid_starters = set()

    for pid, group in df_filtered.groupby("family_person"):
        years_arr = group['year'].values
        quintiles_arr = group['quintile_label'].values

        for i, sy in enumerate(years_arr):
            if start_year is not None and sy != start_year:
                continue
            if quintiles_arr[i] not in start_range:
                continue

            goal_start = sy + horizon
            future_years = get_next_n_available_years(years_arr, goal_start, consec)

            if len(future_years) < consec:
                continue

            mask = np.isin(years_arr, future_years)
            observed_quints = quintiles_arr[mask]

            if len(observed_quints) == consec and all(q in goal_range for q in observed_quints):
                achievers_map[pid] = sy
                valid_starters.add(pid)
                break
            else:
                valid_starters.add(pid)

    return list(achievers_map.keys()), len(achievers_map), len(valid_starters), achievers_map



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

        if any(q in start_range for q in quintiles):
            total += 1
            if any(q in goal_range for q in quintiles):
                reached += 1
                reached_ids.append(pid)

    return reached, total, reached_ids


def ever_reached_goal_by_period(df, start_range, goal_range, period_1, period_2):
    def check_ever(df_subset):
        total, reached = 0, 0
        for pid, group in df_subset.groupby("family_person"):
            quintiles = group.sort_values("year")["quintile_label"].values
            if any(q in start_range for q in quintiles):
                total += 1
                if any(q in goal_range for q in quintiles):
                    reached += 1
        return reached, total

    df1 = df[df['year'].between(*period_1)]
    df2 = df[df['year'].between(*period_2)]
    r1, t1 = check_ever(df1)
    r2, t2 = check_ever(df2)
    return (r1, t1), (r2, t2)

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
        result = robust_achievers(df, start_range, goal_range, time_horizon, consec_years)
    else:
        result = robust_achievers(df, start_range, goal_range, time_horizon, consec_years, int(start_year))

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

        fig.update_yaxes(title=ytitle, tickmode='linear' if yvar == 'quintile_num' else None,
                         dtick=1 if yvar == 'quintile_num' else None)

        sy_to_plot = achievers_map.get(plot_id)
        if sy_to_plot:
            years_arr = person_data["year"].values
            q_arr = person_data["quintile_label"].values
            goal_years = get_next_n_available_years(years_arr, sy_to_plot + time_horizon, consec_years)
            mask = np.isin(years_arr, goal_years)

            if mask.sum() == consec_years and np.all([q in goal_range for q in q_arr[mask]]):
                fig.add_vline(x=sy_to_plot, line_dash="dash", line_color="green", annotation_text="Start")
                fig.add_vline(x=sy_to_plot + time_horizon, line_dash="dash", line_color="orange",
                              annotation_text="Time Horizon")
                fig.add_scatter(x=goal_years,
                                y=person_data[person_data['year'].isin(goal_years)][yvar],
                                mode="markers",
                                marker=dict(symbol='diamond', color="red", size=11),
                                name="Goal Years")
            else:
                st.info(f"Selected person {plot_id} was marked as an achiever but couldn’t be plotted with current settings.")
        else:
            st.info("Selected individual does not have a trajectory that fits the chosen criteria.")

        with col1:
            st.plotly_chart(fig, use_container_width=True)

            # --- Optional: Secondary Reach Probability --- #
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
            goal_years = get_next_n_available_years(years_arr, sy_to_plot + time_horizon, consec_years)

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


# ========================== Tab 2: Distribution Chart ========================== #
# ========================== Shared Color Mapping ========================== #
quintile_colors = {
    'top': '#9467bd',  # purple
    'fourth': '#1f77b4',  # blue
    'third': '#2ca02c',  # green
    'second': '#ff7f0e',  # orange
    'lowest': '#d62728'  # red
}

# ========================== Tab 2: Matrix Check ========================== #
with tabs[1]:
    st.header("Mobility Matrix Check")

    # Set quintile order
    # NOTE: Changed order from original. If you want 'lowest' at the bottom of the bars, revert this.
    quintile_order = ['lowest', 'second', 'third', 'fourth', 'top']  # Changed from ['top', 'fourth', ...]
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

    # Data
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
        color_discrete_sequence=px.colors.qualitative.Set1  # Optional: adjust color scheme
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

    # Fix capitalization and formatting inconsistencies if present
    quintile_cols = [
        'Lowest',
        'Second',
        'Third',
        'Fourth',
        'Lower.limit.of.top.5.percent..dollars.'
    ]

    # Check which columns actually exist
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

        # Melt for better formatting in Plotly
        melted = quintiles_by_year.melt(id_vars='year', var_name='Quintile', value_name='Threshold')

        # Human-friendly labels
        label_map = {
            'Lowest': '1st Quintile (Lowest)',
            'Second': '2nd Quintile',
            'Third': '3rd Quintile',
            'Fourth': '4th Quintile',
            'Lower.limit.of.top.5.percent..dollars.': 'Top 5% Threshold'
        }
        melted['Quintile'] = melted['Quintile'].map(label_map)

    # Log Tranformed visual to address exponential nature of data

    # Define the income threshold columns you want to analyze
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
        # Use robust_achievers for each period
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


# --- Footer ---
st.markdown("---")
st.markdown(
    "**DISCLAIMER:** The information contained in this dashboard reflects average probabilities and should not be interpreted in absolute terms. Life is not always easy and hardwork will always improve your odds of success. Certainly, anything can happen 😊! However, in this pursuit it is imperative to maintain selfless community values to support and promote a society with high 'neighborhood quality' avoid rampant individualism that historical ensured inequalities persisted. One may define rampant individualism as a society's collective proclivity to pursue an undefinable, subjective, and continually-changing view of success—independent of help—fueled by the notion that America is rich in opportunity and success is limitless; the absence of opportunity combined with rampant individualism, however, ensures issues persist, and a large portion population is unable to compete in the capitalist system (Chetty, p ,2024). By and large, most Americans still believe that success is the product of individual effort. The myth that hard work will allow anyone to overcome even the most difficult circumstances has endured across the centuries—even in the face of evidence to the contrary. Though this ‘boot-strap’ mentality is not entirely false, this myth creates the idea that the poorest in America can work hard and achieve anything. The notion that the United States is a “mythical land of plenty” in which the individual is free to secure success is belied by the fact that success is shaped-and at times pre-conditioned by forces largely outside of individual control—class, race/ethnicity, and gender. A primary source of inspiration for this dashboard was the work completed by Dr. Raj Chetty's team at Opportunity Insights who identified a variable they call 'neighborhood quality' as the most impactful variables for upward mobility. ")
