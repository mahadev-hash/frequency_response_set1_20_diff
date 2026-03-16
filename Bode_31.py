import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output

# =========================
# Load CSV
# =========================
CSV_PATH = r"F:\New folder\New folder\pvn20.csv"

data = pd.read_csv(CSV_PATH, sep=None, engine="python")
data.columns = data.columns.str.strip().str.lower()

# =========================
# Detect datasets
# =========================
sets = sorted([int(col.split("_")[1]) for col in data.columns if "frequency_" in col])

colors = [
"#1f77b4","#ff7f0e","#2ca02c","#d62728",
"#9467bd","#8c564b","#e377c2","#7f7f7f",
"#bcbd22","#17becf",
"#393b79","#637939","#8c6d31","#843c39",
"#7b4173","#3182bd","#e6550d","#31a354",
"#756bb1","#636363"
]

# =========================
# Extract data
# =========================
def get_set_data(i):

    freq = data[f"frequency_{i}"].dropna() / 1e6   # Hz → MHz
    gain = data[f"gain_{i}"].dropna()

    return freq, gain


# =========================
# Reference Set
# =========================
ref_freq, ref_gain = get_set_data(1)


# =========================
# Dash App
# =========================
app = Dash(__name__)
app.title = "Gain Comparison Dashboard"

app.layout = html.Div(

    style={"height":"100vh","display":"flex","flexDirection":"column"},

    children=[

        html.H3(
            "Gain Comparison (Reference = Set 1)",
            style={"textAlign":"center","margin":"5px"}
        ),

        html.Div([

            html.Label("Select Dataset"),

            dcc.Dropdown(
                id="dataset",
                options=[{"label":f"Set {i}","value":i} for i in sets if i != 1],
                value=sets[1],
                clearable=False,
                style={"width":"200px"}
            )

        ],style={
            "display":"flex",
            "justifyContent":"center",
            "alignItems":"center",
            "gap":"10px",
            "marginBottom":"5px"
        }),

        dcc.Graph(
            id="comparison-graph",
            style={"flexGrow":"1"}
        )
    ]
)


# =========================
# Callback
# =========================
@app.callback(
    Output("comparison-graph","figure"),
    Input("dataset","value")
)
def update_graph(selected_set):

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Gain Curves","Gain Difference vs Set 1")
    )

    freq,gain = get_set_data(selected_set)

    # Reference curve
    fig.add_trace(
        go.Scatter(
            x=ref_freq,
            y=ref_gain,
            name="Set 1 (Reference)",
            line=dict(color="black",width=3)
        ),
        row=1,col=1
    )

    # Selected curve
    fig.add_trace(
        go.Scatter(
            x=freq,
            y=gain,
            name=f"Set {selected_set}",
            line=dict(color=colors[(selected_set-1)%len(colors)],width=3)
        ),
        row=1,col=1
    )

    # Gain difference
    gain_diff = gain - ref_gain

    fig.add_trace(
        go.Scatter(
            x=freq,
            y=gain_diff,
            name="Difference",
            line=dict(color="red",width=3)
        ),
        row=1,col=2
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40,r=20,t=20,b=40)
    )

    fig.update_xaxes(title="Frequency (MHz)",row=1,col=1)
    fig.update_xaxes(title="Frequency (MHz)",row=1,col=2)

    fig.update_yaxes(title="Gain (dB)",row=1,col=1)
    fig.update_yaxes(title="Gain Difference (dB)",row=1,col=2)

    return fig


# =========================
# Run
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=8051)
