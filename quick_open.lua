--
--       python_completion.lua
--
--       Copyright 2012 Eddy Ernesto del Valle Pino <edelvalle@hab.uci.cu>
--
--       This program is free software; you can redistribute it and/or modify
--       it under the terms of the GNU General Public License as published by
--       the Free Software Foundation; either version 2 of the License, or
--       (at your option) any later version.
--
--       This program is distributed in the hope that it will be useful,
--       but WITHOUT ANY WARRANTY; without even the implied warranty of
--       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--       GNU General Public License for more details.
--
--       You should have received a copy of the GNU General Public License
--       along with this program; if not, write to the Free Software
--       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
--       MA 02110-1301, USA.
--
--

PROJECT_ROOT_FILES = {'.git', '.hg', '.bzr', '.ropeproject', '.pro'}


function get_project_path()
    local folder = geany.filename()
    local last_folder = '/'
    local is_root = false
    while not is_root do
        folder = geany.dirname(folder)
        for file_name in geany.dirlist(folder) do
            for i, project_root_file in pairs(PROJECT_ROOT_FILES) do
                if file_name == project_root_file then
                    is_root = true
                    break
                end
            end
        end
        if last_folder == folder then
            return geany.dirname(geany.filename())
        else
            last_folder = folder
        end
    end
    return folder
end


project_path = get_project_path()
if project_path ~= '' then
    local qopen = geany.dirname(geany.script)..geany.dirsep..'main.py'
    io.popen('python '..qopen..' '..project_path..' geany')
end
