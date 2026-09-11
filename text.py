import tavily
import inspect

print(tavily.__version__ if hasattr(
    tavily, "__version__") else "version unknown")

# List exception-like classes exposed by the module
for name, obj in inspect.getmembers(tavily, inspect.isclass):
    if "error" in name.lower() or "exception" in name.lower():
        print(name, obj)
