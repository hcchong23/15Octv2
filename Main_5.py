import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from DPD_DCD_2 import refresh_DPD_DCD
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# year_list1, class_list1, dummy_months,  snapshot_list1  = refresh_DPD_DCD()
year_list1 = pd.read_excel("Dashboard_data_summary.xlsx", sheet_name="Years")["Year"].dropna().astype(str).tolist()
class_list1 = pd.read_excel("Dashboard_data_summary.xlsx", sheet_name="Classes")["Class"].dropna().astype(str).tolist()
dummy_months = pd.read_excel("Dashboard_data_summary.xlsx", sheet_name="DummyMonths")["Month"].dropna().astype(str).tolist()
snapshot_list1 = pd.read_excel("Dashboard_data_summary.xlsx", sheet_name="Snapshots")["Snapshot"].dropna().astype(str).tolist()


latest_year = ['2025']

# Convert to datetime, sort and back to string
snapshot_list1_dt = [datetime.strptime(x, "%m-%Y") for x in snapshot_list1]
snapshot_list1_dt.sort()
snapshot_list1 = [dt.strftime("%m-%Y") for dt in snapshot_list1_dt]

dummy_months = [datetime.strptime(date_str, "%m-%Y") for date_str in dummy_months]
latest_Tran_MonthYear = max(dummy_months)
# Format back to string
latest_Tran_MonthYear = latest_Tran_MonthYear.strftime("%m-%Y")

# Latest MPC file, not overwrite "NA" as nan 
df_final = pd.read_excel('Dashboard_data_summary.xlsx',sheet_name='Summary',keep_default_na=False)
scheme_list1 = df_final['Cls'].unique().tolist()

df_mcf = pd.read_excel('Dashboard_data_summary.xlsx',sheet_name='MCF',keep_default_na=False)
df_mcf_year = df_mcf['UwYr'].unique().tolist()

# Loss Ratio Chart by UY    
def create_loss_ratio_chart():
    summary = (
        df_final
        .groupby(["UWY", "Tran_MonthYear","Tran_MonthYear_dt"], as_index=False)
        [["PremiumAmount_cumsum", "ClaimAmount"]]
        .sum()
    )
    
    # Fix loss ratio calculation - ensure no division by zero
    summary["LossRatio"] = summary["ClaimAmount"] / summary["PremiumAmount_cumsum"]
    summary['LossRatio'] = pd.to_numeric(summary['LossRatio'], errors='coerce')
    summary['UWY'] = summary['UWY'].astype(str)
    summary = summary[summary['Tran_MonthYear'].isin(snapshot_list1)]
    summary = summary.sort_values(by="Tran_MonthYear_dt")

    
    # Remove invalid values (inf, -inf, very large numbers)
    summary = summary[summary['LossRatio'].between(-10, 10)]  # Reasonable loss ratio range
    summary = summary.dropna(subset=['LossRatio'])
    
    
    # Create the chart
    lossratio_uy_fig = px.line(
        summary,
        x="Tran_MonthYear",
        y="LossRatio",
        color="UWY",
        title="Month-to-Month Loss Ratio by Underwriting Year",
        labels={"LossRatio": "Loss Ratio", "Tran_MonthYear": "Cutoff Date"},
        markers=True,
        category_orders={"UWY": sorted(summary["UWY"].unique())}
    )
    
    # Fix x-axis formatting
    lossratio_uy_fig.update_layout(
        xaxis=dict(
            tickmode='array',
            title="Cutoff Date"
        ),
        yaxis=dict(
            title="Loss Ratio",
            tickformat=".0%"  # Format to 2 decimal places
        ),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    # Add horizontal line at 100% loss ratio (1.0)
    lossratio_uy_fig.add_hline(
        y=0.65, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Break-even (65%)"
    )
    
    return lossratio_uy_fig


# Call the function
lossratio_uy_fig = create_loss_ratio_chart()





main_app=html.Div([

    # Main content container
    html.H1("📊 Portfolio Performance - Main",className="main-title"),

    html.Div([
        html.Div([
            html.Button("Refresh DPD and DCD data", id="run-button-3", n_clicks=0, style={'width': '300px'})
        ], style={'display': 'flex', 'gap': '100px', 'margin-bottom': '10px'}),
        
        html.Div(id="refresh-output-3"),   # Show Feedback (e.g., "Data refreshed!")
    ]),

    html.Div([
        html.Button("Download CSV", id="btn-download-1",style={'width': '100%','margin-bottom': '10px'}),
        dcc.Download(id="download-dataframe1-csv")
    ]),

    html.Div([
        html.H3("Summary by UW Year")
    ]),

    html.Div([
        dcc.Graph(id='Graph1-LossRatio_by_UY', figure=lossratio_uy_fig)
    ], className="graph", style={'width': '100%'}),

    html.Div([
        html.H3("Premium Info by Class")
    ]),

    html.Div([
        dcc.Checklist(
            id="Year_button",
            options=[{'label': year, 'value': year} for year in year_list1],
            value=latest_year ,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Snapshot_button",
            options=[{'label': cutoff, 'value': cutoff} for cutoff in snapshot_list1],
            value=snapshot_list1[-1],
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Policy_info_button",
            options=[
                {'label': cutoff, 'value': cutoff}
                for cutoff in ["Average Premium", "Policy Count", "Total Premium"]
            ],
            value="Average Premium",  # default selected value
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),



    html.Div([
        dcc.Graph(id='Graph2-Premium_by_Class')
    ], className="graph", style={'width': '85%'}),

    html.Div([
        dcc.Graph(id='Graph3-NonMotor_donutchart')
    ],className="graph", style={
        'display': 'flex',
        'justify-content': 'center',
        'align-items': 'center',
        'height': '500px' ,
        'width': '85%' 
    }),

    html.Div([
        dcc.Graph(id='Graph3-LossRatio_by_Class')
    ],className="graph",style={'width': '85%'}),

    html.Div([
        html.H3("Premium Info by Sub Class")
    ]),

    html.Div([
        dcc.RadioItems(
            id="Class_button2",
            options=[{'label': cls, 'value': cls} for cls in class_list1],
            value=class_list1[0],  # default year
            inline=True,
            labelStyle={'margin-right': '20px'}
        )
    ]),

    html.Div([
        dcc.Checklist(
            id="Year_button2",
            options=[{'label': year, 'value': year} for year in year_list1],
            value=latest_year ,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Snapshot_button2",
            options=[{'label': cutoff, 'value': cutoff} for cutoff in snapshot_list1],
            value=snapshot_list1[-1],
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Policy_info_button2",
            options=[
                {'label': cutoff, 'value': cutoff}
                for cutoff in ["Average Premium", "Policy Count", "Total Premium"]
            ],
            value="Average Premium",  # default selected value
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.Graph(id='Graph5-Premium_by_SubClass', style={'width': '85%','margin-bottom': '20px'})
    ]),

    html.Div([
        dcc.Graph(id='Graph6-LossRatio_by_SubClass', style={'width': '85%','margin-bottom': '20px'})
    ]),


    html.Div([
        html.H3("Loss Ratio - MCF by Insured Name")
    ]),
    html.Button(
        "Download Excel",
        id="btn-download-excel",
        n_clicks=0,
        style={'width': '200px'}
    ),
    dcc.Download(id="download-excel"),

    html.Div([
        dcc.RadioItems(
            id="select-mcf-year",
            options=[{"label": str(year), "value": year} for year in df_mcf_year],
            value=df_mcf_year[0],   # default = first year
            labelStyle={"display": "inline-block", "margin-right": "15px"}
        )
    ]),

    html.Div([
        dcc.RadioItems(
                id="mcf-toggle",
                options=[
                    {"label": "Vehicles Count", "value": "vehicles"},
                    {"label": "Loss Ratio", "value": "lossratio"}
                ],
                value="vehicles",   # default
                labelStyle={"display": "inline-block", "margin-right": "15px"}
            ),
            dcc.Graph(id="Graph9-LossRatio_MCF", style={'width': '85%', 'margin-bottom': '20px'})
        ]),
    dcc.Store(id="store-mcf-data"),


    html.Div([
        html.H3("Average Burning Cost for MCF ")
    ]),
    dcc.Store(id="store-mcf-filtered"),
    html.Button(
        "Download Excel",
        id="btn-download2",
        n_clicks=0,
        style={'width': '200px'}
    ),
    dcc.Download(id="download-excel2"),
    html.Div([
        dcc.RadioItems(
            id="select-mcf-year2",
            options=[{"label": str(year), "value": year} for year in df_mcf_year],
            value=df_mcf_year[0],   # default = first year
            labelStyle={"display": "inline-block", "margin-right": "15px"}
        ),
        dcc.Graph(
            id="Graph10-bc-MCF",
            style={'width': '85%', 'margin-bottom': '20px'},
        )
    ]),

    html.Div([
        html.H3("📈 Month-to-Month Movement by Class"),
    ]),
    
    html.Div([
        dcc.Checklist(
            id="Year_button3",
            options=[{'label': year, 'value': year} for year in year_list1],
            value=latest_year ,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Class_button3",
            options=[{'label': cls, 'value': cls} for cls in class_list1],
            value=class_list1[0],
            inline=True,
            labelStyle={'margin-right': '20px'}
        ),

        dcc.Checklist(
            id='Toggle-check3',
            options=[{'label': 'Show scheme options', 'value': 'show'}],
            value=[]
        ),

        html.Div(
            id='Radio-container3',
            children=dcc.Checklist(
                id='Subclass_checklist3',
                options=[],  # start empty, fill dynamically
                inline=True
            ),
            hidden=True
        )
    ]),

    html.Div([
        html.H3("🔍 Loss Ratio Movement")
    ]),


    html.Div([
        dcc.Graph(id='Graph7-LossRatio_Movement', style={'width': '85%','margin-bottom': '20px'})
    ]),

    html.Div([
        html.H3("🔍Claims OS and Paid Movement")
    ]),

    html.Div([
        dcc.Checklist(
            id="Year_button4",
            options=[{'label': year, 'value': year} for year in year_list1],
            value=latest_year ,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
        dcc.RadioItems(
            id="Class_button4",
            options=[{'label': cls, 'value': cls} for cls in class_list1],
            value=class_list1[0],
            inline=True,
            labelStyle={'margin-right': '20px'}
        ),

        dcc.Checklist(
            id='Toggle-check4',
            options=[{'label': 'Show scheme options', 'value': 'show'}],
            value=[]
        ),

        html.Div(
            id='Radio-container4',
            children=dcc.Checklist(
                id='Scheme_checklist4',
                options=[],  # start empty, fill dynamically
                inline=True
            ),
            hidden=True
        ),

        dcc.Checklist(
            id='Toggle-check5',
            options=[{'label': 'Show claims type breakdown: BI, OD, PD... (Only for Motor)', 'value': 'show'}],
            value=[]
        ),

        html.Div(
            id='ClaimsType-container',
            children=dcc.Checklist(
                id='ClaimsType_checklist',
                options=[
                    {'label': 'BI', 'value': 'BI'},
                    {'label': 'OD', 'value': 'OD'},
                    {'label': 'PD', 'value': 'PD'}
                ],
                value=['BI', 'OD', 'PD'],
                inline=True
            ),
            hidden=True  # Initially hidden
        ),
    ]),

    html.Div([
        dcc.Graph(id='Graph8-Claims_Movement', style={'width': '85%','margin-bottom': '20px'})
    ]),



], id='mainContainer', className= "main-container" )


def register_main_callbacks(app):
    
    @app.callback(
        Output("refresh-output-3", "children"),
        Input("run-button-3", "n_clicks"),
        prevent_initial_call=True
    )
    def run_script(n_clicks):
        # Run the external script using subprocess
        if n_clicks and n_clicks > 0:
            try:
                refresh_DPD_DCD()    

                return "✅ Task completed: dashboard_data.xlsx has been created."
            except Exception as e:
                    return f"❌ Failed to update: {str(e)}"
        return ""
    
    @app.callback(
        Output("download-dataframe1-csv", "data"),
        Input("btn-download-1", "n_clicks"),
        prevent_initial_call=True
    )
    def generate_csv(n_clicks):
        return dcc.send_data_frame(df_final.to_csv, "dashboard_data1.csv", index=False)


    @app.callback(
        Output("Graph2-Premium_by_Class", "figure"),
        Input("Year_button", "value"),
        Input("Snapshot_button", "value"),
        Input("Policy_info_button","value")
    )
    def premium_bar_chart1(selected_year,selected_cutoff,selected_info):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df = filtered_df[filtered_df["Tran_MonthYear"]==selected_cutoff]


        # Choose the type of snapshot: Total, Average, or Count
        if selected_info == "Total Premium":
            summary = filtered_df.groupby("Class", observed=False, as_index=False)["PremiumAmount_cumsum"].sum()
            fig = px.bar(
                summary,
                x="Class",
                y="PremiumAmount_cumsum",
                title="Total Premium by Class - " + ", ".join(selected_year),
                labels={"PremiumAmount_cumsum": "Total Premium"},
                text_auto=True
            )

        elif selected_info == "Average Premium":
            summary = (
                filtered_df.groupby("Class", observed=False, as_index=False)
                .agg({"PremiumAmount_cumsum": "sum", 
                      "Vehicles_in_Fleet":"sum"})
               #       "PolNo": "count"})
            )

            summary["AveragePremium"] = summary["PremiumAmount_cumsum"] / summary["Vehicles_in_Fleet"]
    

            fig = px.bar(
                summary,
                x="Class",
                y="AveragePremium",
                title="Average Premium by Class - " + ", ".join(selected_year),
                labels={"AveragePremium": "Average Premium"},
                text_auto=True
            )

        elif selected_info == "Policy Count":
            summary = (
                filtered_df.groupby("Class",  observed=False, as_index=False)
                .agg({"PolNo": "sum"})
                .rename(columns={"PolNo": "PolicyCount"})
            )
            fig = px.bar(
                summary,
                x="Class",
                y="PolicyCount",
                title="Policy Count by Class - " + ", ".join(selected_year),
                labels={"PolicyCount": "No. of Policies"},
                text_auto=True
            )

        else:
            fig = px.bar(title="Invalid snapshot option selected")

        fig.update_yaxes(tickformat=',.0f')   
        
        return fig
    
    @app.callback(
        Output("Graph3-NonMotor_donutchart", "figure"),
        Input("Year_button", "value"),
        Input("Snapshot_button", "value")
    )
    def premium_donut_chart1(selected_year,selected_cutoff):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df = filtered_df[filtered_df["Tran_MonthYear"].astype(str)==selected_cutoff]
        filtered_df = filtered_df[~filtered_df["Class"].isin(["Motor","Motor fleet"])]
        summary = filtered_df.groupby("Class", as_index=False)["PremiumAmount_cumsum"].sum()

        fig = px.pie(
            summary,
            values='PremiumAmount_cumsum',
            names='Class',
            hole=0.4,  
            title=f"Premium Distribution by Class (Non-Motor) for year {', '.join(selected_year)}"
        )

        fig.update_traces(domain=dict(x=[0, 1], y=[0, 1]))

        return fig

    @app.callback(
        Output("Graph3-LossRatio_by_Class", "figure"),
        Input("Year_button", "value"),
        Input("Snapshot_button", "value")

    )
    def lossratio_line_chart1(selected_year,selected_cutoff):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df = filtered_df[filtered_df["Tran_MonthYear"].astype(str)==selected_cutoff]

        summary = (
            filtered_df
            .groupby("Class", as_index=False)
            [["PremiumAmount_cumsum", "ClaimAmount"]]
            .sum()
        )
        summary["LossRatio"] = summary["ClaimAmount"] / summary["PremiumAmount_cumsum"]
        summary['LossRatio'] = pd.to_numeric(summary['LossRatio'], errors='coerce')  # Convert to numeric

        fig = px.scatter(
            summary,
            x="Class",               
            y="LossRatio",
            title="Loss Ratio by Class - " + ", ".join(selected_year),
            labels={"LossRatio": "Loss Ratio"}
        )

        fig.update_traces(
            text=summary["LossRatio"].apply(lambda x: f"{x:.0%}"),  # Format as %
            mode="lines+markers+text",
            textposition="top center"
        )

        return fig

    @app.callback(
        Output("Graph5-Premium_by_SubClass", "figure"),
        Input("Year_button2", "value"),
        Input("Class_button2","value"),
        Input("Snapshot_button2","value"),
        Input("Policy_info_button2","value")
    )
    def premium_bar_chart2(selected_year,selected_class,selected_cutoff,selected_info):
        if selected_year is None:
            return "Loss Ratio by SubClass - No Year Selected"
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df =  filtered_df[filtered_df ["Tran_MonthYear"]==selected_cutoff]
        filtered_df =filtered_df[filtered_df["Class"].isin([selected_class])]
        summary = filtered_df.groupby("Cls", as_index=False)["PremiumAmount_cumsum"].sum()

    
        # Choose the type of snapshot: Total, Average, or Count
        if selected_info == "Total Premium":
            summary = filtered_df.groupby("Cls", observed=False, as_index=False)["PremiumAmount_cumsum"].sum()
            fig = px.bar(
                summary,
                x="Cls",
                y="PremiumAmount_cumsum",
                title="Total Premium by Sub Class - " + ", ".join(selected_year),
                labels={"PremiumAmount_cumsum": "Total Premium"},
                text_auto=True
            )

        elif selected_info == "Average Premium":
            summary = (
                filtered_df.groupby("Cls", observed=False, as_index=False)
                .agg({"PremiumAmount_cumsum": "sum",
                       "Vehicles_in_Fleet": "sum"})
            )
            summary["AveragePremium"] = summary["PremiumAmount_cumsum"] / summary["Vehicles_in_Fleet"]
            fig = px.bar(
                summary,
                x="Cls",
                y="AveragePremium",
                title="Average Premium by Sub Class - " + ", ".join(selected_year),
                labels={"AveragePremium": "Average Premium"},
                text_auto=True
            )

        elif selected_info == "Policy Count":
            summary = (
                filtered_df.groupby("Cls",  observed=False, as_index=False)
                .agg({"PolNo": "sum"})
                .rename(columns={"PolNo": "PolicyCount"})
            )
            fig = px.bar(
                summary,
                x="Cls",
                y="PolicyCount",
                title="Policy Count by Sub Class - " + ", ".join(selected_year),
                labels={
                     "Cls": "Scheme",
                    "PolicyCount": "No. of Policies"},
                text_auto=True
            )

        else:
            fig = px.bar(title="Invalid snapshot option selected")

        fig.update_yaxes(tickformat=',.0f')   
        return fig

    @app.callback(
        Output("Graph6-LossRatio_by_SubClass", "figure"),
        Input("Year_button2", "value"),
        Input("Class_button2","value"),
        Input("Snapshot_button2","value"),
    )
    def lossratio_line_chart2(selected_year,selected_class,selected_cutoff):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df =filtered_df[filtered_df["Class"]==selected_class]
        filtered_df =filtered_df[filtered_df["Tran_MonthYear"]==selected_cutoff]

        summary = (
            filtered_df
            .groupby("Cls", as_index=False)
            [["PremiumAmount_cumsum", "ClaimAmount"]]
            .sum()
        )
        summary["LossRatio"] = summary["ClaimAmount"] / summary["PremiumAmount_cumsum"]
        summary['LossRatio'] = pd.to_numeric(summary['LossRatio'], errors='coerce')  # Convert to numeric
        summary = summary.dropna(subset=['LossRatio'])

        fig = px.line(
            summary,
            x="Cls",               
            y="LossRatio",
            title="Loss Ratio by Sub Class - " + ", ".join(selected_year),
            labels={"LossRatio": "Loss Ratio"},
            markers=True
        )

        fig.update_traces(
            text=summary["LossRatio"].apply(lambda x: f"{x:.0%}"),  # Format as %
            mode="lines+markers+text",
            textposition="top center"
        )


        return fig
    
    
    @app.callback(
        Output('Subclass_checklist3', 'options'),
        Input('Class_button3', 'value')
    )
    def update_scheme_list(selected_class):
        df_filtered = df_final[df_final['Class'] == selected_class]
        schemes = df_filtered['Cls'].dropna().unique().tolist()
        return [{'label': s, 'value': s} for s in schemes]
    
    @app.callback(
        Output('Radio-container3', 'hidden'),
        Input('Toggle-check3', 'value')
    )
    def toggle_scheme_visibility(toggle_val):
        return 'show' not in toggle_val
    
    @app.callback(
        Output("Graph7-LossRatio_Movement", "figure"),
        Input("Year_button3", "value"),
        Input("Class_button3","value"),
        Input("Subclass_checklist3","value"),
        Input("Toggle-check3","value")
    )
    def loss_ratio_line_chart2(selected_year,selected_class,selected_subclass, toggle_val):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df =filtered_df[filtered_df["Class"].isin([selected_class])]
        filtered_df = filtered_df[filtered_df["Tran_MonthYear"].isin(snapshot_list1)]
        if toggle_val and 'show' in toggle_val and selected_subclass:
            filtered_df = filtered_df[filtered_df["Cls"].isin(selected_subclass)]

        summary = (
            filtered_df
            .groupby(["Tran_MonthYear","Tran_MonthYear_dt"], as_index=False)
            [["PremiumAmount_cumsum", "ClaimAmount"]]
            .sum()
        )
        summary["LossRatio"] = summary["ClaimAmount"] / summary["PremiumAmount_cumsum"]
        summary = summary.sort_values(by="Tran_MonthYear_dt").reset_index()

        fig1 = px.line(
            summary,
            x="Tran_MonthYear",               
            y="LossRatio",
            title="Loss Ratio by Class - " + ", ".join(selected_year),
            labels={"LossRatio": "Loss Ratio",
                        "Tran_MonthYear":"Cutoff Date"},
            markers=True
        )

        fig1.update_traces(
            text=summary["LossRatio"].apply(lambda x: f"{x:.0%}"),  # Format as %
            mode="lines+markers+text",
            textposition="top center"
        )

        fig1.update_yaxes(
            tickformat=".0%"     # ✅ Format y-axis as percentage
        )

        return fig1
    

    
    @app.callback(
        Output('Scheme_checklist4', 'options'),
        Input('Class_button4', 'value')
    )
    def update_scheme_list(selected_class):
        df_filtered = df_final[df_final['Class'] == selected_class]
        schemes = df_filtered['Cls'].dropna().unique().tolist()
        return [{'label': s, 'value': s} for s in schemes]

    @app.callback(
        Output('Radio-container4', 'hidden'),
        Input('Toggle-check4', 'value')
    )
    def toggle_claimstype_visibility(toggle_val):
        return 'show' not in toggle_val
    
    @app.callback(
        Output('ClaimsType-container', 'hidden'),
        Input('Toggle-check5', 'value'),
        Input('Class_button4', 'value')

    )
    def show_checklist(toggle_val, class_val):
        # Show checklist only if both conditions are met
        return not ('show' in toggle_val and class_val == 'Motor')
        
    # Claims payment and os bar chart
    @app.callback(
        Output("Graph8-Claims_Movement", "figure"),
        Output("Graph8-Claims_Movement", "style"),
        Input("Year_button4", "value"),
        Input("Class_button4","value"),
        Input("Scheme_checklist4","value"),
        Input("Toggle-check4","value"),
        Input("ClaimsType_checklist","value"),
        Input("Toggle-check5","value")
    )
    def loss_ratio_line_chart2(selected_year, selected_class, selected_scheme, toggle_val, selected_clmtype, toggle_val2):
        filtered_df = df_final[df_final["UWY"].astype(str).isin(selected_year)]
        filtered_df = filtered_df[filtered_df["Class"].isin([selected_class])]
        filtered_df = filtered_df[filtered_df["Tran_MonthYear"].isin(snapshot_list1)]

        # aggregate only if the user picked *multiple* UWYs

        if not selected_year:       
            return go.Figure(), {'width': '75%', 'margin-bottom': '20px'}

        elif len(selected_year) > 1:
            filtered_df = (
                filtered_df
                .groupby(["Class","Cls", "Tran_MonthYear","Tran_MonthYear_dt"], as_index=False)[[
                    'BI_Amount', 'OD_Amount', 'PD_Amount', 'WS_Amount',
                    'BI_Paid', 'OD_Paid', 'PD_Paid', 'WS_Paid',
                    'ClaimAmount', 'ClaimPaid'
                ]].sum()
            )
        
    # filtered_df = filtered_df[sum_cols].sum().to_frame().T
        if selected_class=="Motor":
            amount_cols = ['BI_Amount', 'OD_Amount', 'PD_Amount', 'WS_Amount']
            paid_cols = ['BI_Paid', 'OD_Paid', 'PD_Paid', 'WS_Paid']
            sum_cols =  amount_cols + paid_cols
            

            # Show all schemes if checklist is unticked (i.e., 'show' not in toggle_val)
            if 'show' in toggle_val:
            # Filter by selected_scheme only if 'show' is toggled
                if selected_scheme:  # Make sure it's not None or empty
                    filtered_df = filtered_df[filtered_df["Cls"].isin(selected_scheme)]
                else:
                    pass

            summary2 = (
                    filtered_df
                .groupby(["Class","Tran_MonthYear","Tran_MonthYear_dt"], as_index=False)[sum_cols]
                .sum()
            )
            summary2 = summary2.sort_values(by="Tran_MonthYear_dt").reset_index()


            summary2["BI_OS"] = summary2["BI_Amount"] - summary2["BI_Paid"]
            summary2["OD_OS"] = summary2["OD_Amount"] - summary2["OD_Paid"]
            summary2["PD_OS"] = summary2["PD_Amount"] - summary2["PD_Paid"]
            summary2["WS_OS"] = summary2["WS_Amount"] - summary2["WS_Paid"]
            os_cols = ['BI_OS', 'OD_OS', 'PD_OS', 'WS_OS']

            df_paid =  summary2.melt(
                id_vars=["Class","Tran_MonthYear","Tran_MonthYear_dt"],
                value_vars=paid_cols,
                var_name="ClaimType2",
                value_name="Value"
            )
            df_os =  summary2.melt(
                id_vars=["Class","Tran_MonthYear","Tran_MonthYear_dt"],
                value_vars=os_cols,
                var_name="ClaimType2",
                value_name="Value"
            )

            # Merge paid and amount
            summary2 = pd.concat([df_paid, df_os], ignore_index=True)
            
            # Split the 'ClaimType' column into two columns: 'Claim' and 'Type'
            if not summary2.empty and 'ClaimType2' in summary2.columns:
                summary2[['ClaimCategory', 'ClaimType']] = (
                    summary2['ClaimType2'].str.split('_', n=1, expand=True)
                )
            else:
                # Create empty columns so downstream code doesn’t break
                summary2['ClaimCategory'] = pd.NA
                summary2['ClaimType']     = pd.NA
         

            # Show all heads of damage if checklist is unticked (i.e., 'show' not in toggle_val)
            if 'show' in toggle_val2:
                # Filter by selected_scheme only if 'show' is toggled
                if selected_clmtype:  # Make sure it's not None or empty
                   summary2  = summary2[summary2["ClaimCategory"].isin(selected_clmtype)]
            else:
                # If not showing scheme options, don't filter (keep all schemes)
                pass  # No filter applied
            # Aggregate PD, OD, BI etc
            summary2 = (
                summary2
                .groupby(["Class","Tran_MonthYear","Tran_MonthYear_dt","ClaimType"], as_index=False)
                [["Value"]]
                .sum()
            )
            summary2 = summary2.sort_values(by="Tran_MonthYear_dt").reset_index()

            # Plot
            fig2 = px.bar(
                summary2,
                x="Tran_MonthYear",
                y="Value",
                color="ClaimType",  # Show Paid vs OS separately
                barmode="group",
                text=summary2["Value"].apply(lambda x: f"${x:,.0f}"),
                labels={"Tran_MonthYear": "Cutoff Date", "Value": "Amount"},
                title="Claims Paid vs Outstanding"
            )
            # Set y-axis to currency format
            fig2.update_layout(
                yaxis_tickformat='$,.0f'
            )

        # Filter based on Toggle-check5 and selected claim types
        else:

            summary2 = (
                filtered_df
                .groupby(["Class","Tran_MonthYear","Tran_MonthYear_dt"], as_index=False)
                [["ClaimAmount", "ClaimPaid"]]
                .sum()
            )
            # Final reshape for plotting
            summary2["ClaimOS"] = summary2["ClaimAmount"] - summary2["ClaimPaid"]
            summary2 =  summary2.melt(
                id_vars=["Class","Tran_MonthYear","Tran_MonthYear_dt"],
                value_vars=["ClaimOS", "ClaimPaid"],
                var_name="ClaimType",
                value_name="Value"
            )
            # Rename
            summary2['ClaimType'] = summary2['ClaimType'].replace({
                'ClaimOS': 'OS',
                'ClaimPaid': 'Paid'
            })
            summary2 = summary2.sort_values(by="Tran_MonthYear_dt")

            # Plot
            fig2 = px.bar(
                summary2,
                x="Tran_MonthYear",
                y="Value",
                color="ClaimType",  # Show Paid vs OS separately
                barmode="group",
                text=summary2["Value"].apply(lambda x: f"${x:,.0f}"),
                labels={"Tran_MonthYear": "Cutoff Date", "Value": "Amount"},
                title="Claims Paid vs Outstanding"
            )
            # Set y-axis to currency format
            fig2.update_layout(
                yaxis_tickformat='$,.0f'
            )

        return fig2, {'width': '75%', 'margin-bottom': '20px'}
    

    @app.callback(
        [Output("Graph9-LossRatio_MCF", "figure"),
        Output("store-mcf-data", "data")],
        [Input("mcf-toggle", "value"),
        Input("select-mcf-year", "value")]
    )
    # MCF loss ratio
    def loss_ratio_mcf(toggle_value, select_year):
        filtered_df = df_mcf.copy()
        filtered_df = filtered_df[filtered_df['UwYr'] == select_year]
        filtered_df["Tran_MonthYear_dt"] = pd.to_datetime(
            filtered_df["Tran_MonthYear"], 
            format="%m-%Y"
        )
        latest_cutoff = filtered_df["Tran_MonthYear_dt"].max()

        filtered_df = filtered_df[filtered_df["Tran_MonthYear_dt"] == latest_cutoff]
        filtered_df["ClaimAmount"] = pd.to_numeric(filtered_df["ClaimAmount"], errors="coerce")
        filtered_df["PremiumAmount_cumsum"] = pd.to_numeric(filtered_df["PremiumAmount_cumsum"], errors="coerce")
        export_df=filtered_df.copy()
        filtered_df = (
            filtered_df.groupby("InsdName")
            .agg({
                "PremiumAmount_cumsum": "sum",
                "ClaimAmount": "sum",
                "Vehicles_in_Fleet": "sum",
            })
            .reset_index()
        )


        filtered_df.loc[:, "Loss_Ratio"] = (
            filtered_df["ClaimAmount"].fillna(0) /
            filtered_df["PremiumAmount_cumsum"].replace(0, np.nan)  # avoid divide by zero
        )
       
        if toggle_value == "vehicles":
            fig = px.bar(
                filtered_df,
                x="InsdName",
                y="Vehicles_in_Fleet",   # <-- must exist in your df
                title=f"MCF Vehicles Count - {latest_cutoff.strftime('%b %Y')}",
                text="Vehicles_in_Fleet"
            )
            fig.update_traces(
                texttemplate="%{text:.0f}",   # format labels (no decimals here)
                textposition="outside"        # put labels on top of bars
            )
            fig.update_layout(
                xaxis=dict(title="Insured Name"),
                yaxis=dict(title="Vehicles Count"),
                legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=0.5),
                bargap=0.2,
                width=1000,
                height=600
            )

        else:  # loss ratio view
            fig = go.Figure()

            # Bar = Premium
            fig.add_trace(
                go.Bar(
                    x=filtered_df["InsdName"],
                    y=filtered_df["PremiumAmount_cumsum"],
                    name="Premium Amount",
                    text=filtered_df["PremiumAmount_cumsum"],   # add labels
                    textposition="outside",
                    texttemplate="%{text:,.0f}"
                )
            )

            # Line = Loss Ratio
            fig.add_trace(
                go.Scatter(
                    x=filtered_df["InsdName"],
                    y=filtered_df["Loss_Ratio"],
                    mode="lines+markers",
                    name="Loss Ratio",
                    yaxis="y2",
                    text=filtered_df["Loss_Ratio"],   # add labels,
                    textposition="top center",
                    texttemplate="%{text:.1%}"  
                )
            )

            fig.update_layout(
                title=f"MCF Loss Ratio - {latest_cutoff.strftime('%b %Y')}",
                xaxis=dict(title="Insured Name"),
                yaxis=dict(title="Premium Amount"),
                yaxis2=dict(
                    title="Loss Ratio",
                    overlaying="y",
                    side="right",
                    tickformat=".0%",  # percent format
                ),
                legend=dict(x=0.8, y=1, bordercolor="Black", borderwidth=0.5),
                bargap=0.2,
                width=1000,
                height=600
            )

        return fig,export_df.to_dict("records")


    @app.callback(
        Output("download-excel", "data"),
        Input("btn-download-excel", "n_clicks"),
        State("store-mcf-data", "data"),
        prevent_initial_call=True
    )
    def download_excel(n_clicks, stored_data):
        df_grouped = pd.DataFrame(stored_data)
        return dcc.send_data_frame(df_grouped.to_excel, "MCF_LossRatio.xlsx", index=False)
    
    @app.callback(
        Output("Graph10-bc-MCF", "figure"),
        Output("store-mcf-filtered", "data"),
        Input("select-mcf-year2", "value"),
    )

    def MCF_burning_cost(selected_year):
        filtered_df = df_mcf[df_mcf["UwYr"] == selected_year]

        filtered_df=filtered_df.copy()
        filtered_df["BI_Amount"] = pd.to_numeric(filtered_df["BI_Amount"], errors="coerce")
        filtered_df["PD_Amount"] = pd.to_numeric(filtered_df["PD_Amount"], errors="coerce")
        filtered_df["OD_Amount"] = pd.to_numeric(filtered_df["OD_Amount"], errors="coerce")
        filtered_df["WS_Amount"] = pd.to_numeric(filtered_df["WS_Amount"], errors="coerce")
        filtered_df["Vehicles_in_Fleet"] = pd.to_numeric(filtered_df["Vehicles_in_Fleet"], errors="coerce")

       
        filtered_df['Tran_MonthYear_dt'] = pd.to_datetime(
            filtered_df['Tran_MonthYear'], format="%m-%Y", errors="coerce"
        )
        filtered_df['Vehicles_in_Fleet_TP'] = np.where(
            (filtered_df['BI_Amount'] + filtered_df['PD_Amount'] > 0),
            filtered_df['Vehicles_in_Fleet'],
            0
        )
        filtered_df['Vehicles_in_Fleet_OD'] = np.where(
            (filtered_df['OD_Amount'] + filtered_df['WS_Amount'] > 0),
            filtered_df['Vehicles_in_Fleet'],
            0
        )

        filtered_df2 = (
            filtered_df
            .groupby(["Tran_MonthYear","Tran_MonthYear_dt" ])[["BI_Amount", "PD_Amount", "OD_Amount","WS_Amount","Vehicles_in_Fleet_TP","Vehicles_in_Fleet_OD"]]
            .sum()
            .reset_index()
        )

        filtered_df2['TP'] = (
            (filtered_df2['BI_Amount'] + filtered_df2['PD_Amount']) 
            / filtered_df2['Vehicles_in_Fleet_TP']
        )

        
        filtered_df2['OD'] = (
            (filtered_df2['OD_Amount'] + filtered_df2['WS_Amount']) 
            / filtered_df2['Vehicles_in_Fleet_OD']
        )


        filtered_df2 = filtered_df2.sort_values(by="Tran_MonthYear_dt")

        
        fig = px.line(
            filtered_df2,
            x="Tran_MonthYear",
            y=["TP", "OD"],
            color_discrete_sequence=["blue", "red"],
            markers=True,
            title="Burning Cost Trend (TP vs OD)",
        )
        fig.update_traces(
            mode="lines+markers+text",          # show line, markers, and text
            texttemplate="%{y:.0f}",            # label format (2 decimals)
            textposition="top center"           # position of the labels
        )

        fig.update_layout(
            xaxis_title="Cutoff Date",
            yaxis_title="Burning Cost",
            legend_title="Burning Cost Type",
            xaxis=dict(tickformat="%b-%Y"),  # e.g. Jan-2024
        )

        return fig, filtered_df.to_dict("records")

    @app.callback(
        Output("download-excel2", "data"),
        Input("btn-download2", "n_clicks"),
        State("store-mcf-filtered", "data"),
        prevent_initial_call=True
    )
    def download_filtered_df(n_clicks, stored_data):
        filtered_df = pd.DataFrame(stored_data)
        return dcc.send_data_frame(filtered_df.to_excel, "MCF_burning_cost.xlsx", index=False)

def get_layout():
    return main_app



if __name__ == "__main__":
    app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])
    app.layout = get_layout()
    register_main_callbacks(app)
    app.run(debug=True, port=8050)