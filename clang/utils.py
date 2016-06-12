import platform
import logging
import subprocess

from os import path

log = logging.getLogger(__name__)


class ClangUtils:
    """docstring for ClangUtils"""
    libclang_name = None

    linux_suffixes = ['.so', '.so.1']
    osx_suffixes = ['.dylib']
    windows_suffixes = ['.dll', '.lib']

    hack_systems = ["Darwin", "Windows"]

    @staticmethod
    def get_suffixes():
        if platform.system() == "Windows":
            return ClangUtils.windows_suffixes
        if platform.system() == "Linux":
            return ClangUtils.linux_suffixes
        if platform.system() == "Darwin":
            return ClangUtils.osx_suffixes
        return None

    @staticmethod
    def dir_from_output(output):
        log.debug(" real output: %s", output)
        if platform.system() == "Darwin":
            # [HACK] uh... I'm not sure why it happens like this...
            folder_to_search = path.join(output, '..', '..')
            log.debug(" folder to search: %s", folder_to_search)
            return folder_to_search
        elif platform.system() == "Windows":
            log.debug(" architecture: %s", platform.architecture())
            return path.normpath(output)
        elif platform.system() == "Linux":
            return path.dirname(output)
        return None

    @staticmethod
    def find_libclang_dir(clang_binary):
        for suffix in ClangUtils.get_suffixes():
            # pick a name for a file
            log.info(" we are on '%s'", platform.system())
            file = "libclang{}".format(suffix)
            log.info(" searching for: '%s'", file)
            # let's find the library
            if platform.system() == "Darwin":
                # [HACK]: wtf??? why does it not find libclang.dylib?
                get_library_path_cmd = [clang_binary, "-print-file-name="]
            elif platform.system() == "Windows":
                # [HACK]: wtf??? why does it not find libclang.dylib?
                get_library_path_cmd = [clang_binary, "-print-prog-name="]
            else:
                get_library_path_cmd = [clang_binary, "-print-file-name={}".format(file)]
            output = subprocess.check_output(
                get_library_path_cmd).decode('utf8').strip()
            log.info(" libclang search output = '%s'", output)
            if output:
                libclang_dir = ClangUtils.dir_from_output(output)
                if path.isdir(libclang_dir) and path.exists(path.join(libclang_dir, file)):
                    log.info(" found libclang dir: '%s'", libclang_dir)
                    log.info(" found library file: '%s'", file)
                    ClangUtils.libclang_name = file
                    return libclang_dir
            log.warning(" clang could not find '%s'", file)
        # if we haven't found anything there is nothing to return
        log.error(" no libclang found at all")
        return None
