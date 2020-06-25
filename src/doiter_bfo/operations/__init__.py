#
#from doiter_bfo.plugins.package import PackagePlugin
#from doiter_bfo.plugins.template import TemplatePlugin
#from doiter_bfo.plugins.service import ServicePlugin
#from doiter_bfo.plugins.pyinfra import Pyinfra


USE_PYINFRA = True


def decorator_cls(cls):
    if USE_PYINFRA:
        setattr(cls, '__call__', cls._apply_pyinfra)
    else:
        setattr(cls, '__call__', cls._apply_manual)
    return cls
