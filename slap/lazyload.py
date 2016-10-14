"""
Lazily load modules

usage: call ``from lazyload import lazyload; lazyload("some_module")` before any `import some_module`

Implementation idea from https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
"""

import logging
import sys
import threading

lock = threading.RLock()

class LazyLoad(object):

    real_modules = {}

    def __init__(self, module_name):
        self.module_name = module_name
    
    def __getattr__(self, name):
        if self.module_name not in self.real_modules:
            with lock:
                logging.debug("lazily importing `%s`", self.module_name)
                del sys.modules[self.module_name]
                self.real_modules[self.module_name] = __import__(self.module_name)
                sys.modules[self.module_name] = self
                logging.debug("   `%s` imported", self.module_name)
        return getattr(self.real_modules[self.module_name], name)

def lazyload(module_name):
    if module_name in sys.modules:
        logging.warning("module %s is already loaded; not lazy loading", module_name)
        return
    sys.modules[module_name] = LazyLoad(module_name)
