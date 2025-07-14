import json
import sys

from func import ArgsParser, memory
from func.BuildManager import BuildManager
from func.OutProgressBar import ProgressBar
from func.installer import MinecraftInstaller, ForgeInstaller, FabricInstaller, QuiltInstaller
from func.runner import VanillaLauncher, QuiltLauncher, FabricLauncher, ForgeLauncher


def check():
    if ArgsParser.msg.get('getAllBuilds'):
        build_manager = BuildManager(
            minecraft_versions=memory.get("minecraft_versions", []),
            core_types=memory.get("core_types", []),
            core_versions=memory.get("core_versions", {})
        )
        b = build_manager.get_all_builds()
        print(b)
    if ArgsParser.msg.get('instcore') and ArgsParser.msg.get('nogui'):
        build = {'core_version': ArgsParser.msg.get('instcore')[1], 'core_type': ArgsParser.msg.get('instcore')[0],
                 'minecraft': ArgsParser.msg.get('instcore')[2]}
        installer = None
        path = "./minecraft"
        if build['core_type'].lower() == "vanilla":
            installer = MinecraftInstaller(path=path, version=build['minecraft'])
        elif build['core_type'].lower() == "forge":
            forge_version = build['core_version'].replace(f"Forge {build['minecraft']}-", "")
            installer = ForgeInstaller(path=path, version=build['minecraft'], loaderVersion=forge_version)
        elif build['core_type'].lower() == "fabric":
            fabric_version = build['core_version'].replace("Fabric Loader ", "")
            installer = FabricInstaller(path=path, version=build['minecraft'], loaderVersion=fabric_version)
        elif build['core_type'].lower() == "quilt":
            quilt_version = build['core_version'].replace("Quilt Loader ", "")
            installer = QuiltInstaller(path=path, version=build['minecraft'], loaderVersion=quilt_version)
        p = ProgressBar()

        callback_dict = {
            'setStatus': lambda status: p.set_status(status),
            'setProgress': lambda progress: p.set_progress(progress),
            'setMax': lambda max_val: p.set_max(max_val)
        }
        installer.callback = callback_dict
        installer.install_version()
    if ArgsParser.msg.get('sff'):
        d = ArgsParser.msg.get('sff')
        launcher = None
        if d[2].lower() == 'vanilla':
            launcher = VanillaLauncher(d[1], path="./minecraft", game_dir=d[0], username=d[4])
        elif d[2].lower() == 'forge':
            launcher = ForgeLauncher(d[1], d[3], path="./minecraft", game_dir=d[0], username=d[4])
        elif d[2].lower() == 'fabric':
            launcher = FabricLauncher(d[1], d[3], path="./minecraft", game_dir=d[0], username=d[4])
        elif d[2].lower() == 'quilt':
            launcher = QuiltLauncher(d[1], d[3], path="./minecraft", game_dir=d[0], username=d[4])
        launcher.run(False)
        sys.exit(0)
    if (ArgsParser.msg.get('nostart') and
            (ArgsParser.msg.get('swbn') or ArgsParser.msg.get('MCClose') or (
                    ArgsParser.msg.get('instcore') and not ArgsParser.msg.get('nogui')))):
        print('Executing commands "--start-with-build-name", "--close-by-name", "--install-core (with UI)" is impossible without a launcher!')
    if ArgsParser.msg.get('sp') is not None:
        with open("profiles.json", 'r', encoding="utf-8") as f:
            d = json.load(f)
        for i, e in enumerate(d):
            if i == ArgsParser.msg.get('sp'):
                print("'"+e['nickname']+"' Installed as the main profile")
                e['active'] = True
            else: e['active'] = False
        with open("profiles.json", 'w', encoding="utf-8") as f:
            json.dump(d, f, indent=4)
    if ArgsParser.msg.get('p'):
        with open("profiles.json", 'r', encoding="utf-8") as f:
            d = json.load(f)
            for i, e in enumerate(d):
                if e['active']:
                    print(e)
                    break
