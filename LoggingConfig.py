import logging



class MaxLevelFilter(logging.Filter):
    """
    This class is for the debug.log 
    which we only want the debug messages
    """
    def __init__(self, max_level):
        self.max_level = max_level
        super().__init__()

    def filter(self, record):
        return record.levelno <= self.max_level



"""
Sets the fields and variables for logging. 
This way we control the prints and messages.
"""

# Create a logger
logger = logging.getLogger('my_application')
# Set the logger to the lowest level to capture all logs
logger.setLevel(logging.DEBUG)  # should be decided by the application

# Create handlers
#console_handler = logging.StreamHandler()
file_app_handler = logging.FileHandler('app.log', mode='w')
file_debug_handler = logging.FileHandler('debug.log', mode='w') # will depend on what we want 
file_debug_handler.addFilter(MaxLevelFilter(logging.DEBUG))

# Set level for handlers
#console_handler.setLevel(logging.INFO)
file_app_handler.setLevel(logging.INFO)
file_debug_handler.setLevel(logging.DEBUG)

# Create formatters and add them to the handlers
console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#console_handler.setFormatter(console_format)
file_app_handler.setFormatter(file_format)
file_debug_handler.setFormatter(file_format)


# Add handlers to the logger
logger.addHandler(file_app_handler)
logger.addHandler(file_debug_handler)
