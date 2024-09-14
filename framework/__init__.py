

from importlib import reload, import_module
from pathlib import Path
import sys
from typing import Dict, Any, List, Optional, Callable


from .utilities.common import get_module_import_dotpath, get_variables as _get_variables
from .exceptions import ModuleFileTypeNotSupported, NotRelativePath, SysPathNotSet, SystemPathNotAdded, FunctionNotFoundError


class Script:
    supported_extensions = [".py"]
    
    def __init__(self, path: Path, sys_path: Optional[Path] = None) -> None:
        self.path = path
        if sys_path:
            self.sys_path = sys_path
        else:
            self._sys_path = None
        
    @property
    def path(self) -> Path:
        return self._path
    
    @path.setter
    def path(self, value: Any) -> None:
        if not isinstance(value, Path):
            raise TypeError("Cannot set path since value passed is not Path Type")
        if not value.is_file():
            raise FileNotFoundError("Cannot set path since file does not exist")
        if value.suffix not in self.supported_extensions:
            raise ModuleFileTypeNotSupported(f"Cannot set path since the type of the file passed is not supported: {value.suffix}")
        self._path = value
    
    @property
    def sys_path(self) -> Path:
        return self._sys_path
    
    @sys_path.setter
    def sys_path(self, value: Any) -> None:
        if not isinstance(value, Path):
            raise TypeError("Cannot set path since value passed is not Path Type")
        if not value.is_dir():
            raise NotADirectoryError("Cannot set path since not found directory")
        # checking if script path is relative to sys_path passed
        if not self.path.is_relative_to(value):
            raise NotRelativePath(f"The script ({self.path}) is not child to sys path dir: {value}")
        self._sys_path = value
        
    def load(self, sys_path: Optional[Path] = None) -> None:
        self._set_dotpath(sys_path)
        self._module = import_module(self._dot_path)
        
    def _set_dotpath(self, sys_path: Optional[Path]= None):
        if (self.sys_path is None) and (sys_path is None):
            raise SysPathNotSet("System Path is not set. To import module please first set syspath")
        elif sys_path:
            self.sys_path = sys_path
        
        # setting system path to sys.path list
        if str(self.sys_path) not in sys.path:
            raise SystemPathNotAdded("System path is not yet added to sys.path")
        
        self._dot_path = get_module_import_dotpath(self.sys_path, Path(self.path))
    
    def run(self, sys_path: Optional[Path] = None) -> None:
        self.load(sys_path)
        self.reload()
    
    def reload(self) -> None:
        self._module = reload(self._module)
    
    @property
    def variables(self) -> Dict[str, Any]:
        return self.get_variables(load_hiddenvars=False, reload=False)
    
    def get_variables(self, load_hiddenvars: bool = True, reload=False) -> Dict[str, Any]:
        if reload:
            self.reload()
        return _get_variables(self._module, load_hiddenvars)
    
    def __repr__(self) -> str:
        return f"Script({self.path.stem}: {self.path})"
    
    def get_function(self, fn_name: str) -> Callable:
        for var_name, var_value in self.variables.items():
            if (var_name == fn_name) and isinstance(var_value, Callable):
                return var_value
        else:
            raise FunctionNotFoundError(f"Function {repr(fn_name)} not found")


class ScriptsScanner:
    _directory = None
    
    def __init__(self, scripts_dir: Path) -> None:
        self.directory = scripts_dir
        
    @property
    def directory(self) -> Path:
        if self._directory:
            return self._directory
        raise ValueError("directory not yet set")
    
    @directory.setter
    def directory(self, value: Any) -> None:
        if not isinstance(value, Path):
            raise TypeError(f"{value=}")
        if not value.is_dir():
            raise NotADirectoryError(f"Not a valid directory: {value}")
        self._directory = value
    
    def scan_files(self) -> None:
        self._scripts: List[Path] = list(self._directory.rglob("*.py"))


class ScriptsFramework(ScriptsScanner):
    def __init__(self, scripts_dir: Path, *args, **kwargs) -> None:
        super().__init__(scripts_dir, *args, **kwargs)
        
    def add_sys_path(self) -> None:
        self.sys_path = self.directory.parent
        if str(self.sys_path) in sys.path:
            sys.path.remove(str(self.sys_path))
        sys.path.append(str(self.sys_path))
    
    def scan(self) -> None:
        self.scan_files()  # second times
        self.add_sys_path()
        self._modules: List[Script] = []
        for script_path in self._scripts:
            script = Script(script_path, self.sys_path)
            self._modules.append(script)
        
    def load_modules(self) -> None:
        self.scan()
        self._loaded_modules = []
        for mdl in self._modules:
            mdl.load()
            mdl.reload()
            self._loaded_modules.append(mdl)
    
    @property
    def loaded_modules(self) -> List[Script]:
        return self._loaded_modules
    
    @property
    def scripts(self) -> List[Script]:
        return self._modules
            
