#!/usr/bin/python
# coding: utf-8

import gettext
gettext.install('combobox')
import urwid
import urwid_more as urwidm

def pause():
  raw_input("pause")

class ComboBoxMoreException(Exception):
  """ Custom exception. """
  pass

class ComboBoxMore(urwid.PopUpLauncher, urwidm.WidgetWrapMore):
  """A ComboBox of text objects"""
  class ComboSpace(urwidm.WidgetWrapMore):
    """The actual menu-like space that comes down from the ComboBox"""
    signals = ['close', 'validate']
    def __init__(self, items, show_first = 0, item_attrs = ('comboitem', 'comboitem_focus')):
      """
      items     : stuff to include in the combobox
      show_first: index of the element in the list to pick first
      """
      normal_attr = item_attrs[0]
      focus_attr = item_attrs[1]
      sepLeft = urwidm.AttrMapMore(urwid.SolidFill(u"│"), normal_attr)
      sepRight = urwidm.AttrMapMore(urwid.SolidFill(u"│"), normal_attr)
      sepBottomLeft = urwidm.AttrMapMore(urwid.Text(u"└"), normal_attr)
      sepBottomRight = urwidm.AttrMapMore(urwid.Text(u"┘"), normal_attr)
      sepBottomCenter = urwidm.AttrMapMore(urwid.Divider(u"─"), normal_attr)
      self._content = []
      for item in items:
        if isinstance(item, urwid.Widget):
          if item.selectable and hasattr(item, "text") and hasattr(item, "attr"): # duck typing
            self._content.append(item)
          else:
            raise ValueError, "items in ComboBoxMore should be strings or selectable widget with a text and attr properties"
        else:
          self._content.append(urwidm.SelText(item))
      self._listw = urwidm.PileMore(self._content)
      if show_first is None:
        show_first = 0
      self.set_selected_pos(show_first)
      columns = urwidm.ColumnsMore([
        ('fixed', 1, urwidm.PileMore([urwid.BoxAdapter(sepLeft, len(items)), sepBottomLeft])),
        urwidm.PileMore([self._listw, sepBottomCenter]),
        ('fixed', 1, urwidm.PileMore([urwid.BoxAdapter(sepRight, len(items)), sepBottomRight])),
      ])
      filler = urwidm.FillerMore(columns)
      self.__super.__init__(filler)
      self._deco = [sepLeft, sepRight, sepBottomLeft, sepBottomRight, sepBottomCenter, self._listw]
      self.set_item_attrs(item_attrs)
    def get_size(self):
      maxw = 1
      maxh = 0
      for widget in self._content:
        w = 0
        h = 0
        for s in (None, ()):
          try:
            (w, h) = widget.pack(s)
          except:
            pass
        maxw = max(maxw, w + 1)
        maxh += h
      return (maxw + 2, maxh + 1)
    def set_item_attrs(self, item_attrs):
      for w in self._content:
        if hasattr(w, "attr"):
          w.attr = item_attrs
      w.attr = item_attrs
      for w in self._deco:
        w.attr = item_attrs
    def keypress(self, size, key):
      if key in 'esc':
        self.set_selected_pos(None)
        self._emit('close')
      if key in ('enter', u' '):
        self.set_selected_item(self._listw.get_focus())
        self._emit('validate')
      else:
        return self.__super.keypress(size, key)
    def get_selected_item(self):
      return self._selected_item
    def set_selected_item(self, item):
      try:
        pos = [i.text for i in self._content].index(item.text)
      except:
        pos = None
      self.set_selected_pos(pos)
    selected_item = property(get_selected_item, set_selected_item)
    def get_selected_pos(self):
      return self._selected_pos
    def set_selected_pos(self, pos):
      if pos is not None and pos < len(self._content):
        self._listw.set_focus(pos)
        self._selected_item = self._content[pos].text
        self._selected_pos = pos
      else:
        self._selected_item = None
        self._selected_pos = None
    selected_pos = property(get_selected_pos, set_selected_pos)

  _default_sensitive_attr = ('body', '')
  _default_unsensitive_attr = ('body', '')
  DOWN_ARROW = u"↓"
  signals = ['displaycombo']
  
  def __init__(self, label = u'', items = None, use_enter = True, focus = 0, callback = None, user_args = None):
    """
    label     : bit of text that preceeds the combobox.  If it is "", then ignore it
    items     : stuff to include in the combobox
    use_enter : does enter trigger the combo list
    focus     : index of the element in the list to pick first
    callback  : function that takes (combobox, sel_index, user_args = None)
    user_args : user_args in the callback
    """
    self.label = urwid.Text(label)
    if items is None:
      items = []
    self.set_list(items)
    self.cbox = self._create_cbox_widget()
    if label:
      w = urwidm.ColumnsMore(
        [
          ('fixed', len(label), self.label),
          self.cbox,
          ('fixed', len(self.DOWN_ARROW), urwid.Text(self.DOWN_ARROW))
        ], dividechars = 1)
    else:
      w = urwidm.ColumnsMore(
        [
          self.cbox,
          ('fixed', len(self.DOWN_ARROW), urwid.Text(self.DOWN_ARROW))
        ], dividechars = 1)
    self.__super.__init__(w)
    self.combo_attrs = ('comboitem', 'comboitem_focus')
    self.use_enter = use_enter
    self.set_selected_item(focus)
    self._overlay_left = 0
    self._overlay_width = len(self.DOWN_ARROW)
    self._overlay_height = len(items)
    self.callback = callback
    self.user_args = user_args
    urwid.connect_signal(self, 'displaycombo', self.displaycombo)
  def _create_cbox_widget(self):
    return urwidm.SelText(u'')
  def _set_cbox_text(self, text):
    ok = False
    if not ok and hasattr(self.cbox, "set_text"):
      try:
        self.cbox.set_text(text)
        ok = True
      except:
        pass
    if not ok and hasattr(self.cbox, "set_edit_text"):
      try:
        self.cbox.set_edit_text(text)
        ok = True
      except:
        pass
    if not ok:
      raise Exception, "Do not know how to set the text in the widget {0}".format(self.cbox)
  def _item_text(self, item):
    if isinstance(item, basestring):
      return item
    else:
      return item.text
  def get_selected_item(self):
    """ Return (text, index) or (text, None) if the selected text is not in the list """
    curr_text = self.cbox.text
    try:
      index = [self._item_text(i) for i in self.list].index(curr_text)
    except:
      index = None
    return (curr_text, index)
  def set_selected_item(self, index):
    """ Set widget focus. """
    if index is not None and isinstance(index, int):
      curr_text = self._item_text(self.list[index])
    elif index is not None and isinstance(index, basestring):
      curr_text = text
    else:
      curr_text = u''
    self._set_cbox_text(curr_text)
  selected_item = property(get_selected_item, set_selected_item)
  def get_sensitive(self):
    return self.cbox.get_sensitive()
  def set_sensitive(self, state):
    self.cbox.set_sensitive(state)
  def selectable(self):
    return self.cbox.selectable()
  def get_list(self):
    return self._list
  def set_list(self, items):
    self._list = items
  list = property(get_list, set_list)
  def set_combo_attrs(self, normal_attr, focus_attr):
    self.combo_attrs = item_attrs
  def keypress(self, size, key):
    """
    If we press space or enter, be a combo box!
    """
    if key == ' ' or (self.use_enter and key == 'enter'):
      self._emit("displaycombo")
    else:
      return self._original_widget.keypress(size, key)
  def displaycombo(self, src):
    self.open_pop_up()
  def create_pop_up(self):
    index = self.selected_item[1]
    popup = self.ComboSpace(self.list, index, self.combo_attrs)
    self._overlay_left = 0
    if self.label.text:
      self._overlay_left = len(self.label.text) + 1
    (self._overlay_width, self._overlay_height) = popup.get_size()
    urwid.connect_signal(popup, 'close', lambda x: self.close_pop_up())
    urwid.connect_signal(popup, 'validate', self.validate_pop_up)
    return popup
  def get_pop_up_parameters(self):
    return {'left':self._overlay_left, 'top':1, 'overlay_width':self._overlay_width, 'overlay_height':self._overlay_height}
  def validate_pop_up(self, popup):
    pos = self._pop_up_widget.selected_pos
    self.close_pop_up()
    if self.callback:
      self.callback(self, pos, self.user_args)
    self.set_selected_item(pos)

class ComboBoxEditMore(ComboBoxMore):
  def _create_cbox_widget(self):
    return urwidm.EditMore(edit_text = u'')
  def keypress(self, size, key):
    """
    If we press enter, be a combo box!
    """
    if key == 'enter': # discard state of self.use_enter
      self._emit("displaycombo")
    else:
      return self._original_widget.keypress(size, key)

class ComboBoxEditAddMore(ComboBoxEditMore):
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
  urwid.Padding(ComboBoxMore(items = l1, focus = 0), 'center', 10),
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
