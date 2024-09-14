from pathlib import Path
from typing import Callable
from framework import ScriptsFramework

from framework.exceptions import FunctionNotFoundError

scripts_dir = Path(r"/Users/santokalayil/Developer/projects/framework/.temp/scripts/")
fw = ScriptsFramework(scripts_dir)

fw.load_modules()
        
mdl = fw.loaded_modules[0]     

mdl.get_function()   
    # else:
    # isinstance()
    # break
        
# scripts_dir = Path(r"/Users/santokalayil/Developer/projects/framework/.temp/scripts/")
# fw = ScriptsFramework(scripts_dir)      


# fw.scan()
# fw.scripts
    
# module = fw._modules[0]
# module.variables


# script_dir = Path(r"/Users/santokalayil/Developer/projects/framework/.temp/scripts/")
# sys_path = script_dir.parent
# script_path = Path(r"/Users/santokalayil/Developer/projects/framework/.temp/scripts/script1.py")
# script = Script(script_path, sys_path)

# script.path
# script.sys_path

# if str(sys_path) in sys.path:
#     sys.path.remove(str(sys_path))
# sys.path.append(str(sys_path))


# script.load()

# script.variables

# dir(script._module)

    
# class Function:
#     ...





