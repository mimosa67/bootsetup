#!/usr/bin/python
# coding: utf-8

import gettext
gettext.install('combobox')
import urwid
import urwid_more as urwidm

def pause():
  raw_input("pause")

class ComboBoxEditAddMore(urwidm.ComboBoxEditMore):
  def keypress(self, size, key):
    if key == '+':
      (item, pos) = self.get_selected_item()
      if pos is None:
        self.list.append(item)
    else:
      return self.__super.keypress(size, key)

def main_event(input):
  if input in ('q', 'Q', 'f10'):
    raise urwid.ExitMainLoop

l1 = [
  u"val1",
  u"val2",
  u"val3",
]
class ComplexWidget(urwidm.WidgetWrapMore):
  def __init__(self, left = u'', center = u'', right = u''):
    w = urwidm.ColumnsMore([
      ('fixed', len(left), urwid.Text(left)),
      ('fixed', len(center), urwid.Text(center)),
      ('fixed', len(right), urwid.Text(right))
    ])
    self.__super.__init__(w)
  def get_text(self):
    return self._w.widget_list[1].text
  def set_text(self, text):
    self._w.widget_list[1].set_text(text)
  text = property(get_text)
  def set_sensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._sensitive_attr = attr
    try:
      if hasattr(self._w, 'sensitive_attr'):
        self._w.sensitive_attr = attr
      for w in self._w.widget_list:
        if hasattr(w, 'sensitive_attr'):
          w.sensitive_attr = attr
    except:
      pass
  def set_unsensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._unsensitive_attr = attr
    try:
      if hasattr(self._w, 'unsensitive_attr'):
        wself._.unsensitive_attr = attr
      for w in self._w.widget_list:
        if hasattr(w, 'unsensitive_attr'):
          w.unsensitive_attr = attr
    except:
      pass
  def keypress(self, size, key):
    return key
  def selectable(self):
    return True
  def pack(self, size = None, focus = False):
    if size is None:
      w = 0
      for sw in self._w.widget_list:
        w += len(sw.text)
      return (w, 1)
    else:
      self.__super.pack(size, focus)

l2 = [
  urwidm.SelText(u"prop1"),
  ComplexWidget(u"«left,", u"prop2", u",right»"),
]
fill = urwid.Filler(urwidm.PileMore([
  urwid.Padding(urwid.Text(u"ComboBox tests"), 'center'),
  urwid.Divider(),
  urwid.Padding(urwidm.ComboBoxMore(items = l1, focus = 0), 'center', 10),
  urwid.Divider(),
  urwid.Padding(urwid.Text(u"Use + to add an item to the list"), 'center'),
  urwid.Padding(ComboBoxEditAddMore(label = u"props:", items = l2, focus = 0), 'center', 20),
  urwid.Divider(),
  urwid.Padding(urwid.Text(u"Q or F10 to quit"), 'center'),
]))
loop = urwid.MainLoop(
    fill,
    [
      ('body', 'light gray', 'black'),
      ('header', 'dark blue', 'light gray'),
      ('footer', 'light green', 'black', 'bold'),
      ('footer_key', 'yellow', 'black', 'bold'),
      ('strong', 'white', 'black', 'bold'),
      ('focusable', 'light green', 'black'),
      ('unfocusable', 'brown', 'black'),
      ('focus', 'black', 'light green'),
      ('focus_edit', 'yellow', 'black'),
      ('focus_icon', 'yellow', 'black'),
      ('focus_radio', 'yellow', 'black'),
      ('comboitem', 'dark blue', 'dark cyan'),
      ('comboitem_focus', 'black', 'brown'),
      ('error', 'white', 'light red'),
      ('focus_error', 'light red', 'black'),
    ],
    pop_ups=True,
    unhandled_input=main_event)
loop.run()
