#!/usr/bin/env python3
"""5-bit written-text encoding, fixed semantic windows; not historic interoperable ITA2."""
import importlib.util
import json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
F=R/'BRAILLE_FIXED_WINDOW_20261108'
spec=importlib.util.spec_from_file_location('rll_braille_reference',F/'medir.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
text=(F/'texto_portugues.txt').read_text(encoding='utf-8')
BR=getattr(ref,'braille',None) or ref.to_braille
FROM_BR=getattr(ref,'decode_braille',None) or ref.from_braille
PACK_BR=getattr(ref,'packed6',None) or ref.pack6
COMPRESS=getattr(ref,'compress',None) or ref.zstd_window_1k
ALPH='abcdefghijklmnopqrstuvwxyz .,:'
LET={'e':1,'a':3,' ':4,'s':5,'i':6,'u':7,'d':9,'r':10,'j':11,'n':12,'f':13,'c':14,
'k':15,'t':16,'z':17,'l':18,'w':19,'h':20,'y':21,'p':22,'q':23,'o':24,'b':25,
'g':26,'m':28,'x':29,'v':30}
FIG={'3':1,'-':3,' ':4,"'":5,'8':6,'7':7,'4':10,',':12,':':14,'(':15,'5':16,
'+':17,')':18,'2':19,'6':21,'0':22,'1':23,'9':24,'?':25,'.':28,'/':29,'=':30}
RL={v:k for k,v in LET.items()};RF={v:k for k,v in FIG.items()}

def escape(ch):
    bs=ch.encode('utf-8');return [0,len(bs),*(x for byte in bs for x in (byte>>5,byte&31))]

def code_custom(s):
    return [v for ch in s for v in ([ALPH.index(ch)] if ch in ALPH else [31,*escape(ch)[1:]])]

def code_ita(s):
    seq=[];state='L'
    for ch in s:
        if ch==' ':seq.append(4)
        elif ch in LET:
            if state!='L':seq.append(31);state='L'
            seq.append(LET[ch])
        elif ch in FIG:
            if state!='F':seq.append(27);state='F'
            seq.append(FIG[ch])
        else:seq.extend(escape(ch))
    return seq

def pack(seq):
    b=bytearray(len(seq).to_bytes(4,'big'));acc=bits=0
    for x in seq:
        if not 0<=x<32:raise ValueError('not five bits')
        acc=(acc<<5)|x;bits+=5
        while bits>=8:
            bits-=8;b.append(acc>>bits);acc&=(1<<bits)-1
    if bits:b.append(acc<<(8-bits))
    return bytes(b)

def unpack(data):
    n=int.from_bytes(data[:4],'big')
    if len(data)!=4+(5*n+7)//8:raise ValueError('length invalid')
    out=[];acc=bits=0
    for x in data[4:]:
        acc=(acc<<8)|x;bits+=8
        while bits>=5 and len(out)<n:
            bits-=5;out.append((acc>>bits)&31);acc&=(1<<bits)-1
    if acc:raise ValueError('padding invalid')
    return out

def unescape(codes,i):
    n=codes[i];i+=1
    if not 1<=n<=4 or i+2*n>len(codes):raise ValueError('bad UTF8 escape')
    raw=bytes((codes[i+2*k]<<5)|codes[i+2*k+1] for k in range(n))
    char=raw.decode('utf-8')
    if len(char)!=1:raise ValueError('not a single unicode scalar')
    return char,i+2*n

def decode(codes,ita=False):
    out=[];i=0;mode='L'
    while i<len(codes):
        x=codes[i];i+=1
        if ita and x==27:mode='F';continue
        if ita and x==31:mode='L';continue
        if x==(0 if ita else 31):
            ch,i=unescape(codes,i);out.append(ch);continue
        if ita:
            if x==4:out.append(' ');continue
            table=RL if mode=='L' else RF
            if x not in table:raise ValueError('invalid ITA2 symbol')
            out.append(table[x])
        else:
            if x>=len(ALPH):raise ValueError('invalid custom symbol')
            out.append(ALPH[x])
    return ''.join(out)

def run():
    assert len(text)==1256
    sums={}
    for i,start in enumerate(range(0,len(text),256),1):
        part=text[start:start+256];braille=BR(part)
        assert FROM_BR(braille)==part
        custom=code_custom(part);ita=code_ita(part)
        for codes,flag in ((custom,False),(ita,True)):
            assert decode(unpack(pack(codes)),flag)==part
        cases={'PT_UTF8':part.encode(),'BRAILLE_6BIT':PACK_BR(braille),
               'CUSTOM_5BIT':pack(custom),'ITA2_EXT_5BIT':pack(ita)}
        for name,payload in cases.items():
            zipped=COMPRESS(payload)
            assert len(zipped)>0
            sums.setdefault(name,[0,0]);sums[name][0]+=len(payload);sums[name][1]+=len(zipped)
    expected={'PT_UTF8':(1304,945),'BRAILLE_6BIT':(984,1049),
              'CUSTOM_5BIT':(1016,1081),'ITA2_EXT_5BIT':(1027,1092)}
    if {k:tuple(v) for k,v in sums.items()}!=expected:raise ValueError('measurement drift')
    print(json.dumps({'windows':[256,256,256,256,232], 'bytes':sums,
                      'claim_allowed':False,'roundtrip':True},ensure_ascii=False,indent=2))
    print('PASS_SCOPED: 5 matched windows; lossless decoding; no source execution claims')
if __name__=='__main__':run()
