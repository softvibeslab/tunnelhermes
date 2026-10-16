import sys,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from client import NoRedirect

class RedirectTests(unittest.TestCase):
 def test_no_auth_forward_to_redirect_target(self):
  hits=[]
  class Target(BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def do_GET(self):hits.append(self.headers.get('Authorization'));self.send_response(200);self.end_headers()
  target=ThreadingHTTPServer(('127.0.0.1',0),Target)
  class Redirect(BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def do_GET(self):
    self.send_response(302);self.send_header('Location','http://127.0.0.1:'+str(target.server_address[1])+'/target');self.end_headers()
  origin=ThreadingHTTPServer(('127.0.0.1',0),Redirect)
  for s in [target,origin]:
   threading.Thread(target=s.serve_forever,daemon=True).start()
   self.addCleanup(s.server_close);self.addCleanup(s.shutdown)
  req=urllib.request.Request('http://127.0.0.1:'+str(origin.server_address[1])+'/',headers={'Authorization':'Bearer synthetic-test-token-not-real'})
  try:
   urllib.request.build_opener(NoRedirect()).open(req,timeout=3)
   self.fail('Redirect was followed')
  except urllib.error.HTTPError as e:
   self.assertEqual(e.code,302);e.close()
  self.assertEqual(hits,[])
 def test_redirect_handler_blocks_http_and_https_targets(self):
  h=NoRedirect();r=urllib.request.Request('https://origin.example/path')
  for dest in ['http://origin.example/path','https://other.example/path','https://origin.example/new']:
   with self.assertRaises(urllib.error.HTTPError):h.redirect_request(r,None,307,'Redirect',{},dest)
