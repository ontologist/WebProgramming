<!-- Copyright (c) 2026 Yuri Tijerino. All rights reserved. -->
<!-- Unauthorized copying, modification, or distribution of this file is prohibited. -->

# WP-200 Assignment Descriptions

## Assignment 1: MySite HTML Pages (Session 2)
Create a personal website with three pages:
- **aboutme.htm** - Your self-introduction (name, hobbies, background)
- **hobbies.htm** - Your hobbies and interests with images
- **job.htm** - Your dream job or career aspirations

Requirements:
- Use semantic HTML5 tags (header, nav, section, article, footer)
- Navigation menu linking all three pages
- At least one image per page
- Proper HTML document structure (DOCTYPE, html, head, body)
- Use heading tags (h1, h2) appropriately

## Assignment 2: CSS Styling (Session 3)
Style your MySite with a consistent visual design:
- Create an external CSS file (style.css) linked to all pages
- Use at least 3 different selector types (element, class, id)
- Apply box model properties (margin, padding, border)
- Set consistent colors and fonts across all pages
- Use Flexbox for at least one layout section

## Assignment 3: Canvas Drawing (Session 4)
Create a new page (game.htm) with a canvas element:
- Add a <canvas> element (480x320 pixels)
- Get the 2D drawing context
- Draw a circle (ball) using arc() and fill()
- Draw a rectangle using rect() or fillRect()
- Use variables (let/const) for x, y positions and radius/size
- Use fillStyle to set different colors

## Assignment 4: Ball Animation (Session 5)
Make the ball move on the canvas:
- Create a draw() function that contains all drawing logic
- Use setInterval() to call draw() repeatedly (every 10ms)
- Clear the canvas each frame with clearRect()
- Create dx and dy velocity variables
- Update ball position each frame: x += dx, y += dy
- The ball should move diagonally across the screen

## Assignment 5: Paddle & Input (Session 7)
Add a paddle controlled by the player:
- Draw a paddle (rectangle) at the bottom of the canvas
- Add keydown and keyup event listeners for arrow keys
- Use boolean flags (rightPressed, leftPressed) for smooth movement
- Add mousemove event listener for mouse control
- Keep paddle within canvas boundaries
- Implement game over when ball passes below paddle
- Reset game with location.reload()

## Assignment 6: Brick Field (Session 8)
Build a field of bricks:
- Create a 2D array to store brick objects: {x, y, status}
- Use nested for loops to initialize brick positions
- Draw all bricks with status === 1
- Implement AABB collision detection between ball and bricks
- Set brick status to 0 when hit (brick disappears)
- Reverse ball dy on brick collision
- At least 3 rows and 5 columns of bricks

## Assignment 7: Complete Breakout Game (Session 9)
Finish the game with score, lives, and win condition:
- Display score using fillText() (top-left corner)
- Increment score on each brick destroyed
- Display lives count (top-right corner, start with 3)
- Decrease lives when ball misses paddle
- Reset ball and paddle position on life lost
- Win condition: alert("YOU WIN!") when all bricks destroyed
- Game over: alert("GAME OVER") when lives reach 0
- Replace setInterval with requestAnimationFrame (bonus)

## Assignment 8: Ball Class - OOP (Session 10)
Refactor the ball into a class:
- Create a Ball class in Ball.js
- Constructor takes canvas and optional radius parameter
- Properties: x, y, dx, dy, radius, canvas
- draw(ctx) method: draws the ball on canvas
- move() method: updates x and y by dx and dy
- reset() method: returns ball to starting position
- Import Ball.js with <script src="Ball.js">
- Create ball instance: const ball = new Ball(canvas)
- Game must still work correctly with the class

## Assignment 9: Full OOP Refactor (Session 12)
Refactor the entire game into classes:
- **Ball.js** - Ball class (from Assignment 8)
- **Paddle.js** - Paddle class with draw(), moveLeft(), moveRight(), moveTo(), reset()
- **Brick.js** - Brick class with draw(), destroy(), isAlive() AND BrickGrid class
- **Game.js** - Game class that orchestrates everything: constructor, startGame(), draw(), handleCollisions(), handleInput(), gameOver(), winGame()
- **game.htm** - HTML file that creates Game instance and starts it
- All classes in separate .js files loaded via script tags
- Game must be fully playable
