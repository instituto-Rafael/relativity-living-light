"""Isolated host build + independent exact-reference comparisons. No physics."""
import ctypes
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
C_SOURCE = ROOT / 'core/lowlevel_runtime/c/rll_quantized_orbit_u32.c'
PY_ORACLE = ROOT / 'tools/rll_exact_quantized_orbit.py'

class Result(ctypes.Structure):
    _fields_ = [('status', ctypes.c_uint32), ('base', ctypes.c_uint32),
                ('exponent', ctypes.c_uint32), ('exact_step', ctypes.c_uint32),
                ('boundary_integer', ctypes.c_uint32), ('cycles', ctypes.c_uint32),
                ('vertices_per_cycle', ctypes.c_uint32), ('permutation_sign', ctypes.c_int)]

class FreestandingU32Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cc = shutil.which('clang') or shutil.which('gcc')
        if not cls.cc: raise unittest.SkipTest('missing host C compiler: NOT_RUN')
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / 'orbit.so'
        args = [cls.cc, '-O2', '-std=c11', '-ffreestanding', '-fno-builtin',
                '-fno-stack-protector', '-fPIC', '-shared', '-nostdlib',
                '-Wl,-z,defs', '-Wall', '-Wextra', '-Werror',
                str(C_SOURCE), '-o', str(output)]
        subprocess.run(args, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.lib.rll_q_orbit_u32.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.rll_q_orbit_u32.restype = Result
        spec = importlib.util.spec_from_file_location('rll_ref', PY_ORACLE)
        cls.ref = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ref)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'tmp'): cls.tmp.cleanup()

    def test_positive_matrices_compare_oracle(self):
        for b in [1, 2, 3, 6, 7, 8, 13, 16, 42, 75, 100, 255, 65535]:
            for n in range(32):
                out = self.lib.rll_q_orbit_u32(b, n)
                if b <= 100 and n <= 8:
                    self.assertEqual(out.status, 0, (b, n))
                if out.status != 0:
                    self.assertEqual(out.status, 2)
                    continue  # conservatively bounded, never claim PASS result
                ref = self.ref.audit(b, n)
                self.assertEqual(out.exact_step, ref['exact_step'], (b,n))
                self.assertEqual(bool(out.boundary_integer), ref['integer_boundary'], (b,n))
                self.assertEqual(out.cycles, ref['orbit']['cycles'], (b,n))
                self.assertEqual(out.vertices_per_cycle, ref['orbit']['vertices_per_cycle'], (b,n))
                self.assertEqual(out.permutation_sign, ref['orbit']['permutation_sign'], (b,n))

    def test_negative_and_boundary(self):
        self.assertEqual(self.lib.rll_q_orbit_u32(0,2).status, 1)
        self.assertEqual(self.lib.rll_q_orbit_u32(100,64).status, 2)
        self.assertEqual(self.lib.rll_q_orbit_u32(0xffffffff,1).status, 2)
        self.assertEqual(self.lib.rll_q_orbit_u32(100,2).exact_step, 75)
        self.assertEqual(self.lib.rll_q_orbit_u32(16,4).exact_step, 9)
        self.assertEqual(self.lib.rll_q_orbit_u32(100,2).cycles, 25)
        self.assertEqual(self.lib.rll_q_orbit_u32(100,2).permutation_sign, -1)
        self.assertEqual(self.lib.rll_q_orbit_u32(7,0).cycles, 7)
        self.assertEqual(self.lib.rll_q_orbit_u32(7,1).permutation_sign, 1)

    def test_runtime_no_dynamic_imports(self):
        nm = shutil.which('nm')
        if nm is None: raise unittest.SkipTest('nm not installed: NOT_RUN')
        # The host .so is compiled without libc and has no unresolved symbols.
        library = self.lib._name
        p = subprocess.run([nm, '-u', library], check=True, text=True, capture_output=True)
        self.assertFalse(p.stdout.strip(), p.stdout)

if __name__ == '__main__':
    unittest.main()
