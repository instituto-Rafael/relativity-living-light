#!/usr/bin/env python3
"""Produce scoped evidence receipt and deterministic manifest; never assert hardware tests."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile
r=Path(__file__).resolve().parents[1]
def output(args):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True).stdout
metrics=json.loads((r/'results/compression_42_compositions.json').read_text())
models=json.loads((r/'results/models42.json').read_text())
def valid_elf(p,cls,machine):
 s=output(['readelf','-h',str(p)])
 return cls in s and machine in s
assert valid_elf(r/'build/librllcad_android_armv7.so','ELF32','ARM')
assert valid_elf(r/'build/librllcad_android_arm64.so','ELF64','AArch64')
assert not output(['nm','-u',str(r/'build/rll_cad_armv7_neon.o')]).strip()
assert not output(['nm','-u',str(r/'build/rll_cad_svg_armv7.o')]).strip()
assert not any('NEEDED' in output(['readelf','-d',str(r/'build'/filename)]) for filename in ('librllcad_android_armv7.so','librllcad_android_arm64.so'))
qasm=(r/'build/rll_cad_armv7_neon.s').read_text()
crc_asm=(r/'build/rll_crc_hw_arm64.s').read_text()
neon=sum(len(re.findall(k,qasm)) for k in [r'vadd\.i32',r'vld1\.32',r'vst1\.32'])
crc_count=crc_asm.count('crc32b')
assert neon>=1 and crc_count>=1
receipt={
 'schema':'rll.t7_cad_q16_prototype_receipt.v1','date':'2026-11-08',
 'scope':'SCOPED_ANALYTIC_THREE_BAR_TRUSS',
 'source_is_not_artifact_is_not_execution_is_not_evidence_is_not_claim':True,
 'claim_allowed':False,'engineering_certified':False,
 'sample_count':len(models['samples']),'core_numeric':'Q16.16, software signed u64 division for no runtime',
 'scoped_unit_tests':15,'local_unit_tests_status':'PASS',
 'independent_analytic_reference_samples':42,'independent_analytic_reference':'double-precision Python model in qa/cad_checks.py',
 'hosted_8_pthread_shards':'PASS_SCOPED_SERIAL_BIT_IDENTICAL','hosted_shared_state_bytes':5208,
 'model_svg_per_sample':42,'svg_canonical_record_reconstruction':'PASS',
 'csv_binary_json_parity':'PASS',
 'svg_renderer_preview':'PASS_LOCAL_CAIROSVG',
 'armv7_elf32':'STATIC_LINKED_ANDROID_SHARED_OBJECT_NOT_DEVICE_EXECUTED',
 'arm64_elf64':'STATIC_LINKED_ANDROID_SHARED_OBJECT_NOT_DEVICE_EXECUTED',
 'android_dependency_DT_NEEDED':'NONE',
 'android_jni_and_dex':'SOURCE_ONLY_DEX_APK_NOT_BUILT',
 'jni_java_class':'HOST_JAVAC_COMPILED',
 'neon_armv7_instruction_occurrences':neon,'neon_runtime':'NOT_RUN_ON_ARM',
 'crc32_ieee_sw_known_vector':'PASS_123456789_CBF43926','aarch64_crc32b_assembly_mentions':crc_count,
 'aarch64_crc_hw_runtime':'NOT_RUN',
 'l2_cache_residency':'NOT_MEASURED',
 'torsion_shear_bending':'NOT_IMPLEMENTED',
 'physical_construction_safety':'NOT_CERTIFIED',
 'user_freestanding_boundary':'CORE_ONLY; I/O and pthreads are hosted adapters',
 'compression_stats':metrics,
 'source_of_math':'docs/ENGINEERING_CONTRACT.md',
 'next':'independent FEA, beam shear/torsion, Android ABI/DEX build and physical ARMv7 tests with receipts'
}
(r/'results/RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
files=sorted(p for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt' and not p.name.endswith('.pyc'))
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(r).as_posix() for p in files]
(r/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
files.append(r/'SHA256SUMS.txt')
zip_path=Path('/mnt/data/RAFAELIA_T7_CAD_FREESTANDING_Q16_ELF_SVG_20261108.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,arcname=r.name+'/'+p.relative_to(r).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None and len(z.namelist())==len(files)
print(json.dumps({'zip':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'files':len(files),'neon_occurrences':neon,'crc_hw_occurrences':crc_count,'svg_files':len(list((r/'svg').glob('design_*.svg'))),'elf_arm32':(r/'build/librllcad_android_armv7.so').stat().st_size,'elf_arm64':(r/'build/librllcad_android_arm64.so').stat().st_size},indent=2))
