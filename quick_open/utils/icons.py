#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       icons.py
#
#       Copyright 2012 Eddy Ernesto del Valle Pino <edelvalle@hab.uci.cu>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

import os

import gio
import glib
import gtk

_itheme = gtk.icon_theme_get_default()
_extensions_pixbuf_cache = {}


def get_icon(icon_name, size=16):
    return _itheme.load_icon(icon_name, size, 0)

_unknown_pixbuf = get_icon('txt')


def _load_mimetypes_icon_names():
    mime_icons = []
    contexts = [(c, c.lower()) for c in _itheme.list_contexts()]
    for name, lowered in contexts:
        if 'mime' in lowered:
            mime_icons.extend(_itheme.list_icons(context=name))
    return set(mime_icons)

_mimetypes_icon_names = _load_mimetypes_icon_names()


def get_icon_for(file_path, size=16):
    gio_file = gio.File(file_path)
    gio_themed_icon = gio_file.query_info("standard::icon").get_icon()
    for icon_name in gio_themed_icon.get_names():
        try:
            icon = get_icon(icon_name, size=size)
        except glib.GError:
            continue
        else:
            return icon


def fast_get_icon_for(file_path):
    """
    Tries to get the icon for the mimetype if cannot returns unknown icon
    """
    _, extension = os.path.splitext(file_path)
    if not extension:
        return get_icon_for(file_path)
    if extension not in  _extensions_pixbuf_cache:
        _extensions_pixbuf_cache[extension] = get_icon_for(file_path)
    return _extensions_pixbuf_cache[extension]
