import pygame, sys
import pygame.locals as lcs

class KeyManager:
    def __init__(self):
        self.keys = {}
        self.buttons = {}

    def update(self):
        for i in list(self.keys.keys()):
            if self.keys[i] == -1:
                self.keys.pop(i)
        for i in list(self.buttons.keys()):
            if self.buttons[i] == -1:
                self.buttons.pop(i)
        

        for i in self.keys:
            self.keys[i] += 1
        for i in self.buttons:
            self.buttons[i] += 1
        
        
    
    def exit(self):
        pygame.quit()
        sys.exit()
    
    def update_manager(self, events, kill=True):
        self.update()
        for event in events:
            self.update_event(event)
            if kill:
                if event.type == lcs.QUIT:
                    self.exit()
        

    def update_event(self, event:pygame.event.Event):
        if event.type == lcs.KEYDOWN:
            if not event.key in self.keys:
                self.keys[event.key] = 0
        if event.type == lcs.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = -1
        if event.type == lcs.MOUSEBUTTONDOWN:
            if not event.button in self.buttons:
                self.buttons[event.button] = 0
        if event.type == lcs.MOUSEBUTTONUP:
            if event.button in self.buttons:
                self.buttons[event.button] = -1

    def mouse_press(self, button):
        return button in self.buttons and self.buttons[button] >= 0
    def mouse_check(self, button):
        return button in self.buttons and self.buttons[button] == 0
    def mouse_released(self, button):
        return button in self.buttons and self.buttons[button] == -1

    def keys_press(self, *keys):
        for key in keys:
            if self.key_press(key):
                return True
        return False

    def key_press(self, key):
        return key in self.keys and self.keys[key] >= 0
    def key_check(self, key):
        return key in self.keys and self.keys[key] == 0
    def key_released(self, key):
        return key in self.keys and self.keys[key] == -1