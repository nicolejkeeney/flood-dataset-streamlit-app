"""
Preprocess GAUL 2015 administrative boundary data.

Filters GAUL Level 1 boundaries to only include administrative units
present in the flood dataset, then exports as optimized parquet format
for use in the Streamlit application.
"""

import geopandas as gpd
import pandas as pd

# Input data
INPUT_DATA_DIR = "./data/boundaries_original/"
GAUL_L1_FILEPATH = f"{INPUT_DATA_DIR}GAUL_2015/g2015_2014_1/"
UNSD_M49_FILEPATH = f"{INPUT_DATA_DIR}UNSD_M49.csv"
COUNTRY_BOUNDARIES_FILEPATH = f"{INPUT_DATA_DIR}/ne_110m_admin_0_countries"

# Output data
OUTPUT_DATA_DIR = "./data/boundaries_preprocessed/"
GAUL_L1_EXPORT_FILEPATH = f"{OUTPUT_DATA_DIR}GAUL_L1_2015.parquet"
UN_SUBREGIONS_EXPORT_FILEPATH = f"{OUTPUT_DATA_DIR}UN_subregions.parquet"


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

    ## ====== Preprocess GAUL data =====

    print("Preprocessing GAUL L1 data...")
    gaul_l1.rename(
        columns={"ADM1_CODE": "adm1_code"}, inplace=True
    )  # Rename column to match flood_df
    gaul_l1 = gaul_l1[["adm1_code", "geometry"]]  # Get only necessary columns
    print(f"✓ Complete")

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

    countries_gdf.rename(columns={"ISO_A3": "ISO"}, inplace=True)

    # Drop Antarctica
    countries_gdf = countries_gdf[countries_gdf["ADMIN"] != "Antarctica"]

    # Get geometries for each country from natural earth dataset
    m49_gdf = m49_df.merge(countries_gdf[["ISO", "geometry"]], on="ISO", how="left")
    m49_gdf = gpd.GeoDataFrame(m49_gdf)

    # Merge country geometries by subregion
    # Drop countries with NaN for geometry
    m49_subregion_gdf = (
        m49_gdf[["Subregion", "geometry"]]
        .dropna(subset=["geometry"])
        .dissolve(by="Subregion")
    )
    print(f"✓ Complete")

    ## ====== Export data ======

    print(f"Exporting preprocessed GAUL L1 file to {GAUL_L1_EXPORT_FILEPATH}...")
    gaul_l1.to_parquet(GAUL_L1_EXPORT_FILEPATH, index=False)
    print("✓ Exported")

    print(
        f"Exporting preprocessed UN subregion file to {UN_SUBREGIONS_EXPORT_FILEPATH}..."
    )
    m49_subregion_gdf.to_parquet(UN_SUBREGIONS_EXPORT_FILEPATH, index=False)
    print("✓ Exported")


if __name__ == "__main__":
    main()
