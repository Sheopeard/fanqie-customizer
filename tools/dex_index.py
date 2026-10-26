import struct,zipfile,json,pathlib
def parse(b):
 def u(o):return struct.unpack_from('<I',b,o)[0]
 def leb(o):
  v=s=0
  while True:
   c=b[o];o+=1;v|=(c&127)<<s;s+=7
   if c<128:return v,o
 def table(o):return u(o),u(o+4)
 n,p=table(56);strings=[]
 for i in range(n):
  _,s=leb(u(p+4*i));e=b.index(0,s);strings.append(b[s:e].decode('utf8','replace'))
 n,p=table(64);types=[strings[u(p+4*i)] for i in range(n)]
 n,p=table(72);protos=[]
 for i in range(n):
  o=p+12*i;args=u(o+8);params=[] if not args else [types[struct.unpack_from('<H',b,args+4+2*j)[0]] for j in range(u(args))]
  protos.append((types[u(o+4)],params))
 n,p=table(80);fields=[]
 for i in range(n):
  c,t,s=struct.unpack_from('<HHI',b,p+8*i);fields.append((strings[s],types[t]))
 n,p=table(88);methods=[]
 for i in range(n):
  c,t,s=struct.unpack_from('<HHI',b,p+8*i);methods.append((strings[s],*protos[t]))
 n,p=table(96);out={}
 for i in range(n):
  o=p+i*32;c,flags,sup,interfaces,source,annotations,data,static=struct.unpack_from('<8I',b,o)
  info={'source':strings[source] if source!=0xffffffff else None,'super':types[sup] if sup!=0xffffffff else None,'fields':[],'methods':[]}
  if data:
   counts=[]
   for _ in range(4):v,data=leb(data);counts.append(v)
   for ct in counts[:2]:
    idx=0
    for _ in range(ct):
     diff,data=leb(data);idx+=diff;access,data=leb(data);info['fields'].append(fields[idx])
   for ct in counts[2:]:
    idx=0
    for _ in range(ct):
     diff,data=leb(data);idx+=diff;access,data=leb(data);code,data=leb(data);info['methods'].append(methods[idx])
  out[types[c][1:-1].replace('/','.')]=info
 return out
