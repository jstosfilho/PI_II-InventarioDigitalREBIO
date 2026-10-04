"""Servidor isolado para revisão visual; não modifica o banco do usuário."""
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[1]))
import json
import secrets
import sqlite3
from pathlib import Path
from inventario import create_app
from werkzeug.security import generate_password_hash
from waitress import serve

if __name__=='__main__':
    folder=Path('tmp/figma-qa')
    folder.mkdir(parents=True,exist_ok=True)
    database=folder/'preview.sqlite3'
    app=create_app({'DATABASE':str(database.resolve()),'SECRET_KEY':secrets.token_hex(32),'TEMPLATES_AUTO_RELOAD':True})
    app.test_cli_runner().invoke(args=['init-db'])
    connection=sqlite3.connect(database)
    with connection:
        connection.execute('INSERT OR IGNORE INTO users(username,password_hash,role) VALUES (?,?,?)',('revisao',generate_password_hash('somente-teste-figma'),'gestor'))
        uid=connection.execute('SELECT id FROM users WHERE username=?',('revisao',)).fetchone()[0]
        if not connection.execute('SELECT id FROM features LIMIT 1').fetchone():
            for index,(name,kind,description) in enumerate([
                ('Trilha da Cachoeira','trilha','Extensão demonstrativa, nível moderado, mata preservada.'),
                ('Nascente Principal','nascente','Vazão permanente monitorada, bacia norte da reserva.'),
                ('Trilha do Mirante','trilha','Acesso ao pico de observação e torre de fiscalização.'),
                ('Nascente Três Córregos','nascente','Ponto de confluência hidrológica sul.'),
                ('Trilha da Boa Vista','trilha','Rota primária de patrulhamento da guarda florestal.')]):
                coords=[-46.30+index*.005,-23.77+index*.004]
                geometry={'type':'Point','coordinates':coords} if kind=='nascente' else {'type':'LineString','coordinates':[coords,[coords[0]+.003,coords[1]+.002]]}
                connection.execute('INSERT INTO features(name,kind,description,status,geometry,source,observed_on,created_by,photo_url,category) VALUES (?,?,?,?,?,?,?,?,?,?)',(name,kind,description,'a_verificar',json.dumps(geometry),'Dados fictícios de revisão visual','2026-01-01',uid,'https://drive.google.com/drive/folders/exemplo','Rota de Pesquisa' if kind=='trilha' else 'Nascente'))
    connection.close()
    print('Revisão visual isolada: http://127.0.0.1:5051',flush=True)
    serve(app,host='127.0.0.1',port=5051)
