"""
Preprocess data for use in Streamlit app

"""

import geopandas as gpd
import pandas as pd

# Dictionary mapping problematic adm1_codes to correct countries per GAUL
# These codes appear in multiple countries in the source data but should be assigned to one country
COUNTRY_CORRECTIONS = {
    2720: "Spain",
    2961: "Timor-Leste",
    25351: "Montenegro",
    25355: "Montenegro",
    25356: "Montenegro",
    25365: "Montenegro",
    25372: "Serbia",
    25373: "Serbia",
    25375: "Serbia",
    25376: "Serbia",
    25378: "Serbia",
    25379: "Serbia",
    25381: "Serbia",
    25385: "Serbia",
    25389: "Serbia",
    25394: "Serbia",
    25395: "Serbia",
    40408: "Jammu and Kashmir",
    40409: "Jammu and Kashmir",
    40422: "Jammu and Kashmir",
    40423: "Jammu and Kashmir",
    40424: "Jammu and Kashmir",
    40425: "Jammu and Kashmir",
    40426: "Jammu and Kashmir",
    40427: "Jammu and Kashmir",
    40428: "Jammu and Kashmir",
    40429: "Jammu and Kashmir",
    40430: "Jammu and Kashmir",
    40431: "Jammu and Kashmir",
}

# Input data
INPUT_DATA_DIR = "./data/original/"
GAUL_L1_FILEPATH = f"{INPUT_DATA_DIR}GAUL_2015/g2015_2014_1/"
UNSD_M49_FILEPATH = f"{INPUT_DATA_DIR}UNSD_M49.csv"
COUNTRY_BOUNDARIES_FILEPATH = f"{INPUT_DATA_DIR}/ne_110m_admin_0_countries"
LAND_FILEPATH = f"{INPUT_DATA_DIR}ne_110m_land"
FLOOD_CSV_FILEPATH = f"{INPUT_DATA_DIR}event_level_flood_dataset.csv"

# Output data
OUTPUT_DATA_DIR = "./data/preprocessed/"
ADMIN1_AGGREGATED_FILEPATH = f"{OUTPUT_DATA_DIR}app_admin1_aggregated.parquet"
COUNTRY_AGGREGATED_FILEPATH = f"{OUTPUT_DATA_DIR}app_country_aggregated.parquet"
SUBREGION_AGGREGATED_FILEPATH = f"{OUTPUT_DATA_DIR}app_subregion_aggregated.parquet"
ANNUAL_GLOBAL_FILEPATH = f"{OUTPUT_DATA_DIR}app_annual_global_totals.parquet"
LAND_OUTLINE_FILEPATH = f"{OUTPUT_DATA_DIR}app_land_outline.parquet"


def main():
    """Main preprocessing pipeline for GAUL L1 boundaries."""

    ## ====== Read in data ======
    print("Loading GAUL L1 (admin1) boundaries...")
    gaul_l1 = gpd.read_file(GAUL_L1_FILEPATH)
    print(f"✓ Loaded")

    print("Loading M49 United Nations Statistics Division table...")
    m49_df = pd.read_csv(UNSD_M49_FILEPATH)
    print(f"✓ Loaded")

    print("Loading natural earth boundary shapefile...")
    countries_gdf = gpd.read_file(COUNTRY_BOUNDARIES_FILEPATH)
    print(f"✓ Loaded")

    print("Loading natural earth land shapefile...")
    land_gdf = gpd.read_file(LAND_FILEPATH)
    print(f"✓ Loaded")

    print("Loading flood dataset...")
    flood_df = pd.read_csv(FLOOD_CSV_FILEPATH)
    print(f"✓ Loaded")

    ## ====== Preprocess GAUL data =====

    print("Preprocessing GAUL L1 data...")
    gaul_l1.rename(
        columns={"ADM1_CODE": "adm1_code"}, inplace=True
    )  # Rename column to match flood_df
    gaul_l1 = gaul_l1[["adm1_code", "geometry"]]  # Get only necessary columns

    # Simplify geometries for faster rendering (tolerance in degrees, ~0.1 ≈ 11km)
    print("Simplifying Admin1 geometries...")
    gaul_l1["geometry"] = gaul_l1["geometry"].simplify(
        tolerance=0.1, preserve_topology=True
    )
    print(f"✓ Complete")

    ## ====== Preprocess flood dataset =====

    # Subset table to get columns needed in app only
    app_cols = [
        "id",
        "mon-yr-adm1-id",
        "mon-yr",
        "adm1_code",
        "adm1_name",
        "ISO",
        "Country",
        "Subregion",
        "flooded_area",
        "flooded_area (normalized by adm1 area)",
        "Total Damage, Adjusted ('000 US$) (population-weighted)",
        "Total Damage, Adjusted ('000 US$) (population-weighted, normalized by GDP)",
        "Total Affected (population-weighted)",
        "Total Affected (population-weighted, normalized)",
        "event_precip_mean (mm/day)",
        "event_precip_75_quant_mean (mm/day)",
    ]
    flood_df_subset = flood_df[app_cols].copy()

    # Drop all rows with missing time info
    flood_df_subset = flood_df_subset.dropna(subset=["mon-yr"])

    # Correct country assignments for problematic admin1 codes
    print("Correcting country assignments for problematic admin1 codes...")
    for code, correct_country in COUNTRY_CORRECTIONS.items():
        mask = flood_df_subset["adm1_code"] == code
        if mask.any():
            flood_df_subset.loc[mask, "Country"] = correct_country
    print(f"✓ Corrected {len(COUNTRY_CORRECTIONS)} admin1 codes")

    # Rename columns for better readibility in app
    flood_df_subset.rename(
        columns={
            "Subregion": "UN Subregion",
            "adm1_name": "Admin1 (States/Provinces)",
            "flooded_area (normalized by adm1 area)": "flooded_area_norm",
            "event_precip_mean (mm/day)": "avg_precip",
            "event_precip_75_quant_mean (mm/day)": "extreme_precip_75",
            "Total Affected (population-weighted)": "pop_affected",
            "Total Affected (population-weighted, normalized)": "pop_affected_norm",
            "Total Damage, Adjusted ('000 US$) (population-weighted)": "damages",
            "Total Damage, Adjusted ('000 US$) (population-weighted, normalized by GDP)": "damages_norm",
        },
        inplace=True,
    )

    # Multiply damages by 1000 to go from $ in thousands to just $
    # Improves display on streamlit
    flood_df_subset["damages"] = flood_df_subset["damages"] * 1000

    # Add year column
    flood_df_subset["year"] = flood_df_subset["mon-yr"].str[-4:].astype(int)

    ## ====== Preprocess country boundaries =====

    print("Preprocessing country boundaries...")
    countries_gdf.rename(columns={"ISO_A3": "ISO"}, inplace=True)
    countries_subset = countries_gdf[["ISO", "geometry"]].copy()

    ## ====== Preprocess UN subregions =====

    print("Preprocessing UN subregion data...")
    # Rename & subset columns
    m49_df = m49_df[["ISO-alpha3 Code", "Sub-region Name", "Region Name"]].rename(
        columns={
            "ISO-alpha3 Code": "ISO",
            "Sub-region Name": "Subregion",
            "Region Name": "Region",
        }
    )

    # Get geometries for each country from natural earth dataset
    m49_gdf = m49_df.merge(countries_subset[["ISO", "geometry"]], on="ISO", how="left")
    m49_gdf = gpd.GeoDataFrame(m49_gdf)

    # Merge country geometries by subregion
    # Drop countries with NaN for geometry
    m49_subregion_gdf = (
        m49_gdf[["Subregion", "geometry"]]
        .dropna(subset=["geometry"])
        .dissolve(by="Subregion")
    )

    ## ====== Aggregate flood data by geographic level ======

    # Define metrics to aggregate
    metrics = [
        "damages",
        "damages_norm",
        "pop_affected",
        "pop_affected_norm",
        "flooded_area",
        "flooded_area_norm",
        "avg_precip",
        "extreme_precip_75",
    ]

    # Aggregation functions
    agg_funcs = ["mean", "median", "max", "sum"]

    print("Aggregating flood data at Admin1 level...")

    # Group by admin1 and compute all metrics
    admin1_agg = (
        flood_df_subset.groupby("adm1_code")[metrics].agg(agg_funcs).reset_index()
    )

    # Flatten column names: e.g., ('damages', 'mean') -> 'damages_mean'
    admin1_agg.columns = ["adm1_code"] + [
        f"{metric}_{func}" for metric in metrics for func in agg_funcs
    ]

    # Add flood count
    admin1_count = (
        flood_df_subset.groupby("adm1_code").size().reset_index(name="flood_count")
    )
    admin1_agg = admin1_agg.merge(admin1_count, on="adm1_code")

    # Add region name and country name for display
    admin1_names = flood_df_subset[
        ["adm1_code", "Admin1 (States/Provinces)", "Country"]
    ].drop_duplicates(subset=["adm1_code"])
    admin1_agg = admin1_agg.merge(admin1_names, on="adm1_code", how="left")

    # Replace None or "Administrative region not available" with "Unknown Name (code: [code])"
    mask = (admin1_agg["Admin1 (States/Provinces)"].isna()) | (
        admin1_agg["Admin1 (States/Provinces)"] == "Administrative unit not available"
    )
    admin1_agg.loc[mask, "Admin1 (States/Provinces)"] = (
        "Unknown Name (code: "
        + admin1_agg.loc[mask, "adm1_code"].astype(int).astype(str)
        + ")"
    )

    # Merge with geometries
    admin1_final = gaul_l1.merge(admin1_agg, on="adm1_code", how="inner")
    print(f"✓ Complete ({len(admin1_final)} regions)")

    print("Aggregating flood data at Country level...")
    country_agg = flood_df_subset.groupby("ISO")[metrics].agg(agg_funcs).reset_index()
    country_agg.columns = ["ISO"] + [
        f"{metric}_{func}" for metric in metrics for func in agg_funcs
    ]
    country_count = (
        flood_df_subset.groupby("ISO").size().reset_index(name="flood_count")
    )
    country_agg = country_agg.merge(country_count, on="ISO")

    # Add country name for hover display
    country_names = flood_df_subset[["ISO", "Country"]].drop_duplicates()
    country_agg = country_agg.merge(country_names, on="ISO", how="left")
    country_final = countries_subset.merge(country_agg, on="ISO", how="inner")
    print(f"✓ Complete ({len(country_final)} countries)")

    print("Aggregating flood data at UN Subregion level...")
    subregion_agg = (
        flood_df_subset.groupby("UN Subregion")[metrics].agg(agg_funcs).reset_index()
    )
    subregion_agg.columns = ["UN Subregion"] + [
        f"{metric}_{func}" for metric in metrics for func in agg_funcs
    ]
    subregion_count = (
        flood_df_subset.groupby("UN Subregion").size().reset_index(name="flood_count")
    )
    subregion_agg = subregion_agg.merge(subregion_count, on="UN Subregion")

    # Reset index on m49_subregion_gdf to get Subregion as a column
    m49_subregion_gdf_reset = m49_subregion_gdf.reset_index()

    # Rename to match the flood data column name
    m49_subregion_gdf_reset.rename(columns={"Subregion": "UN Subregion"}, inplace=True)
    subregion_final = m49_subregion_gdf_reset.merge(
        subregion_agg, on="UN Subregion", how="inner"
    )
    print(f"✓ Complete ({len(subregion_final)} subregions)")

    ## ====== Create annual global totals for timeseries ======

    print("Creating annual global totals...")

    # Sum all metrics by year
    annual_global = flood_df_subset.groupby("year")[metrics].sum().reset_index()

    # Add flood count
    annual_count = (
        flood_df_subset.groupby("year").size().reset_index(name="flood_count")
    )
    annual_global = annual_global.merge(annual_count, on="year")
    print(f"✓ Complete ({len(annual_global)} years)")

    ## ====== Export data ======

    print(f"Exporting Admin1 aggregated data to {ADMIN1_AGGREGATED_FILEPATH}...")
    admin1_final.to_parquet(ADMIN1_AGGREGATED_FILEPATH, index=False)
    print("✓ Exported")

    print(f"Exporting Country aggregated data to {COUNTRY_AGGREGATED_FILEPATH}...")
    country_final.to_parquet(COUNTRY_AGGREGATED_FILEPATH, index=False)
    print("✓ Exported")

    print(
        f"Exporting UN Subregion aggregated data to {SUBREGION_AGGREGATED_FILEPATH}..."
    )
    subregion_final.to_parquet(SUBREGION_AGGREGATED_FILEPATH, index=False)
    print("✓ Exported")

    print(f"Exporting annual global totals to {ANNUAL_GLOBAL_FILEPATH}...")
    annual_global.to_parquet(ANNUAL_GLOBAL_FILEPATH, index=False)
    print("✓ Exported")

    print(f"Exporting land outline to {LAND_OUTLINE_FILEPATH}...")
    land_gdf.to_parquet(LAND_OUTLINE_FILEPATH, index=False)
    print("✓ Exported")


if __name__ == "__main__":
    main()
