#!/usr/bin/env python3
"""Contained hostile-archive and exact-tree acceptance tests. No native/model/network."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packet_installer', ROOT/'scripts/install_p3_review_packet.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(files, entries=None, extra=None, duplicate=False, symlink=False):
    entries = entries or [{'path':name,'sha256':sha(data),'kind':'text'} for name,data in sorted(files.items())]
    manifest = (json.dumps({'schema_version':1,'files':entries},indent=2)+'\n').encode()
    payload = dict(files)
    payload[m.MANIFEST_FILE] = manifest
    if extra:
        payload.update(extra)
    out = io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = ((stat.S_IFLNK if symlink and name == 'a.txt' else stat.S_IFREG)|0o600)<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
        if duplicate:
            z.writestr('a.txt',files['a.txt'])
    return out.getvalue(),manifest,entries

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='packet-install-test-',dir=ROOT/'delivery')
        self.root=Path(self.temp.name)/'lab'
        (self.root/'delivery').mkdir(parents=True)
        self.archive=self.root/'delivery'/m.ARCHIVE_NAME
        self.destination=self.root/'delivery'/m.PACKET_NAME
        self.files={'a.txt':b'alpha\n','nested/b.txt':b'beta\n'}
        self.patches=[]
        self.configure()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def configure(self,**kwargs):
        raw,manifest,entries=blob(self.files,**kwargs)
        self.archive.write_bytes(raw)
        for name,value in [('ARCHIVE_SHA256',sha(raw)),('ARCHIVE_BYTES',len(raw)),
                           ('MANIFEST_SHA256',sha(manifest)),('MANIFEST_ENTRIES',len(entries))]:
            p=patch.object(m,name,value);p.start();self.patches.append(p)
    def refuse(self):
        with self.assertRaises((m.Stop,OSError)):
            m.install_packet(self.root,self.archive)
        self.assertFalse(self.destination.exists())
    def test_complete_install_and_reuse_without_archive(self):
        first=m.install_packet(self.root,self.archive)
        self.assertTrue(first['writes_performed'])
        self.assertEqual((self.destination/'a.txt').read_bytes(),b'alpha\n')
        self.archive.unlink()
        second=m.install_packet(self.root,self.archive)
        self.assertFalse(second['writes_performed'])
        self.assertEqual(first['manifest_sha256'],second['manifest_sha256'])
    def test_inspection_writes_nothing(self):
        result=m.inspect_packet(self.root)
        self.assertFalse(result['writes_performed'])
        self.assertFalse(self.destination.exists())
    def test_wrong_outer_hash_stops_before_destination(self):
        b=self.archive.read_bytes();self.archive.write_bytes(b[:-1]+bytes([b[-1]^1]));self.refuse()
    def test_absolute_path_rejected(self):
        self.files={'/escape.txt':b'no'};self.configure();self.refuse()
    def test_traversal_path_rejected(self):
        self.files={'../escape.txt':b'no'};self.configure();self.refuse()
        self.assertFalse((self.root/'delivery'/'escape.txt').exists())
    def test_symlink_member_rejected(self):
        self.configure(symlink=True);self.refuse()
    def test_duplicate_member_rejected(self):
        self.configure(duplicate=True);self.refuse()
    def test_extra_member_rejected(self):
        self.configure(extra={'extra.txt':b'extra'});self.refuse()
    def test_member_hash_mismatch_rejected(self):
        entries=[{'path':name,'sha256':'0'*64,'kind':'text'} for name in self.files]
        self.configure(entries=entries);self.refuse()
    def test_partial_tree_preserved(self):
        self.destination.mkdir();sentinel=self.destination/'a.txt';sentinel.write_bytes(b'partial-original')
        with self.assertRaises((m.Stop,OSError)):m.install_packet(self.root,self.archive)
        self.assertEqual(sentinel.read_bytes(),b'partial-original')
    def test_changed_complete_tree_preserved(self):
        m.install_packet(self.root,self.archive);sentinel=self.destination/'a.txt';sentinel.write_bytes(b'changed')
        with self.assertRaises(m.Stop):m.verify_packet(self.root)
        self.assertEqual(sentinel.read_bytes(),b'changed')
    def test_extra_empty_directory_rejected(self):
        m.install_packet(self.root,self.archive);(self.destination/'unexpected').mkdir()
        with self.assertRaises(m.Stop):m.verify_packet(self.root)
    def test_destination_symlink_rejected(self):
        elsewhere=Path(self.temp.name)/'elsewhere';elsewhere.mkdir();self.destination.symlink_to(elsewhere,target_is_directory=True)
        with self.assertRaises(m.Stop):m.install_packet(self.root,self.archive)
        self.assertEqual(list(elsewhere.iterdir()),[])
    def test_nonfixed_archive_argument_rejected(self):
        with self.assertRaises(m.Stop):m.install_packet(self.root,self.archive.parent/'another.zip')
        self.assertFalse(self.destination.exists())
    def test_hardlinked_packet_member_rejected(self):
        m.install_packet(self.root,self.archive)
        os.link(self.destination/'a.txt',self.root/'outside-link.txt')
        with self.assertRaises(m.Stop):m.verify_packet(self.root)
    def test_writer_rejects_symlink_intermediate(self):
        self.destination.mkdir();outside=Path(self.temp.name)/'outside';outside.mkdir()
        (self.destination/'nested').symlink_to(outside,target_is_directory=True)
        fd=os.open(self.destination,os.O_RDONLY|os.O_DIRECTORY)
        try:
            with self.assertRaises(OSError):m._write_relative(fd,'nested/escape.txt',b'no')
        finally:os.close(fd)
        self.assertEqual(list(outside.iterdir()),[])

if __name__=='__main__':unittest.main(verbosity=2)
