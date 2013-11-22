#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
More widgets for Urwid
Based on the work on curses_misc.py in Wicd.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS, 2008-2009 Andrew Psaltis'
__license__ = 'GPL2+'

#from urwid import *
import urwid
import gettext
import re

class FocusEventWidget(urwid.Widget):
  signals = ['focusgain', 'focuslost'] # will be used by the metaclass of Widget to call register_signal
  _has_focus = False
  @property
  def has_focus(self):
    return self._has_focus
  def _can_gain_focus(self):
    return True
  def _can_loose_focus(self):
    return True
  def _emit_focus_event(self, name, *args):
    """
    Return True if there is no callback, or if all callback answer True
    """
    result = True
    signal_obj = urwid.signals._signals
    d = getattr(self, signal_obj._signal_attr, {})
    for callback, user_arg in d.get(name, []):
      args_copy = (self,) + args
      if user_arg is not None:
        args_copy = args_copy + (user_arg,)
      result &= bool(callback(*args_copy))
    return result
  def emit_focusgain(self):
    """
    Return True if there is no callback, or if all callback answer True
    """
    return self._emit_focus_event('focusgain')
  def emit_focuslost(self):
    """
    Return True if there is no callback, or if all callback answer True
    """
    return self._emit_focus_event('focuslost')
  def gain_focus(self):
    ret = self._can_gain_focus()
    if ret:
      ret = self.emit_focusgain()
    if ret:
      self._has_focus = True
    return ret
  def loose_focus(self):
    ret = self._can_loose_focus()
    if ret:
      ret = self.emit_focuslost()
    if ret:
      self._has_focus = False
    return ret
  def _gain_focus_with_subwidget(self, subwidget):
    ret = self._can_gain_focus()
    if ret:
      if subwidget and isinstance(subwidget, FocusEventWidget):
        ret = subwidget.gain_focus()
      else:
        ret = self.emit_focusgain()
    if ret:
      self._has_focus = True
    return ret
  def _loose_focus_with_subwidget(self, subwidget):
    ret = self._can_loose_focus()
    if ret:
      if subwidget and isinstance(subwidget, FocusEventWidget):
        ret = subwidget.loose_focus()
      else:
        ret = self.emit_focuslost()
    if ret:
      self._has_focus = False
    return ret

class SensitiveWidgetBehavior(object):
  """
  Makes an object have mutable selectivity.
  """
  _default_sensitive_attr = ('focusable', 'focus')
  """
  sensitive_attr = tuple of (attr, focus_attr) when sensitive
      attr = attribute to apply to w
      focus_attr = attribute to apply when in focus, if None use attr
  """
  _default_unsensitive_attr = ('unfocusable', '')
  """
  unsensitive_attr = tuple of (attr, focus_attr) when not sensitive
      attr = attribute to apply to w
      focus_attr = attribute to apply when in focus, if None use attr
  """

  def __init__(self, sensitive = True):
    if hasattr(self, '_sensitive_attr'):
      return # already initialized
    self.set_sensitive_attr(self._default_sensitive_attr)
    self.set_unsensitive_attr(self._default_unsensitive_attr)
    self.set_sensitive(sensitive)
  def get_sensitive_attr(self):
    return self._sensitive_attr
  def set_sensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._sensitive_attr = attr
  sensitive_attr = property(get_sensitive_attr, set_sensitive_attr)
  def get_unsensitive_attr(self):
    return self._unsensitive_attr
  def set_unsensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._unsensitive_attr = attr
  unsensitive_attr = property(get_unsensitive_attr, set_unsensitive_attr)
  def get_attr(self):
    return (self.sensitive_attr, self.unsensitive_attr)
  def set_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self.set_sensitive_attr(attr)
    self.set_unsensitive_attr(attr)
  attr = property(get_attr, set_attr)
  def get_sensitive(self):
    return self._selectable
  def set_sensitive(self, state):
    self._selectable = state
  sensitive = property(get_sensitive, set_sensitive)
  def selectable(self):
    return self.get_sensitive()
  def render_with_attr(self, canvas, focus = False):
    """ Taken from AttrMap """
    new_canvas = urwid.CompositeCanvas(canvas)
    if self.sensitive:
      attr_tuple = self._sensitive_attr
    else:
      attr_tuple = self._unsensitive_attr
    if focus and attr_tuple[1]:
      attr_map = attr_tuple[1]
    else:
      attr_map = attr_tuple[0]
    if type(attr_map) != dict:
      attr_map = {None: attr_map}
    new_canvas.fill_attr_apply(attr_map)
    return new_canvas

class More(FocusEventWidget, SensitiveWidgetBehavior):
  """
  Class that combine a FocusEventWidget and a SensitiveWidgetBehavior.
  Parent of all other widgets defined here.
  """
  def __init__(self, sensitive = True):
    SensitiveWidgetBehavior.__init__(self, sensitive)
  def render(self, size, focus = False):
    for cls in self.__class__.__bases__:
      if cls != More and hasattr(cls, 'render') and callable(cls.render) and cls.render != More.render: # skip me
        canvas = cls.render(self, size, focus)
        if canvas:
          return self.render_with_attr(canvas, focus)
        else:
          return canvas

class EditMore(More, urwid.Edit):
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, caption = u"", edit_text = u"", multiline = False, align = urwid.LEFT, wrap = urwid.SPACE, allow_tab = False, edit_pos = None, layout = None, mask = None):
    More.__init__(self)
    urwid.Edit.__init__(self, caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)

class IntEditMore(More, urwid.IntEdit):
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, caption = "", default = None):
    More.__init__(self)
    urwid.IntEdit.__init__(self, caption, default)

class SelectableIconMore(More, urwid.SelectableIcon):
  _default_sensitive_attr = ('focusable', 'focus_icon')
  def __init__(self, text, cursor_position = 1):
    More.__init__(self)
    urwid.SelectableIcon.__init__(self, text, cursor_position)

class ButtonMore(More, urwid.Button):
  def __init__(self, label, on_press = None, user_data = None):
    More.__init__(self)
    urwid.Button.__init__(self, label, on_press, user_data)

class CheckBoxMore(More, urwid.CheckBox):
  _default_sensitive_attr = ('focusable', 'focus_radio')
  states = {
    True: SelectableIconMore(u"[X]"),
    False: SelectableIconMore(u"[ ]"),
    'mixed': SelectableIconMore(u"[#]") }
  def __init__(self, label, state = False, has_mixed = False, on_state_change = None, user_data = None):
    More.__init__(self)
    urwid.CheckBox.__init__(self, label, state, has_mixed, on_state_change, user_data)

class RadioButtonMore(More, urwid.RadioButton):
  _default_sensitive_attr = ('focusable', 'focus_radio')
  states = {
    True: SelectableIconMore(u"(X)"),
    False: SelectableIconMore(u"( )"),
    'mixed': SelectableIconMore(u"(#)") }
  def __init__(self, group, label, state = "first True", on_state_change = None, user_data = None):
    More.__init__(self)
    urwid.RadioButton.__init__(self, group, label, state, on_state_change, user_data)

class WidgetWrapMore(More, urwid.WidgetWrap):
  def __init__(self, w):
    More.__init__(self)
    self._wrapped_widget = w
  def render(self, size, focus = False):
    canvas = self._w.render(size, focus = focus)
    return self.render_with_attr(urwid.CompositeCanvas(canvas), focus)
  def _can_gain_focus(self):
    if isinstance(self._w, FocusEventWidget):
      return self._w._can_gain_focus()
    else:
      return FocusEventWidget._can_gain_focus(self)
  def _can_loose_focus(self):
    if isinstance(self._w, FocusEventWidget):
      return self._w._can_loose_focus()
    else:
      return FocusEventWidget._can_loose_focus(self)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self._w)
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self._w)

class WidgetDecorationMore(More, urwid.WidgetDecoration):
  def __init__(self, original_widget):
    More.__init__(self)
    urwid.WidgetDecoration.__init__(self, original_widget)
  def _can_gain_focus(self):
    if isinstance(self._original_widget, FocusEventWidget):
      return self._original_widget._can_gain_focus()
    else:
      return FocusEventWidget._can_gain_focus(self)
  def _can_loose_focus(self):
    if isinstance(self._original_widget, FocusEventWidget):
      return self._original_widget._can_loose_focus()
    else:
      return FocusEventWidget._can_loose_focus(self)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self._original_widget)
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self._original_widget)

class WidgetPlaceholderMore(WidgetDecorationMore, urwid.WidgetPlaceholder):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, original_widget):
    WidgetDecorationMore.__init__(self, original_widget)

class AttrMapMore(WidgetDecorationMore, urwid.AttrMap):
  def __init__(self, w, attr_map, focus_map = None):
    WidgetDecorationMore.__init__(self, w)
    urwid.AttrMap.__init__(self, w, attr_map, focus_map)

class AttrWrapMore(WidgetDecorationMore, urwid.AttrWrap):
  def __init__(self, w, attr, focus_attr = None):
    WidgetDecorationMore.__init__(self, w)
    urwid.AttrWrap.__init__(self, w, attr, focus_attr)

class PaddingMore(WidgetDecorationMore, urwid.Padding):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, w, align = urwid.LEFT, width = urwid.PACK, min_width = None, left = 0, right = 0):
    WidgetDecorationMore.__init__(self, w)
    urwid.Padding.__init__(self, w, align, width, min_width, left, right)

class FillerMore(WidgetDecorationMore, urwid.Filler):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, body, valign = "middle", height = None, min_height = None):
    WidgetDecorationMore.__init__(self, body)
    urwid.Filler.__init__(self, body, valign, height, min_height)

class BoxAdapterMore(WidgetDecorationMore, urwid.BoxAdapter):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, box_widget, height):
    WidgetDecorationMore.__init__(self, box_widget)
    urwid.BoxAdapter.__init__(self, box_widget, height)

class WidgetContainerMore(More, urwid.WidgetContainer):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list):
    More.__init__(self)
    urwid.WidgetContainer.__init__(self, widget_list)

class FrameMore(More, urwid.Frame):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  _filler_widget_class = FillerMore
  def __init__(self, body, header = None, footer = None, focus_part = 'body'):
    More.__init__(self)
    urwid.Frame.__init__(self, body, header, footer, focus_part)
  def render(self, size, focus = False):
    """Render frame and return it."""
    (maxcol, maxrow) = size
    (htrim, ftrim),(hrows, frows) = self.frame_top_bottom((maxcol, maxrow), focus)
    combinelist = []
    depends_on = []
    head = None
    if htrim and htrim < hrows:
      head = self._filler_widget_class(self.header, 'top').render((maxcol, htrim), focus and self.focus_part == 'header')
    elif htrim:
      head = self.header.render((maxcol,), focus and self.focus_part == 'header')
      assert head.rows() == hrows, "rows, render mismatch"
    if head:
      combinelist.append((head, 'header', self.focus_part == 'header'))
      depends_on.append(self.header)
    if ftrim + htrim < maxrow:
      body = self.body.render((maxcol, maxrow - ftrim - htrim), focus and self.focus_part == 'body')
      combinelist.append((body, 'body', self.focus_part == 'body'))
      depends_on.append(self.body)
      pass
    foot = None
    if ftrim and ftrim < frows:
      foot = self._filler_widget_class(self.footer, 'bottom').render((maxcol, ftrim), focus and self.focus_part == 'footer')
    elif ftrim:
      foot = self.footer.render((maxcol,), focus and self.focus_part == 'footer')
      assert foot.rows() == frows, "rows, render mismatch"
    if foot:
      combinelist.append((foot, 'footer', self.focus_part == 'footer'))
      depends_on.append(self.footer)
    return self.render_with_attr(urwid.CanvasCombine(combinelist), focus)
    #return urwid.CanvasCombine(combinelist)
  def _get_focus_widget(self, part):
    assert part in ('header', 'footer', 'body')
    if part == 'header':
      focus_w = self.get_header()
    elif part == 'footer':
      focus_w = self.get_footer()
    else: # part == 'body'
      focus_w = self.get_body()
    return focus_w
  def set_focus(self, part):
    """
    Set the part of the frame that is in focus.
    part -- 'header', 'footer' or 'body'
    """
    assert part in ('header', 'footer', 'body')
    ok = True
    if self.has_focus:
      focus_w = self._get_focus_widget(self.get_focus())
      if focus_w and isinstance(focus_w, FocusEventWidget):
        ok = focus_w.loose_focus()
      if ok:
        focus_w = self._get_focus_widget(part)
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      urwid.Frame.set_focus(self, part)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self._get_focus_widget(self.get_focus()))
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self._get_focus_widget(self.get_focus()))

class PileMore(More, urwid.Pile):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list, focus_item = None):
    More.__init__(self)
    urwid.Pile.__init__(self, widget_list, focus_item)
  def keypress(self, size, key):
    """
    Pass the keypress to the widget in focus.
    Unhandled 'up' and 'down' keys may cause a focus change.
    Copied from original Pile but with custom focus event handling.
    """
    item_rows = None
    if len(size) == 2:
      item_rows = self.get_item_rows(size, focus = True)
    i = self.widget_list.index(self.focus_item)
    f, height = self._get_item_types(i)
    if self.focus_item.selectable():
      tsize = self.get_item_size(size, i, True, item_rows)
      key = self.focus_item.keypress(tsize, key)
      if self._command_map[key] not in ('cursor up', 'cursor down'):
        return key
    if self._command_map[key] == 'cursor up':
      candidates = range(i - 1, -1, -1) # count backwards to 0
    else: # self._command_map[key] == 'cursor down'
      candidates = range(i + 1, len(self.widget_list))
    if not item_rows:
      item_rows = self.get_item_rows(size, focus = True)
    for j in candidates:
      if not self.widget_list[j].selectable():
        continue
      self._update_pref_col_from_focus(size)
      old_focus = self.focus_item
      self.set_focus(j)
      if old_focus == self.focus_item: # focus change has been denied
        return
      if not hasattr(self.focus_item,'move_cursor_to_coords'):
        return
      f, height = self._get_item_types(i)
      rows = item_rows[j]
      if self._command_map[key] == 'cursor up':
        rowlist = range(rows-1, -1, -1)
      else: # self._command_map[key] == 'cursor down'
        rowlist = range(rows)
      for row in rowlist:
        tsize=self.get_item_size(size,j,True,item_rows)
        if self.focus_item.move_cursor_to_coords(tsize, self.pref_col, row):
          break
      return
    # nothing to select
    return key
  def set_focus(self, item):
    """
    Set the item in focus.
    item -- widget or integer index
    """
    ok = True
    if not hasattr(self, "focus_item"):
      urwid.Pile.set_focus(self, item)
    if self.has_focus:
      focus_w = self.get_focus()
      if type(item) == int:
        new_focus_w = self.widget_list[item]
      else:
        new_focus_w = item
      if focus_w != new_focus_w:
        if focus_w and isinstance(focus_w, FocusEventWidget):
          ok = focus_w.loose_focus()
        if ok:
          if isinstance(new_focus_w, FocusEventWidget):
            ok = new_focus_w.gain_focus()
    if ok:
      urwid.Pile.set_focus(self, item)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self.get_focus())
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self.get_focus())

class ColumnsMore(More, urwid.Columns):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list, dividechars = 0, focus_column = None, min_width = 1, box_columns = None):
    More.__init__(self)
    urwid.Columns.__init__(self, widget_list, dividechars, focus_column, min_width, box_columns)
  def set_focus_column(self, num):
    """Set the column in focus by its index in self.widget_list."""
    ok = True
    if self.has_focus:
      if self.get_focus_column():
        focus_w = self.get_focus()
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.loose_focus()
      if ok:
        focus_w = self.widget_list[num]
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      urwid.Columns.set_focus_column(self, num)
  def set_focus(self, item):
    """Set the item in focus. item -- widget or integer index"""
    if type(item) == int:
      assert item>=0 and item<len(self.widget_list)
      position = item
    else:
      position = self.widget_list.index(item)
    ok = True
    if self.has_focus:
      if self.get_focus_column():
        focus_w = self.get_focus()
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.loose_focus()
      if ok:
        focus_w = self.widget_list[position]
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      self.focus_col = position
      self._invalidate()
    return ok
  def mouse_event(self, size, event, button, col, row, focus):
    """
    Send event to appropriate column.
    May change focus on button 1 press.
    """
    widths = self.column_widths(size)
    x = 0
    for i in range(len(widths)):
      if col < x:
        return False
      w = self.widget_list[i]
      end = x + widths[i]
      if col >= end:
        x = end + self.dividechars
        continue
      focus = focus and self.focus_col == i
      ok = True
      if urwid.util.is_mouse_press(event) and button == 1:
        if w.selectable():
          ok = self.set_focus(w)
      if not ok or not hasattr(w,'mouse_event'):
        return False
      return w.mouse_event((end-x,)+size[1:], event, button, col - x, row, focus)
    return False
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self.get_focus())
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self.get_focus())

class GridFlowMore(More, urwid.GridFlow):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  _column_widget_class = ColumnsMore
  _padding_widget_class = PaddingMore
  _pile_widget_class = PileMore
  def __init__(self, cells, cell_width, h_sep, v_sep, align):
    More.__init__(self)
    urwid.GridFlow.__init__(self, cells, cell_width, h_sep, v_sep, align)
  def generate_display_widget(self, size):
    """
    Actually generate display widget (ignoring cache)
    Copied from original GridFlow but with custom sub-widgets.
    """
    (maxcol,) = size
    d = urwid.Divider() # don't customize Divider, it's really a basic class.
    if len(self.cells) == 0: # how dull
      return d
    if self.v_sep > 1:
      # increase size of divider
      d.top = self.v_sep-1
    # cells per row
    bpr = (maxcol+self.h_sep) // (self.cell_width+self.h_sep)
    if bpr == 0: # too narrow, pile them on top of eachother
      l = [self.cells[0]]
      f = 0
      for b in self.cells[1:]:
        if b is self.focus_cell:
          f = len(l)
        if self.v_sep:
          l.append(d)
        l.append(b)
      return self._pile_widget_class(l, f)
    if bpr >= len(self.cells): # all fit on one row
      k = len(self.cells)
      f = self.cells.index(self.focus_cell)
      cols = self._column_widget_class(self.cells, self.h_sep, f)
      rwidth = (self.cell_width+self.h_sep)*k - self.h_sep
      row = self._padding_widget_class(cols, self.align, rwidth)
      return row
    out = []
    s = 0
    f = 0
    while s < len(self.cells):
      if out and self.v_sep:
        out.append(d)
      k = min(len(self.cells), s + bpr)
      cells = self.cells[s:k]
      if self.focus_cell in cells:
        f = len(out)
        fcol = cells.index(self.focus_cell)
        cols = self._column_widget_class(cells, self.h_sep, fcol)
      else:
        cols = self._column_widget_class(cells, self.h_sep)
      rwidth = (self.cell_width+self.h_sep)*(k-s)-self.h_sep
      row = self._padding_widget_class(cols, self.align, rwidth)
      out.append(row)
      s += bpr
    return self._pile_widget_class(out, f)    
  def set_focus(self, cell):
    """
    Set the cell in focus.  
    cell -- widget or integer index into self.cells
    """
    ok = True
    if self.has_focus:
      focus_w = self.get_focus()
      if focus_w and isinstance(focus_w, FocusEventWidget):
        ok = focus_w.loose_focus()
      if ok:
        if type(cell) == int:
          focus_w = self.cells[cell]
        else:
          focus_w = cell
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      urwid.GridFlow.set_focus(self, cell)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self.get_focus())
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self.get_focus())

class OverlayMore(More, urwid.Overlay):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, top_w, bottom_w, align, width, valign, height, min_width = None, min_height = None):
    More.__init__(self)
    urwid.Overlay.__init__(self, top_w, bottom_w, align, width, valign, height, min_width, min_height)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self.top_w)
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self.top_w)

class ListBoxMore(More, urwid.ListBox):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, body):
    More.__init__(self)
    urwid.ListBox.__init__(self, body)
  def change_focus(self, size, position, offset_inset = 0, coming_from = None, cursor_coords = None, snap_rows = None):
    old_widget, old_focus_pos = self.body.get_focus()
    new_focus_pos = position
    # hack for found the current widget in the list walker.
    new_widget = self.body.get_next(new_focus_pos - 1)[0]
    ok = True
    if isinstance(old_widget, FocusEventWidget):
      ok = old_widget.loose_focus()
    if ok and isinstance(new_widget, FocusEventWidget):
      ok = new_widget.gain_focus()
    if ok:
      urwid.ListBox.change_focus(self, size, position, offset_inset, coming_from, cursor_coords, snap_rows)
    return ok
  def mouse_event(self, size, event, button, col, row, focus):
    """
    Pass the event to the contained widgets.
    May change focus on button 1 press.
    """
    (maxcol, maxrow) = size
    middle, top, bottom = self.calculate_visible((maxcol, maxrow), focus = True)
    if middle is None:
      return False
    _ignore, focus_widget, focus_pos, focus_rows, cursor = middle
    trim_top, fill_above = top
    _ignore, fill_below = bottom
    fill_above.reverse() # fill_above is in bottom-up order
    w_list = (fill_above + [(focus_widget, focus_pos, focus_rows)] + fill_below)
    wrow = -trim_top
    for w, w_pos, w_rows in w_list:
      if wrow + w_rows > row:
        break
      wrow += w_rows
    else:
      return False
    focus = focus and w == focus_widget
    ok = True
    if urwid.util.is_mouse_press(event) and button == 1:
      if w.selectable():
        ok = self.change_focus((maxcol,maxrow), w_pos, wrow)
    if not ok or not hasattr(w,'mouse_event'):
      return False
    return w.mouse_event((maxcol,), event, button, col, row-wrow, focus)
  def gain_focus(self):
    return self._gain_focus_with_subwidget(self.get_focus()[0])
  def loose_focus(self):
    return self._loose_focus_with_subwidget(self.get_focus()[0])

class LineBoxMore(WidgetDecorationMore, urwid.LineBox):
  def __init__(self, original_widget, title = "", tlcorner = u'┌', tline = u'─', lline = u'│', trcorner = u'┐', blcorner = u'└', rline = u'│', bline = u'─', brcorner = u'┘'):
    """See urwid.LineBox"""
    tline, bline = urwid.Divider(tline), urwid.Divider(bline)
    lline, rline = urwid.SolidFill(lline), urwid.SolidFill(rline)
    tlcorner, trcorner = urwid.Text(tlcorner), urwid.Text(trcorner)
    blcorner, brcorner = urwid.Text(blcorner), urwid.Text(brcorner)
    self.title_widget = urwid.Text(self.format_title(title))
    self.tline_widget = ColumnsMore([
      tline,
      ('flow', self.title_widget),
      tline,
    ])
    top = ColumnsMore([
      ('fixed', 1, tlcorner),
      self.tline_widget,
      ('fixed', 1, trcorner)
    ])
    middle = ColumnsMore([
      ('fixed', 1, lline),
      original_widget,
      ('fixed', 1, rline),
    ], box_columns = [0, 2], focus_column = 1)
    bottom = ColumnsMore([
      ('fixed', 1, blcorner), bline, ('fixed', 1, brcorner)
    ])
    pile = PileMore([('flow', top), middle, ('flow', bottom)], focus_item = 1)
    WidgetDecorationMore.__init__(self, original_widget)
    urwid.WidgetWrap.__init__(self, pile)

class SelText(More, urwid.Text):
  """A selectable text widget. See urwid.Text."""
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, markup, align = urwid.LEFT, wrap = urwid.SPACE, layout = None):
    More.__init__(self)
    urwid.Text.__init__(self, markup, align, wrap, layout)
  def keypress(self, size, key):
    """Don't handle any keys."""
    return key

class ComboBoxMore(urwid.PopUpLauncher, WidgetWrapMore):
  """A ComboBox of text objects"""
  class ComboSpace(WidgetWrapMore):
    """The actual menu-like space that comes down from the ComboBox"""
    signals = ['close', 'validate']
    def __init__(self, items, show_first = 0, item_attrs = ('comboitem', 'comboitem_focus')):
      """
      items     : stuff to include in the combobox
      show_first: index of the element in the list to pick first
      """
      normal_attr = item_attrs[0]
      focus_attr = item_attrs[1]
      sepLeft = AttrMapMore(urwid.SolidFill(u"│"), normal_attr)
      sepRight = AttrMapMore(urwid.SolidFill(u"│"), normal_attr)
      sepBottomLeft = AttrMapMore(urwid.Text(u"└"), normal_attr)
      sepBottomRight = AttrMapMore(urwid.Text(u"┘"), normal_attr)
      sepBottomCenter = AttrMapMore(urwid.Divider(u"─"), normal_attr)
      self._content = []
      for item in items:
        if isinstance(item, urwid.Widget):
          if item.selectable and hasattr(item, "text") and hasattr(item, "attr"): # duck typing
            self._content.append(item)
          else:
            raise ValueError, "items in ComboBoxMore should be strings or selectable widget with a text and attr properties"
        else:
          self._content.append(SelText(item))
      self._listw = PileMore(self._content)
      if show_first is None:
        show_first = 0
      self.set_selected_pos(show_first)
      columns = ColumnsMore([
        ('fixed', 1, PileMore([urwid.BoxAdapter(sepLeft, len(items)), sepBottomLeft])),
        PileMore([self._listw, sepBottomCenter]),
        ('fixed', 1, PileMore([urwid.BoxAdapter(sepRight, len(items)), sepBottomRight])),
      ])
      filler = FillerMore(columns)
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
      w = ColumnsMore(
        [
          ('fixed', len(label), self.label),
          self.cbox,
          ('fixed', len(self.DOWN_ARROW), urwid.Text(self.DOWN_ARROW))
        ], dividechars = 1)
    else:
      w = ColumnsMore(
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
    return SelText(u'')
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
  """
  A ComboBox with an editable zone.
  The combo trigger on 'enter' only, disregarding the state for self.use_enter
  """
  def _create_cbox_widget(self):
    return EditMore(edit_text = u'')
  def keypress(self, size, key):
    """
    If we press enter, be a combo box!
    """
    if key == 'enter': # discard state of self.use_enter
      self._emit("displaycombo")
    else:
      return self._original_widget.keypress(size, key)

# This is a h4x3d copy of some of the code in Ian Ward's dialog.py example.
class DialogExit(Exception):
  """ Custom exception. """
  pass

class Dialog2(WidgetWrapMore):
  """ Base class for other dialogs. """
  def __init__(self, text, height, width, body = None):
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
      body = FillerMore(urwid.Divider(), 'top')
    self.frame = FrameMore(body, focus_part = 'footer')
    if text is not None:
      self.frame.header = PileMore([
        urwid.Text(text, align='right'),
        urwid.Divider()
      ])
    w = AttrWrapMore(self.frame, 'body')
    self.__super.__init__(w)
  # buttons: tuple of name,exitcode
  def add_buttons(self, buttons):
    """ Add buttons. """
    l = []
    maxlen = 0
    for name, exitcode in buttons:
      b = ButtonMore(name, self.button_press)
      b.exitcode = exitcode
      b = AttrWrapMore(b, 'body', 'focus')
      l.append(b)
      maxlen = max(len(name), maxlen)
    maxlen += 4  # because of '< ... >'
    self.buttons = GridFlowMore(l, maxlen, 3, 1, 'center')
    self.frame.footer = PileMore([
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
    overlay = OverlayMore(
      LineBoxMore(self._w),
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
          if urwid.util.is_mouse_event(k):
            event, button, col, row = k
            overlay.mouse_event(size, event, button, col, row, focus = True)
          else:
            if k == 'window resize':
              size = ui.get_cols_rows()
            k = self._w.keypress(size, k)
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
    buttons=(_(u'OK'), 1)):
    l = [urwid.Text(text)]
    body = ListBoxMore(urwid.SimpleListWalker(l))
    body = AttrWrapMore(body, 'body')
    Dialog2.__init__(self, header, height + 2, width + 2, body)
    if type(buttons) == list:
      self.add_buttons(buttons)
    else:
      self.add_buttons([buttons])
  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up', 'down', 'page down'):
      self.frame.set_focus('body')
      self._w.keypress(size, k)
      self.frame.set_focus('footer')

class InputDialog(Dialog2):
  """ Simple dialog with text and entry. """
  def __init__(self, text, height, width, ok_name=_(u'OK'), edit_text=''):
    self.edit = EditMore(wrap='clip', edit_text=edit_text)
    body = ListBoxMore(urwid.SimpleListWalker([self.edit]))
    body = AttrWrapMore(body, 'editbx', 'editfc')
    Dialog2.__init__(self, text, height, width, body)
    self.frame.set_focus('body')
    self.add_buttons([(ok_name, 0), (_(u'Cancel'), -1)])
  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up'):
      self.frame.set_focus('body')
    if k in ('down', 'page down'):
      self.frame.set_focus('footer')
    if k == 'enter':
      # pass enter to the "ok" button
      self.frame.set_focus('footer')
      self._w.keypress(size, k)
  def on_exit(self, exitcode):
    """ Handle dialog exit. """
    return exitcode, self.edit.get_edit_text()

class ClickCols(WidgetWrapMore):
  """ Clickable menubar. """
  def __init__(self, items, callback = None, keys = None):
    cols = ColumnsMore(items)
    self.__super.__init__(cols)
    self.callback = callback
    self.keys = keys

  def mouse_event(self, size, event, button, x, y, focus):
    if event == "mouse press":
      self.callback(self.keys) # possible keys

class OptCols(WidgetWrapMore):
  """ Htop-style menubar on the bottom of the screen. """
  # tuples = [((key1, key2, …), desc)], on_event gets passed a key
  # handler = function passed the key of the "button" pressed
  # attrs = (attr_key, attr_desc)
  # mentions of 'left' and right will be converted to <- and -> respectively
  def __init__(self, tuples, handler, attrs = ('body', 'infobar')):
    # Construct the texts
    textList = []
    # callbacks map the text contents to its assigned callback.
    self.callbacks = []
    for cmd in tuples:
      keys = cmd[0]
      if type(keys) != tuple:
        keys = (keys,)
      newKeys = {}
      for key in keys:
        newkey = reduce(lambda s, (f, t): s.replace(f, t), [
          (u'ctrl ', u'Ctrl+'),
          (u'meta ', u'Alt+'),
          (u'left', u'←'),
          (u'right', u'→'),
          (u'up', u'↑'),
          (u'down', u'↓'),
          (u'page up', u'Page Up'),
          (u'page down', u'Page Down'),
          (u'esc', u'ESC'),
          (u'enter', u'Enter')],
          key)
        if re.match(r"^[a-z]([0-9]*)$", newkey):
          newkey = newkey.upper()
        newKeys[key] = newkey
      desc = cmd[1]
      keyText = u" / ".join([newKeys[key] for key in keys]) + ":"
      col = ClickCols([('fixed', len(keyText) + 1, urwid.Text((attrs[0], keyText))), urwid.Text((attrs[1], desc))], handler, keys)
      textList.append(col)
    cols = ColumnsMore(textList)
    WidgetWrapMore.__init__(self, cols)

  def mouse_event(self, size, event, button, x, y, focus):
    """ Handle mouse events. """
    # Widgets are evenly long (as of current), so...
    return self._w.mouse_event(size, event, button, x, y, focus)
