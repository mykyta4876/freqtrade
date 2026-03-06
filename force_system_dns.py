"""
Force aiohttp to use system DNS by monkey-patching before any imports
This must be imported BEFORE aiohttp or ccxt
"""
import sys
import os

# Set environment variable
os.environ['AIOHTTP_NO_EXTENSIONS'] = '1'

# Monkey patch aiohttp.resolver before it's imported
_original_import = __import__

def _force_system_dns_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Intercept imports and patch aiohttp.resolver"""
    module = _original_import(name, globals, locals, fromlist, level)
    
    # Patch aiohttp.resolver when it's imported
    if name == 'aiohttp.resolver' or (fromlist and 'resolver' in fromlist):
        try:
            # Force use of DefaultResolver instead of AsyncResolver
            from aiohttp.resolver import DefaultResolver
            # Replace AsyncResolver class with DefaultResolver
            if hasattr(module, 'AsyncResolver'):
                # Make AsyncResolver an alias for DefaultResolver
                module.AsyncResolver = DefaultResolver
                print("Patched aiohttp.resolver to use DefaultResolver", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not patch aiohttp.resolver: {e}", file=sys.stderr)
    
    return module

# Replace __import__ to intercept
__builtins__['__import__'] = _force_system_dns_import
