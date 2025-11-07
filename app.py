import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Global Flood Analysis", layout="wide")

# Global text colors
HEADER_COLOR = "#003D5C"

# Plot styling
PLOT_HEIGHT = 600
PLOT_BG_COLOR = "white"
WATER_COLOR = "#E6F7FF"
GRID_COLOR = "lightgray"

# Data years
START_YEAR = 2000
END_YEAR = 2024

# Widget defaults
DEFAULT_VARIABLE = "Economic Damages"
DEFAULT_NORMALIZE = True
DEFAULT_GEO_SCALE = "Admin1 (States/Provinces)"
DEFAULT_AGG_METRIC = "Mean"
DEFAULT_NUM_REGIONS = 15
MAX_NUM_REGIONS = 30

# Variable descriptions
VARIABLE_DESCRIPTIONS = {
    "Economic Damages": {
        "long_name": "Total economic damages ('000 $USD) adjusted to 2023 U.S dollar equivalent.",
        "norm_descrip": "Normalized by GDP",
    },
    "Population Affected": {
        "long_name": "Number of people injured, made homeless, or otherwise impacted by the flood.",
        "norm_descrip": "Normalized by total population",
    },
    "Flooded Area": {
        "long_name": "Total inundated area derived from MODIS satellite imagery.",
        "norm_descrip": "Normalized by total area",
    },
    "Flood Count": {"long_name": "Number of recorded floods.", "norm_descrip": ""},
    "Avg Precipitation (Flood)": {
        "long_name": "Average precipitation rate during floods.",
        "norm_descrip": "",
    },
    "Avg 75th Percentile Precipitation (Flood)": {
        "long_name": "Average of the top 25% of precipitation rates during floods. Indicates heavy rainfall.",
        "norm_descrip": "",
    },
}

# Variable-specific color palettes
COLOR_PALETTES = {
    "Flooded Area": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues
    "Economic Damages": [
        "#E8F5E9",
        "#81C784",
        "#66BB6A",
        "#4CAF50",
        "#388E3C",
        "#1B5E20",
    ],  # Greens
    "Population Affected": [
        "#F3E5F5",
        "#CE93D8",
        "#BA68C8",
        "#AB47BC",
        "#8E24AA",
        "#6A1B9A",
    ],  # Purples
    "Flood Count": [
        "#FFEBEE",
        "#EF9A9A",
        "#E57373",
        "#EF5350",
        "#E53935",
        "#C62828",
    ],  # Reds
    "Avg Precipitation (Flood)": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues (same as Flooded Area)
    "Avg 75th Percentile Precipitation (Flood)": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues (same as Flooded Area)
}


# Helper functions
def get_plot_title_config(title_text):
    """Create standardized title configuration for plots"""
    return dict(
        text=title_text, x=0.5, xanchor="center", font=dict(size=20, color=HEADER_COLOR)
    )


def generate_title(variable, agg_metric, normalize):
    """Generate appropriate title based on variable and normalization"""
    if variable == "Flood Count":
        return "Flood Event Count"

    # Precipitation variables don't use normalization
    precip_vars = [
        "Avg Precipitation (Flood)",
        "Avg 75th Percentile Precipitation (Flood)",
    ]
    if variable in precip_vars:
        return f"{agg_metric} {variable}"

    if normalize:
        norm_labels = {
            "Economic Damages": f"{agg_metric} Economic Damages (% of GDP)",
            "Population Affected": f"{agg_metric} Population Affected (% of Total)",
            "Flooded Area": f"{agg_metric} Flooded Area (% of Total Area)",
        }
        return norm_labels.get(variable, f"{agg_metric} {variable}")

    return f"{agg_metric} {variable}"


def reset_defaults():
    """Reset all widgets to their default values"""
    st.session_state.year_range = (START_YEAR, END_YEAR)
    st.session_state.variable = DEFAULT_VARIABLE
    st.session_state.normalize = DEFAULT_NORMALIZE
    st.session_state.geo_scale = DEFAULT_GEO_SCALE
    st.session_state.agg_metric = DEFAULT_AGG_METRIC
    st.session_state.num_regions_slider = DEFAULT_NUM_REGIONS


# Generate dummy data for visualization
@st.cache_data
def create_dummy_data():
    """Create fake flood data for layout testing"""
    countries = [
        "USA",
        "CHN",
        "IND",
        "BRA",
        "IDN",
        "PAK",
        "NGA",
        "BGD",
        "RUS",
        "MEX",
        "JPN",
        "ETH",
        "PHL",
        "EGY",
        "VNM",
        "COD",
        "TUR",
        "IRN",
        "DEU",
        "THA",
    ]

    data = []
    for country in countries:
        for year in range(START_YEAR, END_YEAR + 1):
            n_events = np.random.poisson(3)
            for _ in range(n_events):
                data.append(
                    {
                        "country_code": country,
                        "year": year,
                        "damages": np.random.lognormal(15, 2),
                        "damages_norm": np.random.lognormal(5, 1.5),
                        "population_affected": np.random.lognormal(10, 2),
                        "pop_affected_norm": np.random.lognormal(3, 1),
                        "flooded_area": np.random.lognormal(8, 1.5),
                        "flooded_area_norm": np.random.lognormal(2, 1),
                        "flood_type": np.random.choice(
                            ["Riverine", "Flash", "General"]
                        ),
                        "avg_precip": np.random.lognormal(3, 0.5),  # mm/day
                        "extreme_precip_75": np.random.lognormal(
                            4, 0.6
                        ),  # mm/day, higher than avg
                    }
                )

    return pd.DataFrame(data)


df = create_dummy_data()

# Sidebar
st.sidebar.title("Data Options")
st.sidebar.caption(
    "Explore spatially and temporally disaggregated flood dataset. Dataset integrated from satellite observations, disaster records, and climate reanalysis data."
)

# Core filters
st.sidebar.markdown("**Data Selection**")
year_range = st.sidebar.slider(
    "Time Period", START_YEAR, END_YEAR, (START_YEAR, END_YEAR), key="year_range"
)

variable = st.sidebar.selectbox(
    "Variable",
    [
        "Economic Damages",
        "Population Affected",
        "Flooded Area",
        "Flood Count",
        "Avg Precipitation (Flood)",
        "Avg 75th Percentile Precipitation (Flood)",
    ],
    index=[
        "Economic Damages",
        "Population Affected",
        "Flooded Area",
        "Flood Count",
        "Avg Precipitation (Flood)",
        "Avg 75th Percentile Precipitation (Flood)",
    ].index(DEFAULT_VARIABLE),
    key="variable",
)

# Show variable description
st.sidebar.caption(VARIABLE_DESCRIPTIONS[variable]["long_name"])

# Derive theme colors from COLOR_PALETTES
palette = COLOR_PALETTES[variable]
colors = {
    "light": palette[0],  # Lightest shade
    "medium": palette[2],  # Medium shade
    "primary": palette[3],  # Primary brand color
    "accent": palette[4],  # Accent color
    "secondary": palette[5],  # Darkest shade
}

# Apply dynamic CSS
st.markdown(
    f"""
    <style>
    /* Main title styling */
    h1 {{
        color: {HEADER_COLOR};
        font-weight: 700;
    }}

    /* Headers */
    h2, h3 {{
        color: {HEADER_COLOR};
        font-size: 2rem;
        font-weight: 600;
    }}

    /* Metric cards */
    [data-testid="stMetricValue"] {{
        color: {colors['primary']};
        font-size: 2rem;
    }}

    /* Tabs - Full width tab style */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0px;
        background-color: transparent;
        width: 100%;
        display: flex;
    }}

    .stTabs [data-baseweb="tab-list"] button {{
        font-size: 1.2rem;
        font-weight: 600;
        background-color: #f0f2f6;
        color: #000000;
        border-radius: 0px;
        padding: 16px 24px;
        border: none;
        border-bottom: 3px solid transparent;
        flex: 1;
    }}

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background-color: white;
        color: {colors['secondary']};
        border-bottom: 3px solid {colors['primary']};
    }}

    .stTabs [data-baseweb="tab-list"] button:hover {{
        background-color: #e8eaed;
        color: {colors['secondary']};
    }}

    .stTabs [data-baseweb="tab-border"] {{
        display: none;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {colors['light']} 0%, {colors['light']}dd 100%);
        min-width: 300px;
        max-width: 400px;
    }}

    [data-testid="stSidebar"] h1 {{
        color: #000000 !important;
    }}

    /* Info boxes */
    .stAlert {{
        background-color: {colors['light']};
        border-left: 4px solid {colors['medium']};
    }}

    /* Buttons */
    .stButton button {{
        background: {colors['secondary']};
        color: white;
        border: none;
        font-weight: 600;
    }}

    .stButton button:hover {{
        background: {colors['accent']};
    }}

    /* Dividers */
    hr {{
        border-color: {colors['medium']};
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# Simple toggle for absolute vs normalized (only show if not Flood Count or precipitation)
precip_vars = ["Avg Precipitation (Flood)", "Avg 75th Percentile Precipitation (Flood)"]
if variable not in ["Flood Count"] + precip_vars:
    normalize = st.sidebar.checkbox(
        "Normalize", value=DEFAULT_NORMALIZE, key="normalize"
    )
    # Show normalization description if it exists
    norm_desc = VARIABLE_DESCRIPTIONS[variable]["norm_descrip"]
    if norm_desc:
        st.sidebar.caption(norm_desc)
else:
    normalize = False  # Normalization doesn't apply to counts or precipitation

st.sidebar.divider()

# Aggregation options
st.sidebar.markdown("**Aggregation**")
geo_scale = st.sidebar.selectbox(
    "Geographic Level",
    ["Admin1 (States/Provinces)", "Country", "UN Subregion"],
    index=["Admin1 (States/Provinces)", "Country", "UN Subregion"].index(
        DEFAULT_GEO_SCALE
    ),
    key="geo_scale",
)

agg_metric = st.sidebar.selectbox(
    "Statistic",
    ["Mean", "Median", "Max", "Sum"],
    index=["Mean", "Median", "Max", "Sum"].index(DEFAULT_AGG_METRIC),
    key="agg_metric",
)

# Reset button at bottom of sidebar
st.sidebar.divider()
st.sidebar.button(
    "Reset to defaults", on_click=reset_defaults, use_container_width=True
)

# Main content
st.title(f"Global Flood Impact Analysis")

# Filter data
filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

# Map variable to column name
var_map = {
    "Economic Damages": ("damages", "damages_norm"),
    "Population Affected": ("population_affected", "pop_affected_norm"),
    "Flooded Area": ("flooded_area", "flooded_area_norm"),
    "Flood Count": (None, None),
    "Avg Precipitation (Flood)": ("avg_precip", None),
    "Avg 75th Percentile Precipitation (Flood)": ("extreme_precip_75", None),
}

abs_col, norm_col = var_map[variable]

# Aggregate data
if variable == "Flood Count":
    agg_data = filtered_df.groupby("country_code").size().reset_index(name="count")
    value_col = "count"
else:
    value_col = norm_col if (normalize and norm_col) else abs_col

    agg_funcs = {"Mean": "mean", "Median": "median", "Max": "max", "Sum": "sum"}
    agg_data = (
        filtered_df.groupby("country_code")[value_col]
        .agg(agg_funcs[agg_metric])
        .reset_index()
    )

# Dynamic title
title = generate_title(variable, agg_metric, normalize)

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(
    ["Map View", "Top Regions", "Global Timeseries", "About"]
)

# Get the color palette for current variable
current_colors = COLOR_PALETTES[variable]

with tab1:
    fig = px.choropleth(
        agg_data,
        locations="country_code",
        locationmode="ISO-3",
        color=value_col,
        color_continuous_scale=current_colors,
        hover_name="country_code",
    )

    fig.update_layout(
        height=PLOT_HEIGHT,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            oceancolor=WATER_COLOR,
            lakecolor=WATER_COLOR,
        ),
        font=dict(color=HEADER_COLOR),
        title=get_plot_title_config(f"{title} by {geo_scale}"),
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Slider to select number of regions to display
    max_regions = (
        DEFAULT_NUM_REGIONS if geo_scale == "UN Subregion" else MAX_NUM_REGIONS
    )
    num_regions = st.slider(
        "Number of regions",
        min_value=5,
        max_value=max_regions,
        value=DEFAULT_NUM_REGIONS,
        step=5,
        key="num_regions_slider",
    )

    top_n = agg_data.nlargest(num_regions, value_col).copy()
    top_n.columns = ["Country Code", title]
    top_n = top_n.reset_index(drop=True)
    top_n.index = top_n.index + 1

    # Create bar chart with matching colors
    bar_fig = px.bar(
        top_n,
        x=title,
        y="Country Code",
        orientation="h",
        color=title,
        color_continuous_scale=current_colors,
        labels={title: title, "Country Code": ""},
    )

    bar_fig.update_layout(
        height=PLOT_HEIGHT,
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        font=dict(color=HEADER_COLOR),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PLOT_BG_COLOR,
        title=get_plot_title_config(title),
        coloraxis_showscale=False,
    )

    bar_fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" + title + ": %{x:.2f}<extra></extra>"
    )

    st.plotly_chart(bar_fig, use_container_width=True)

with tab3:
    # Time series - total across all countries (always sum, regardless of aggregation setting)
    if variable == "Flood Count":
        time_series = filtered_df.groupby("year").size().reset_index(name="Total")
        ts_label = "Total Flood Events"
    else:
        ts_value_col = norm_col if (normalize and norm_col) else abs_col
        time_series = filtered_df.groupby("year")[ts_value_col].sum().reset_index()
        time_series.columns = ["year", "Total"]
        ts_label = generate_title(variable, "Total", normalize)

    # Create line chart
    line_fig = px.line(
        time_series,
        x="year",
        y="Total",
        markers=True,
        labels={"year": "Year", "Total": ts_label},
    )

    line_fig.update_traces(line_color=colors["primary"], marker=dict(size=8))

    line_fig.update_layout(
        height=PLOT_HEIGHT,
        font=dict(color=HEADER_COLOR),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PLOT_BG_COLOR,
        showlegend=False,
        title=get_plot_title_config(f"{ts_label} Over Time"),
    )

    line_fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR)
    line_fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR)

    st.plotly_chart(line_fig, use_container_width=True)

with tab4:
    st.subheader("About This Project")
    st.markdown("Master's Thesis, Colorado State University, 2025")

    st.markdown("### Data Sources")
    st.markdown(
        """
    This application visualizes flood event data derived from multiple sources:
    - **EM-DAT International Disaster Database**: Disaster impact metrics including economic damages, population affected, and event records
    - **MODIS Surface Reflectance Imagery**: Satellite-derived flood extent and duration data
    - **Other geospatial and demographic datasets**
    """
    )

    st.markdown("### Author")
    st.markdown(
        """
        <div style="margin-top: 10px;">
            <div>Nicole Keeney</div>
            <div style="margin-top: 10px;">
                <a href="https://linkedin.com/in/nicole-keeney" target="_blank" style="text-decoration: none; margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="20" height="20" style="vertical-align: middle;">
                </a>
                <a href="https://github.com/nicolejkeeney" target="_blank" style="text-decoration: none;">
                    <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="20" height="20" style="vertical-align: middle;">
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
