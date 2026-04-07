<!-- Copyright (c) 2026 Yuri Tijerino. All rights reserved. -->
<!-- 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有. -->
<!-- Unauthorized copying, modification, or distribution of this file is prohibited. -->
<!-- 本ファイルの無断複製、改変、配布を禁じます。 -->

# WP-200 Weekly Curriculum

## Phase 1: HTML & CSS Foundations

### Session 1: Course Overview & HTML Basics
- What is the web? How browsers work
- HTML document structure: html, head, body
- Basic tags: h1-h6, p, a, img, ul/ol
- VS Code installation and setup
- Browser developer tools (F12)
- Concepts: Document structure, tags and elements, attributes, file paths

### Session 2: Semantic HTML5 & Multi-page Website
- Semantic elements: header, nav, section, article, footer
- Creating multiple HTML pages
- Linking pages with anchor tags
- File and folder organization
- MySite template introduction
- **Assignment 1:** Create MySite with About Me, Hobbies, and Job pages
- Self-study reference: W3Schools HTML Tutorial

### Session 3: CSS3 Fundamentals & Styling
- CSS syntax: selectors, properties, values
- Element, class, and id selectors
- Colors, fonts, text styling
- Box model: margin, border, padding, content
- Introduction to Flexbox
- External stylesheets with link tag
- **Assignment 2:** Style MySite with external CSS

## Phase 2: Procedural JavaScript - Breakout Game
Based on MDN 2D Breakout Game Tutorial: https://developer.mozilla.org/en-US/docs/Games/Tutorials/2D_Breakout_game_pure_JavaScript

### Session 4: Canvas & Drawing (MDN Lesson 1)
- The canvas HTML element
- Getting the 2D rendering context: canvas.getContext("2d")
- Canvas coordinate system (x, y)
- Drawing shapes: rect(), arc(), beginPath(), fill()
- Colors with fillStyle
- Programming concepts: Variables (let, const), data types (numbers, strings)
- **Assignment 3:** Draw a ball and rectangle on canvas

### Session 5: Animation & Game Loop (MDN Lesson 2)
- Animation with setInterval()
- Clearing the canvas: clearRect()
- Position variables (x, y) and velocity variables (dx, dy)
- The clear-update-draw pattern
- Programming concepts: Functions (defining, calling, parameters)
- **Assignment 4:** Make the ball move across the screen

### Session 6: Collision Detection & Conditionals (MDN Lesson 3)
- Boundary/edge detection against canvas walls
- Velocity reversal: dx = -dx, dy = -dy
- Accounting for ball radius in collision math
- Programming concepts: if/else statements, comparison operators (<, >, <=, >=), logical operators (&&, ||)

### Session 7: Paddle & User Input (MDN Lessons 4, 5, 9)
- Event listeners: keydown, keyup, mousemove
- event.key for identifying pressed keys
- Boolean flags for tracking continuous input
- Drawing and moving the paddle
- Game over condition (ball misses paddle)
- Programming concepts: Events, addEventListener(), boolean data type, callback functions
- **Assignment 5:** Paddle with keyboard/mouse control and game over

### Session 8: Brick Field - Arrays & Loops (MDN Lessons 6 & 7)
- 2D arrays for brick grid representation
- Nested for loops for grid creation
- Object literals: {x, y, status}
- Grid positioning math (column * (width + padding) + offset)
- AABB collision detection for ball-brick interaction
- Destroying bricks by toggling status property
- Programming concepts: Arrays (1D, 2D), for loops, object literals
- **Assignment 6:** Build brick field with collision detection

### Session 9: Score, Lives & Game Completion (MDN Lessons 8 & 10)
- Canvas text rendering: ctx.font, ctx.fillText()
- Score counter incremented on brick collision
- Win condition: score equals total brick count
- Lives system: decrement on miss, reset position
- requestAnimationFrame() vs setInterval()
- Programming concepts: State management, string concatenation, requestAnimationFrame
- **Assignment 7:** Complete Breakout game with score, lives, win/lose

## Phase 3: Object-Oriented JavaScript

### Session 10: Introduction to OOP - Ball Class
- Why OOP? Code organization and reusability
- Class syntax: class Ball {}
- Constructor: constructor(canvas, radius)
- The this keyword
- Methods: draw(), move(), reset()
- Creating Ball.js as external file
- Instantiation with new keyword
- Programming concepts: Classes, constructors, this, methods vs functions
- **Assignment 8:** Refactor ball into Ball class

### Session 11: Paddle & Brick Classes
- Paddle class with moveLeft(), moveRight(), moveTo() methods
- Brick class with destroy(), isAlive() methods
- BrickGrid class (composition - contains Brick objects)
- Single responsibility principle
- Encapsulation: data + behavior together
- Programming concepts: Multiple classes, encapsulation, composition

### Session 12: Game Class & Modularization
- Game class to orchestrate the entire game
- Splitting code into external files: Ball.js, Paddle.js, Brick.js, Game.js
- Script loading order with <script src="...">
- Separation of concerns
- Programming concepts: Orchestrator pattern, modularization
- **Assignment 9:** Complete OOP refactor with separate files

### Session 13: Enhancements - Audio, Storage & Customization
- HTML5 Audio API: sound effects and background music
- localStorage for persistent settings
- Customization features: colors, audio
- Settings page
- Programming concepts: Browser APIs, persistent storage, user preferences

## Phase 4: Presentation & Review

### Session 14: Final Project Presentation
- Student game presentations with live demos
- Code walkthrough and explanation
- Peer feedback
- **Final Assignment:** Present enhanced Breakout game

### Session 15: Course Review & Reflection
- Course review: from zero to OOP game development
- Skills reflection
- Next steps for continued learning
