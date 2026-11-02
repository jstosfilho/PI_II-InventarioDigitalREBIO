import json
import io
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash
from inventario import create_app


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':str(Path(self.temp.name)/'test.sqlite3')})
        result=self.app.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code,0,result.output)
        with sqlite3.connect(self.app.config['DATABASE']) as connection:
            for role in ['gestor','editor','leitor']:
                connection.execute('INSERT INTO users(username,password_hash,role) VALUES (?,?,?)',(role,generate_password_hash('teste-seguro-123'),role))
        connection.close()
        self.client=self.app.test_client()
        self.login()
        self.data=dict(name='Nascente de teste',kind='nascente',description='Dado fictício de teste',status='a_verificar',source='Teste automatizado',observed_on='2026-01-01',geometry={'type':'Point','coordinates':[-46.3,-23.77]})

    def tearDown(self):
        self.temp.cleanup()

    def login(self,role='gestor'):
        response=self.client.post('/api/login',json={'username':role,'password':'teste-seguro-123'})
        self.assertEqual(response.status_code,200)
        self.headers={'X-CSRF-Token':response.json['csrf']}

    def create(self):
        response=self.client.post('/api/features',json=self.data,headers=self.headers)
        self.assertEqual(response.status_code,201,response.json)
        return response.json['id']

    def test_authentication_and_logout(self):
        self.assertEqual(self.client.post('/api/logout',headers=self.headers).status_code,204)
        self.assertEqual(self.client.get('/api/features').status_code,401)
        self.assertEqual(self.client.get('/api/geojson').status_code,401)
        self.assertEqual(self.client.post('/api/login',json={'username':'gestor','password':'errada'}).status_code,401)

    def test_csrf_required(self):
        self.assertEqual(self.client.post('/api/features',json=self.data).status_code,403)
        self.assertEqual(self.client.post('/api/logout').status_code,403)

    def test_create_edit_archive_and_history(self):
        feature_id=self.create()
        self.data.update(name='Nome atualizado',version=1)
        self.assertEqual(self.client.put(f'/api/features/{feature_id}',json=self.data,headers=self.headers).status_code,200)
        self.assertEqual(self.client.post(f'/api/features/{feature_id}/archive',json={'version':2},headers=self.headers).status_code,204)
        self.assertEqual(self.client.get('/api/features').json['items'],[])
        history=self.client.get(f'/api/features/{feature_id}/history').json['items']
        self.assertEqual([x['action'] for x in history],['arquivamento','edicao','cadastro'])
        self.assertEqual(json.loads(history[-1]['snapshot'])['name'],'Nascente de teste')

    def test_concurrent_edit_does_not_overwrite(self):
        feature_id=self.create()
        self.data['version']=1
        self.assertEqual(self.client.put(f'/api/features/{feature_id}',json=self.data,headers=self.headers).status_code,200)
        self.data['name']='Alteração desatualizada'
        self.assertEqual(self.client.put(f'/api/features/{feature_id}',json=self.data,headers=self.headers).status_code,409)
        self.assertEqual(self.client.get('/api/features').json['items'][0]['name'],'Nascente de teste')

    def test_roles(self):
        feature_id=self.create()
        self.login('leitor')
        self.assertEqual(self.client.get('/api/features').status_code,200)
        self.assertEqual(self.client.post('/api/features',json=self.data,headers=self.headers).status_code,403)
        self.data['version']=1
        self.assertEqual(self.client.put(f'/api/features/{feature_id}',json=self.data,headers=self.headers).status_code,403)
        self.login('editor')
        self.assertEqual(self.client.put(f'/api/features/{feature_id}',json=self.data,headers=self.headers).status_code,200)
        self.assertEqual(self.client.post(f'/api/features/{feature_id}/archive',json={'version':2},headers=self.headers).status_code,403)

    def test_coordinates_are_validated(self):
        for coords in [[181,0],[0,-91],[True,0],['-46',0],[],[None,0],[float('inf'),0]]:
            with self.subTest(coords=coords):
                self.data['geometry']['coordinates']=coords
                self.assertEqual(self.client.post('/api/features',json=self.data,headers=self.headers).status_code,400)
        self.assertEqual(self.client.get('/api/features').json['items'],[])

    def test_trail_and_geojson_order(self):
        self.data.update(kind='trilha',name='Trilha de teste',geometry={'type':'LineString','coordinates':[[-46.3,-23.77],[-46.31,-23.78]]})
        self.create()
        collection=self.client.get('/api/geojson').json
        self.assertEqual(collection['type'],'FeatureCollection')
        self.assertEqual(collection['features'][0]['geometry'],self.data['geometry'])

    def test_degenerate_trails_rejected(self):
        self.data['kind']='trilha'
        for coords in [[[-46,-23]],[[-46,-23],[-46,-23]],None]:
            self.data['geometry']={'type':'LineString','coordinates':coords}
            self.assertEqual(self.client.post('/api/features',json=self.data,headers=self.headers).status_code,400)

    def test_filters_and_export_match(self):
        self.create()
        self.data.update(name='Trilha fictícia',kind='trilha',status='atencao',geometry={'type':'LineString','coordinates':[[-46,-23],[-46.1,-23.1]]})
        self.create()
        for query, count in [('kind=trilha',1),('status=conservado',0),('q=Nascente',1),('kind=nascente&status=atencao',0)]:
            self.assertEqual(len(self.client.get('/api/features?'+query).json['items']),count)
            self.assertEqual(len(self.client.get('/api/geojson?'+query).json['features']),count)

    def test_validation_of_date_and_required_fields(self):
        for changes in [{'name':'x'},{'source':''},{'observed_on':'inválido'},{'observed_on':(date.today()+timedelta(days=1)).isoformat()},{'kind':'visitante'},{'status':'qualquer'}]:
            self.assertEqual(self.client.post('/api/features',json={**self.data,**changes},headers=self.headers).status_code,400)
        for body in [[],None,'texto']:
            self.assertEqual(self.client.post('/api/features',json=body,headers=self.headers).status_code,400)

    def test_database_survives_application_restart(self):
        self.create()
        second=create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':self.app.config['DATABASE']})
        client=second.test_client()
        client.post('/api/login',json={'username':'gestor','password':'teste-seguro-123'})
        self.assertEqual(len(client.get('/api/features').json['items']),1)

    def test_initialization_preserves_existing_data(self):
        self.create()
        result=self.app.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code,0)
        self.assertEqual(len(self.client.get('/api/features').json['items']),1)

    def test_html_and_static_files(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'lang="pt-BR"',response.data)
        self.assertEqual(response.headers['Referrer-Policy'],'strict-origin-when-cross-origin')
        for path in ['/static/app.js','/static/style.css']:
            response=self.client.get(path)
            self.assertEqual(response.status_code,200)
            response.close()

    def test_photo_link_and_classification(self):
        self.data.update(photo_url='https://drive.google.com/drive/folders/exemplo',category='Rota de Pesquisa')
        self.create()
        item=self.client.get('/api/features').json['items'][0]
        self.assertEqual(item['category'],'Rota de Pesquisa')
        self.assertEqual(item['photo_url'],self.data['photo_url'])
        for url in ['javascript:alert(1)','http://drive.google.com','https://usuario:senha@example.com','https://bad url']:
            self.data['photo_url']=url
            self.assertEqual(self.client.post('/api/features',json=self.data,headers=self.headers).status_code,400)

    def test_permanent_delete_permissions_and_version(self):
        feature_id=self.create()
        self.login('editor')
        self.assertEqual(self.client.delete(f'/api/features/{feature_id}',json={'version':1},headers=self.headers).status_code,403)
        self.login()
        self.assertEqual(self.client.delete(f'/api/features/{feature_id}',json={'version':0},headers=self.headers).status_code,409)
        self.assertEqual(self.client.delete(f'/api/features/{feature_id}',json={'version':1}).status_code,403)
        self.assertEqual(self.client.delete(f'/api/features/{feature_id}',json={'version':1},headers=self.headers).status_code,204)
        self.assertEqual(self.client.get('/api/features').json['items'],[])
        self.assertEqual(self.client.get(f'/api/features/{feature_id}/history').status_code,404)

    def test_import_endpoint(self):
        response=self.client.post('/api/import-geometry',data={'kind':'nascente','file':(io.BytesIO(b'<gpx><wpt lon="-46" lat="-23"/></gpx>'),'nascente.gpx')},headers=self.headers)
        self.assertEqual(response.status_code,200,response.json)
        self.assertEqual(response.json['geometry']['coordinates'],[-46,-23])
        self.assertEqual(response.json['geometry_file'],'nascente.gpx')
        self.login('leitor')
        self.assertEqual(self.client.post('/api/import-geometry',data={},headers=self.headers).status_code,403)

    def test_existing_database_migration_preserves_data(self):
        feature_id=self.create()
        connection=sqlite3.connect(self.app.config['DATABASE'])
        try:
            for column in ['photo_url','category','geometry_file']:
                connection.execute(f'ALTER TABLE features DROP COLUMN {column}')
            connection.commit()
        finally:
            connection.close()
        migrated=create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':self.app.config['DATABASE']})
        client=migrated.test_client()
        client.post('/api/login',json={'username':'gestor','password':'teste-seguro-123'})
        item=client.get('/api/features').json['items'][0]
        self.assertEqual(item['id'],feature_id)
        self.assertEqual(item['photo_url'],'')
        self.assertTrue(Path(self.app.config['DATABASE']+'.pre-figma.bak').exists())

    def test_user_management(self):
        users=self.client.get('/api/users').json['items']
        self.assertEqual(len(users),3)
        me=next(u for u in users if u['username']=='gestor')
        created=self.client.post('/api/users',json=dict(username='visitante1',password='senha-bem-longa',role='leitor'),headers=self.headers)
        self.assertEqual(created.status_code,201)
        self.assertEqual(self.client.post('/api/users',json=dict(username='visitante1',password='senha-bem-longa',role='leitor'),headers=self.headers).status_code,409)
        self.assertEqual(self.client.post('/api/users',json=dict(username='x1234',password='curta',role='leitor'),headers=self.headers).status_code,400)
        self.assertEqual(self.client.post('/api/users',json=dict(username='abc',password='senha-bem-longa',role='root'),headers=self.headers).status_code,400)
        uid=created.json['id']
        self.assertEqual(self.client.patch(f'/api/users/{uid}',json=dict(role='editor'),headers=self.headers).status_code,200)
        self.assertEqual(self.client.patch(f'/api/users/{me["id"]}',json=dict(role='leitor'),headers=self.headers).status_code,400)
        self.assertEqual(self.client.delete(f'/api/users/{me["id"]}',headers=self.headers).status_code,400)
        self.assertEqual(self.client.delete(f'/api/users/{uid}',headers=self.headers).status_code,204)
        for role in ('editor','leitor'):
            self.login(role)
            self.assertEqual(self.client.get('/api/users').status_code,403)
            self.assertEqual(self.client.post('/api/users',json=dict(username='intruso1',password='senha-bem-longa',role='gestor'),headers=self.headers).status_code,403)

    def test_audit_log(self):
        self.client.post('/api/login',json={'username':'gestor','password':'errada-errada'})
        self.login()
        created=self.client.post('/api/users',json=dict(username='visitante2',password='senha-bem-longa',role='leitor'),headers=self.headers).json['id']
        self.client.patch(f'/api/users/{created}',json=dict(role='editor',password='outra-senha-longa'),headers=self.headers)
        self.client.delete(f'/api/users/{created}',headers=self.headers)
        feature=self.create()
        self.client.delete(f'/api/features/{feature}',json={'version':1},headers=self.headers)
        items=self.client.get('/api/audit').json['items']
        actions=[i['action'] for i in items]
        for expected in ('login_falha','login','usuario_criado','usuario_alterado','usuario_excluido','cadastro','exclusao'):
            self.assertIn(expected,actions)
        changed=next(i for i in items if i['action']=='usuario_alterado')
        self.assertIn('leitor -> editor',changed['details'])
        self.assertNotIn('senha-longa',json.dumps(items))
        self.assertEqual(items[0]['id'],max(i['id'] for i in items))
        self.assertEqual(self.client.get('/api/audit?limit=abc').status_code,400)
        self.assertEqual(self.client.get('/api/audit?from=ontem').status_code,400)
        only=self.client.get('/api/audit?action=login_falha').json['items']
        self.assertTrue(only and all(i['action']=='login_falha' for i in only))
        mine=self.client.get('/api/audit?actor=GEST').json['items']
        self.assertTrue(mine and all('gest' in i['actor_name'] for i in mine))
        self.assertEqual(self.client.get('/api/audit?actor=%25').json['items'],[])
        today=date.today().isoformat()
        self.assertTrue(self.client.get(f'/api/audit?from={today}&to={today}').json['items'])
        self.assertEqual(self.client.get('/api/audit?to=2000-01-01').json['items'],[])
        page=self.client.get('/api/audit?limit=2').json['items']
        older=self.client.get(f'/api/audit?limit=2&before={page[-1]["id"]}').json['items']
        self.assertTrue(older and older[0]['id']<page[-1]['id'])
        for role in ('editor','leitor'):
            self.login(role)
            self.assertEqual(self.client.get('/api/audit').status_code,403)


if __name__=='__main__':
    unittest.main()
