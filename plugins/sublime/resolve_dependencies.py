import sublime
import sublime_plugin
import urllib
import urllib.parse

def file_path_to_header(file_path):
    data = {'file_path': file_path}
    to_send = urllib.parse.urlencode(data).encode('ascii')
    res = urllib.request.urlopen('http://localhost:5001/', data=to_send)
    return res.read().decode('ascii')

class DependencyFindCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        top_region = sublime.Region(0, 0)
        # add header to top
        file_path = self.view.file_name()
        header = file_path_to_header(file_path)
        self.view.replace(edit, top_region, header)
