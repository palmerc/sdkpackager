import pathlib
import plistlib
import subprocess


class Xcode:
    default_toolchain = 'XcodeDefault.xctoolchain'

    @classmethod
    def version(cls):
        with open(Xcode.install_path().parent / 'version.plist', 'rb') as f:
            version_plist = plistlib.load(f)
            return version_plist['CFBundleShortVersionString']

    @classmethod
    def install_path(cls):
        cmd = ['xcode-select', '--print-path']
        return pathlib.Path(subprocess.check_output(cmd).strip().decode('utf-8'))

    @classmethod
    def toolchains_path(cls):
        return Xcode.install_path() / 'Toolchains'

    @classmethod
    def platforms_path(cls):
        return Xcode.install_path() / 'Platforms'

    @classmethod
    def available_platforms_paths(cls):
        suffix = '.platform'
        return [p for p in Xcode.platforms_path().glob(f'*{suffix}')]

    @classmethod
    def available_platforms(cls):
        suffix = '.platform'
        return [p.name.removesuffix(suffix).casefold() for p in Xcode.available_platforms_paths()]

    @classmethod
    def platform_path(cls, platform):
        return [p for p in Xcode.available_platforms_paths() if p.name.casefold().startswith(platform)].pop()

    @classmethod
    def platform_short_name(cls, platform):
        return Xcode.platform_path(platform).name.removesuffix('.platform')

    @classmethod
    def platform_version(cls, platform):
        with open(Xcode.platform_path(platform) / 'Info.plist', 'rb') as f:
            version_plist = plistlib.load(f)
            return version_plist['Version']

    @classmethod
    def platform_sdks_path(cls, platform):
        return Xcode.platform_path(platform) / 'Developer' / 'SDKs'
