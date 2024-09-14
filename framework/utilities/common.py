import inspect
from pathlib import Path
from types import ModuleType, FunctionType
from typing import Dict, Any

from ..exceptions import PathNotFound, NotRelativePath, ModuleFileTypeNotSupported


def get_module_import_dotpath(sys_path: Path, script_path: Path) -> str:
    supported_extensions = [".py"]  # change if new extensions, in return line as well
    
    if not sys_path.exists():
        raise PathNotFound(f"sys_path passed does not exist: {sys_path}")
    if not sys_path.is_dir():
        raise NotADirectoryError(f"sys_path is not a directory path: {sys_path}")
    
    parent_path = sys_path
    
    if not script_path.is_relative_to(parent_path):
        raise NotRelativePath(f"The path {script_path} is not child to sys path dir {sys_path}")
    
    child_abs_path = script_path
    
    if not script_path.is_file():
        raise FileNotFoundError(f"Script path does not exist: {script_path}")
    
    if child_abs_path.suffix not in supported_extensions:
        raise ModuleFileTypeNotSupported(f"The file type with extension {child_abs_path.suffix} is not supported for importing as python module")
        
    child_rel_path = child_abs_path.relative_to(parent_path)
    *basepaths, scriptname = child_rel_path.parts
    if basepaths:
        return ".".join(basepaths) + f".{scriptname.removesuffix('.py')}"
    else:
        return scriptname.removesuffix(".py")

def get_variables(module: ModuleType, load_hiddenvars: bool = False) -> Dict:
    if load_hiddenvars:
        needed_vars = dir(module)
    else:
        needed_vars = [i for i in dir(module) if not(i.startswith("__") or i.endswith("__"))]
    return {k: v for k, v in vars(module).items() if k in needed_vars}


def execute_function(fn: FunctionType, preset_kwargs: Dict[str, Any] = None, validate_params=True) -> Any:
    # figuring out input params
    fn_sign = inspect.signature(fn)
    fn_params = fn_sign.parameters
    # fn_return_type = fn_sign.return_annotation
    if not preset_kwargs:
        preset_kwargs = {}
    if validate_params:
        # checking all parameters valid?
        invalid_params = []
        for param_name in fn_params.keys():
            if param_name not in preset_kwargs.keys():
                invalid_params.append(param_name)
        if invalid_params:
            raise Exception("Invalid parameters found")

        # constructing kwargs
        kwargs = {param: preset_kwargs[param] for param in fn_params.keys()}
        return fn.__call__(**kwargs)
    else:
        return fn.__call__(**preset_kwargs)
