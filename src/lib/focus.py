#!/usr/bin/env python
# coding=utf-8

import sys

class Widget(object):
  def keypress(self, key):
    print "W", key
    return key
  def _emit(self, signal):
    print "emit", signal, "from", self

class Edit(Widget):
  def keypress(self, key):
    print "E", key
    key = super(Edit, self).keypress(key)
    if key in ('DOWN', 'UP'):
      return key
    # manage key in the widget
    return

class FocusEventWidget(Widget):
  def _can_gain_focus(self):
    return True
  def _can_loose_focus(self):
    return True
  def gain_focus(self):
    print "gain focus", self
    ret = self._can_gain_focus()
    if ret:
      self._emit('focusgain')
    return ret
  def loose_focus(self):
    print "loose focus", self
    ret = self._can_loose_focus()
    if ret:
      self._emit('focuslost')
    return ret

class EditMore(Edit, FocusEventWidget):
  pass

class EditMoreRefuseFocusLost(EditMore):
  def _can_loose_focus(self):
    print "→ deny focus lost", self
    return False


class Pile(Widget):
  def __init__(self, list):
    self._list = list
    self._current = 0
  def keypress(self, key):
    print "Pile", key
    if hasattr(self._list[self._current], "keypress"):
      key = self._list[self._current].keypress(key)
    if not key or key not in ('DOWN', 'UP'):
      return key
    if key == 'UP' and self._current > 0 or key == 'DOWN' and self._current < len(self._list) - 1:
      if key == 'UP':
        offset = -1
      else: # 'DOWN'
        offset = +1
      self._current += offset
    else:
      return key
  def get_current(self):
    return self._current

class PileMore(Pile, FocusEventWidget):
  def __init__(self, list):
    super(PileMore, self).__init__(list)
  def keypress(self, key):
    """ Reimplementation """
    if hasattr(self._list[self._current], "keypress"):
      key = self._list[self._current].keypress(key)
    if not key or key not in ('DOWN', 'UP'):
      return key
    if key == 'UP' and self._current > 0 or key == 'DOWN' and self._current < len(self._list) - 1:
      ok = True
      if isinstance(self._list[self._current], FocusEventWidget):
        ok = self._list[self._current].loose_focus()
      if not ok:
        print "* focus lost refused"
        return
      if key == 'UP':
        offset = -1
      else: # 'DOWN'
        offset = +1
      if isinstance(self._list[self._current + offset], FocusEventWidget):
        ok = self._list[self._current + offset].gain_focus()
      if not ok:
        print "* focus gain refused"
        return
      self._current += offset
    else:
      return key
  def gain_focus(self):
    print "pile gain focus", self
    if isinstance(self._list[self._current], FocusEventWidget):
      return self._list[self._current].gain_focus()
    else:
      return super(PileMore, self).gain_focus()
  def loose_focus(self):
    print "pile loose focus", self
    if isinstance(self._list[self._current], FocusEventWidget):
      return self._list[self._current].loose_focus()
    else:
      return super(PileMore, self).loose_focus()



print "\n\n** p **"
p = PileMore([EditMore(), EditMore()])
p.gain_focus()
print p.get_current()
print '\nUP'
p.keypress('UP')
print p.get_current()
print '\nDOWN'
p.keypress('DOWN')
print p.get_current()
print '\nDOWN'
p.keypress('DOWN')
print p.get_current()

print "\n\n** p2/p3 **"
p3 = PileMore([EditMore(), EditMoreRefuseFocusLost()])
p2 = PileMore([Edit(), EditMore(), p3])
p2.gain_focus()
print p2.get_current()
print p3.get_current()
print '\nUP'
p2.keypress('UP')
print p2.get_current()
print p3.get_current()
print '\nDOWN'
p2.keypress('DOWN')
print p2.get_current()
print p3.get_current()
print '\nA'
p2.keypress('A')
print p2.get_current()
print p3.get_current()
print '\nDOWN'
p2.keypress('DOWN')
print p2.get_current()
print p3.get_current()
print '\nUP'
p2.keypress('UP')
print p2.get_current()
print p3.get_current()
print '\nDOWN'
p2.keypress('DOWN')
print p2.get_current()
print p3.get_current()
print '\nDOWN'
p2.keypress('DOWN')
print p2.get_current()
print p3.get_current()
print '\nUP'
p2.keypress('UP')
print p2.get_current()
print p3.get_current()
