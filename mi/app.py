'''
Main script where all scraping scripts are run from
'''

import os
import importlib

def app():
    '''
    Dynamically imports web-scraping scripts from utils.
    '''
    folder_run_scripts = 'utils'
    # Path to the utils directory
    utils_dir = os.path.join(os.path.dirname(__file__), folder_run_scripts)

    # Iterate over all files in the utils directory
    for filename in os.listdir(utils_dir):
        # Check if the file is a Python file
        if filename.endswith('.py') and filename != '__init__.py' and filename != 'functions.py':
            # Construct the module name (utils.script1, utils.script2, etc.)
            module_name = f"{folder_run_scripts}.{filename[:-3]}"
            
            try:
                # Import the module dynamically
                module = importlib.import_module(module_name)
                
                # Call a function named 'main' in the module if it exists
                if hasattr(module, 'main'):
                    print(f"\nRunning {module_name}.main()")
                    module.main()
                else:
                    print(f"{module_name} does not have a main() function")
            except Exception as e:
                print(f"Failed to run {module_name}: {e}")

    return 0

if __name__ == '__main__':

    app()


