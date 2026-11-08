#!/usr/bin/env python3
"""Deterministic 128x128 glyph raster FFT (stdlib) and gated real Libras frame input.

FFT power entropy is NOT language entropy. Synthetic hand glyph is NOT a
validated Libras sign and NEVER fills the real-image evidence field.
"""
from __future__ import annotations
import argparse
from collections import Counter
import cmath
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

ROOT=Path(__file__).resolve().parents[2]
N=128

def blank():return bytearray([255])*(N*N)
def rectangle(arr,x0,y0,x1,y1,color=0):
    for y in range(max(0,y0),min(N,y1)):
        k=y*N
        for x in range(max(0,x0),min(N,x1)):arr[k+x]=color

def ellipse(arr,cx,cy,rx,ry,color=0):
    for y in range(max(0,cy-ry),min(N,cy+ry+1)):
        for x in range(max(0,cx-rx),min(N,cx+rx+1)):
            if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1:arr[y*N+x]=color

def line(arr,x0,y0,x1,y1,width=3):
    steps=max(abs(x1-x0),abs(y1-y0),1)
    for s in range(steps+1):
        t=s/steps;ellipse(arr,round(x0+(x1-x0)*t),round(y0+(y1-y0)*t),max(1,width//2),max(1,width//2))

def braille(cells):
    arr=blank();n=len(cells);spacing= (N-16)//n
    coords=((0,0),(0,1),(0,2),(1,0),(1,1),(1,2))
    for i,c in enumerate(cells):
        bits=ord(c)-0x2800
        if not (0<=bits<=63):raise ValueError('NOT_SIX_DOT_BRAILLE')
        center=8+i*spacing+spacing//2
        for j,(column,row) in enumerate(coords):
            x=center+(column*10-5);y=49+row*13
            if bits&(1<<j):ellipse(arr,x,y,4,4)
    return arr

def western_five():
    # Seven-segment numeral 5 encoded with three horizontal, two vertical strokes.
    a=blank()
    for seg in ((45,25,83,32),(45,57,83,64),(45,89,83,96),(43,26,50,63),(78,60,85,96)):
        rectangle(a,*seg)
    return a

def mayan_five():
    # For number 5, one bar in vigesimal notation. Simplified diagram, not glyph font.
    a=blank();rectangle(a,29,62,100,70);return a

def egyptian_five():
    # Five strokes as schematic tally, distinct from the actual glyph rendering font.
    a=blank()
    for i in range(5):line(a,32+i*16,34,32+i*16,94,4)
    return a

def hand_proxy():
    # Deliberately nonvalidated stylized open-hand icon: NO REAL LIBRAS CLAIM.
    a=blank();rectangle(a,42,62,90,104)
    for x,y in ((43,30),(54,20),(65,15),(76,20),(87,30)):
        rectangle(a,x,y,x+8,70)
    line(a,44,68,21,47,10)
    return a

def pgm_bytes(a):return f'P5\n{N} {N}\n255\n'.encode('ascii')+bytes(a)
def png_bytes(a):
    def chunk(kind,contents):return struct.pack('>I',len(contents))+kind+contents+struct.pack('>I',zlib.crc32(kind+contents)&0xffffffff)
    raw=b''.join(b'\x00'+bytes(a[r*N:(r+1)*N]) for r in range(N))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')

def fft1(a):
    n=len(a)
    if n&(n-1):raise ValueError('FFT_NON_POWER_OF_TWO')
    a=list(a);j=0
    for i in range(1,n):
        b=n>>1
        while j&b:j^=b;b>>=1
        j^=b
        if i<j:a[i],a[j]=a[j],a[i]
    length=2
    while length<=n:
        angle=-2*math.pi/length
        wn=complex(math.cos(angle),math.sin(angle))
        for pos in range(0,n,length):
            w=1+0j
            for k in range(length//2):
                u=a[pos+k];v=a[pos+k+length//2]*w
                a[pos+k]=u+v;a[pos+k+length//2]=u-v;w*=wn
        length*=2
    return a

def spectral_entropy(pixels):
    if len(pixels)!=N*N:raise ValueError('FRAME_SIZE_NOT_128_SQUARE')
    # subtract mean, zero DC; FFT separately across rows and columns.
    mean=sum(pixels)/len(pixels)
    rows=[fft1([complex(pixels[y*N+x]-mean,0) for x in range(N)]) for y in range(N)]
    transformed=[[0j]*N for _ in range(N)]
    for x in range(N):
        col=fft1([rows[y][x] for y in range(N)])
        for y in range(N):transformed[y][x]=col[y]
    spectrum=[abs(transformed[y][x])**2 for y in range(N) for x in range(N) if x or y]
    total=sum(spectrum)
    if total<=0: return 0.0,0.0
    ent=-sum((p/total)*math.log2(p/total) for p in spectrum if p)
    return ent, ent/math.log2(N*N-1)

def h_pixel(pixels):
    c=Counter(pixels);total=len(pixels)
    return -sum((n/total)*math.log2(n/total) for n in c.values())

def read_pgm(path):
    raw=path.read_bytes();header=f'P5\n{N} {N}\n255\n'.encode()
    if not raw.startswith(header) or len(raw)!=len(header)+N*N:
        raise ValueError('PGM_SOURCE_DIMENSIONS_OR_FORMAT_INVALID')
    return bytearray(raw[len(header):])

def result(label, pixels, kind, source_ref):
    raw=bytes(pixels);pgm=pgm_bytes(pixels);png=png_bytes(pixels)
    e,norm=spectral_entropy(pixels)
    return {'id':label,'kind':kind,'width':N,'height':N,'raw_grayscale_bytes':len(raw),
       'pgm_bytes':len(pgm),'png_bytes':len(png),
       'raw_zlib9_bytes':len(zlib.compress(raw,9)),
       'pixel_entropy_bits':round(h_pixel(pixels),6),
       'spatial_fft_power_entropy_bits':round(e,6),
       'fft_entropy_normalized':round(norm,6),
       'sha256_pgm':hashlib.sha256(pgm).hexdigest(),
       'source_ref':source_ref,'claim_allowed':False},pgm,png

def visual_benchmark(outdir,libras=None,provenance=None):
    outdir.mkdir(parents=True,exist_ok=True)
    glyphs=[
      ('digit_5',western_five(),'SYNTHETIC_NUMERAL_GLYPH','AUTHOR_7_SEGMENT'),
      ('braille_pt_cinco',braille('⠉⠊⠝⠉⠕'),'SYNTHETIC_RASTER_OF_VERIFIED_DOT_CELLS','UNICODE_BRAILLE_PT'),
      ('braille_pt_numeric_5',braille('⠼⠑'),'SYNTHETIC_RASTER_OF_DOT_CELLS','UNICODE_BRAILLE_PT_NUMERIC'),
      ('mayan_five',mayan_five(),'SYNTHETIC_SCHEMATIC_BAR_NOT_FONT','UNICODE_MAYAN_NUMERAL_FIVE'),
      ('egyptian_five',egyptian_five(),'SYNTHETIC_SCHEMATIC_5_STROKES_NOT_FONT','UNICODE_EGYPTIAN_Z015D'),
      ('open_hand_PROXY_NOT_LIBRAS',hand_proxy(),'NONVALIDATED_SYNTHETIC_HAND_GLYPH','NO_REAL_LIBRAS_EVIDENCE')]
    if libras:
        if not provenance:raise ValueError('LIBRAS_PROVENANCE_REQUIRED')
        p=json.loads(provenance.read_text(encoding='utf-8'))
        for k in ('corpus','gloss','license','source_sha256','crop_policy','frame_number'):
            if not p.get(k):raise ValueError('LIBRAS_PROVENANCE_MISSING_'+k)
        if p['gloss'].casefold() not in ('cinco','five','5'):raise ValueError('NOT_ALIGNED_TO_5')
        glyphs.append(('REAL_LIBRAS_CINCO',read_pgm(libras),'REAL_FRAME_INPUT_NOT_TRANSLATION_PROOF',p))
    results=[]
    for key,img,kind,source in glyphs:
        record,pgm,png=result(key,img,kind,source)
        (outdir/(key+'.pgm')).write_bytes(pgm)
        (outdir/(key+'.png')).write_bytes(png)
        results.append(record)
    receipt={'schema':'rll.visual_fft_v2','image_size':[N,N],'color':'L8','FFT':'2D_FFT_DC_REMOVED_POWER_NORMALIZED',
       'real_libras':'INPUT_PROVIDED_NOT_YET_LINGUISTICALLY_VALIDATED' if libras else 'TOKEN_VAZIO_REAL_LIBRAS_FRAME',
       'fft_is_language_entropy':False,'compare_across_modalities':'NOT_JUSTIFIED_BY_FFT',
       'images':results,'claim_allowed':False}
    (outdir/'fft_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return receipt

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT/'results/audit/rll_visual_fft_v2');p.add_argument('--libras-pgm',type=Path);p.add_argument('--provenance',type=Path)
    a=p.parse_args();r=visual_benchmark(a.output_dir,a.libras_pgm,a.provenance)
    print(json.dumps({'status':'PASS_SCOPED_SYNTHETIC_IMAGES_ONLY','images':len(r['images']),'libras':r['real_libras']}))
if __name__=='__main__':main()
