"""Inventário acadêmico da REBIO. Coordenadas GeoJSON: longitude, latitude."""
import functools
import json
import os
import secrets
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit

import click
from flask import Flask, g, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .geography import validate_geometry, length_m, parse_file, MAX_FILE_SIZE


def db():
    if 'db' not in g:
        g.db = sqlite3.connect(g.app_database, timeout=15)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def protected(write=False):
    def decorate(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            if not g.user:
                return jsonify(error='Entre para acessar o inventário.'), 401
            if write:
                if g.user['role'] == 'leitor':
                    return jsonify(error='Perfil sem permissão de edição.'), 403
                if not secrets.compare_digest(request.headers.get('X-CSRF-Token', ''), session.get('csrf', '')):
                    return jsonify(error='Sessão inválida. Entre novamente.'), 403
            return fn(*args, **kwargs)
        return wrapped
    return decorate


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('Envie um objeto JSON.')
    result = {}
    for field, limit in [('name',120),('description',4000),('source',250),('photo_url',2048),('category',120),('geometry_file',250)]:
        value = data.get(field, '')
        if not isinstance(value, str) or len(value.strip()) > limit:
            raise ValueError(f'Campo {field} inválido (máximo {limit} caracteres).')
        result[field] = value.strip()
    if result['photo_url']:
        try:
            link = urlsplit(result['photo_url'])
            valid = link.scheme == 'https' and bool(link.hostname) and not link.username and not link.password and not any(c.isspace() for c in result['photo_url'])
        except ValueError:
            valid = False
        if not valid:
            raise ValueError('O link das fotos deve ser uma URL HTTPS válida.')
    if len(result['name']) < 3 or not result['source']:
        raise ValueError('Informe nome com pelo menos 3 caracteres e origem dos dados.')
    if data.get('kind') not in ('trilha','nascente') or data.get('status') not in ('a_verificar','conservado','atencao'):
        raise ValueError('Tipo ou situação inválidos.')
    result.update(kind=data['kind'], status=data['status'])
    try:
        observed = date.fromisoformat(data.get('observed_on',''))
    except (ValueError, TypeError):
        raise ValueError('Informe uma data de observação válida.') from None
    if observed > date.today():
        raise ValueError('A data de observação não pode ser futura.')
    result['observed_on'] = observed.isoformat()
    geometry = validate_geometry(data.get('geometry'), data['kind'])
    result['geometry'] = json.dumps(geometry, allow_nan=False)
    return result


def serialize(row):
    item = dict(row)
    item['geometry'] = json.loads(item['geometry'])
    item['length_m'] = length_m(item['geometry'])
    return item


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    # A chave local persiste entre reinícios; produção recebe segredo por variável.
    key_path = Path(app.instance_path) / 'session.key'
    if not os.environ.get('REBIO_SECRET_KEY') and not key_path.exists():
        key_path.write_text(secrets.token_hex(32), encoding='utf-8')
    app.config.update(
        SECRET_KEY=os.environ.get('REBIO_SECRET_KEY') or key_path.read_text(encoding='utf-8'),
        DATABASE=os.environ.get('REBIO_DATABASE', str(Path(app.instance_path)/'inventario.sqlite3')),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('REBIO_SECURE_COOKIE') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=4), MAX_CONTENT_LENGTH=256*1024,
    )
    if test_config:
        app.config.update(test_config)
    # Migração aditiva: preserva contas/registros e faz backup antes da alteração.
    if Path(app.config['DATABASE']).exists():
        connection = sqlite3.connect(app.config['DATABASE'], timeout=15)
        try:
            columns = {row[1] for row in connection.execute('PRAGMA table_info(features)')}
            missing = {'photo_url','category','geometry_file'} - columns
            if columns and missing:
                backup_path = Path(str(app.config['DATABASE']) + '.pre-figma.bak')
                if not backup_path.exists():
                    backup = sqlite3.connect(backup_path)
                    try:
                        connection.backup(backup)
                    finally:
                        backup.close()
                with connection:
                    for column in sorted(missing):
                        connection.execute(f"ALTER TABLE features ADD COLUMN {column} TEXT NOT NULL DEFAULT ''")
        finally:
            connection.close()

    @app.before_request
    def load_user():
        request.max_content_length = (16*1024*1024 if request.path == '/api/import-geometry'
                                      else 8*1024*1024 if request.path.startswith('/api/features') and request.method in ('POST','PUT')
                                      else 256*1024)
        g.app_database = app.config['DATABASE']
        g.user = db().execute('SELECT id, username, role FROM users WHERE id=?', (session.get('uid'),)).fetchone() if session.get('uid') else None

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop('db', None)
        if connection:
            connection.close()

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        # Tiles OSM exigem Referer; apenas a origem é enviada a outros sites.
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(400)
    @app.errorhandler(413)
    def invalid_request(error):
        return jsonify(error='Requisição inválida ou muito grande.'), error.code

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/health')
    def health():
        return jsonify(status='ok')

    @app.post('/api/login')
    def login():
        data = request.get_json(silent=True) or {}
        if not isinstance(data,dict) or not isinstance(data.get('username'),str) or not isinstance(data.get('password'),str):
            return jsonify(error='Informe usuário e senha.'), 400
        user = db().execute('SELECT * FROM users WHERE username=?',(data['username'],)).fetchone()
        if not user or not check_password_hash(user['password_hash'],data['password']):
            return jsonify(error='Usuário ou senha incorretos.'), 401
        session.clear()
        session.update(uid=user['id'], csrf=secrets.token_hex(32))
        session.permanent = True
        return jsonify(username=user['username'],role=user['role'],csrf=session['csrf'])

    @app.get('/api/session')
    @protected()
    def current_session():
        return jsonify(**dict(g.user),csrf=session['csrf'])

    @app.post('/api/logout')
    @protected()
    def logout():
        if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.get('csrf','')):
            return jsonify(error='Sessão inválida.'),403
        session.clear()
        return '',204

    def rows():
        query = 'SELECT * FROM features WHERE archived=0'
        args = []
        for field in ('kind','status'):
            if request.args.get(field):
                query += f' AND {field}=?'
                args.append(request.args[field])
        if request.args.get('q'):
            query += ' AND (name LIKE ? OR description LIKE ?)'
            args.extend(['%'+request.args['q']+'%']*2)
        return db().execute(query+' ORDER BY id DESC',args).fetchall()

    @app.get('/api/features')
    @protected()
    def list_features():
        return jsonify(items=[serialize(row) for row in rows()])

    @app.get('/api/geojson')
    @protected()
    def geojson():
        features=[]
        for row in rows():
            item=serialize(row)
            geometry=item.pop('geometry')
            features.append(dict(type='Feature',id=item['id'],geometry=geometry,properties=item))
        response=jsonify(type='FeatureCollection',features=features)
        response.headers['Content-Disposition']='attachment; filename="inventario-rebio.geojson"'
        return response

    def log_change(feature_id,action):
        row=db().execute('SELECT * FROM features WHERE id=?',(feature_id,)).fetchone()
        db().execute('INSERT INTO history(feature_id,actor_id,action,snapshot) VALUES (?,?,?,?)',
                     (feature_id,g.user['id'],action,json.dumps(serialize(row),ensure_ascii=False)))

    @app.post('/api/features')
    @protected(write=True)
    def create_feature():
        try:
            data=validate(request.get_json(silent=True))
        except ValueError as error:
            return jsonify(error=str(error)),400
        with db():
            cursor=db().execute('INSERT INTO features(name,kind,description,status,geometry,source,observed_on,photo_url,category,geometry_file,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                               tuple(data[k] for k in ('name','kind','description','status','geometry','source','observed_on','photo_url','category','geometry_file'))+(g.user['id'],))
            log_change(cursor.lastrowid,'cadastro')
        return jsonify(id=cursor.lastrowid),201

    @app.put('/api/features/<int:feature_id>')
    @protected(write=True)
    def update_feature(feature_id):
        body=request.get_json(silent=True)
        try:
            data=validate(body)
        except ValueError as error:
            return jsonify(error=str(error)),400
        if type(body.get('version')) is not int:
            return jsonify(error='Informe a versão do registro.'),400
        with db():
            cursor=db().execute("UPDATE features SET name=?,kind=?,description=?,status=?,geometry=?,source=?,observed_on=?,photo_url=?,category=?,geometry_file=?,version=version+1,updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id=? AND version=? AND archived=0",
                               tuple(data[k] for k in ('name','kind','description','status','geometry','source','observed_on','photo_url','category','geometry_file'))+(feature_id,body['version']))
            if not cursor.rowcount:
                exists=db().execute('SELECT id FROM features WHERE id=? AND archived=0',(feature_id,)).fetchone()
                return jsonify(error='Registro alterado por outra pessoa. Recarregue.' if exists else 'Registro não encontrado.'),409 if exists else 404
            log_change(feature_id,'edicao')
        return jsonify(id=feature_id)

    @app.post('/api/features/<int:feature_id>/archive')
    @protected(write=True)
    def archive(feature_id):
        if g.user['role'] != 'gestor':
            return jsonify(error='Somente o gestor pode arquivar.'),403
        body=request.get_json(silent=True)
        if not isinstance(body,dict) or type(body.get('version')) is not int:
            return jsonify(error='Informe a versão do registro.'),400
        with db():
            cursor=db().execute("UPDATE features SET archived=1,version=version+1,updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id=? AND archived=0 AND version=?",(feature_id,body['version']))
            if not cursor.rowcount:
                return jsonify(error='Registro ausente ou alterado. Recarregue.'),409
            log_change(feature_id,'arquivamento')
        return '',204

    @app.post('/api/import-geometry')
    @protected(write=True)
    def import_geometry():
        uploaded = request.files.get('file')
        if not uploaded or not uploaded.filename:
            return jsonify(error='Selecione um arquivo GPX ou KML.'),400
        try:
            geometry = parse_file(uploaded.stream.read(MAX_FILE_SIZE+1), uploaded.filename, request.form.get('kind'))
        except ValueError as error:
            return jsonify(error=str(error)),400
        return jsonify(geometry=geometry,geometry_file=secure_filename(uploaded.filename)[:250],length_m=length_m(geometry))

    @app.delete('/api/features/<int:feature_id>')
    @protected(write=True)
    def delete_feature(feature_id):
        if g.user['role'] != 'gestor':
            return jsonify(error='Somente o gestor pode excluir.'),403
        body = request.get_json(silent=True)
        if not isinstance(body,dict) or type(body.get('version')) is not int:
            return jsonify(error='Informe a versão do registro.'),400
        with db():
            db().execute('BEGIN IMMEDIATE')
            row = db().execute('SELECT version FROM features WHERE id=?',(feature_id,)).fetchone()
            if not row:
                return jsonify(error='Registro não encontrado.'),404
            if row['version'] != body['version']:
                return jsonify(error='Registro alterado. Recarregue antes de excluir.'),409
            db().execute('DELETE FROM history WHERE feature_id=?',(feature_id,))
            db().execute('DELETE FROM features WHERE id=?',(feature_id,))
        return '',204

    @app.get('/api/features/<int:feature_id>/history')
    @protected()
    def history(feature_id):
        if not db().execute('SELECT id FROM features WHERE id=?',(feature_id,)).fetchone():
            return jsonify(error='Registro não encontrado.'),404
        entries=db().execute('SELECT h.action,h.snapshot,h.created_at,u.username FROM history h JOIN users u ON u.id=h.actor_id WHERE feature_id=? ORDER BY h.id DESC',(feature_id,)).fetchall()
        return jsonify(items=[dict(entry) for entry in entries])

    @app.cli.command('init-db')
    def init_db():
        Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
        connection=sqlite3.connect(app.config['DATABASE'])
        connection.executescript(Path(app.root_path,'schema.sql').read_text(encoding='utf-8'))
        connection.close()
        click.echo('Banco inicializado (registros existentes preservados).')

    @app.cli.command('create-user')
    @click.argument('username')
    @click.option('--role',type=click.Choice(['gestor','editor','leitor']),default='gestor')
    @click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True)
    def create_user(username,role,password):
        if len(password)<10:
            raise click.ClickException('Use uma senha de pelo menos 10 caracteres.')
        g.app_database=app.config['DATABASE']
        try:
            with db():
                db().execute('INSERT INTO users(username,password_hash,role) VALUES (?,?,?)',(username,generate_password_hash(password),role))
        except sqlite3.IntegrityError:
            raise click.ClickException('Usuário já existe.') from None
        click.echo('Usuário criado.')

    return app
