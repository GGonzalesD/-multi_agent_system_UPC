
import pygame
import pygame.locals as lcs
from key_manager import KeyManager


class Widget:

    widgets = []

    def __init__(self, position, text, font:pygame.font.Font, fg, bg=None):
        self.text = text
        self.font = font

        self.fg = fg
        self.bg = bg

        self.img = font.render(self.text, True, self.fg)
        self.rect = self.img.get_rect()

        self.rect.center = position

        Widget.widgets.append(self)
    
    def update(self, surface, manager):
        self.loop(manager)
        self.draw(surface)

    def loop(self, manager):
        pass

    def draw(self, surface:pygame.Surface):
        if self.bg != None:
            pygame.draw.rect(surface, self.bg, self.rect)
        surface.blit(self.img, self.rect)

class Range(Widget):
    def __init__(self, position, w, s, font, fg, bg):
        super(Range, self).__init__(position, str(0), font, fg, bg)
        self.w = w
        self.s = s
        self.v = 0.5
        rect = self.rect.copy()
        rect.w = self.w
        rect.center = self.rect.center
        self.rect = rect
        self.img = self.font.render(str(int(self.v*self.s)), True, self.fg)


        self.hold = False
    
    def get_int(self):
        return int(self.get())

    def get(self):
        return self.v * self.s

    def loop(self, manager:KeyManager):
        xmouse, ymouse = pygame.mouse.get_pos()

        if self.rect.collidepoint(xmouse, ymouse) and manager.mouse_check(1):
            self.hold = True
        if manager.mouse_released(1):
            self.hold = False

        if self.hold:
            r = min(max(self.rect.left, xmouse), self.rect.right) - self.rect.left
            self.v = r / self.w
            self.img = self.font.render(str(int(self.v*self.s)), True, self.fg)


    def draw(self, surface:pygame.Surface):
        rect = self.rect.copy()
        rect.w = int(self.rect.w*self.v)
        pygame.draw.rect(surface, self.bg, rect)
        imgr = self.img.get_rect()
        imgr.center = self.rect.center
        surface.blit(self.img, imgr)
        pygame.draw.rect(surface, self.fg, self.rect, 1)

class Button(Widget):
    def __init__(self, position, text, font, fg, bg, command=None, args=[]):
        super(Button, self).__init__(position, text, font, fg, bg)
        self.command = command
        self.args = args
        self.hover = False
    
    def loop(self, manager:KeyManager):
        xmouse, ymouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(xmouse, ymouse):
            self.hover = True
            if self.command != None and manager.mouse_check(1):
                self.command(*self.args)
        else:
            self.hover = False

    def draw(self, surface:pygame.Surface):
        if self.hover:
            rect = self.rect.copy()
            rect.w += 4
            rect.h += 4
            rect.center = self.rect.center
            pygame.draw.rect(surface, self.fg, rect)
        
        super(Button, self).draw(surface)


if __name__ == "__main__":

    pygame.init()
    pygame.font.init()


    c_white = pygame.Color(255, 255, 255)
    c_gray = pygame.Color(40, 40, 40)

    font = pygame.font.SysFont("Fira code", 40)

    win = pygame.display.set_mode((640, 480))

    key_manager = KeyManager()

    btn_ok = Button((200, 300), "Poggers", font, c_white, c_gray, print, ["Hola mundo"])

    ranger = Range((200, 200), 300, 100, font, c_white, c_gray)

    while True:
        win.fill((0, 0, 0))

        key_manager.update_manager(pygame.event.get())

        btn_ok.update(win, key_manager)

        ranger.update(win, key_manager)

        pygame.display.update()
