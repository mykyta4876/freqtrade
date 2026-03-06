"""
DNS Fix for Windows - Forces aiohttp to use system DNS instead of aiodns
This should be imported before any aiohttp/ccxt code runs
"""
import sys
import os

# Set environment variable to disable aiodns before any imports
os.environ.setdefault('AIOHTTP_NO_EXTENSIONS', '1')

# Patch aiohttp to use DefaultResolver instead of AsyncResolver
# This must be done before aiohttp is imported
def patch_aiohttp_resolver():
    """Force aiohttp to use system DNS resolver"""
    try:
        # Check if aiohttp is already imported
        if 'aiohttp' in sys.modules:
            # Patch after import
            import aiohttp.resolver
            from aiohttp.resolver import DefaultResolver
            
            # Replace AsyncResolver with DefaultResolver
            if hasattr(aiohttp.resolver, 'AsyncResolver'):
                aiohttp.resolver.AsyncResolver = DefaultResolver
        else:
            # Patch before import by monkey-patching the import
            # We'll intercept the import and replace AsyncResolver
            import importlib.util
            import importlib.machinery
            
            # Store original import
            original_import = __import__
            
            def patched_import(name, *args, **kwargs):
                module = original_import(name, *args, **kwargs)
                
                # If importing aiohttp.resolver, patch it
                if name == 'aiohttp.resolver' or (name == 'aiohttp' and 'resolver' in str(args)):
                    try:
                        from aiohttp.resolver import DefaultResolver
                        if hasattr(module, 'AsyncResolver'):
                            module.AsyncResolver = DefaultResolver
                    except:
                        pass
                
                return module
            
            # Replace __import__ temporarily (this is tricky, so we'll use a different approach)
            # Instead, we'll patch it when aiohttp.resolver is actually imported
            pass
            
    except Exception as e:
        # If patching fails, log but don't crash
        try:
            import logging
            logging.warning(f"Could not patch aiohttp resolver: {e}")
        except:
            pass

# Apply the patch immediately when this module is imported
# Also set up a hook to patch when aiohttp is imported
_original_import = __import__

def _patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    module = _original_import(name, globals, locals, fromlist, level)
    
    # Patch aiohttp.resolver when it's imported
    if name == 'aiohttp.resolver' or (fromlist and 'resolver' in fromlist and 'aiohttp' in name):
        try:
            from aiohttp.resolver import DefaultResolver
            if hasattr(module, 'AsyncResolver'):
                module.AsyncResolver = DefaultResolver
        except:
            pass
    
    return module

# Replace __import__ to intercept aiohttp imports
__builtins__['__import__'] = _patched_import

# Also try to patch immediately if aiohttp is already loaded
patch_aiohttp_resolver()
