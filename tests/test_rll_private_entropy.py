"""Bounded falsifiers on synthetic pixels only; no private RLL or Voynich data."""
import base64
import json
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "private_entropy"))
import joao_matheus as e

class EntropyTests(unittest.TestCase):
    def test_flat_vs_gradient(self):
        flat = bytes([50] * 256)
        noisy = bytes((i*73 + i//16*29) % 256 for i in range(256))
        a = e.quadrant_metrics(flat,16,16)
        b = e.quadrant_metrics(noisy,16,16)
        self.assertEqual(len(a),16)
        self.assertEqual(a[0]['entropy_4bit_normalized'],0)
        self.assertGreater(sum(z['entropy_4bit_normalized'] for z in b),0)
    def test_inverse_order_with_same_measurements(self):
        x = e.quadrant_metrics(bytes(i%256 for i in range(256)),16,16)
        p=e.paired_matrices(x)
        self.assertEqual(set(v['quadrant'] for v in p['JOAO_low_complexity_first']),
                         set(v['quadrant'] for v in p['MATHEUS_high_complexity_first']))
        self.assertEqual(sorted(x,key=lambda v:(v['complexity_proxy'],v['quadrant'])),p['JOAO_low_complexity_first'])
    def test_too_small_rejected(self):
        with self.assertRaises(e.GateBlocked): e.quadrant_metrics(bytes([0]*9),3,3)
    def test_missing_key_rejected(self):
        for expected,entered in [('','pass'),('short','short'),('x'*24,'y'*24)]:
            with self.assertRaises(e.GateBlocked):e.require_operator_secret(expected,entered)
    def test_correct_key(self):
        e.require_operator_secret('a'*32,'a'*32)
    def test_pat_denies_elevated_and_missing_permissions(self):
        class Resp:
            def __init__(self,perm):self.perm=perm
            def __enter__(self):return self
            def __exit__(self,*_):return False
            def read(self,_):return json.dumps({'full_name':e.REPOSITORY,'permissions':self.perm}).encode()
        for perms in ({'pull': True,'push':True,'admin':True},
                      {'pull':True},None):
            with self.assertRaises(e.GateBlocked): e.verify_read_only_pat('never-real',opener=lambda *a,**kw:Resp(perms))
        e.verify_read_only_pat('never-real',opener=lambda *a,**kw:Resp({'pull':True,'push':False,'admin':False}))
    @unittest.skipUnless(importlib.util.find_spec("cryptography"), "cryptography dependency not installed")
    def test_encrypt_roundtrip_and_tamper(self):
        from cryptography.hazmat.primitives.asymmetric import x25519
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
        sk=x25519.X25519PrivateKey.generate()
        pub=sk.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
        sealed=e.encrypt_to_recipient(b'PRIVATE_TEST_ONLY',pub)
        epk=x25519.X25519PublicKey.from_public_bytes(base64.b64decode(sealed['ephemeral_public_b64']))
        key=HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=e.AUDIENCE).derive(sk.exchange(epk))
        nonce=base64.b64decode(sealed['nonce_b64']);ct=base64.b64decode(sealed['ciphertext_b64'])
        self.assertEqual(AESGCM(key).decrypt(nonce,ct,e.AUDIENCE),b'PRIVATE_TEST_ONLY')
        self.assertNotIn('PRIVATE_TEST_ONLY',json.dumps(sealed))
        with self.assertRaises(Exception): AESGCM(key).decrypt(nonce,ct[:-1]+bytes([ct[-1]^1]),e.AUDIENCE)
    def test_no_input_read_before_gate(self):
        class A:
            input_private_image='/not/an/image.png';source_ref='x';out_encrypted='/tmp/nonexistent.json'
        with patch.dict(e.os.environ,{'RLL_ENTROPY_OPERATOR_KEY':'a'*32}):
            with patch.object(e.getpass,'getpass',return_value='wrong'):
                with patch.object(e.Path,'read_bytes',side_effect=AssertionError('must not read')):
                    with self.assertRaises(e.GateBlocked):e.run(A())

if __name__=='__main__':unittest.main()
