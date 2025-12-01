import requests, json
from datetime import datetime
BASE_URL = "http://127.0.0.1:8001"
FRONTEND_URL = "http://localhost:3000"
class T:
    def __init__(self):
        self.s = requests.Session(); self.e=f"test_{int(datetime.now().timestamp())}@example.com"; self.p="Test123!"; self.id=None
    def log(self,name,ok,details=""):
        print(("PASS" if ok else "FAIL"),"|",name,details)
    def backend(self):
        try:
            r=self.s.get(f"{BASE_URL}/healthz",timeout=5); self.log("health",r.status_code==200,f"status={r.status_code}"); return r.status_code==200
        except Exception as e: self.log("health",False,str(e)); return False
    def signup(self):
        try:
            r=self.s.post(f"{BASE_URL}/api/v1/auth/signup",json={"email":self.e,"password":self.p,"full_name":"Test User"},timeout=10); self.log("signup",r.status_code==200,f"status={r.status_code}"); return r.status_code==200
        except Exception as e: self.log("signup",False,str(e)); return False
    def login(self):
        try:
            r=self.s.post(f"{BASE_URL}/api/v1/auth/login",json={"email":self.e,"password":self.p},timeout=10); self.log("login",r.status_code==200,f"status={r.status_code}"); return r.status_code==200
        except Exception as e: self.log("login",False,str(e)); return False
    def me(self):
        try:
            r=self.s.get(f"{BASE_URL}/api/v1/auth/me",timeout=5); self.log("me",r.status_code==200,f"status={r.status_code}"); return r.status_code==200
        except Exception as e: self.log("me",False,str(e)); return False
    def create(self):
        try:
            r=self.s.post(f"{BASE_URL}/api/v1x/resumes/",json={"title":"Test Resume","full_name":"John Doe","email":"john.doe@example.com","phone":"+1-555-0123","professional_summary":"Experienced dev"},timeout=10); ok=r.status_code==201; self.id = (r.json().get('id') if ok else None); self.log("create",ok,f"status={r.status_code} id={self.id}"); return ok
        except Exception as e: self.log("create",False,str(e)); return False
    def get(self):
        if not self.id: self.log("get",False,"no id"); return False
        try:
            r=self.s.get(f"{BASE_URL}/api/v1x/resumes/{self.id}",timeout=5); self.log("get",r.status_code==200,f"status={r.status_code}"); return r.status_code==200
        except Exception as e: self.log("get",False,str(e)); return False
    def export_pdf(self):
        if not self.id: self.log("export_pdf",False,"no id"); return False
        try:
            r=self.s.get(f"{BASE_URL}/api/v1x/resumes/{self.id}/export?format=pdf",timeout=15); ok=r.status_code==200 and 'application/pdf' in r.headers.get('content-type',''); self.log("export_pdf",ok,f"status={r.status_code} size={len(r.content)}"); return ok
        except Exception as e: self.log("export_pdf",False,str(e)); return False
    def run(self):
        steps=[self.backend,self.signup,self.login,self.me,self.create,self.get,self.export_pdf]; return all(s() for s in steps)
if __name__=="__main__":
    t=T(); ok=t.run(); import sys; sys.exit(0 if ok else 1)
