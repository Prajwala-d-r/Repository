import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash import no_update
from flask import session
from functools import wraps
from flask import session, copy_current_request_context


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.config.suppress_callback_exceptions = True
app.title = 'Authentication'

server = app.server
server.config['SECRET_KEY'] = 'k1LUZ1fZShowB6opoyUIEJkJvS8RBF6MMgmNcDGNmgGYr' 


users = {
    'user':'user123'
}

def authenticate_user(credentials):
    '''
    generic authentication function
    returns True if user is correct and False otherwise
    '''
    #
    # replace with your code
    authed = (credentials['user'] in users) and (credentials['password'] == users[credentials['user']])
    # 
    #
    return authed

def validate_login_session(f):
    '''
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session. 
    If not, returns an error with link to the login page
    '''
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('authed',None)==True:
            return f(*args,**kwargs)
        return html.Div(
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H2('401 - Unauthorized',className='card-title'),
                                html.A(dcc.Link('Login',href='/login'))
                            ],
                            body=True
                        )
                    ],
                    width=5
                ),
                justify='center'
            )
        )
    return wrapper


# login layout content
def login_layout():
    return html.Div(
        [
            dcc.Location(id='login-url',pathname='/login',refresh=False),
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.H4('Login',className='card-title'),
                                    dbc.Input(id='login-email',placeholder='Username',autoComplete='off'),
                                    dbc.Input(id='login-password',placeholder='Assigned password',type='password',autoComplete='off'),
                                    dbc.Button('Submit',id='login-button',color='success',block=True),
                                    html.Br(),
                                    html.Div(id='login-alert')
                                ],
                                body=True
                            ),
                            width=6
                        ),
                        justify='center'
                    )
                ]
            )
        ]
    )

# home layout content
@validate_login_session
def app_layout():
    return \
        html.Div([
            dcc.Location(id='home-url',pathname='/home'),
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            [
                                html.Div(
                                html.Div([
                                html.Div(children=[
                                                html.H1('Welcome to the app'),
                                                html.H3('You are successfully authorized'),
                                                html.H3('Choose Your Plot'),]),
            
                                html.Div([
                                dcc.Dropdown(
                                id= 'dropdown',
                                    options=[
                                                {'label': 'Scatter Graph', 'value': 'Scatter Graph'},
                                                {'label': 'Bar Chart', 'value': 'Bar Chart'},
                                                {'label': 'Histogram', 'value': 'Histogram'}
                                            ],
                                value='Scatter Graph'          
            
                                        ),
                                html.Div(id='output')
        
                                        ])    
                                        ])
                                        )

                            ],
                        ),
                        justify='center'
                    ),

                    html.Br(),

                    dbc.Row(
                        dbc.Col(
                            dbc.Button('Logout',id='logout-button',color='danger',block=True,size='sm'),
                            width=4
                        ),
                        justify='center'
                    ),

                    
                    html.Br()
                ],
            )
        ]
    )

# main app layout
app.layout = html.Div(
    [
        dcc.Location(id='url',refresh=False),
        html.Div(
            login_layout(),
            id='page-content'
        ),
    ]
)


###############################################################################
# utilities
###############################################################################

# router
@app.callback(
    Output('page-content','children'),
    [Input('url','pathname')]
)
def router(url):
    if url=='/home':
        return app_layout()
    elif url=='/login':
        return login_layout()
    else:
        return login_layout()

# authenticate 
@app.callback(
    [Output('url','pathname'),
     Output('login-alert','children')],
    [Input('login-button','n_clicks')],
    [State('login-email','value'),
     State('login-password','value')])
def login_auth(n_clicks,email,pw):
    '''
    check credentials
    if correct, authenticate the session
    otherwise, authenticate the session and send user to login
    '''
    if n_clicks is None or n_clicks==0:
        return no_update,no_update
    credentials = {'user':email,"password":pw}
    if authenticate_user(credentials):
        session['authed'] = True
        return '/home',''
    session['authed'] = False
    return no_update,dbc.Alert('Incorrect credentials.',color='danger',dismissable=True)

@app.callback(
    Output('home-url','pathname'),
    [Input('logout-button','n_clicks')]
)
def logout_(n_clicks):
    '''clear the session and send user to login'''
    if n_clicks is None or n_clicks==0:
        return no_update
    session['authed'] = False
    return '/login'

@app.callback(dash.dependencies.Output('output', 'children'),
                  [dash.dependencies.Input('dropdown', 'value')])
def display_graphs(value):
    if value=='Scatter Graph':         
        return(html.Div(  
                    
                dcc.Graph(
                id='Scatter Graph',
                figure={
                    'data': [
                        {'x': ['A', 'B', 'C', 'D'], 'y': [111, 22, 3, 34], 'type': 'scatter', 'name': 'One ', 'width': .05},
                    ],
                       
                    }
                ),
                
                )),
    if value=='Bar Chart':            
        return(html.Div(                   
                    
                dcc.Graph(
                id='Bar Chart',
                figure={
                    'data': [
                        {'x': ['A', 'B', 'C', 'D'], 'y': [111, 22, 3, 34], 'type': 'bar', 'name': 'Two ', 'width': .05},
                        
                    ],
                       
                    }
                ),
                
                )),
    else:
        return(html.Div(              
                    
                    
                dcc.Graph(
                id='Histogram',
                figure={
                    'data': [
                        {'x': ['A', 'B', 'C', 'D'], 'y': [111, 22, 3, 34], 'type': 'histogram', 'name': 'Three ', 'width': .05},
                    ],
                       
                    }
                ),
                
                )),

###############################################################################
# callbacks
###############################################################################

# @app.callback(
#     Output('...'),
#     [Input('...')]
# )
# def func(...):
#     ...

###############################################################################
# run app
###############################################################################

if __name__ == '__main__':
        app.run_server(debug=False)


