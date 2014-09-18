import sublime
import sublime_plugin

# The default morph lamda, just returns the input
_DEFAULT_MORPH = lambda s: s


def get_user_morph(morph):
    try:
        exec("user_morph = lambda s: {}".format(morph))
    except:
        return _DEFAULT_MORPH
    else:
        return locals()["user_morph"]


class SortSelection(sublime_plugin.TextCommand):
    def run(self, edit, case_sensitive=True, morph=_DEFAULT_MORPH):
        self.morph = get_user_morph(morph)
        self.edit = edit
        self.case_sensitive = case_sensitive
        self._sort_selection()

    def _sort_selection(self):
        selections = self.view.sel()

        self._remove_duplicate_lines(selections)
        self._sort_lines(selections)

        selections.clear()
        for i in reversed(range(len(self.non_duplicate_selections))):
            # Replace the current lines with the sorted lines
            self.view.replace(self.edit,
                              self.non_duplicate_lines[i],
                              self.sorted_lines_text[i])

            # Update the selection
            start = (self.non_duplicate_lines[i].begin() +
                     self.sorted_regions[i].begin() -
                     self.sorted_lines[i].begin())
            end = start + self.sorted_regions[i].size()
            selections.add(sublime.Region(start, end))

    def _remove_duplicate_lines(self, selections):
        self.non_duplicate_lines = []
        self.non_duplicate_selections = []
        for selection in self.view.sel():
            line = self.view.line(selection)
            if line in self.non_duplicate_lines:
                continue

            self.non_duplicate_selections.append(selection)
            self.non_duplicate_lines.append(self.view.line(selection))

    def _sort_lines(self, selections):
        self._sort_regions(selections)

        self.sorted_lines = []
        self.sorted_lines_text = []
        for region in self.sorted_regions:
            line = self.view.line(region)
            self.sorted_lines.append(line)
            self.sorted_lines_text.append(self.view.substr(line))

    def _sort_regions(self, selections):
        morph = self.morph
        if not self.case_sensitive:
            morph = lambda s: self.morph(s.lower())

        # Sort the selection regions based on the text
        self.sorted_regions = sorted(
            selections,
            key=lambda r: morph(self.view.substr(r))
        )
