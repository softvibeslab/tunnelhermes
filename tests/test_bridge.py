import copy,json,os,socket,subprocess,sys,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bridge

class ContractTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
  self.addCleanup(self.tmp.cleanup)
  self.token=Path(self.tmp.name)/'token';self.token.write_text('test-only-not-a-real-credential-'+'x'*32);self.token.chmod(0o600)
  self.c={'host':'127.0.0.1','port':0,'token_file':str(self.token),'projects':['pilot'],'repositories':{'pilot':['repo-approved']},'scratch':self.tmp.name,'profile':'test-bridge','hermes_bin':sys.executable,'workspace':self.tmp.name,'timeout':60,'policy_reviewed':True}
  self.p={'operation':'enrich_user_story','request_id':'test-001','project':'pilot','mode':'draft_only','story':{'title':'Synthetic test','description':'Only a test fixture'},'repo_candidates':[]}
 def server(self,runner=None):
  s=bridge.make_server(self.c,runner or (lambda p,c:(200,{'test_fixture':True})))
  t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
  self.addCleanup(s.server_close);self.addCleanup(s.shutdown)
  return s
 def req(self,s,p=None,auth=True,raw=None,ctype='application/json',path='/v1/enrich-user-story',method='POST'):
  h={'Content-Type':ctype}
  if auth:h['Authorization']='Bearer '+self.token.read_text()
  data=raw if raw is not None else json.dumps(self.p if p is None else p).encode()
  q=urllib.request.Request('http://127.0.0.1:'+str(s.server_address[1])+path,data=None if method=='GET' else data,headers=h,method=method)
  try:
   with urllib.request.urlopen(q,timeout=3) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:
   try:return e.code,json.load(e)
   finally:e.close()
 def test_health(self):self.assertEqual(self.req(self.server(),path='/health',method='GET'),(200,{'status':'ok'}))
 def test_unauthorized(self):self.assertEqual(self.req(self.server(),auth=False)[0],401)
 def test_unknown_route(self):self.assertEqual(self.req(self.server(),path='/other')[0],404)
 def test_invalid_operation(self):
  p=copy.deepcopy(self.p);p['operation']='execute';self.assertEqual(self.req(self.server(),p)[0],422)
 def test_draft_only(self):
  p=copy.deepcopy(self.p);p['mode']='write_requires_approval';self.assertEqual(self.req(self.server(),p)[0],422)
 def test_bad_json(self):self.assertEqual(self.req(self.server(),raw=b'{')[0],400)
 def test_bad_root(self):self.assertEqual(self.req(self.server(),raw=b'[]')[0],422)
 def test_wrong_media_type(self):self.assertEqual(self.req(self.server(),ctype='text/plain')[0],415)
 def test_body_limit(self):self.assertEqual(self.req(self.server(),raw=b'x'*(bridge.MAX_BODY+1))[0],413)
 def test_project_not_allowed(self):
  p=copy.deepcopy(self.p);p['project']='other';self.assertEqual(self.req(self.server(),p)[0],422)
 def test_repo_not_allowed(self):
  p=copy.deepcopy(self.p);p['repo_candidates']=['other'];p['branch']='main';self.assertEqual(self.req(self.server(),p)[0],422)
 def test_branch_required(self):
  p=copy.deepcopy(self.p);p['repo_candidates']=['repo-approved'];self.assertEqual(self.req(self.server(),p)[0],422)
 def test_nested_types(self):
  p=copy.deepcopy(self.p);p['story']['title']={};self.assertEqual(self.req(self.server(),p)[0],422)
 def test_unknown_fields(self):
  p=copy.deepcopy(self.p);p['command']='arbitrary';self.assertEqual(self.req(self.server(),p)[0],422)
 def test_success_runner_fixture(self):
  result=self.req(self.server());self.assertEqual(result,(200,{'test_fixture':True}))
 def test_token_rotation(self):
  s=self.server();self.token.write_text('rotated-test-only-'+'x'*40);self.assertEqual(self.req(s)[0],200)
 def test_empty_token_fails_closed(self):
  s=self.server();self.token.write_text('');self.assertEqual(self.req(s)[0],503)
 def test_insecure_token_permissions_fail_closed(self):
  s=self.server();self.token.chmod(0o644);self.assertEqual(self.req(s)[0],503)
 def test_missing_token_fails_closed(self):
  s=self.server();self.token.unlink();self.assertEqual(self.req(s,auth=False)[0],503)
 def test_error_is_sanitized(self):
  def fail(p,c):raise RuntimeError('sensitive-test-fixture')
  code,data=self.req(self.server(fail));self.assertEqual(code,500);self.assertNotIn('sensitive',json.dumps(data))
 def test_concurrency(self):
  started=threading.Event();release=threading.Event()
  def runner(p,c):started.set();release.wait(3);return 200,{'test_fixture':True}
  s=self.server(runner);results=[]
  t=threading.Thread(target=lambda:results.append(self.req(s)));t.start();self.assertTrue(started.wait(2))
  try:self.assertEqual(self.req(s)[0],429)
  finally:release.set();t.join(3)
  self.assertEqual(results[0][0],200)
 def test_private_bind_config(self):
  c=copy.deepcopy(self.c);c['host']='0.0.0.0';c['port']=8797
  p=Path(self.tmp.name)/'config.json';p.write_text(json.dumps(c))
  with self.assertRaisesRegex(ValueError,'private_bind'):bridge.load_config(p)
 def test_policy_blocks_start(self):
  c=copy.deepcopy(self.c);c['policy_reviewed']=False;c['port']=8797
  p=Path(self.tmp.name)/'config.json';p.write_text(json.dumps(c))
  with self.assertRaisesRegex(ValueError,'review_permissions'):bridge.load_config(p)
 def test_default_profile_rejected(self):
  c=copy.deepcopy(self.c);c['profile']='default';c['port']=8797
  p=Path(self.tmp.name)/'config.json';p.write_text(json.dumps(c))
  with self.assertRaisesRegex(ValueError,'dedicated'):bridge.load_config(p)
 def test_process_json_envelope(self):
  # El subprocess escribe una fixture; no es una respuesta de Hermes real.
  def child(*args,**kw):
   kw['stdout'].write(b'{"summary":"controlled-test-fixture"}');kw['stdout'].flush()
   return mock.Mock(wait=mock.Mock(return_value=0),returncode=0)
  with mock.patch('bridge.subprocess.Popen',side_effect=child):code,data=bridge.execute(self.p,self.c)
  self.assertEqual(code,200);self.assertFalse(data['evidence_verified']);self.assertEqual(data['status'],'draft')
 def test_process_bad_json(self):
  def child(*args,**kw):
   kw['stdout'].write(b'not json test fixture');kw['stdout'].flush()
   return mock.Mock(wait=mock.Mock(return_value=0),returncode=0)
  with mock.patch('bridge.subprocess.Popen',side_effect=child):code,data=bridge.execute(self.p,self.c)
  self.assertEqual(code,502)
 def test_process_timeout(self):
  proc=mock.Mock();proc.pid=12345;proc.wait.side_effect=[subprocess.TimeoutExpired('test',60),0]
  with mock.patch('bridge.subprocess.Popen',return_value=proc),mock.patch('bridge.os.killpg') as kill:
   code,data=bridge.execute(self.p,self.c)
  self.assertEqual(code,504);kill.assert_called_once()
 def test_real_subprocess_failure(self):
  # sys.executable recibe flags de Hermes, falla realmente sin llamar a un modelo.
  code,data=bridge.execute(self.p,self.c)
  self.assertEqual(code,502);self.assertEqual(data,{'error':'hermes_execution_failed'})

if __name__=='__main__':unittest.main()
