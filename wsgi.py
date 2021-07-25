from flask import Flask, request, render_template, session, redirect
from markupsafe import escape
import os
import pandas as pd
app = Flask(__name__)
cwd = os.getcwd()

@app.route('/')
def main():
    players_table = pd.read_csv(f'{cwd}/dataframes/allplayers.csv')
    return render_template('aram.html',  tables=[players_table.to_html(classes='data')], titles=players_table.columns.values)


@app.route('/<name>')
def userpage(name=None):
    by_champ_table = pd.read_csv(f'{cwd}/dataframes/{name}.csv')
    return render_template('userpage.html',  tables=[by_champ_table.to_html(classes='data')], titles=by_champ_table.columns.values, name=name)
