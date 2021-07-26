from flask import Flask, request, render_template, session, redirect
from markupsafe import escape
import os
import pandas as pd
app = Flask(__name__)
cwd = os.getcwd()


@app.route('/')
def main():
    players_table = pd.read_csv(f'{cwd}/dataframes/allplayers.csv')
    table = [players_table.to_html(border=3)]
    return render_template('aram.html',  tables=table)


@app.route('/<name>')
def userpage(name=None):
    by_champ_table = pd.read_csv(f'{cwd}/dataframes/{name}.csv')
    table = [by_champ_table.to_html()]
    return render_template('userpage.html',  tables=table, name=name)

