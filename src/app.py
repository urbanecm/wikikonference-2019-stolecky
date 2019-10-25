# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import yaml
from flask import redirect, request, render_template, url_for, flash
from flask import Flask
import requests
from flask_jsonlocale import Locales
from flask_mwoauth import MWOAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='../static')
application = app

db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    title = db.Column(db.String(255), default='')
    description = db.Column(db.Text, default='')
    name = db.Column(db.String(255), default='')

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, os.environ.get(
        'FLASK_CONFIG_FILE', 'config.yaml')))))

@app.route('/')
def index():
    tables = Table.query.all()
    known_tables = {}
    for table in tables:
        known_tables[table.number] = table
    return render_template('index.html', max_tables=20, tables=known_tables)

@socketio.on('lock-table')
def on_lock_table(json):
    emit('lock-table', json, broadcast=True)

@socketio.on('unlock-table')
def on_unlock_table(json):
    emit('unlock-table', json, broadcast=True)

@socketio.on('update-table')
def on_update_table(json):
    emit('update-table', json, broadcast=True)
    table = Table.query.filter_by(number=int(json['tableId'])).first()
    if not table:
        table = Table(number=int(json['tableId']))
    if json['type'] == 'title':
        table.title = json['value']
    if json['type'] == 'description':
        table.description = json['value']
    if json['type'] == 'name':
        table.name = json['value']
    db.session.add(table)
    db.session.commit()

if __name__ == '__main__':
    socketio.run(app)
