import sys
import pygame
import pygame_gui

# Program entry point
def main():
    # Initialize pygame safely
    try:
        pygame.init()
    except Exception as e:
        print("Failed to initialize pygame:", e)
        sys.exit(1)

    # Window setup
    width, height = 900, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pygame Paint with UI")

    clock = pygame.time.Clock()

    # UI Manager
    manager = pygame_gui.UIManager((width, height))

    # UI Components
    color_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 10, 120, 30),
        text="Brush Color:",
        manager=manager
    )

    # Color buttons
    colors = {
        "Black": (0, 0, 0),
        "Red": (255, 0, 0),
        "Green": (0, 200, 0),
        "Blue": (0, 0, 255),
        "Yellow": (255, 255, 0)
    }

    color_buttons = []
    x_offset = 10
    for name in colors:
        btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x_offset, 50, 80, 30),
            text=name,
            manager=manager
        )
        color_buttons.append(btn)
        x_offset += 90

    # Brush size slider
    size_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect(10, 100, 200, 30),
        start_value=5,
        value_range=(1, 50),
        manager=manager
    )

    size_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(220, 100, 120, 30),
        text="Brush Size: 5",
        manager=manager
    )

    # Clear button
    clear_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(10, 150, 100, 30),
        text="Clear",
        manager=manager
    )

    # Canvas surface
    canvas = pygame.Surface((width, height))
    canvas.fill((255, 255, 255))  # Start white

    current_color = (0, 0, 0)
    brush_size = 5
    drawing = False

    # Main loop
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            # Quit handler
            if event.type == pygame.QUIT:
                running = False

            # Start drawing
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    drawing = True

            # Stop drawing
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False

            # UI Event Handling
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # Color button pressed
                    for btn in color_buttons:
                        if event.ui_element == btn:
                            name = btn.text
                            current_color = colors.get(name, (0, 0, 0))

                    # Clear button
                    if event.ui_element == clear_button:
                        canvas.fill((255, 255, 255))

                # Slider changed
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == size_slider:
                        brush_size = int(size_slider.get_current_value())
                        size_label.set_text(f"Brush Size: {brush_size}")

            # Pass event to UI manager
            manager.process_events(event)

        # Drawing action
        if drawing:
            try:
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.circle(canvas, current_color, mouse_pos, brush_size)
            except Exception:
                # Fail-safe to prevent crash from invalid mouse state
                pass

        # GUI update
        manager.update(time_delta)

        # Render
        screen.blit(canvas, (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
