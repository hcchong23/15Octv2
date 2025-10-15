import plotly.express as px
import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash import html, dcc, Output, Input
from DPD_DCD_2 import assign_agency

df1 = pd.read_excel("Dashboard_renewal.xlsx")
expired_dt = pd.to_datetime(df1['Expired_Month'], format='%m-%Y')
latest_12 = sorted(expired_dt.unique())[-12:] 
latest_12 = [d.strftime("%m-%Y") for d in latest_12]
agency_list=sorted(df1['Agency'].unique().tolist())

# === Data refresh function ===
def refresh_STP():
    df1 = pd.read_excel("scrutiny_list_STP_2024-2025.xlsx")
    df2 = pd.read_excel("Dashboard_data.xlsx")
    # Keep last row by PolNo only, already sorted
    df2 = df2.drop_duplicates(subset='PolNo', keep='last')[['PolNo', 'Renew_Next_Year']]
    df1 = pd.merge(df1, df2, left_on="Policy No", right_on="PolNo", how='left')
    df1['Expired_Month'] = pd.to_datetime(df1['Expiring Month']).dt.strftime('%m-%Y')
    df1['Agency'] = assign_agency(df1,agent_col='Agent')
    df1.to_excel("Dashboard_renewal.xlsx", index=False)


# === Chart generation function ===


def renewal_chart2(month_list=latest_12):
    grouped=df1.copy()
    grouped =grouped[grouped["Expired_Month"].isin(month_list)]
    grouped = (
        grouped
        .groupby(['Agency', 'Renew_Next_Year'], observed=False)
        .agg(Total_Count=('PolNo', 'nunique'))
        .reset_index()
    )
    
    summary = grouped.pivot(index='Agency', columns='Renew_Next_Year', values='Total_Count').fillna(0)
    summary.columns = ['Not_Renewed', 'Renewed']
    summary = summary.reset_index()
    summary['Invited'] = summary['Renewed'] + summary['Not_Renewed']
    summary['Renewal_Rate'] = summary['Renewed'] / summary['Invited']

    fig = go.Figure()
    fig.add_trace(go.Bar(  
        x=summary['Agency'],
        y=summary['Invited'],
        name="Invited for Renewals",
        marker_color='#9E9E9E',
        text=summary['Invited'].fillna(0).round(0).astype(int).astype(str),
        textposition='outside',
        yaxis="y",  # Left axis
        hovertemplate="Agency: %{x}<br>Invited: %{y}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=summary['Agency'],
        y=summary['Renewal_Rate'],
        name="Renewal %",
        mode='lines+markers+text',
        marker=dict(color='#B100FF'),
        text=[f"{y:.1%}" for y in summary['Renewal_Rate']],  # format as percent
        textposition='top center', 
        line=dict(color='#B100FF', width=2),
        yaxis="y2",  # Right axis
        hovertemplate=f"Agency: %{{x}}<br>Renewal: %{{y:.1%}}"
    ))

    fig.update_layout(
        yaxis=dict( 
            title="Invited for Renewal",
            tickformat=".0f",
            showgrid=True,
            side='right',  # Important: to flip the y primary and secondary axis 
        ),
        yaxis2=dict(  
            title="Renewal Rate (%)",  
            overlaying='y',
            tickformat=".0%",
            range=[0, 1],   
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        margin=dict(l=40, r=40, t=40, b=40),
        title="Renewal Count and Rate (Last 12 months)",
    )
    return fig

#  === Dash app ===
renew_app = html.Div([
    html.Button("Refresh STP file", id="refresh-button", n_clicks=0, style={'width': '300px'}),
    html.H1("Renewal - STP", className="main-title"),
    html.Div(id="status-message"),  
     html.H2("Breakdown by Month",className="secondary-title"),
    dcc.Dropdown(
        options=[{'label': agency, 'value': agency} for agency in agency_list],
        value=None, 
        placeholder="Select an agency",
        id='agency-dropdown',
        clearable=True,
        style={"width": "55%"}    
    ),
    dcc.Graph(id="agency_renewalMonth_chart"),
    html.H2("Breakdown by Agent",className="secondary-title"),
    dcc.Graph(id="renewal-agent-graph", figure=renewal_chart2()), 
])



def register_renew_callbacks(app):

    @app.callback(
        Output("agency_renewalMonth_chart", "figure"),
        Input("agency-dropdown", "value")
    )
    def renewal_chart1(selected_agency):
        if selected_agency is None or selected_agency == "":
            df=df1.copy()
        else:
            df=df1[df1["Agency"] == selected_agency]
        grouped = (
            df
            .groupby(['Expired_Month', 'Renew_Next_Year'], observed=False)
            .agg(Total_Count=('PolNo', 'nunique'))
            .reset_index()
        )
        summary = grouped.pivot(index='Expired_Month', columns='Renew_Next_Year', values='Total_Count').fillna(0)
        summary.columns = ['Not_Renewed', 'Renewed']
        summary = summary.reset_index()
        summary['Invited'] = summary['Renewed'] + summary['Not_Renewed']
        summary['Renewal_Rate'] = summary['Renewed'] / summary['Invited']

        summary['Expired_Month_dt'] = pd.to_datetime(summary['Expired_Month'], format='%m-%Y')
        summary = summary.sort_values("Expired_Month_dt")  # sort by actual date
        summary['Expired_Month'] =summary['Expired_Month_dt'].dt.strftime('%m-%Y')  # for display

        fig = go.Figure()
        fig.add_trace(go.Bar(  
            x=summary['Expired_Month'],
            y=summary['Invited'],
            name="Invited for Renewals",
            marker_color='#FFA07A',
            text=summary['Invited'].fillna(0).round(0).astype(int).astype(str),
            textposition='outside',
            yaxis="y",  # Left axis
            hovertemplate="Expired Month: %{x}<br>Invited: %{y}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=summary['Expired_Month'],
            y=summary['Renewal_Rate'],
            name="Renewal %",
            mode='lines+markers+text',
            marker=dict(color='green'),
            text=[f"{y:.1%}" for y in summary['Renewal_Rate']],  # format as percent
            textposition='top center', 
            line=dict(color='green', width=2),
            yaxis="y2",  # Right axis
            hovertemplate=f"Expired_Month: %{{x}}<br>Renewal: %{{y:.1%}}"
        ))

        fig.update_layout(
            yaxis=dict( 
                title="Invited for Renewal",
                tickformat=".0f",
                showgrid=True,
                side='right',  # Important: to flip the y primary and secondary axis 
            ),
            yaxis2=dict(  
                title="Renewal Rate (%)",  
                overlaying='y',
                tickformat=".0%",
                range=[0, 1],   
                showgrid=False
            ),
            legend=dict(x=0.01, y=0.99),
            margin=dict(l=40, r=40, t=40, b=40),
            title="Renewal Count and Rate",
        )
        return fig
    

def get_layout():
    return renew_app

if __name__ == '__main__':
    app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
    app.layout = get_layout()
    register_renew_callbacks(app)
    app.run(debug=True)