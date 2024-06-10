import logging

# Configure the logging system
def configure_logging():
    logging.basicConfig(
        filename='app.log',
        filemode='w',
        level=logging.DEBUG,  # Set to logging.INFO or another level to reduce verbosity
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )