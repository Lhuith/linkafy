from utils import print_w, print_g, print_p, print_y, print_r

# like great philosophers before us, we too must set a global string and ask in general terms
# with alot of colours and frustration ... WHAAAAAAAAAAAAAAAAAAAAAAAAT?
# global string case set that will trigger below printer functions, pain never looked so good
WHAT = ''

# sets the above what, we can directly do that too but im a professional, who would never use global variables
# explicitly
def set_what(w):
    what = w


def wth(a):
    return WHAT != "" and WHAT.lower() in a


def wth_print_w(msg, a):
    if wth(a):
        print_w(msg)


def wth_print_g(msg, a):
    if wth(a):
        print_g(msg)


def wth_print_p(msg, a):
    if wth(a):
        print_p(msg)


def wth_print_y(msg, a):
    if wth(a):
        print_y(msg)


def wth_print_r(msg, a):
    if wth(a):
        print_r(msg)
