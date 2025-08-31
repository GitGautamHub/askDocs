# app/core/utils.py
import functools
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def log_timing(func):
    """
    A decorator to log the execution time of a function.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Function '{func.__name__}' executed in {duration:.4f} seconds.")
        return result
    return wrapper