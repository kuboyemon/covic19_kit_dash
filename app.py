#ライブラリのインポート
import pandas as pd
import openpyxl
import requests as req
from bs4 import BeautifulSoup

#スクレイピングの実行、ベースとなるdfの作成
url="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000082537_00001.html"
res=req.get(url)
soup=BeautifulSoup(res.text,'html.parser')

result = soup.select("a[href]")

link_list =[]
for link in result:
    href = link.get("href")
    link_list.append(href)

xlsx_list = [temp for temp in link_list if temp.endswith('xlsx')]
url_covic_xlsx='https://www.mhlw.go.jp'+f'{xlsx_list[0]}'

df=pd.read_excel(url_covic_xlsx)

df_tochigi=df[df['都道府県名']=='栃木県']
df_tochigi.reset_index(drop=True,inplace=True)

df_select=pd.DataFrame(df_tochigi[['薬局名称','所在地','電話番号']])

def make_clickable(val):
    return '<a href="https://www.google.co.jp/maps/place/{}" target="_blank">{}</a>'.format(val,val)

def make_telable(tel_num):
    return "<a href='tel:{}'>{}</a>".format(tel_num,tel_num)

# df_select.style.format({'所在地':make_clickable,'電話番号':make_telable})

#アプリ部分の作成
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#Procfile　通常は必要ないがherokuにデプロイする際は必ず追記
server = app.server

app.layout=html.Div([
    html.H1(children='検査キット薬局検索システム'),
    html.H5('市町を選択'),
    dcc.Dropdown(
        id='city-dropdown',
        options=['宇都宮市','足利市','栃木市','佐野市','鹿沼市',
    '日光市','小山市','真岡市','大田原市','矢板市','那須塩原市',
    'さくら市','那須烏山市','下野市',
    '上三川町','益子町','茂木町','市貝町',
    '芳賀町','壬生町','野木町','塩谷町','高根沢町','那須町','那珂川町'
        ],
        value='宇都宮市'
    ),
    html.Div(id='output-container', style={"margin": "5%"})

])

@app.callback(
    Output('output-container', 'children'),
    [Input('city-dropdown', 'value')])
def input_triggers_spinner(value):
    df_filtered = df_select[df_select['所在地'].str.contains(value)]
    df_filtered.style.format({'所在地':make_clickable,'電話番号':make_telable})

    output_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_filtered.columns],
        data=df_filtered.to_dict('records'),
        editable=True,
        #filter_action="native",
        #sort_action="native",
        #sort_mode="multi",
        #column_selectable="single",
        #row_selectable="single",
        #row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 5,
        style_cell={'textAlign': 'left'}
    )
    return output_table



#アプリの実行
if __name__=='__main__':
    app.run_server(debug=True)