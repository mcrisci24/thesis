import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="The American Dream: A Dashboard for Relative Economic Mobility")

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

DATA_PATH = "dream_92.csv"

df = load_data(DATA_PATH)

df = df[df['year'] != 1992].copy()  # <-- REMOVE 1992 FROM WHOLE DATASET as it has 0 for everyone in 1992--flawed


# Sidebar controls
st.sidebar.header("Mobility Calculator Options")

# years = sorted(df['year'].unique())
# years_with_all = ['All years'] + years
years = sorted([y for y in df['year'].unique()])
years_with_all = ['All years'] + years
quintile_options = ["lowest", "second", "third", "fourth", "top"]
comp_options = ["Exact", "No higher than", "No lower than"]

start_year = st.sidebar.selectbox("Select A Start Year (childhood):", years_with_all, index=0)
start_quintile_comp = st.sidebar.selectbox("Start Quintile Comparison:", comp_options, index=0)
start_quintile = st.sidebar.selectbox("Select A Start Quintile (childhood):", quintile_options, index=0)
time_horizon = st.sidebar.number_input("Time horizon (years):", min_value=1, max_value=40, value=10)
goal_quintile_comp = st.sidebar.selectbox("GOAL Quintile Comparison:", comp_options, index=0)
goal_quintile = st.sidebar.selectbox("Select A GOAL Quintile:", quintile_options, index=4)

# -- Remove 1992 from years list for sidebar and all logic
years = sorted([y for y in df['year'].unique() if y != 1992])
years_with_all = ['All years'] + years

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

# @st.cache_data
# def robust_achievers_single_year(
#     df, start_quintile_range, goal_quintile_range, time_horizon, start_year=None
# ):
#     df = df[df['quintile_label'].isin(quintile_options)].copy()
#     df = df[df['year'] != 1992].sort_values(["family_person", "year"])
#     achievers = []
#     denominator = set()
#     achievers_map = dict()  # Will map PID to list of (sy, goal_y) pairs
#
#     for pid, group in df.groupby("family_person"):
#         years = group['year'].values
#         quintiles = group['quintile_label'].values
#
#         # Get valid start years (not 1992)
#         if start_year is None:
#             possible_starts = years[np.isin(quintiles, start_quintile_range)]
#             possible_starts = possible_starts[possible_starts != 1992]
#         else:
#             if int(start_year) == 1992:
#                 continue
#             mask = (years == int(start_year)) & np.isin(quintiles, start_quintile_range)
#             possible_starts = years[mask]
#
#         if len(possible_starts) == 0:
#             continue
#
#         found_windows = []
#         for sy in possible_starts:
#             goal_y = sy + time_horizon
#             if goal_y == 1992 or goal_y not in years:
#                 continue
#             idx = np.where(years == goal_y)[0][0]
#             denominator.add(pid)
#             if quintiles[idx] in goal_quintile_range:
#                 found_windows.append((sy, goal_y))
#
#         if found_windows:
#             achievers.append(pid)
#             achievers_map[pid] = found_windows
#         elif len(possible_starts) > 0:
#             denominator.add(pid)
#
#     return achievers, len(achievers), len(denominator), achievers_map

@st.cache_data
def robust_achievers_single_year(
    df, start_quintile_range, goal_quintile_range, time_horizon, start_year=None
):
    df = df[df['quintile_label'].isin(quintile_options)].sort_values(["family_person", "year"])
    achievers = []
    denominator = set()
    achievers_map = dict()

    for pid, group in df.groupby("family_person"):
        years = group['year'].values
        quintiles = group['quintile_label'].values

        # Get valid start years
        if start_year is None:
            possible_starts = years[np.isin(quintiles, start_quintile_range)]
        else:
            mask = (years == int(start_year)) & np.isin(quintiles, start_quintile_range)
            possible_starts = years[mask]

        if len(possible_starts) == 0:
            continue

        found_windows = []
        for sy in possible_starts:
            goal_y = sy + time_horizon
            if goal_y not in years:
                continue
            idx = np.where(years == goal_y)[0][0]
            denominator.add(pid)
            if quintiles[idx] in goal_quintile_range:
                found_windows.append((sy, goal_y))

        if found_windows:
            achievers.append(pid)
            achievers_map[pid] = found_windows
        elif len(possible_starts) > 0:
            denominator.add(pid)

    return achievers, len(achievers), len(denominator), achievers_map



#quintile colors for income trend plotting (tab 3)
quintile_colors = {
    'top': '#9467bd',
    'fourth': '#1f77b4',
    'third': '#2ca02c',
    'second': '#ff7f0e',
    'lowest': '#d62728'
}

# --- Tab Layout ---
tabs = st.tabs([
    "Mobility Calculator",
    "Matrix Check",
    "Income Trends",
    "Income Trends: Mean, Median & Std Dev",
    # "Ever Reached Comparison (Early vs Later Years)",
    "Multi-Person Income Trajectories"
])

# ====================== TAB 0: Mobility Calculator ====================== #
with tabs[0]:
    st.title("The American Dream: A Dashboard for Relative Economic Mobility")
    start_range = get_quintile_range(start_quintile, start_quintile_comp, quintile_options)
    goal_range = get_quintile_range(goal_quintile, goal_quintile_comp, quintile_options)

    if start_year == "All years":
        result = robust_achievers_single_year(df, start_range, goal_range, time_horizon)
    else:
        result = robust_achievers_single_year(df, start_range, goal_range, time_horizon, int(start_year))
    achiever_ids, n_achievers, n_total, achievers_map = result

    if n_total == 0:
        st.warning("No valid cases found for these criteria.")
    else:
        st.success(f"Probability: {n_achievers / n_total:.2%} ({n_achievers}/{n_total})")
        st.info(f"Achiever IDs (first 20): {achiever_ids[:20]}")

    # Plot individual trajectory
    if achiever_ids:
        st.subheader("Individual Mobility Trajectory")
        plot_id = st.selectbox("Select an individual ID to plot trajectory:", achiever_ids, index=0)
        col1, col2 = st.columns([4, 1])
        with col2:
            plot_yaxis = st.radio("Plot y-axis:", ["Quintile (1–5)", "head_labor_income"], index=0)
        # person_data = df[(df['family_person'] == plot_id) & (df['head_labor_income'] > 0)].copy()
        person_data = df[(df['family_person'] == plot_id)].copy()
        person_data = person_data.sort_values("year")
        quintile_num_map = {q: i+1 for i, q in enumerate(quintile_options)}
        person_data['quintile_num'] = person_data['quintile_label'].map(quintile_num_map)
        yvar = 'quintile_num' if plot_yaxis == "Quintile (1–5)" else 'head_labor_income'
        ytitle = "Income Quintile (1=Lowest, 5=Top)" if yvar == "quintile_num" else "Head Labor Income ($)"
        fig = px.line(person_data, x="year", y=yvar, title=f"Trajectory for ID {plot_id}", markers=True)
        if yvar == "quintile_num":
            fig.update_yaxes(title=ytitle, tickmode='linear', dtick=1)
        else:
            fig.update_yaxes(title=ytitle, tickformat=",", rangemode="tozero", showgrid=True)

        # --- Add horizon lines for each success window this individual achieved ---
        sy_goal_pairs = achievers_map.get(plot_id, [])
        for sy, gy in sy_goal_pairs:
            if sy != 1992:
                fig.add_vline(x=sy, line_dash="dash", line_color="green", annotation_text="Start",
                              annotation_position="top left")
            if gy != 1992:
                fig.add_vline(x=gy, line_dash="dash", line_color="orange", annotation_text="Goal Year",
                              annotation_position="top right")

        with col1:
            st.plotly_chart(fig, use_container_width=True)

    # DEBUG
    with st.expander("How mobility probability is calculated (method/math)", expanded=False):
        st.markdown("""
            **Mobility Probability Calculation:**
            - For a chosen starting quintile (and year, or all years), we find all individuals in the dataset who were in that quintile.
            - We track those same individuals to a future year (the 'time horizon' after start year), and check whether they reached the goal quintile.
            
            Each person can only “count” once in the probability calculation, and only for their first valid transition after each start window.

            If someone makes the move multiple times (from start → goal, after the time horizon), they are only counted once in the denominator and numerator.

            If someone reached and stayed in the goal quintile for several years, they are still only counted for being in the goal quintile at the first checked year after the horizon.

            A person is NOT require staying in the goal quintile for multiple years.

            People are NOT excluded who move to the goal quintile and then leave it, as long as they reached it at the right check year after the start+time horizon, they are counted as an achiever.

            If a person leaves and later re-enters the goal quintile at another valid window, they are still only counted once.


            - The probability is:
        """)
        st.latex(
            r"P(\text{Mobility}) = \frac{\text{Number who reach goal at horizon}}{\text{Number who started in start quintile}}"
        )
        st.markdown("This is an empirical estimate using real PSID longitudinal data.")

# --- Make sure you define robust_achievers_single_year as above ---
# --- Also, define quintile_colors, quintile_options as in your code ---

# ========== TAB 1: Matrix Check ==========
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

    # Animated Income Distribution & Static Side-by-Side
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


# ========== TAB 2: Income Trends (Quintile Thresholds Linear & Log) ==========
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
        # Linear Chart
        fig_original = px.line(
            melted, x='year', y='Threshold', color='Quintile', markers=True,
            title='Income Quintile and Top 5% Thresholds Over Time (Linear Scale)',
            labels={'year': 'Year', 'Threshold': 'Income Threshold ($)', 'Quintile': 'Income Group'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.subheader("Linear Scale")
        st.plotly_chart(fig_original, use_container_width=True)
        # Log Chart
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
                Log transformation reveals that income growth has **been evenly distributed** when scaled to across quintiles.
                    -This stablization across all qwuintiles suggests that the first plot that show exponential growth can be explained by inflation
                    - Which is the likely cause of sharp increases income during certain periods --> as present in the first plot head of households' labor income in higher quintiles (particularly "top") appear to sky rocket after  2008, onward i.e., the higher a starting heads' labor income, the larger the increase will be as inflation increase with time. Calcuation have were not completed on any relationship between certain years where income for the top quintile appears to increase at a faster rate than previous years, that correspond with years that the US experienced economic downturns like the Great Recession (~2009-2014) as well as the sharper increases after 1991 as the US economy bounced back from the brief recession of 1990 (CITE or you're a DUMBASS MARK). Certainly, there are other confounding variables that played into the economic downturns, but inflation general explains the expontential growth that is commonly found in longitudinal studies of income trajectories over time. Therefore, by log-scaling the data that is plotted above, we adjust for inflation factors, and are able to see all quintiles have similarly--stable--average trajectories between 1968-2022.
                """)

# ========== TAB 3: Income Trends (Mean, Median, Std Dev, with log plot) ==========
with tabs[3]:
    st.header("Income Trends: Mean, Median, & Std Dev (Linear & Log Scales)")
    income_stats = df.groupby('year')['head_labor_income'].agg(['mean', 'median', 'std']).reset_index()
    # Linear plot
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

# # ========== TAB 4: Ever Reached Comparison (Early vs Later) ==========
# with tabs[4]:
#     st.header("Mobility at Horizon: Early vs. Later Periods (1968–1995 vs 1996–2022)")

#     start_range = get_quintile_range(start_quintile, start_quintile_comp, quintile_options)
#     goal_range = get_quintile_range(goal_quintile, goal_quintile_comp, quintile_options)
#     early_period = (1968, 1995)
#     late_period = (1996, 2022)

#     # Calculate using the ONLY valid logic!
#     _, n_achievers_early, n_total_early, _ = robust_achievers_single_year(
#         df[df['year'].between(*early_period)], start_range, goal_range, time_horizon)
#     _, n_achievers_late, n_total_late, _ = robust_achievers_single_year(
#         df[df['year'].between(*late_period)], start_range, goal_range, time_horizon)

#     reached_early, total_early = n_achievers_early, n_total_early
#     reached_late, total_late = n_achievers_late, n_total_late

#     explanation = (
#         "Counts anyone who was observed in the start range and was in the goal range at the time horizon (start year + time horizon), for each period. "
#         "All metrics use strict, year-matched horizon mobility, not ever-reached logic."
#     )

#     if total_early == 0 and total_late == 0:
#         st.warning("No valid individuals found in either period.")
#     else:
#         col1, col2 = st.columns(2)
#         with col1:
#             st.metric("1968–1995", f"{reached_early / total_early:.2%}" if total_early else "N/A", f"{reached_early}/{total_early}")
#         with col2:
#             st.metric("1996–2022", f"{reached_late / total_late:.2%}" if total_late else "N/A", f"{reached_late}/{total_late}")

#         results_df = pd.DataFrame({
#             "Period": ["1968–1995", "1996–2022"],
#             "Reached Goal (%)": [
#                 reached_early / total_early * 100 if total_early else 0,
#                 reached_late / total_late * 100 if total_late else 0
#             ]
#         })
#         fig = px.bar(
#             results_df,
#             x="Period",
#             y="Reached Goal (%)",
#             text="Reached Goal (%)",
#             color="Period",
#             color_discrete_map={
#                 "1968–1995": "#1f77b4",
#                 "1996–2022": "#d62728"
#             },
#             title="% Reached Goal Quintile at Horizon",
#             labels={"Reached Goal (%)": "% Reached Goal"},
#             template="plotly_white"
#         )
#         fig.update_traces(texttemplate='%{text:.2f}%', textposition="outside")
#         st.plotly_chart(fig, use_container_width=True)
#     st.info(f"**Calculation Explanation:** {explanation}")


# ========== TAB 4: Multi-Person Income Trajectories ========== #
with tabs[4]:
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
        max_selections=20
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
            "- **Select up to 20 people** to visualize their income journeys.\n"
            "- Use the slider to restrict the year range shown.\n"
            "- Useful for exploring heterogeneity in income dynamics."
        )


# --- Footer ---
st.markdown("---")
st.markdown(
    "**DISCLAIMER:** The information contained in this dashboard reflects average probabilities and should not be interpreted in absolute terms. Life is not always easy and hardwork will always improve your odds of success. Certainly, anything can happen 😊! However, in this pursuit it is imperative to maintain selfless community values to support and promote a society with high 'neighborhood quality' avoid rampant individualism that historical ensured inequalities persisted. One may define rampant individualism as a society's collective proclivity to pursue an undefinable, subjective, and continually-changing view of success—independent of help—fueled by the notion that America is rich in opportunity and success is limitless; the absence of opportunity combined with rampant individualism, however, ensures issues persist, and a large portion population is unable to compete in the capitalist system (Chetty, p ,2024). By and large, most Americans still believe that success is the product of individual effort. The myth that hard work will allow anyone to overcome even the most difficult circumstances has endured across the centuries—even in the face of evidence to the contrary. Though this ‘boot-strap’ mentality is not entirely false, this myth creates the idea that the poorest in America can work hard and achieve anything. The notion that the United States is a “mythical land of plenty” in which the individual is free to secure success is belied by the fact that success is shaped-and at times pre-conditioned by forces largely outside of individual control—class, race/ethnicity, and gender. A primary source of inspiration for this dashboard was the work completed by Dr. Raj Chetty's team at Opportunity Insights who identified a variable they call 'neighborhood quality' as the most impactful variables for upward mobility. ")



