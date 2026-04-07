<!-- Copyright (c) 2026 Yuri Tijerino. All rights reserved. -->
<!-- 著作権 (c) 2026 ティヘリノ ユリ. 全著作権所有. -->
<!-- Unauthorized copying, modification, or distribution of this file is prohibited. -->
<!-- 本ファイルの無断複製、改変、配布を禁じます。 -->

# Programming Concepts Reference for WP-200

## Session 4: Variables and Data Types
- **let** - declares a variable that can be reassigned: `let x = 100;`
- **const** - declares a constant that cannot be reassigned: `const RADIUS = 10;`
- **Numbers** - integers and decimals: `let score = 0; let speed = 2.5;`
- **Strings** - text in quotes: `let name = "Player 1";`
- Variables store values that your program can use and change

## Session 5: Functions
- A function is a reusable block of code: `function draw() { ... }`
- Functions can take parameters: `function drawCircle(x, y, radius) { ... }`
- Call a function by name: `draw();` or `drawCircle(100, 200, 10);`
- Functions help organize code and avoid repetition

## Session 6: Conditionals
- **if statement** - run code only when a condition is true:
  ```javascript
  if (x + dx > canvas.width) {
      dx = -dx;  // reverse direction
  }
  ```
- **if/else** - two paths:
  ```javascript
  if (score === totalBricks) {
      alert("YOU WIN!");
  } else {
      // keep playing
  }
  ```
- **Comparison operators:** `<`, `>`, `<=`, `>=`, `===`, `!==`
- **Logical operators:** `&&` (AND), `||` (OR), `!` (NOT)

## Session 7: Events
- Events are things that happen in the browser (key press, mouse move, click)
- **addEventListener** attaches a function to an event:
  ```javascript
  document.addEventListener("keydown", function(e) {
      if (e.key === "ArrowRight") {
          rightPressed = true;
      }
  });
  ```
- Common events: keydown, keyup, mousemove, click
- **Boolean flags** track state: `let rightPressed = false;`

## Session 8: Arrays and Loops
- **Array** - ordered list of values: `let colors = ["red", "blue", "green"];`
- Access by index (starts at 0): `colors[0]` is "red"
- **2D Array** - array of arrays (grid):
  ```javascript
  let bricks = [];
  for (let c = 0; c < columns; c++) {
      bricks[c] = [];
      for (let r = 0; r < rows; r++) {
          bricks[c][r] = { x: 0, y: 0, status: 1 };
      }
  }
  ```
- **for loop** - repeat code a set number of times:
  ```javascript
  for (let i = 0; i < 5; i++) {
      console.log(i);  // prints 0, 1, 2, 3, 4
  }
  ```
- **Object literal** - group related data: `{ x: 10, y: 20, status: 1 }`

## Session 9: State Management
- Game state = all the variables that describe the current game situation
- **Score** - counter variable: `let score = 0; score++;`
- **Lives** - countdown: `let lives = 3; lives--;`
- **Win condition** - check if all bricks destroyed
- **requestAnimationFrame()** - better than setInterval for animations:
  ```javascript
  function draw() {
      // ... game logic ...
      requestAnimationFrame(draw);
  }
  draw();  // start the loop
  ```

## Session 10: Classes and OOP
- **Class** - blueprint for creating objects:
  ```javascript
  class Ball {
      constructor(canvas, radius = 10) {
          this.canvas = canvas;
          this.x = canvas.width / 2;
          this.y = canvas.height - 30;
          this.radius = radius;
          this.dx = 2;
          this.dy = -2;
      }

      draw(ctx) {
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
          ctx.fillStyle = "#0095DD";
          ctx.fill();
          ctx.closePath();
      }

      move() {
          this.x += this.dx;
          this.y += this.dy;
      }
  }
  ```
- **this** keyword refers to the current object instance
- **new** creates an instance: `const ball = new Ball(canvas);`
- **Methods** are functions that belong to a class

## Session 11: Encapsulation and Composition
- **Encapsulation** - keeping data and behavior together in a class
- **Composition** - objects containing other objects:
  ```javascript
  class BrickGrid {
      constructor() {
          this.bricks = [];  // contains Brick objects
      }
  }
  ```
- **Single Responsibility** - each class does one thing well

## Session 12: Modularization
- Split code into separate files: Ball.js, Paddle.js, Brick.js, Game.js
- Load files in correct order with script tags:
  ```html
  <script src="Ball.js"></script>
  <script src="Paddle.js"></script>
  <script src="Brick.js"></script>
  <script src="Game.js"></script>
  ```
- **Separation of concerns** - each file handles one aspect

## Session 13: Browser APIs
- **Audio API** - play sounds: `const audio = new Audio("bounce.mp3"); audio.play();`
- **localStorage** - save data in browser permanently:
  ```javascript
  localStorage.setItem("highScore", score);
  let saved = localStorage.getItem("highScore");
  ```
