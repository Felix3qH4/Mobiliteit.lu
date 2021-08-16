import pygame as pg
import math

run : bool = True

pg.init()
pg.font.init()


WINDOW_W : int = 1600
WINDOW_H : int = 1000


fps : int = 60
clock = pg.time.Clock()
drag_allowed : bool = False
zoom : float = 1

GREEN : tuple = (220, 230, 190)
window = pg.display.set_mode((WINDOW_W, WINDOW_H))
pg.display.set_caption("Live Bus Map")



map_path : str = r"C:\Users\Felix\Documents\Python\Mobiliteit\map\images\map.png"
map_img = pg.image.load(map_path)
map_rect = map_img.get_rect()

map_image = pg.transform.scale(map_img, (int(map_img.get_width() * zoom), int(map_img.get_width() * zoom)))
map_rectangle = map_image.get_rect()
map_rectangle.center = (int(WINDOW_W/2), int(WINDOW_H/2))


stations : dict = {"Capellen Police" : (133, 500),
            "Capellen Klouschter" : (100, 550),
            "Windhof" : (1050, 720),
            "Windhof Ecoparc" : (1030, 703)
            }
stations_points : list = list(stations.values())

bus_colors : list = [pg.Color("green"), pg.Color("yellow"), pg.Color("orange"), pg.Color("red")]

class Bus():
    def __init__(self, number, start, end, screen):
        self.screen = screen
        self.number : int = number # Bus line number
        self.start : str = start
        self.end : str = end
        self.state : int = 0  # Different states = how late is the bus; 0 = on time, 1 = a bit late, 2 = late, 3 = very late
        self.station : str = "" # Gives the station at which the bus is
        self.pos : tuple = (100, 100) # Actual position of the bus with x and y coordinates

    def move_to(self):
        pass

    def draw(self):
        pg.draw.rect(self.screen, bus_colors[self.state], (self.pos[0], self.pos[1], 10, 10))




def draw_stations(screen):
    #for x, y in stations.values():
    for x, y in stations_points:
        pg.draw.rect(screen, (117, 94, 189), (x, y, int(10 * zoom), int(10 * zoom)))

    pg.display.update()


font =pg.font.SysFont(None, 24)
center_map_text = font.render('Center Map', True, pg.Color("red"))
center_map_rect = center_map_text.get_rect(x=20, y=20)
center_map_box = pg.draw.rect(window, pg.Color("red"), (center_map_rect.x - 5, center_map_rect.y-5, 100, 25), 3)

bus_one = Bus(2, "Capellen Police", "Capellen Klouschter", window)
done = True


while run == True:
    clock.tick(fps)

    window.fill(GREEN)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            run = False
        
        if event.type == pg.MOUSEBUTTONDOWN:
            mousex, mousey = pg.mouse.get_pos()
            mouserect = pg.Rect(mousex, mousey, 1, 1)
            print(mousex, mousey)
            drag_allowed = not drag_allowed

            if center_map_box.colliderect(mouserect):
                map_rectangle.center = map_rect.center = (int(WINDOW_W/2), int(WINDOW_H/2))
                done = True

            if event.button == 4:
                mouse = pg.mouse.get_pos()
                if (zoom + 0.1) <= 2.5:
                    zoom += 0.1
                    print(f"IMAGE ORIGINAL SIZE: {map_img.get_width(), map_img.get_height()}")
                    
                    img = pg.transform.scale(map_img, (int(map_img.get_width() * zoom), int(map_img.get_height() * zoom)))
                    rect = img.get_rect()
                    print(f"IMAGE SIZE AFTER: {img.get_width(), img.get_height()}")
                    
                    
                    rect.centerx = int((map_rectangle.centerx / map_img.get_width()) * img.get_width())
                    rect.centery = int((map_rectangle.centery / map_img.get_height()) * img.get_height())
                    print(f"RECT CENTER IN: {rect.centerx, rect.centery}")
                    

                    
                    map_image, map_rectangle = img, rect
                print(zoom)
                done = True

            if event.button == 5:
                ## If Mousewheel turned backwards try to zoom out except if reached maximum zoom out
                if (zoom - 0.1) >= 0.1:
                    zoom -= 0.1
                    ## New image with the new width and height adapted to the zoom
                    img = pg.transform.scale(map_img, (int(map_img.get_width() * zoom), int(map_img.get_height() * zoom)))
                    rect = img.get_rect()
                    ## The new center x coordinate of the map = (old center x coordinate of the map / old width of the map) * new width of the map
                    ## Example: old center x = 500, old width = 1000, new width = 1300
                    ##          new center x = (500 / 1000) * 1300 = 0.5 * 1300 = 650
                    ## So the old center was at x = 500 and the new at x = 650
                    rect.centerx = int((map_rectangle.centerx / map_img.get_width()) * img.get_width())
                    rect.centery = int((map_rectangle.centery / map_img.get_height()) * img.get_height())
                    print(f"RECT CENTER OUT: {rect.centerx, rect.centery}")
                    

                    map_image, map_rectangle = img, rect
                print(zoom)
                done = True

        if event.type == pg.MOUSEBUTTONUP:
            drag_allowed = False

        if event.type == pg.MOUSEMOTION and drag_allowed:
            ## Follow the mouse cursor with the map
            map_rect.move_ip(event.rel)
            map_rectangle.move_ip(event.rel)

            index : int = 0
            ## Update all the positions of the stations
            for x, y in stations_points:
                x += event.rel[0]
                y += event.rel[1]
                stations_points[int(index)] = (x, y)

                index += 1
            done = True
        


        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                run = False
            if event.key == pg.K_c:
                map_rectangle.center = map_rect.center = (int(WINDOW_W/2), int(WINDOW_H/2))
                done = True

    if done:
        window.blit(map_image, map_rectangle)
        
        draw_stations(window)
        bus_one.draw()
        pg.draw.rect(window, pg.Color("grey"), (center_map_rect.x - 5, center_map_rect.y-5, 100, 25), 0)
        pg.draw.rect(window, pg.Color("black"), (center_map_rect.x - 5, center_map_rect.y-5, 100, 25), 2)
        window.blit(center_map_text, center_map_rect)
        pg.display.update()
        done = False
    

pg.quit()