"""
author: luowensheng
help: https://developer.android.com/build/building-cmdline
"""
import argparse
from dataclasses import dataclass
import json
import os
from typing import Optional
import shutil
import sys
import pathlib

BUILD_GRADLE_DEPENDENCIES = [
    'classpath "com.android.tools.build:gradle:7.0.3"',
    'classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:1.6.10"'
]
def get_android_sdk_path():
    username = os.getlogin()
    return {
        "d": f"/Users/{username}/Library/Android/sdk",
        "w": r"C\:\\Users\\"+username+ r"\\AppData\\Local\\Android\\Sdk",
        "l": f"/home/{username}/Android/Sdk"
    }.get(sys.platform[0])

SDK_PATH = get_android_sdk_path()
BUILD_GRADLE = "build.gradle"
OUTPUT_HTML_PATH = "app/src/main/java/com/example/{app_name_lower}/html.kt" # "app/src/main/assets/index.html"

def read_dir(full_path: str, create_dir_if_missing:bool=True):
        
    for file in os.listdir(full_path):
        f_path = os.path.join(full_path, file)
        
        if os.path.isdir(f_path):
            for item_path in read_dir(f_path, create_dir_if_missing):
                yield item_path
        
        yield f_path    
    
def copy_file_content(new_file_path: str, old_file_path: str, params:Optional[dict[str, str]]=None):
    dir_path, _ = os.path.split(new_file_path)
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    if params:
        with open(new_file_path, 'w') as f:
            old_file_path = pathlib.Path(old_file_path).as_posix()
            # print(old_file_path)
            content = open(old_file_path).read()
            for k, v in params.items():
                content = content.replace("{"+k+"}", v)
            f.write(content)
    else:
        shutil.copyfile(old_file_path, new_file_path)
    
    assert os.path.exists(new_file_path)    
    print(new_file_path)



@dataclass
class ContentPath:
    path: str
    params: Optional[dict[str, str]] = None
    is_dir: bool = False
    content: Optional[str] = None




def create_project(app_name: str, entry_path: str, directory_path: str, sdk_path: str):

    applicationId = f"com.example.{app_name.lower()}"
    files = [
        ContentPath(path=".gitignore"),
        ContentPath(path= BUILD_GRADLE, params={"dependencies": '\n        '.join(BUILD_GRADLE_DEPENDENCIES)}),
        ContentPath(path="gradle.properties"),
        ContentPath(path="gradlew"),
        ContentPath(path="gradlew.bat"),
        ContentPath(path="local.properties", params={"sdk_dir": sdk_path}),
        ContentPath(path="settings.gradle", params={"project_name": app_name}),
        ContentPath(path="app/.gitignore"),
        ContentPath(path=f"app/{BUILD_GRADLE}", params={"applicationId": applicationId}),
        ContentPath(path="app/proguard-rules.pro"),
        ContentPath(path="app/src/main/AndroidManifest.xml", params={"applicationId": applicationId, "app_name": app_name}),
        ContentPath(path="app/src/main/res/values/colors.xml"),
        ContentPath(path="app/src/main/res/values/strings.xml", params={"app_name": app_name}),
        ContentPath(path="app/src/main/res/values/themes.xml", params={"app_name": app_name}),
        ContentPath(path="app/src/main/res/values-night/themes.xml", params={"app_name": app_name}),
        # ContentPath(path=OUTPUT_HTML_PATH, params={"app_name": app_name}),
        ContentPath(path="app/src/main/java/com/example/{app_name_lower}/MainActivity.kt", params={"app_name_lower":app_name.lower()}),
        ContentPath(path=OUTPUT_HTML_PATH, params={"app_name_lower":app_name.lower()}),

        ContentPath(path=f"app/src/main/res/drawable", is_dir=True),
        ContentPath(path=f"app/src/main/res/drawable-v24", is_dir=True),
        ContentPath(path=f"app/src/main/res/layout", is_dir=True),

        ContentPath(path=f"app/src/main/res/mipmap-anydpi-v26", is_dir=True),
        ContentPath(path=f"app/src/main/res/mipmap-hdpi", is_dir=True),
        ContentPath(path=f"app/src/main/res/mipmap-mdpi", is_dir=True),
        ContentPath(path=f"app/src/main/res/mipmap-xhdpi", is_dir=True),
        ContentPath(path=f"app/src/main/res/mipmap-xxhdpi", is_dir=True),
        ContentPath(path=f"app/src/main/res/mipmap-xxxhdpi", is_dir=True),
        ContentPath(path=f"gradle/wrapper", is_dir=True),

    ]

    for content in files:
     
        full_path = os.path.join(entry_path, content.path)

        if content.is_dir:
            for f_file in read_dir(full_path):
                new_path = f_file.replace(entry_path, directory_path)
                copy_file_content(new_path, f_file)
        else:
            new_path = full_path.replace(entry_path, directory_path).format(app_name_lower=app_name.lower())
            copy_file_content(new_path, full_path.format(app_name_lower="app_name"), content.params)
    
    return applicationId

class AppArgs:
    project: str
    sdk:str

def main():
    parser = argparse.ArgumentParser(
                        prog='AnyDroid',
                        description='Create android apps with javascript',
                        )

    parser.add_argument('-n', '--project', help='project name', required=True)
    # print(SDK_PATH, os.path.exists(SDK_PATH))
    # if SDK_PATH and os.path.exists(SDK_PATH):
    if SDK_PATH:
        parser.add_argument('-s', '--sdk', default=SDK_PATH, type=str, required=False)
    else:
        parser.add_argument('-s', '--sdk', type=str, required=True)


    args: AppArgs = parser.parse_args()
    entry_path = os.path.join(os.getcwd(), "project_files")
    entry_path = pathlib.Path(entry_path).as_posix()

    DIR_PATH = f"./android"

    applicationId = create_project(args.project, entry_path=entry_path, directory_path=DIR_PATH, sdk_path=args.sdk)
    
    build_path = pathlib.Path(os.path.join(DIR_PATH, BUILD_GRADLE)).as_posix()
    gradlew_path = os.path.join(DIR_PATH, "gradlew")

    if sys.platform[0] == "w":
        ext = "bat" 
        gradlew_path = gradlew_path.replace("./", "")
    else:
        ext = "sh"

    # with open(f"./build.{ext}", 'w') as f:
    #     f.writelines([
    #         "@echo off\n",
    #         f"{gradlew_path} assembleDebug -b {build_path}"
    #     ])
    
    # with open(f"./install.{ext}", 'w') as f:
    #     f.writelines([
    #         "@echo off\n",
    #         f"{gradlew_path} installDebug -b {build_path}"
    #     ])    

    with open(f"./run.{ext}", 'w') as f:
        f.writelines([
            "@echo off\n",
            f"python main.py && {gradlew_path} assembleDebug -b {build_path} && {gradlew_path} installDebug -b {build_path}"
        ])       

    if not os.path.exists(f"./{args.project}"):
        os.mkdir(f"./{args.project}")
    

    with open(f"./{args.project}/index.html", 'w') as w:
        w.writelines([
            '<!DOCTYPE html>\n',
            '<html lang="en">\n',
            '<head>\n',
            '    <meta charset="UTF-8">\n',
            '    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n',
            f'    <title>{args.project}</title>\n',
            '</head>\n',
            '<body>\n',
            f'    <h1>Happy Coding {args.project}!</h1>\n',
            '</body>\n',
            '</html>\n',
        ])    

    with open(f"./config.json", 'w') as f:
        json.dump({
            "project_name": args.project,
            "output_html_path": os.path.join("./android", OUTPUT_HTML_PATH.format(app_name_lower=args.project.lower())),
            "build_path": build_path,
            "project_dir": f"./{args.project}",
            "applicationId": applicationId
        }, f)     

    
    return
if __name__ == "__main__":
    main()


