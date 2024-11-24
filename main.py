import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Updated Screen dimensions
WIDTH, HEIGHT = 1500, 700  # Adjusted screen size
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Inside Circle")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Default Circle parameters
circle_center = (WIDTH // 4, HEIGHT // 2)
circle_radius = 200  # Small circle where the balls bounce inside
delete_circle_radius = 250  # Larger circle where balls disappear

# Default Ball parameters
ball_radius = 12
gravity = 0.5
velocity_threshold = 0.1  # Threshold to detect when the ball stops bouncing

# Clock for controlling frame rate
clock = pygame.time.Clock()

# List of balls
balls = []

# Game state
in_menu = False

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

    def update(self):
        # Apply gravity
        self.vy += gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Calculate distance to circle center
        dist_to_center = math.sqrt((self.x - circle_center[0]) ** 2 + (self.y - circle_center[1]) ** 2)

        # Check if the ball is outside the larger circle and delete it if so
        if dist_to_center + ball_radius > delete_circle_radius:
            return True  # Ball is outside the larger circle, remove it

        # Check for bounce within the smaller circle boundary
        if dist_to_center + ball_radius > circle_radius:
            # Calculate the overlap amount to push the ball back inside
            overlap = (dist_to_center + ball_radius) - circle_radius

            # Push the ball back inside the circle
            self.x -= (self.x - circle_center[0]) / dist_to_center * overlap
            self.y -= (self.y - circle_center[1]) / dist_to_center * overlap

            # Calculate the normal vector at the point of collision
            normal_x = (self.x - circle_center[0]) / dist_to_center
            normal_y = (self.y - circle_center[1]) / dist_to_center

            # Reflect velocity to simulate bounce
            dot_product = self.vx * normal_x + self.vy * normal_y
            self.vx -= 2 * dot_product * normal_x
            self.vy -= 2 * dot_product * normal_y

        # Check if ball hits the ground (bottom of the screen)
        if self.y + ball_radius >= HEIGHT:
            if abs(self.vy) < velocity_threshold:
                self.vy = 0  # Stop falling if the velocity is too low
            else:
                self.vy *= -0.8  # Apply bounce with some damping

        return False

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), ball_radius)


def get_random_point_in_circle(center, radius):
    while True:
        # Generate random coordinates
        x = random.uniform(-radius, radius)
        y = random.uniform(-radius, radius)
        if x**2 + y**2 <= radius**2:  # Check if the point is inside the circle
            return center[0] + x, center[1] + y


def draw_text(text, x, y, color, font_size=30):
    try:
        # Load the ADLaM Display font (make sure the font file is in the correct path)
        font = pygame.font.Font("ADLaM_Display.ttf", font_size)  # Make sure this points to the correct file
    except FileNotFoundError:
        # If the font is not found, fall back to a default font (Arial or similar)
        font = pygame.font.Font(None, font_size)
    
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_slider(x, y, width, value, min_value, max_value):
    # Increase the size of the slider track and knob
    slider_height = 15  # Increase slider track height
    knob_size = 15  # Increase knob size for easier clicking

    # Draw the slider track (larger track size for better hitbox)
    pygame.draw.rect(screen, (50, 50, 50), (x, y, width, slider_height))  # Darker background track
    pygame.draw.rect(screen, (100, 100, 255), (x, y, width * value, slider_height))  # Blue progress bar

    # Draw the slider knob (larger knob size)
    pygame.draw.circle(screen, GREEN, (x + int(value * width), y + slider_height // 2), knob_size)

    # Return the slider rectangle for hitbox detection
    return pygame.Rect(x, y, width, slider_height)


# Main loop
running = True
dragging_slider = None  # Keeps track of which slider is being dragged

# Store the hitboxes of sliders
ball_size_slider = None
circle_size_slider = None
delete_circle_slider = None

while running:
    screen.fill(BLACK)

    # Draw the smaller circle (where balls bounce inside)
    pygame.draw.circle(screen, WHITE, circle_center, circle_radius, 2)

    # Draw the larger circle (where balls disappear if they go outside)
    pygame.draw.circle(screen, (100, 100, 100), circle_center, delete_circle_radius, 2)

    # Draw the menu on the right side of the screen
    menu_x = WIDTH - 300  # Menu starts at the right side, leaving space for the simulation
    pygame.draw.rect(screen, GRAY, (menu_x, 0, 300, HEIGHT))  # Draw the menu background

    # Draw Menu Text
    draw_text("Settings", menu_x + 50, 20, WHITE, 50)

    # Add spacing between each setting
    text_y = 100
    slider_y = text_y + 40
    spacing = 50  # Spacing between text and sliders

    draw_text(f"Ball Size: {ball_radius}", menu_x + 20, text_y, WHITE)
    ball_size_slider = draw_slider(menu_x + 20, slider_y, 260, ball_radius / 60, 0, 60)

    text_y += spacing
    slider_y += spacing
    draw_text(f"Bounce Circle Size: {circle_radius}", menu_x + 20, text_y, WHITE)
    circle_size_slider = draw_slider(menu_x + 20, slider_y, 260, circle_radius / 600, 0, 1)

    text_y += spacing
    slider_y += spacing
    draw_text(f"Delete Circle Size: {delete_circle_radius}", menu_x + 20, text_y, WHITE)
    delete_circle_slider = draw_slider(menu_x + 20, slider_y, 260, delete_circle_radius / 700, 0, 1)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.pos[0] < menu_x:  # Spawn a ball in the left part of the screen
                # Spawn a new ball at a random position inside the small circle
                random_x, random_y = get_random_point_in_circle(circle_center, circle_radius)
                balls.append(Ball(random_x, random_y))

            # Check if the mouse is over a slider and start dragging if so
            if ball_size_slider.collidepoint(event.pos):
                dragging_slider = "ball_size"
            elif circle_size_slider.collidepoint(event.pos):
                dragging_slider = "circle_size"
            elif delete_circle_slider.collidepoint(event.pos):
                dragging_slider = "delete_circle"

        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging when mouse button is released
            dragging_slider = None

        elif event.type == pygame.MOUSEMOTION:
            # Update slider values while dragging
            if dragging_slider == "ball_size" and ball_size_slider.collidepoint(event.pos):
                ball_radius = max(1, min(60, int((event.pos[0] - menu_x - 20) / 260 * 60)))
            elif dragging_slider == "circle_size" and circle_size_slider.collidepoint(event.pos):
                circle_radius = max(50, min(600, int((event.pos[0] - menu_x - 20) / 260 * 600)))
            elif dragging_slider == "delete_circle" and delete_circle_slider.collidepoint(event.pos):
                delete_circle_radius = max(50, min(700, int((event.pos[0] - menu_x - 20) / 260 * 700)))

        # Check for "R" key to remove all balls
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                balls.clear()

    # Update balls
    balls = [ball for ball in balls if not ball.update()]  # Remove balls outside the delete circle
    for ball in balls:
        ball.draw()

    # Update the screen
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
