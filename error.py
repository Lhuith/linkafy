import traceback
from utils import print_r, time_pretty

log_path = "output/errors.txt"
def log_error(e, message):
    what = f"error: {e} details: {message}"
    print_r(what)
    traceback.print_stack()

    # write logs out
    f = open(log_path, "a", encoding='utf-8')
    f.write(f"{time_pretty()} - {what}  \n")
    f.close()
