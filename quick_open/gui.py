
import os
import gtk

from subprocess import Popen

from os.path import join, isdir

from quick_open import settings
from quick_open import searcher
from quick_open.utils import BuilderAware
from quick_open.utils import ShortcutActivator
from quick_open.utils import set_activate_the_one_item
from quick_open.utils import join_to_file_dir
from quick_open.utils import refresh_gui
from quick_open.utils import idle
from quick_open.utils import mark, unmark
from quick_open.utils.icons import fast_get_icon_for, get_icon


class QuickOpenDialog(BuilderAware):
    """glade-file: gui.glade"""

    def __init__(self, project_root, program='xdg-open'):
        super(QuickOpenDialog, self).__init__(
            join_to_file_dir(__file__, 'gui.glade'))
        self.project_root = project_root
        self.program = program
        self.setup_ui()

    def setup_ui(self):
        self.shortcuts = ShortcutActivator(self.window)
        self.shortcuts.bind('Escape', self.escape)
        self.filelist = gtk.ListStore(gtk.gdk.Pixbuf, str, str)
        self.filelist_tree.set_model(self.filelist)

        for col in self.filelist_tree.get_columns():
            self.filelist_tree.remove_column(col)

        col1 = gtk.TreeViewColumn()
        col2 = gtk.TreeViewColumn()

        icon_cell = gtk.CellRendererPixbuf()
        name_cell = gtk.CellRendererText()
        path_cell = gtk.CellRendererText()

        col1.pack_start(icon_cell, expand=False)
        col1.pack_end(name_cell, expand=True)
        col2.pack_start(path_cell, expand=True)
        col1.set_attributes(icon_cell, pixbuf=0)
        col1.set_attributes(name_cell, markup=1)
        col2.set_attributes(path_cell, markup=2)

        self.filelist_tree.append_column(col1)
        self.filelist_tree.append_column(col2)

        set_activate_the_one_item(self.search_entry, self.filelist_tree)
        self.on_search_entry_changed()

    def escape(self):
        gtk.main_quit()

    def on_delete_event(self, *args):
        self.escape()
        return True

    def get_selected_file(self):
        (model, iter) = self.filelist_tree.get_selection().get_selected()
        if iter:
            name, top = self.filelist.get(iter, 1, 2)
            return os.path.join(self.project_root, top, name), name, top
        else:
            return None, None, None

    def open_file(self, *args):
        fname, name, top = self.get_selected_file()
        fname = unmark(fname, self.search_entry.get_text().strip())
        if fname:
            if os.path.isdir(fname):
                idle(self.fill_with_dirs, os.path.join(top, name), True)
            else:
                refresh_gui()
                Popen([self.program, fname])
                self.escape()

    def show(self):
        self.search_entry.grab_focus()
        self.window.present()

    def fill_filelist(self, search, current_search):
        self.filelist.clear()

        already_matched = {}
        counter = [-1]

        def tick():
            counter[0] += 1
            if counter[0] % 50 == 0:
                refresh_gui()
                if self.current_search is not current_search:
                    raise StopIteration()

        root = self.project_root

        for m in (searcher.name_start_match, searcher.name_match,
                searcher.path_match, searcher.fuzzy_match):
            result = searcher.search(
                root, '', m(search), already_matched, tick)
            for p in result:
                if self.current_search is not current_search:
                    return

                already_matched[p] = True
                name, path = p
                file_path = join(join(self.project_root, path), name)
                if isdir(file_path):
                    icon = get_icon('folder')
                else:
                    icon = fast_get_icon_for(file_path)
                name, path = mark(name, search), mark(path, search)
                self.filelist.append((icon, name, path))

                if len(self.filelist) > 50:
                    return

    def fill_with_dirs(self, top='', place=False):
        self.filelist.clear()

        dirs = []
        files = []

        hidden_masks = None
        if not settings.SHOW_HIDDEN_FILES:
            hidden_masks = settings.HIDDEN_FILES

        if top and not top.endswith('/'):
            top += '/'

        root = os.path.join(self.project_root, top)
        for name in os.listdir(root):
            if (hidden_masks
                    and (name.startswith('.')
                    or any(name.endswith(m) for m in hidden_masks))):
                continue

            path = os.path.join(root, name)
            if os.path.isdir(path):
                dirs.append(name + '/')
            else:
                files.append(name)

        place_idx = 0
        for i, name in enumerate(sorted(dirs)):
            if name == place:
                place_idx = i
            self.filelist.append((get_icon('folder'), name, top))

        for i, name in enumerate(sorted(files)):
            if name == place:
                place_idx = i + len(dirs)
            file_path = join(join(self.project_root, top), name)
            self.filelist.append((fast_get_icon_for(file_path), name, top))

        if place and len(self.filelist):
            self.filelist_tree.set_cursor((place_idx,))

    def on_search_entry_changed(self, *args):
        search = self.search_entry.get_text().strip()
        self.current_search = object()
        if search:
            idle(self.fill_filelist, search, self.current_search)
        else:
            idle(self.fill_with_dirs)
        self.filelist_tree.columns_autosize()
