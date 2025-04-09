from __future__ import annotations

import logging
import os
import sys
import types

logging.basicConfig(level=logging.INFO)

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from dash import dcc, html
from plotly.graph_objects import Figure

# Monkey patch / patch not required imports (from SelectZyme) as workaround to avoid module not found errors
sys.modules['taxoniq'] = types.SimpleNamespace()

import external.selectzyme.src.pages.dimred as dimred
import external.selectzyme.src.pages.eda as eda
import external.selectzyme.src.pages.mst as mst
import external.selectzyme.src.pages.single_linkage as sl
from external.selectzyme.src.pages.callbacks import register_callbacks
from external.selectzyme.src.selectzyme.visualizer import plot_2d


def import_results(input_dir: str = "data/") -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """
    Imports and loads results from specified input directory.
    Args:
        input_dir (str): Path to the directory containing the input files. Defaults to "data/".
    Returns:
        tuple: A tuple containing the following:
            - pd.DataFrame: DataFrame loaded from "df.parquet".
            - np.ndarray: Reduced feature matrix loaded from "X_red.npz".
            - np.ndarray: Minimum spanning tree (MST) loaded from "hdbscan_structures.npz".
            - np.ndarray: Linkage matrix loaded from "hdbscan_structures.npz".
    """
    df = pd.read_parquet(os.path.join(input_dir, "df.parquet"))
    X_red = np.load(os.path.join(input_dir, "X_red.npz"))["X_red"]
    structures = np.load(os.path.join(input_dir, "hdbscan_structures.npz"))
    mst = structures["mst"]
    linkage = structures["linkage"]

    return df, X_red, mst, linkage


def main(app, input_dir) -> None:
    export_path = "data/"  # paths not really needed here maybe route to /tmp
    legend_attribute = "cluster"
    df, X_red, mst_tree, linkage = import_results(input_dir)

    # Perf: create DimRed and MST plot only once
    fig = plot_2d(df, X_red, legend_attribute=legend_attribute)
    fig_mst = Figure(fig)  # copy required else fig will be modified by mst creation

    # Create page layouts
    dash.register_page("eda", 
                       name="Explanatory Data Analysis", 
                       layout=eda.layout(df, out_file=export_path + "_eda.html"))
    dash.register_page(
        "dim",
        name="Protein Landscape",
        layout=dimred.layout(df, fig),
    )
    dash.register_page(
        "mst", name="Connectivity", layout=mst.layout(mst_tree, df, X_red, fig_mst)
    )
    dash.register_page("slc", name="Phylogeny", layout=sl.layout(_linkage=linkage, 
                                                                 df=df, 
                                                                 legend_attribute=legend_attribute, 
                                                                 out_file=export_path + "_slc.html"))

    # Register callbacks
    register_callbacks(app, df, X_red)


    # App layout with navigation links and page container
    app.layout = dbc.Container(
        [
            dbc.NavbarSimple(
                brand="Analysis results",
                color="primary",
                dark=True,
            ),
            html.Div(
                [
                    dcc.Store(
                        id="shared-data", data=[], storage_type="memory"
                    ),  # !saves table data from layouts via callbacks defined in the page layouts
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink(page["name"], href=page["path"]))
                            for page in dash.page_registry.values()
                        ],
                        pills=True,
                    ),
                    html.Hr(),
                    dash.page_container,  # Displays the content of the current page
                ]
            ),
        ],
        fluid=True,
    )


if __name__ == "__main__":
    app = dash.Dash(
        __name__,
        use_pages=True,
        pages_folder="external/selectzyme/src/pages",
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.BOOTSTRAP],  # Optional for styling
    )
    # server = app.server  # this line is only needed when deployed on a public server
    
    input_dir = "data/blast_psi/"

    main(app, input_dir)
    app.run(host="127.0.0.1", port=8050, debug=False)  # run_server for backwards compatibility (older dash versions)
