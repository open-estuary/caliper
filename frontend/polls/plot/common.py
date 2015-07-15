import os
import sys
try:
    import caliper.client.setup_modules as setup_modules
    client_dir = os.path.dirname(setup_modules.__file__)
except ImportError:
    dirname = os.path.dirname(sys.modules[__name__].__file__)
    caliper_dir = os.path.abspath(os.path.join(dirname, "..", ".."))
    client_dir = os.path.join(caliper_dir, "client")
    sys.path.insert(0, client_dir)
    import setup_modules
    sys.path.pop(0)

setup_modules.setup(base_path=client_dir,
                    root_module_name="caliper.client")
