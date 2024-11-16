import logging
import os

def setup_logger(repo_path, log_name):
    """Sets up the logger.

    Args:
        repo_path (str): The path to the repository.
        log_name (str): The name of the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_file = os.path.join(repo_path, "logs", f"{log_name}.log")
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(log_name)
