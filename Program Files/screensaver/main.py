import os
from DVD import *
import pygame as pg  # Ensure this is present if not already imported in DVD
print("Original project made by hoangdesu at https://github.com/hoangdesu/Bouncing-DVD-logo-Pygame (Ctrl+ Left Click to open link).")

print("This project has been modifided for functionally")
def main():
    pg.init()
    
    # Set fullscreen mode using display info
    info = pg.display.Info()
    window = pg.display.set_mode((info.current_w, info.current_h), pg.FULLSCREEN)
    pg.display.set_caption("Pygame - Bouncing DVD logo")
    pg.mouse.set_visible(False)

    dvd = DVD(window)
    pg.display.set_icon(dvd.logo)
    
    # 1 for foreground color change (default), 2 for background color change
    option = 1
    if option == 2:
        dvd.logo = pg.transform.smoothscale(dvd.sprite, (dvd.width, dvd.height)) 
        dvd.color = (0, 0, 0, 0)
        
    clock = pg.time.Clock()
    
    running = True
    while running:
        for evt in pg.event.get():
            if evt.type == pg.QUIT or evt.type == pg.MOUSEBUTTONDOWN or evt.type == pg.KEYDOWN:
                running = False  # Exit on click or key press

        window.fill('#101010')
        
        dvd.update()
        dvd.render()
        
        clock.tick(60)
        pg.display.flip()

    pg.quit()  # Cleanly shut down Pygame when done

if __name__ == '__main__':
    main()
