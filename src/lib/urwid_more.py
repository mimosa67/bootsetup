#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
More widgets for Urwid
Based on the work on curses_misc.py in Wicd.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS, 2008-2009 Andrew Psaltis'
__license__ = 'GPL2+'

import urwid
import gettext

class SelText(urwid.Text):
  """A selectable text widget. See urwid.Text."""

  def selectable(self):
    """Make widget selectable."""
    return True

  def keypress(self, size, key):
    """Don't handle any keys."""
    return key


class NSelListBox(urwid.ListBox):
  """ Non-selectable ListBox. """
  def selectable(self):
    return False


FOCUSLOST_EVENT = 'focuslost'

class FocusLostWidgetBehavior(object):
  """
  This object trigger the 'focuslost' event if it looses the focus.
  """
  def _register_focus_lost(self):
    urwid.register_signal(self.__class__, FOCUSLOST_EVENT)

  def _loose_focus(self):
    """
    This should be called when this widget looses the focus.
    """
    urwid.emit_signal(self, FOCUSLOST_EVENT, self)


class SensitiveWidgetBehavior(object):
  """
  Makes an object have mutable selectivity.
  """
  def _init_sensitive(self, sensitive, sensitive_attr, unsensitive_attr = None):
    """
    sensitive = boolean indicating if the widget is sensitive or not.
    sensitive_attr = tuple of (attr, focus_attr) when sensitive
    unsensitive_attr = tuple of (attr, focus_attr) when not sensitive, default to sensitive if None
      attr = attribute to apply to w
      focus_attr = attribute to apply when in focus, if None use attr
    """
    assert sensitive_attr, "sensitive_attr must be defined."
    self.set_sensitive_attr(sensitive_attr)
    if not unsensitive_attr:
      unsensitive_attr = sensitive_attr
    self.set_unsensitive_attr(unsensitive_attr)
    self.set_sensitive(sensitive)

  def get_sensitive_attr(self):
    return self._sensitive_attr
  def set_sensitive_attr(self, sensitive_attr):
    self._sensitive_attr = sensitive_attr
  sensitive_attr = property(get_sensitive_attr, set_sensitive_attr)
  
  def get_unsensitive_attr(self):
    return self._unsensitive_attr
  def set_unsensitive_attr(self, unsensitive_attr):
    self._unsensitive_attr = unsensitive_attr
  unsensitive_attr = property(get_unsensitive_attr, set_unsensitive_attr)
  
  def get_sensitive(self):
    return self._sensitive
  def set_sensitive(self, state):
    self._sensitive = state
  sensitive = property(get_sensitive, set_sensitive)

  def selectable(self):
    return self.get_sensitive()
  
  def render(self, size, focus = False):
    """ Taken from AttrMap """
    if self._sensitive:
      attr_tuple = self._sensitive_attr
    else:
      attr_tuple = self._unsensitive_attr
    if focus and attr_tuple[1]:
      attr_map = attr_tuple[1]
    else:
      attr_map = attr_tuple[0]
    canv = super(self.__class__).render(size, focus = focus) # WORKING ?
    canv = CompositeCanvas(canv)
    canv.fill_attr_apply(attr_map)
    return canv


class DynWrap(urwid.AttrWrap):
  """
  Makes an object have mutable selectivity.
  Attributes will change like those in an AttrWrap

  w = widget to wrap
  sensitive = current selectable state
  attrs = tuple of (attr_sens, attr_not_sens)
  attrfoc = attributes when in focus, defaults to nothing
  """
  def __init__(self, w, sensitive=True, attrs=('editbx', 'editnfc'), focus_attr='editfc'):
    self._attrs = attrs
    self._sensitive = sensitive
    if sensitive:
      cur_attr = attrs[0]
    else:
      cur_attr = attrs[1]
    self.__super.__init__(w, cur_attr, focus_attr)

  def get_sensitive(self):
    """ Getter for sensitive property. """
    return self._sensitive

  def set_sensitive(self, state):
    """ Setter for sensitive property. """
    if state:
      self.set_attr(self._attrs[0])
    else:
      self.set_attr(self._attrs[1])
    self._sensitive = state
  property(get_sensitive, set_sensitive)

  def get_attrs(self):
    """ Getter for attrs property. """
    return self._attrs

  def set_attrs(self, attrs):
    """ Setter for attrs property. """
    self._attrs = attrs
  property(get_attrs, set_attrs)

  def selectable(self):
    return self._sensitive


class DynEdit(DynWrap):
  """ Edit DynWrap'ed to the most common specifications. """
  def __init__(self, caption='', edit_text='', multiline = False, align = 'left', wrap = 'space', allow_tab = False, edit_pos = None, layout = None, mask = None,
      sensitive = True, attrs = ('editbx', 'editnfc'), focus_attr = 'editfc'):
    edit = urwid.Edit(caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)
    self.__super.__init__(edit, sensitive, attrs, focus_attr)


class DynIntEdit(DynWrap):
  """ IntEdit DynWrap'ed to the most common specifications. """
  def __init__(self, caption='', default = None, sensitive = True, attrs = ('editbx', 'editnfc'), focus_attr = 'editfc'):
    edit = urwid.IntEdit(caption, default)
    self.__super.__init__(edit, sensitive, attrs, focus_attr)


class DynButton(DynWrap):
  """ Button DynWrap'ed to the most common specifications. """
  def __init__(self, label, on_press = None, user_data = None, sensitive = True, attrs = ('body', 'editnfc'), focus_attr='body'):
    button = urwid.Button(label, on_press, user_data)
    self.__super.__init__(button, sensitive, attrs, focus_attr)


class DynCheckButton(DynWrap):
  """ CheckButton DynWrap'ed to the most common specifications. """
  def __init__(self, label, state = False, hax_mixed = False, on_state_change = None, user_data = None, sensitive = True, attrs = ('body', 'editnfc'), focus_attr='body'):
    button = urwid.Button(label, state, hax_mixed, on_state_change, user_data)
    self.__super.__init__(button, sensitive, attrs, focus_attr)


class DynRadioButton(DynWrap):
  """ RadioButton DynWrap'ed to the most common specifications. """
  def __init__(self, group, label, state = 'first True', on_state_change = None, user_data = None, sensitive = True, attrs = ('body', 'editnfc'), focus_attr = 'body'):
    button = urwid.RadioButton(group, label, state, on_state_change, user_data)
    self.__super.__init__(button, sensitive, attrs, focus_attr)


class EditMore(FocusLostWidgetBehavior, SensitiveWidgetBehavior, urwid.Edit):
  """
  Edit Widget, which handle 'focuslost' event and can be made unsensitive on demand
  """
  def __init__(self, caption='', edit_text='', multiline = False, align = 'left', wrap = 'space', allow_tab = False, edit_pos = None, layout = None, mask = None,
      sensitive = True, sensitive_attr = ('edit_nonfocus', 'edit_focus'), unsensitive_attr = None):
    self._register_focus_lost()
    self._init_sensitive(sensitive, sensitive_attr, unsensitive_attr)
    super(self.__class__).__init__(caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)
  def keypress(self, size, key):
    key = super(self.__class__).keypress(size, key)
    if key and self._command_map[key] in ('cursor up', 'cursor down'):
      self._loose_focus(self)
    return key


class ComboBoxException(Exception):
  """ Custom exception. """
  pass


# A "combo box" of SelTexts
# I based this off of the code found here:
# http://excess.org/urwid/browser/contrib/trunk/rbreu_menus.py
# This is a hack/kludge.  It isn't without quirks, but it more or less works.
# We need to wait for changes in urwid's Canvas API before we can actually
# make a real ComboBox.
class ComboBox(urwid.WidgetWrap):
  """A ComboBox of text objects"""
  class ComboSpace(urwid.WidgetWrap):
    """The actual menu-like space that comes down from the ComboBox"""
    def __init__(self, l, body, ui, show_first, pos = (0, 0), attr = ('body', 'focus')):
      """
      body      : parent widget
      l         : stuff to include in the combobox
      ui        : the screen
      show_first: index of the element in the list to pick first
      pos       : a tuple of (row, col) where to put the list
      attr      : a tuple of (attr_no_focus, attr_focus)
      """
      #Calculate width and height of the menu widget:
      height = len(l)
      width = 0
      for entry in l:
        if len(entry) > width:
          width = len(entry)
      content = [urwid.AttrWrap(SelText(w), attr[0], attr[1]) for w in l]
      self._listbox = urwid.ListBox(urwid.SimpleListWalker(content))
      self._listbox.set_focus(show_first)
      overlay = urwid.Overlay(self._listbox, body, ('fixed left', pos[0]), width + 2, ('fixed top', pos[1]), height)
      self.__super.__init__(overlay)

    def show(self, ui, display):
      """ Show widget. """
      dim = ui.get_cols_rows()
      keys = True
      #Event loop:
      while True:
        if keys:
          ui.draw_screen(dim, self.render(dim, True))
        keys = ui.get_input()
        if "window resize" in keys:
          dim = ui.get_cols_rows()
        if "esc" in keys:
          return None
        if "enter" in keys:
          (wid, pos) = self._listbox.get_focus()
          (text, attr) = wid.get_text()
          return text
        for k in keys:
          #Send key to underlying widget:
          self._w.keypress(dim, k)

  def __init__(self, label = '', l = None, attrs = ('body', 'editnfc'), focus_attr = 'focus', use_enter = True, focus = 0, callback = None, user_args = None):
    """
    label     : bit of text that preceeds the combobox.  If it is "", then ignore it
    l         : stuff to include in the combobox
    attrs     : a tuple of (attr_sensitive, attr_no_sensitive)
    focus_attr: attributes when in focus
    use_enter : does enter trigger the combo list
    focus     : index of the element in the list to pick first
    callback  : function that takes (combobox, sel_index, user_args = None)
    user_args : user_args in the callback
    """
    self.DOWN_ARROW = '  vvv'
    self.label = urwid.Text(label)
    self.attrs = attrs
    self.focus_attr = focus_attr
    if l is None:
      l = []
    self.list = l
    self.overlay = None
    self.cbox = DynWrap(SelText(self.DOWN_ARROW), attrs = attrs, focus_attr = focus_attr)
    if label:
      w = urwid.Columns([('fixed', len(label), self.label), self.cbox], dividechars = 1)
    else:
      w = urwid.Columns([self.cbox])
    self.__super.__init__(w)
    # We need this to pick our keypresses
    self.use_enter = use_enter
    if urwid.VERSION < (1, 1, 0):
      self.focus = focus
    else:
      self._w.focus_position = focus
    self.callback = callback
    self.user_args = user_args
    # Widget references to simplify some things
    self.parent = None
    self.ui = None
    self.row = None

  def set_list(self, l):
    """ Populate widget list. """
    self.list = l

  def set_focus(self, index):
    """ Set widget focus. """
    if urwid.VERSION < (1, 1, 0):
      self.focus = index
    else:
      try:
        self._w.focus_position = index
      except IndexError:
        pass
    # API changed between urwid 0.9.8.4 and 0.9.9
    try:
      self.cbox.set_w(SelText(self.list[index] + self.DOWN_ARROW))
    except AttributeError:
      self.cbox._w = SelText(self.list[index] + self.DOWN_ARROW)
    if self.overlay:
      self.overlay._listbox.set_focus(index)

  def rebuild_combobox(self):
    """ Rebuild combobox. """
    self.build_combobox(self.parent, self.ui, self.row)

  def build_combobox(self, parent, ui, row):
    """ Build combobox. """
    s = self.label.text
    if urwid.VERSION < (1, 1, 0):
      index = self.focus
    else:
      index = self._w.focus_position
    self.cbox = DynWrap(SelText([self.list[index] + self.DOWN_ARROW]), attrs = self.attrs, focus_attr = self.focus_attr)
    if s:
      w = urwid.Columns([('fixed', len(s), self.label), self.cbox], dividechars = 1)
      self.overlay = self.ComboSpace(self.list, parent, ui, index, pos = (len(s) + 1, row))
    else:
      w = urwid.Columns([self.cbox])
      self.overlay = self.ComboSpace(self.list, parent, ui, index, pos = (0, row))
    self._w = w
    self._invalidate()
    self.parent = parent
    self.ui = ui
    self.row = row

  # If we press space or enter, be a combo box!
  def keypress(self, size, key):
    """ Handle keypresses. """
    activate = key == ' '
    if self.use_enter:
      activate = activate or key == 'enter'
    if activate:
      # Die if the user didn't prepare the combobox overlay
      if self.overlay is None:
        raise ComboBoxException('ComboBox must be built before use!')
      retval = self.overlay.show(self.ui, self.parent)
      if retval is not None:
        self.set_focus(self.list.index(retval))
        if self.callback is not None:
          self.callback(self, self.overlay._listbox.get_focus()[1], self.user_args)
    return self._w.keypress(size, key)

  def selectable(self):
    """ Return whether the widget is selectable. """
    return self.cbox.selectable()

  def get_focus(self):
    """ Return widget focus. """
    if self.overlay:
      return self.overlay._listbox.get_focus()
    else:
      if urwid.VERSION < (1, 1, 0):
        return None, self.focus
      else:
        return None, self._w.focus_position

  def get_sensitive(self):
    """ Return widget sensitivity. """
    return self.cbox.get_sensitive()

  def set_sensitive(self, state):
    """ Set widget sensitivity. """
    self.cbox.set_sensitive(state)


# This is a h4x3d copy of some of the code in Ian Ward's dialog.py example.
class DialogExit(Exception):
  """ Custom exception. """
  pass


class Dialog2(urwid.WidgetWrap):
  """ Base class for other dialogs. """
  def __init__(self, text, height, width, body=None):
    self.buttons = None
    self.width = int(width)
    if width <= 0:
      self.width = ('relative', 80)
    self.height = int(height)
    if height <= 0:
      self.height = ('relative', 80)
    self.body = body
    if body is None:
      # fill space with nothing
      body = urwid.Filler(urwid.Divider(), 'top')
    self.frame = urwid.Frame(body, focus_part='footer')
    if text is not None:
      self.frame.header = urwid.Pile([
        urwid.Text(text, align='right'),
        urwid.Divider()
      ])
    w = urwid.AttrWrap(self.frame, 'body')
    self.view = w

  # buttons: tuple of name,exitcode
  def add_buttons(self, buttons):
    """ Add buttons. """
    l = []
    maxlen = 0
    for name, exitcode in buttons:
      b = urwid.Button(name, self.button_press)
      b.exitcode = exitcode
      b = urwid.AttrWrap(b, 'body', 'focus')
      l.append(b)
      maxlen = max(len(name), maxlen)
    maxlen += 4  # because of '< ... >'
    self.buttons = urwid.GridFlow(l, maxlen, 3, 1, 'center')
    self.frame.footer = urwid.Pile([
      urwid.Divider(),
      self.buttons
    ], focus_item = 1)

  def button_press(self, button):
    """ Handle button press. """
    raise DialogExit(button.exitcode)

  def run(self, ui, parent):
    """ Run the UI. """
    ui.set_mouse_tracking()
    size = ui.get_cols_rows()
    overlay = urwid.Overlay(
      urwid.LineBox(self.view),
      parent, 'center', self.width,
      'middle', self.height
    )
    try:
      while True:
        canvas = overlay.render(size, focus=True)
        ui.draw_screen(size, canvas)
        keys = None
        while not keys:
          keys = ui.get_input()
        for k in keys:
          if urwid.VERSION < (1, 0, 0):
            check_mouse_event = urwid.is_mouse_event
          else:
            check_mouse_event = urwid.util.is_mouse_event
          if check_mouse_event(k):
            event, button, col, row = k
            overlay.mouse_event(size, event, button, col, row, focus = True)
          else:
            if k == 'window resize':
              size = ui.get_cols_rows()
            k = self.view.keypress(size, k)
            if k == 'esc':
              raise DialogExit(-1)
            if k:
              self.unhandled_key(size, k)
    except DialogExit, e:
      return self.on_exit(e.args[0])

  def on_exit(self, exitcode):
    """ Handle dialog exit. """
    return exitcode, ""

  def unhandled_key(self, size, key):
    """ Handle keypresses. """
    pass


class TextDialog(Dialog2):
  """ Simple dialog with text and "OK" button. """
  def __init__(self, text, height, width, header=None, align='left',
    buttons=(_('OK'), 1)):
    l = [urwid.Text(text)]
    body = urwid.ListBox(urwid.SimpleListWalker(l))
    body = urwid.AttrWrap(body, 'body')
    Dialog2.__init__(self, header, height + 2, width + 2, body)
    if type(buttons) == list:
      self.add_buttons(buttons)
    else:
      self.add_buttons([buttons])

  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up', 'down', 'page down'):
      self.frame.set_focus('body')
      self.view.keypress(size, k)
      self.frame.set_focus('footer')


class InputDialog(Dialog2):
  """ Simple dialog with text and entry. """
  def __init__(self, text, height, width, ok_name=_('OK'), edit_text=''):
    self.edit = urwid.Edit(wrap='clip', edit_text=edit_text)
    body = urwid.ListBox(urwid.SimpleListWalker([self.edit]))
    body = urwid.AttrWrap(body, 'editbx', 'editfc')
    Dialog2.__init__(self, text, height, width, body)
    self.frame.set_focus('body')
    self.add_buttons([(ok_name, 0), (_('Cancel'), -1)])

  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up'):
      self.frame.set_focus('body')
    if k in ('down', 'page down'):
      self.frame.set_focus('footer')
    if k == 'enter':
      # pass enter to the "ok" button
      self.frame.set_focus('footer')
      self.view.keypress(size, k)

  def on_exit(self, exitcode):
    """ Handle dialog exit. """
    return exitcode, self.edit.get_edit_text()


class ClickCols(urwid.WidgetWrap):
  """ Clickable menubar. """
  def __init__(self, items, callback=None, args=None):
    cols = urwid.Columns(items)
    self.__super.__init__(cols)
    self.callback = callback
    self.args = args

  def mouse_event(self, size, event, button, x, y, focus):
    """ Handle mouse events. """
    if event == "mouse press":
      # The keypress dealie in wicd-curses.py expects a list of keystrokes
      self.callback([self.args])


class OptCols(urwid.WidgetWrap):
  """ Htop-style menubar on the bottom of the screen. """
  # tuples = [(key, desc)], on_event gets passed a key
  # attrs = (attr_key, attr_desc)
  # handler = function passed the key of the "button" pressed
  # mentions of 'left' and right will be converted to <- and -> respectively
  # pylint: disable-msg=W0231
  def __init__(self, tuples, handler, attrs=('body', 'infobar'), debug=False):
    # Find the longest string.  Keys for this bar should be no greater than
    # 2 characters long (e.g., -> for left)
    #maxlen = 6
    #for i in tuples:
    #  newmax = len(i[0])+len(i[1])
    #  if newmax > maxlen:
    #    maxlen = newmax

    # Construct the texts
    textList = []
    i = 0
    # callbacks map the text contents to its assigned callback.
    self.callbacks = []
    for cmd in tuples:
      key = reduce(lambda s, (f, t): s.replace(f, t), [
        ('ctrl ', 'Ctrl+'), ('meta ', 'Alt+'),
        ('left', '<-'), ('right', '->'),
        ('page up', 'Page Up'), ('page down', 'Page Down'),
        ('esc', 'ESC'), ('enter', 'Enter'), ('f10', 'F10')], cmd[0])
      if debug:
        callback = self.debugClick
        args = cmd[1]
      else:
        callback = handler
        args = cmd[0]
      col = ClickCols([('fixed', len(key) + 1, urwid.Text((attrs[0], key + ':'))), urwid.AttrWrap(urwid.Text(cmd[1]), attrs[1])], callback, args)
      textList.append(col)
      i += 1
    if debug:
      self.debug = urwid.Text("DEBUG_MODE")
      textList.append(('fixed', 10, self.debug))
    cols = urwid.Columns(textList)
    self.__super.__init__(cols)

  def debugClick(self, args):
    """ Debug clicks. """
    self.debug.set_text(args)

  def mouse_event(self, size, event, button, x, y, focus):
    """ Handle mouse events. """
    # Widgets are evenly long (as of current), so...
    return self._w.mouse_event(size, event, button, x, y, focus)
