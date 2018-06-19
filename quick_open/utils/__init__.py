
from os.path import dirname, join

import gtk
import gobject

names_by_key = {}


class ShortcutActivator(object):
    def __init__(self, window):
        self.window = window
        self.accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self.accel_group)

        self.shortcuts = {}
        self.pathes = {}

    def bind(self, accel, callback, *args):
        key, modifier = gtk.accelerator_parse(accel)
        self.shortcuts[(key, modifier)] = callback, args

        self.accel_group.connect_group(
                key, modifier, gtk.ACCEL_VISIBLE, self.activate)

    def activate(self, group, window, key, modifier):
        cb, args = self.get_callback_and_args(key, modifier)
        result = cb(*args)
        return result is None or result

    def get_callback_and_args(self, *key):
        try:
            return self.shortcuts[key]
        except KeyError:
            return self.pathes[get_path_by_key(*key)]


class BuilderAware(object):
    def __init__(self, glade_file):
        self.gtk_builder = gtk.Builder()
        self.gtk_builder.add_from_file(glade_file)
        self.gtk_builder.connect_signals(self)

    def __getattr__(self, name):
        obj = self.gtk_builder.get_object(name)
        if not obj:
            raise AttributeError('Builder have no %s object' % name)

        setattr(self, name, obj)
        return obj


def get_registered_shortcuts():
    result = []

    def func(path, key, mod, changed):
        result.append((path, key, mod))

    gtk.accel_map_foreach_unfiltered(func)

    return result


def refresh_names_by_key():
    for path, key, mod in get_registered_shortcuts():
        names_by_key[(key, mod)] = path


def get_path_by_key(key, mod):
    try:
        return names_by_key[(key, mod)]
    except KeyError:
        refresh_names_by_key()
        return names_by_key[(key, mod)]


def set_activate_the_one_item(entry, treeview):
    def activate(*args):
        if len(treeview.get_model()) == 1:
            treeview.set_cursor((0,))
            treeview.row_activated((0,), treeview.get_column(0))

    entry.connect('activate', activate)


def join_to_file_dir(filename, *args):
    return join(dirname(filename), *args)


def refresh_gui():
    while gtk.events_pending():
        gtk.main_iteration_do(block=False)


def idle_callback(callable, args):
    args, kwargs = args
    callable(*args, **kwargs)
    return False


def mark(string, search, tag_start='<b>', tag_end='</b>'):
    return string.replace(search, tag_start + search + tag_end)


def unmark(string, search, tag_start='<b>', tag_end='</b>'):
    return string.replace(tag_start + search + tag_end, search)


def idle(callable, *args, **kwargs):
    options = {}
    if 'priority' in kwargs:
        options['priority'] = kwargs['priority']
        del kwargs['priority']
    return gobject.idle_add(idle_callback, callable, (args, kwargs), **options)
