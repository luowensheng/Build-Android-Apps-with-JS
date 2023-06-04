from dataclasses import dataclass
import json
import os
import re

@dataclass
class Project:
    project_name: str
    output_html_path: str
    build_path: str
    project_dir: str
    applicationId: str

    def load():
        return Project(**json.load(open("./config.json")))


INCLUDES = {}

CONTENT = """
package {applicationId}

object Project {
    const val html = \"\"\"{html}\"\"\"
}
"""



def wrap_with_tag(content: str, ext: str):
    return {
        "css": f"<style>\n{content}\n</style>",
        "js": f"<script>\n{content}\n</script>"
    }[ext]

def include_dependencies(html: str, dir_path:str):
    for include in re.findall("@include\(\"(\S+)\"\)", html):
        if not include in INCLUDES:
            INCLUDES[include] = include_dependencies(open(os.path.join(dir_path, include)).read(), dir_path)
        
        ext = include.split(".")[-1]
        html = html.replace(f'@include("{include}")', wrap_with_tag(INCLUDES[include], ext))

    return html    

def main():

    project = Project.load()
    
    html = open(os.path.join(project.project_dir, "index.html")).read()
    html = include_dependencies(html, project.project_dir)

    content = CONTENT 
    with open(os.path.join(project.output_html_path), 'w') as f:

        for k, v in dict(applicationId=project.applicationId, html=html).items():
            content = content.replace("{"+k+"}", v)

        f.write(content)
    


if __name__ == "__main__":
    main()