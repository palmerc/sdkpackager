#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
import tarfile


def xcode_path():
    if not hasattr(xcode_path, "path"):
        xcode_path.path = None

    if not xcode_path.path:
        cmd = ['xcode-select', '--print-path']
        xcode_path.path = pathlib.Path(subprocess.check_output(cmd).strip().decode('utf-8'))
    return xcode_path.path


def xcode_toolchain_path():
    return xcode_path() / 'Toolchains' / 'XcodeDefault.xctoolchain'


def xcode_toolchain_files():
    usr_include_cxx = xcode_toolchain_path() / 'usr' / 'include' / 'c++'
    return usr_include_cxx.rglob('*')


def sdk_version(sdk):
    if not hasattr(sdk_version, "version"):
        sdk_version.version = {}

    if not sdk in sdk_version.version:
        sdk_version.version[sdk] = None

    if not sdk_version.version[sdk]:
        cmd = ['xcrun', '--sdk', sdk, '--show-sdk-version']
        sdk_version.version[sdk] = subprocess.check_output(cmd).strip().decode('utf-8')
    return sdk_version.version[sdk]


def platforms_path():
    return xcode_path() / 'Platforms'


def platforms():
    return [platform.name.removesuffix('.platform') for platform in platforms_path().glob('*')]


def platform(sdk):
    return [p for p in platforms() if sdk.casefold() == p.casefold()].pop()


def platform_path(sdk):
    return platforms_path() / f'{platform(sdk)}.platform'


def sdk_paths(sdk):
    return platform_path(sdk) / 'Developer' / 'SDKs'


def sdks(sdk):
    return [sdk.name for sdk in sdk_paths(sdk).glob('*')]


def sdk_name(sdk):
    return f'{platform(sdk)}{sdk_version(sdk)}.sdk'


def sdk_path(sdk):
    return sdk_paths(sdk) / sdk_name(sdk)


def sdk_files(sdk):
    return [x for x in sdk_path(sdk).rglob('*')]


def package(sdks):
    with tarfile.open(f'AppleSDK.tar.xz', mode='w:xz') as t:
        for sdk in sdks:
            print(f'Packaging - {sdk_name(sdk)}')
            sdk_file_paths = [x for x in sdk_files(sdk) if x.is_file()]
            for sdk_file_path in sdk_file_paths:
                archive_name = sdk_file_path.relative_to(sdk_path(sdk)).as_posix()
                with open(sdk_file_path, 'rb') as f:
                    name = f'{sdk_name(sdk)}/{archive_name}'
                    info = t.gettarinfo(arcname=name, fileobj=f)
                    t.addfile(tarinfo=info, fileobj=f)

        print(f'Packaging - XcodeDefault.xctoolchain')
        xc_toolchain_paths = [x for x in xcode_toolchain_files() if x.is_file()]
        for xc_toolchain_path in xc_toolchain_paths:
            archive_name = xc_toolchain_path.relative_to(xcode_toolchain_path()).as_posix()
            info = tarfile.TarInfo(name=f'XcodeDefault.xctoolchain/{archive_name}')
            with open(xc_toolchain_path, 'rb') as f:
                t.addfile(info, f)


def main():
    parser = argparse.ArgumentParser(description='Package the Xcode SDKs')
    parser.add_argument('--sdk', default='all', choices=['iphoneos', 'iphonesimulator', 'macosx', 'all'], required=False,
                        help='Specify the SDK to package')
    args = parser.parse_args()
    if args.sdk == 'all':
        sdks = ['iphoneos', 'iphonesimulator', 'macosx']
    else:
        sdks = [args.sdk]

    print(f'Package {",".join(sdks)}')
    package(sdks)


if __name__ == '__main__':
    main()
