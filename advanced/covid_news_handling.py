def e(v):n.extend(a for a in news_API_request()if(a in n or a[d]in b)-1);v in z and(q(86400,v)if z[v][1]else z.pop(v))
def o(t):b.append(t);[n.pop(n.index(a))for a in n if t==a[d]]
def k(w,x,y,j):z[x]={0:w,1:y};q(j,x)
def q(g,h):z[h]=h in z and z[h]or{};z[h][2]=s.enter(g,1,e,h)
d="title";import time as p,sched,requests;*n,b,z,s,news_API_request,update_news=[],{},sched.scheduler(p.time,p.sleep),lambda covid_terms="Covid COVID-19 coronavirus":[x for x in requests.get("http://newsapi.org/v2/top-headlines?country=gb&apiKey=[API_KEY_HERE]").json()['articles']if any(t in x[d]for t in covid_terms.split())],e