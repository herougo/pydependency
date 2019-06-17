import sublime
import sublime_plugin
import os
from pydependency.dependency_finder import DependencyFinder


df = DependencyFinder()


class DependencyFindCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        df.set_current_file(self.view.file_name())
        header = df.extract_missing_dependency_header()
        top_region = sublime.Region(0, 0)
        # add header to top
        self.view.replace(edit, top_region, header)