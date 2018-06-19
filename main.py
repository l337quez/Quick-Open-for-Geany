

import sys
import gtk
from quick_open.gui import QuickOpenDialog


def main():
    program = sys.argv[2] if len(sys.argv) > 2 else 'xdg-open'
    qopen = QuickOpenDialog(sys.argv[1], program=program)
    qopen.show()
    try:
        gtk.main()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
