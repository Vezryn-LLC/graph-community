"""Experimental Win32 ownership primitives; imported safely on other hosts.

Only explicit Graph paths and known PIDs are inspected. No shell, administrator,
task termination, POSIX lock approximation or process enumeration is used.
"""
from contextlib import contextmanager
import ctypes as c
from functools import lru_cache
import ntpath
import os
from pathlib import Path

D = c.c_uint32
H = c.c_void_p
P = c.POINTER
B = c.c_int32


class FileTime(c.Structure):
    _fields_ = [('low', D), ('high', D)]


class FileInfo(c.Structure):
    _fields_ = [('attributes', D), ('created', FileTime), ('accessed', FileTime),
                ('written', FileTime), ('volume', D), ('size_high', D), ('size_low', D),
                ('links', D), ('index_high', D), ('index_low', D)]


class SecurityAttributes(c.Structure):
    _fields_ = [('length', D), ('descriptor', H), ('inherit', B)]


class AclSize(c.Structure):
    _fields_ = [('count', D), ('used', D), ('free', D)]


class AceHeader(c.Structure):
    _fields_ = [('kind', c.c_ubyte), ('flags', c.c_ubyte), ('size', c.c_uint16)]


def local_path(path):
    text = str(path)
    drive, tail = ntpath.splitdrive(text)
    if len(drive) != 2 or drive[1] != ':' or not tail.startswith(('\\', '/')) or ':' in tail:
        raise RuntimeError('Windows Graph requires an absolute local drive path; UNC/device/stream paths unqualified')
    parts = tail.replace('/', '\\').split('\\')[1:] if len(tail) > 1 else []
    for part in parts:
        stem = part.split('.')[0].upper()
        if not part or part.endswith((' ', '.')) or stem in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
            raise RuntimeError('Ambiguous/reserved Windows path is unavailable')
    return text


class WinAPI:
    def __init__(self):
        try:
            self.k = c.WinDLL('kernel32', use_last_error=True)
            self.a = c.WinDLL('advapi32', use_last_error=True)
        except (AttributeError, OSError) as error:
            raise RuntimeError('Native Windows APIs unavailable; no ownership fallback') from error
        signatures = {
            'GetCurrentProcess': (H, []), 'CloseHandle': (B, [H]), 'LocalFree': (H, [H]),
            'CreateFileW': (H, [c.c_wchar_p, D, D, P(SecurityAttributes), D, D, H]),
            'CreateDirectoryW': (B, [c.c_wchar_p, P(SecurityAttributes)]),
            'GetFileAttributesW': (D, [c.c_wchar_p]), 'GetDriveTypeW': (D, [c.c_wchar_p]), 'GetFileType': (D, [H]),
            'GetFileInformationByHandle': (B, [H, P(FileInfo)]),
            'DuplicateHandle': (B, [H, H, H, P(H), D, B, D]),
            'OpenProcess': (H, [D, B, D]), 'WaitForSingleObject': (D, [H, D]),
            'GetProcessTimes': (B, [H, P(FileTime), P(FileTime), P(FileTime), P(FileTime)]),
            'QueryFullProcessImageNameW': (B, [H, D, c.c_wchar_p, P(D)]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(self.k, name)
            function.restype, function.argtypes = result, args
        signatures = {
            'OpenProcessToken': (B, [H, D, P(H)]),
            'GetTokenInformation': (B, [H, c.c_int, H, D, P(D)]),
            'ConvertSidToStringSidW': (B, [H, P(c.c_wchar_p)]),
            'ConvertStringSecurityDescriptorToSecurityDescriptorW': (B, [c.c_wchar_p, D, P(H), P(D)]),
            'GetSecurityInfo': (D, [H, c.c_int, D, P(H), P(H), P(H), P(H), P(H)]),
            'GetAclInformation': (B, [H, H, D, c.c_int]), 'GetAce': (B, [H, D, P(H)]),
            'IsValidAcl': (B, [H]), 'IsValidSid': (B, [H]),
            'LookupAccountNameW': (B, [c.c_wchar_p, c.c_wchar_p, H, P(D), c.c_wchar_p, P(D), P(D)]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(self.a, name)
            function.restype, function.argtypes = result, args
        self.user = self.process_user(self.k.GetCurrentProcess())

    def checked(self, result, operation):
        if not result:
            raise OSError(c.get_last_error(), operation + ' unavailable; ownership unknown')
        return result

    def sid(self, pointer):
        if not pointer:
            raise RuntimeError('Native SID pointer unavailable')
        self.checked(self.a.IsValidSid(pointer), 'SID validation')
        value = c.c_wchar_p()
        self.checked(self.a.ConvertSidToStringSidW(pointer, c.byref(value)), 'SID conversion')
        try:
            return value.value
        finally:
            self.k.LocalFree(c.cast(value, H))

    def process_user(self, process):
        token, size = H(), D()
        self.checked(self.a.OpenProcessToken(process, 8, c.byref(token)), 'Process token')
        try:
            self.a.GetTokenInformation(token, 1, None, 0, c.byref(size))
            if not 8 <= size.value <= 65536:
                raise RuntimeError('Native token size unavailable')
            buffer = c.create_string_buffer(size.value)
            self.checked(self.a.GetTokenInformation(token, 1, buffer, size, c.byref(size)), 'Token owner')
            return self.sid(c.cast(buffer, P(H))[0])
        finally:
            self.k.CloseHandle(token)

    def trusted_installer(self):
        # Resolve one explicit OS service principal. An arbitrary fixed-volume
        # owner is never promoted to a trusted principal.
        cached = getattr(self, '_installer', False)
        if cached is not False:
            return cached
        self._installer = None
        try:
            size, domain_size, kind = D(), D(), D()
            name = r'NT SERVICE\TrustedInstaller'
            self.a.LookupAccountNameW(None, name, None, c.byref(size), None, c.byref(domain_size), c.byref(kind))
            if not 8 <= size.value <= 1024 or not 1 <= domain_size.value <= 1024:
                return None
            sid, domain = c.create_string_buffer(size.value), c.create_unicode_buffer(domain_size.value)
            if not self.a.LookupAccountNameW(None, name, sid, c.byref(size), domain, c.byref(domain_size), c.byref(kind)):
                return None
            value = self.sid(c.cast(sid, H))
            if value.startswith('S-1-5-80-'):
                self._installer = value
        except (AttributeError, OSError, RuntimeError):
            pass  # Unavailable identity remains unknown, never a root-owner wildcard.
        return self._installer

    @contextmanager
    def security(self):
        descriptor = H()
        sddl = f'O:{self.user}D:P(A;OICI;FA;;;{self.user})(A;OICI;FA;;;SY)'
        self.checked(self.a.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, c.byref(descriptor), None), 'Private DACL')
        attributes = SecurityAttributes(c.sizeof(SecurityAttributes), descriptor, False)
        try:
            yield c.byref(attributes)
        finally:
            self.k.LocalFree(descriptor)

    def no_reparse(self, path):
        local_path(path)
        if self.k.GetDriveTypeW(path.anchor) != 3:
            raise RuntimeError('Windows state/source requires a fixed local drive; mapped/removable drives unqualified')
        for item in (*reversed(path.parents), path):
            value = self.k.GetFileAttributesW(str(item))
            if value == 0xffffffff:
                if c.get_last_error() in (2, 3):
                    continue
                raise OSError(c.get_last_error(), 'Native path attributes unavailable')
            if value & 0x400:
                raise RuntimeError('Reparse/junction paths are unqualified: ' + str(item))
            if value & 0x10:
                # Validate every existing ancestor, not just the leaf: a foreign
                # DELETE_CHILD grant above private state could replace its path.
                handle = self.k.CreateFileW(str(item), 0x20000, 7, None, 3, 0x02200000, None)
                if handle in (None, c.c_void_p(-1).value):
                    raise OSError(c.get_last_error(), 'Ancestor security evidence unavailable')
                try:
                    self.validate_acl(handle, shared=True, volume_root=item == type(path)(path.anchor))
                finally:
                    self.k.CloseHandle(handle)

    def open(self, path, access=0x20000, share=7, create=3):
        self.no_reparse(path)
        with self.security() as security:
            handle = self.k.CreateFileW(str(path), access, share, security, create, 0x02200000, None)
            error = c.get_last_error()
        if handle in (None, c.c_void_p(-1).value):
            if error in (32, 33):
                raise BlockingIOError(error, 'Windows runtime handle is already owned')
            raise OSError(error, 'Native file open unavailable')
        return handle

    def validate_acl(self, handle, shared=False, volume_root=False):
        owner, dacl, descriptor = H(), H(), H()
        result = self.a.GetSecurityInfo(handle, 1, 5, c.byref(owner), None, c.byref(dacl), None, c.byref(descriptor))
        if result:
            raise OSError(result, 'Native ACL read unavailable')
        try:
            owners = {self.user} | ({'S-1-5-18', 'S-1-5-32-544'} if shared else set())
            actual_owner = self.sid(owner)
            installer = self.trusted_installer() if volume_root else None
            if installer:
                owners.add(installer)
            if actual_owner not in owners or not dacl or not self.a.IsValidAcl(dacl):
                raise RuntimeError('Private Windows owner/DACL unverified')
            size = AclSize()
            self.checked(self.a.GetAclInformation(dacl, c.byref(size), c.sizeof(size), 2), 'DACL size')
            if not 1 <= size.count <= 4096 or size.used < 8:
                raise RuntimeError('Empty/invalid Windows DACL unavailable')
            for index in range(size.count):
                pointer = H()
                self.checked(self.a.GetAce(dacl, index, c.byref(pointer)), 'DACL entry')
                if not pointer.value or not dacl.value + 8 <= pointer.value <= dacl.value + size.used - c.sizeof(AceHeader):
                    raise RuntimeError('Invalid Windows ACE address')
                header = c.cast(pointer, P(AceHeader)).contents
                if header.size < 16 or pointer.value + header.size > dacl.value + size.used or header.kind != 0:
                    raise RuntimeError('Unsupported Windows ACE; private state unavailable')
                sid_size = 8 + 4 * c.c_ubyte.from_address(pointer.value + 9).value
                if sid_size > header.size - 8:
                    raise RuntimeError('SID extends beyond Windows ACE')
                mask = c.cast(pointer.value + 4, P(D)).contents.value
                sid = self.sid(pointer.value + 8)
                # OWNER RIGHTS denotes this object's owner, already verified
                # above from the same handle/security descriptor as its DACL.
                if sid == 'S-1-3-4':
                    sid = actual_owner
                trusted = {self.user, 'S-1-5-18'} | ({'S-1-5-32-544'} if shared else set()) | ({installer} if installer else set())
                # A shared ancestor may permit creating unrelated directories or
                # inherit-only defaults; protected Graph children never inherit
                # those. Foreign delete/modify-owner/DACL/attribute rights fail.
                if sid not in trusted and (not shared or (not header.flags & 0x08 and mask & ~0x001200ad)):
                    raise RuntimeError('Windows DACL grants access beyond the private user/SYSTEM boundary')
        finally:
            self.k.LocalFree(descriptor)

    def validate(self, handle, directory=False, shared=False):
        info = FileInfo()
        self.checked(self.k.GetFileInformationByHandle(handle, c.byref(info)), 'File identity')
        if self.k.GetFileType(handle) != 1 or info.attributes & 0x400 or bool(info.attributes & 0x10) != directory or (not directory and info.links != 1):
            raise RuntimeError('Regular, unlinked, non-reparse Windows state required')
        self.validate_acl(handle, shared)
        return info

    def check(self, path, directory=False, shared=False):
        handle = self.open(path)
        try:
            return self.validate(handle, directory, shared)
        finally:
            self.k.CloseHandle(handle)

    def directory(self, path):
        self.no_reparse(path)
        if not path.exists():
            if not path.parent.exists():
                self.directory(path.parent)
            self.check(path.parent, directory=True, shared=True)
            with self.security() as security:
                self.checked(self.k.CreateDirectoryW(str(path), security), 'Private directory creation')
        self.check(path, directory=True)

    def duplicate(self, handle):
        result, current = H(), self.k.GetCurrentProcess()
        self.checked(self.k.DuplicateHandle(current, handle, current, c.byref(result), 0, True, 2), 'Inherited ownership handle')
        return result.value

    def process(self, pid):
        if type(pid) is not int or pid < 1:
            raise RuntimeError('Invalid Windows process identity')
        handle = self.k.OpenProcess(0x00101000, False, pid)
        if not handle:
            if c.get_last_error() == 87:
                return None  # Exact PID absent; other errors never establish absence.
            raise OSError(c.get_last_error(), 'Process identity unavailable')
        try:
            waited = self.k.WaitForSingleObject(handle, 0)
            if waited == 0:
                return None
            if waited != 258 or self.process_user(handle) != self.user:
                raise RuntimeError('Process lifetime/owner unknown')
            times = [FileTime() for _ in range(4)]
            self.checked(self.k.GetProcessTimes(handle, *(c.byref(value) for value in times)), 'Process creation time')
            length, image = D(32768), c.create_unicode_buffer(32768)
            self.checked(self.k.QueryFullProcessImageNameW(handle, 0, image, c.byref(length)), 'Process image')
            return {'start': str(times[0].high << 32 | times[0].low), 'image': image.value}
        finally:
            self.k.CloseHandle(handle)


@lru_cache(maxsize=1)
def api():
    return WinAPI()


class ExclusiveLock:
    """CreateFile sharing zero; duplicates retain the same OS file object."""
    def __init__(self, path):
        self.path, self.handle = path, None

    def __enter__(self):
        return self

    def acquire(self):
        if self.handle is not None:
            return
        handle = api().open(self.path, access=0xc0020000, share=0, create=4)
        try:
            api().validate(handle)
        except BaseException:
            api().k.CloseHandle(handle)
            raise
        self.handle = handle

    def fileno(self):
        if self.handle is None:
            raise RuntimeError('Windows ownership not acquired')
        return self.handle

    def __exit__(self, *args):
        if self.handle is not None:
            api().k.CloseHandle(self.handle)
            self.handle = None
