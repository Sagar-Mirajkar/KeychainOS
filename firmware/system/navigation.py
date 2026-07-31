"""Small navigation stack."""
class Navigation:
 def __init__(self): self.stack=[{"screen":"home","selection":0}]
 def current(self): return self.stack[-1]
 def push(self,screen,**state):
  item={"screen":screen,"selection":0}; item.update(state); self.stack.append(item); return item
 def back(self):
  if len(self.stack)>1: self.stack.pop()
  return self.current()
 def home(self): self.stack=self.stack[:1]; return self.current()
