// WP-200 Internationalization (i18n) System
// Supported languages: English, Japanese, Chinese, Korean, Spanish

const TRANSLATIONS = {
    // ========== HEADER ==========
    "site-title": {
        en: "💻 WP-200: Web Programming",
        ja: "💻 WP-200: ウェブ・プログラミング",
        zh: "💻 WP-200: 网页编程",
        ko: "💻 WP-200: 웹 프로그래밍",
        es: "💻 WP-200: Programación Web"
    },
    "site-subtitle": {
        en: "15-Week Web Development Course",
        ja: "15週間のWeb開発コース",
        zh: "15周网页开发课程",
        ko: "15주 웹 개발 과정",
        es: "Curso de Desarrollo Web de 15 Semanas"
    },
    "site-instructor": {
        en: "Instructor: Tijerino Y.A. | School of Policy Studies",
        ja: "担当者: ティヘリノ Y.A. | 総合政策学部",
        zh: "讲师: Tijerino Y.A. | 综合政策学部",
        ko: "강사: Tijerino Y.A. | 종합정책학부",
        es: "Instructor: Tijerino Y.A. | Facultad de Estudios de Políticas"
    },

    // ========== NAVIGATION ==========
    "nav-overview": {
        en: "Overview",
        ja: "概要",
        zh: "概述",
        ko: "개요",
        es: "Resumen"
    },
    "nav-curriculum": {
        en: "Curriculum",
        ja: "カリキュラム",
        zh: "课程安排",
        ko: "커리큘럼",
        es: "Plan de Estudios"
    },
    "nav-bot": {
        en: "WP Bot",
        ja: "WPボット",
        zh: "WP助手",
        ko: "WP 봇",
        es: "Bot WP"
    },
    "nav-submissions": {
        en: "Submissions",
        ja: "提出",
        zh: "提交作业",
        ko: "제출",
        es: "Entregas"
    },
    "nav-resources": {
        en: "Resources",
        ja: "リソース",
        zh: "资源",
        ko: "자료",
        es: "Recursos"
    },

    // ========== OVERVIEW SECTION ==========
    "overview-title": {
        en: "Course Overview",
        ja: "コース概要",
        zh: "课程概述",
        ko: "과정 개요",
        es: "Descripción del Curso"
    },
    "overview-duration-title": {
        en: "📚 Duration",
        ja: "📚 期間",
        zh: "📚 时长",
        ko: "📚 기간",
        es: "📚 Duración"
    },
    "overview-duration-text": {
        en: "15 weeks (Spring Semester)<br>Tuesday Period 2",
        ja: "15週間（春学期）<br>火曜２時限",
        zh: "15周（春季学期）<br>周二第2节",
        ko: "15주 (봄 학기)<br>화요일 2교시",
        es: "15 semanas (Semestre de Primavera)<br>Martes Período 2"
    },
    "overview-audience-title": {
        en: "🎯 Target Audience",
        ja: "🎯 対象者",
        zh: "🎯 目标学生",
        ko: "🎯 대상",
        es: "🎯 Audiencia"
    },
    "overview-audience-text": {
        en: "Second-year students<br>No prior programming experience required",
        ja: "2年生<br>プログラミング経験不要",
        zh: "二年级学生<br>无需编程经验",
        ko: "2학년 학생<br>프로그래밍 경험 불필요",
        es: "Estudiantes de segundo año<br>No se requiere experiencia previa en programación"
    },
    "overview-tools-title": {
        en: "🛠️ Tools",
        ja: "🛠️ ツール",
        zh: "🛠️ 工具",
        ko: "🛠️ 도구",
        es: "🛠️ Herramientas"
    },
    "overview-tools-text": {
        en: "HTML5, CSS3, JavaScript<br>Canvas API, VS Code<br>Browser Developer Tools",
        ja: "HTML5, CSS3, JavaScript<br>Canvas API, VS Code<br>ブラウザ開発ツール",
        zh: "HTML5, CSS3, JavaScript<br>Canvas API, VS Code<br>浏览器开发工具",
        ko: "HTML5, CSS3, JavaScript<br>Canvas API, VS Code<br>브라우저 개발자 도구",
        es: "HTML5, CSS3, JavaScript<br>Canvas API, VS Code<br>Herramientas de Desarrollo del Navegador"
    },
    "overview-learn-title": {
        en: "What You'll Learn",
        ja: "学習内容",
        zh: "学习内容",
        ko: "학습 내용",
        es: "Lo Que Aprenderás"
    },
    "overview-learn-desc": {
        en: "Starting from zero programming experience, you will learn web development by building a complete Breakout game. The course progresses from HTML/CSS fundamentals through procedural JavaScript to object-oriented programming, with each session introducing one new concept that produces a visible result in your game.",
        ja: "プログラミング経験ゼロから始め、ブロック崩しゲームの構築を通じてWeb開発を学びます。HTML/CSSの基礎から手続き型JavaScript、そしてオブジェクト指向プログラミングへと段階的に進み、毎回の授業で1つの新しい概念を学び、ゲームに目に見える変化をもたらします。",
        zh: "从零编程经验开始，通过构建完整的打砖块游戏来学习网页开发。课程从HTML/CSS基础到过程式JavaScript再到面向对象编程，每节课引入一个新概念，并在游戏中产生可见的成果。",
        ko: "프로그래밍 경험이 전혀 없는 상태에서 시작하여 완전한 벽돌깨기 게임을 만들면서 웹 개발을 배웁니다. HTML/CSS 기초부터 절차적 JavaScript를 거쳐 객체지향 프로그래밍까지, 매 수업마다 하나의 새로운 개념을 배우고 게임에 눈에 보이는 변화를 만듭니다.",
        es: "Comenzando desde cero en programación, aprenderás desarrollo web construyendo un juego completo de Breakout. El curso progresa desde los fundamentos de HTML/CSS a través de JavaScript procedural hasta programación orientada a objetos, con cada sesión introduciendo un nuevo concepto que produce un resultado visible en tu juego."
    },
    "overview-phase1": {
        en: "<strong>Phase 1 - HTML & CSS Foundations (Sessions 1-3):</strong> Build a personal website using semantic HTML5 and CSS3 styling",
        ja: "<strong>フェーズ1 - HTML & CSS基礎（第1-3回）:</strong> セマンティックHTML5とCSS3でパーソナルWebサイトを構築",
        zh: "<strong>阶段1 - HTML & CSS基础（第1-3课）:</strong> 使用语义化HTML5和CSS3构建个人网站",
        ko: "<strong>1단계 - HTML & CSS 기초 (1-3회):</strong> 시맨틱 HTML5와 CSS3로 개인 웹사이트 구축",
        es: "<strong>Fase 1 - Fundamentos HTML & CSS (Sesiones 1-3):</strong> Construir un sitio web personal usando HTML5 semántico y CSS3"
    },
    "overview-phase2": {
        en: "<strong>Phase 2 - Procedural JavaScript (Sessions 4-9):</strong> Learn programming fundamentals by building a Breakout game from an empty canvas",
        ja: "<strong>フェーズ2 - 手続き型JavaScript（第4-9回）:</strong> 空のcanvasからブロック崩しゲームを構築してプログラミングの基礎を学ぶ",
        zh: "<strong>阶段2 - 过程式JavaScript（第4-9课）:</strong> 从空白画布开始构建打砖块游戏，学习编程基础",
        ko: "<strong>2단계 - 절차적 JavaScript (4-9회):</strong> 빈 캔버스에서 벽돌깨기 게임을 만들며 프로그래밍 기초 학습",
        es: "<strong>Fase 2 - JavaScript Procedural (Sesiones 4-9):</strong> Aprender fundamentos de programación construyendo un juego Breakout desde un lienzo vacío"
    },
    "overview-phase3": {
        en: "<strong>Phase 3 - Object-Oriented JavaScript (Sessions 10-13):</strong> Refactor the game using classes, encapsulation, and modularization",
        ja: "<strong>フェーズ3 - オブジェクト指向JavaScript（第10-13回）:</strong> クラス、カプセル化、モジュール化でゲームをリファクタリング",
        zh: "<strong>阶段3 - 面向对象JavaScript（第10-13课）:</strong> 使用类、封装和模块化重构游戏",
        ko: "<strong>3단계 - 객체지향 JavaScript (10-13회):</strong> 클래스, 캡슐화, 모듈화로 게임 리팩터링",
        es: "<strong>Fase 3 - JavaScript Orientado a Objetos (Sesiones 10-13):</strong> Refactorizar el juego usando clases, encapsulación y modularización"
    },
    "overview-phase4": {
        en: "<strong>Phase 4 - Presentation & Review (Sessions 14-15):</strong> Showcase your game and reflect on skills learned",
        ja: "<strong>フェーズ4 - 発表とまとめ（第14-15回）:</strong> ゲームを発表し、学んだスキルを振り返る",
        zh: "<strong>阶段4 - 展示与回顾（第14-15课）:</strong> 展示你的游戏，反思所学技能",
        ko: "<strong>4단계 - 발표 및 리뷰 (14-15회):</strong> 게임을 발표하고 배운 기술을 되돌아보기",
        es: "<strong>Fase 4 - Presentación y Revisión (Sesiones 14-15):</strong> Presentar tu juego y reflexionar sobre las habilidades aprendidas"
    },
    "overview-mdn-credit": {
        en: "🎮 <strong>Game tutorial inspired by:</strong>",
        ja: "🎮 <strong>ゲームチュートリアルの参考:</strong>",
        zh: "🎮 <strong>游戏教程灵感来源:</strong>",
        ko: "🎮 <strong>게임 튜토리얼 참고:</strong>",
        es: "🎮 <strong>Tutorial del juego inspirado en:</strong>"
    },

    // ========== CURRICULUM SECTION ==========
    "curriculum-title": {
        en: "📅 Weekly Curriculum",
        ja: "📅 週別カリキュラム",
        zh: "📅 每周课程安排",
        ko: "📅 주간 커리큘럼",
        es: "📅 Plan de Estudios Semanal"
    },
    "phase1-title": {
        en: "Phase 1: HTML & CSS Foundations (Sessions 1-3)",
        ja: "フェーズ1: HTML & CSS基礎（第1-3回）",
        zh: "阶段1: HTML & CSS基础（第1-3课）",
        ko: "1단계: HTML & CSS 기초 (1-3회)",
        es: "Fase 1: Fundamentos HTML & CSS (Sesiones 1-3)"
    },
    "phase2-title": {
        en: "Phase 2: Procedural JavaScript - Building a Breakout Game (Sessions 4-9)",
        ja: "フェーズ2: 手続き型JavaScript - ブロック崩しゲーム開発（第4-9回）",
        zh: "阶段2: 过程式JavaScript - 构建打砖块游戏（第4-9课）",
        ko: "2단계: 절차적 JavaScript - 벽돌깨기 게임 개발 (4-9회)",
        es: "Fase 2: JavaScript Procedural - Construyendo un Juego Breakout (Sesiones 4-9)"
    },
    "phase2-mdn-note": {
        en: "Based on",
        ja: "参考:",
        zh: "基于",
        ko: "참고:",
        es: "Basado en"
    },
    "phase3-title": {
        en: "Phase 3: Object-Oriented JavaScript (Sessions 10-13)",
        ja: "フェーズ3: オブジェクト指向JavaScript（第10-13回）",
        zh: "阶段3: 面向对象JavaScript（第10-13课）",
        ko: "3단계: 객체지향 JavaScript (10-13회)",
        es: "Fase 3: JavaScript Orientado a Objetos (Sesiones 10-13)"
    },
    "phase4-title": {
        en: "Phase 4: Presentation & Review (Sessions 14-15)",
        ja: "フェーズ4: 発表とまとめ（第14-15回）",
        zh: "阶段4: 展示与回顾（第14-15课）",
        ko: "4단계: 발표 및 리뷰 (14-15회)",
        es: "Fase 4: Presentación y Revisión (Sesiones 14-15)"
    },
    "status-available": {
        en: "✅ Available",
        ja: "✅ 公開中",
        zh: "✅ 可用",
        ko: "✅ 이용 가능",
        es: "✅ Disponible"
    },
    "status-coming-soon": {
        en: "⏳ Coming Soon",
        ja: "⏳ 近日公開",
        zh: "⏳ 即将推出",
        ko: "⏳ 곧 공개",
        es: "⏳ Próximamente"
    },
    "label-topics": {
        en: "Topics:",
        ja: "トピック:",
        zh: "主题:",
        ko: "주제:",
        es: "Temas:"
    },
    "label-concepts": {
        en: "Concepts:",
        ja: "概念:",
        zh: "概念:",
        ko: "개념:",
        es: "Conceptos:"
    },
    "label-homework": {
        en: "Homework:",
        ja: "宿題:",
        zh: "作业:",
        ko: "과제:",
        es: "Tarea:"
    },
    "btn-slides": {
        en: "🖥️ Slides",
        ja: "🖥️ スライド",
        zh: "🖥️ 幻灯片",
        ko: "🖥️ 슬라이드",
        es: "🖥️ Diapositivas"
    },
    "btn-lecture": {
        en: "📖 Lecture",
        ja: "📖 講義",
        zh: "📖 讲义",
        ko: "📖 강의",
        es: "📖 Clase"
    },
    "btn-assignment": {
        en: "📝 Assignment",
        ja: "📝 課題",
        zh: "📝 作业",
        ko: "📝 과제",
        es: "📝 Tarea"
    },

    // ========== SESSION TITLES ==========
    "s1-title": {
        en: "Course Overview & HTML Basics",
        ja: "コース概要とHTML基礎",
        zh: "课程概述与HTML基础",
        ko: "과정 개요 및 HTML 기초",
        es: "Descripción del Curso y HTML Básico"
    },
    "s2-title": {
        en: "Semantic HTML5 & Multi-page Website",
        ja: "セマンティックHTML5と複数ページサイト",
        zh: "语义化HTML5与多页面网站",
        ko: "시맨틱 HTML5 및 다중 페이지 웹사이트",
        es: "HTML5 Semántico y Sitio Web Multi-página"
    },
    "s3-title": {
        en: "CSS3 Fundamentals & Styling",
        ja: "CSS3基礎とスタイリング",
        zh: "CSS3基础与样式",
        ko: "CSS3 기초 및 스타일링",
        es: "Fundamentos de CSS3 y Estilos"
    },
    "s4-title": {
        en: "Canvas & Drawing",
        ja: "Canvasと描画",
        zh: "Canvas与绘图",
        ko: "Canvas와 그리기",
        es: "Canvas y Dibujo"
    },
    "s5-title": {
        en: "Animation & the Game Loop",
        ja: "アニメーションとゲームループ",
        zh: "动画与游戏循环",
        ko: "애니메이션과 게임 루프",
        es: "Animación y el Bucle del Juego"
    },
    "s6-title": {
        en: "Collision Detection & Conditionals",
        ja: "衝突検出と条件分岐",
        zh: "碰撞检测与条件语句",
        ko: "충돌 감지와 조건문",
        es: "Detección de Colisiones y Condicionales"
    },
    "s7-title": {
        en: "Paddle & User Input",
        ja: "パドルとユーザー入力",
        zh: "挡板与用户输入",
        ko: "패들과 사용자 입력",
        es: "Paleta y Entrada del Usuario"
    },
    "s8-title": {
        en: "Brick Field: Arrays & Loops",
        ja: "ブロックフィールド：配列とループ",
        zh: "砖块场地：数组与循环",
        ko: "벽돌 필드: 배열과 루프",
        es: "Campo de Ladrillos: Arrays y Bucles"
    },
    "s9-title": {
        en: "Score, Lives & Game Completion",
        ja: "スコア、ライフ、ゲーム完成",
        zh: "得分、生命与游戏完成",
        ko: "점수, 생명, 게임 완성",
        es: "Puntuación, Vidas y Completar el Juego"
    },
    "s10-title": {
        en: "Introduction to OOP: Ball Class",
        ja: "OOP入門：Ballクラス",
        zh: "OOP入门：Ball类",
        ko: "OOP 입문: Ball 클래스",
        es: "Introducción a OOP: Clase Ball"
    },
    "s11-title": {
        en: "Paddle & Brick Classes",
        ja: "PaddleとBrickクラス",
        zh: "Paddle与Brick类",
        ko: "Paddle과 Brick 클래스",
        es: "Clases Paddle y Brick"
    },
    "s12-title": {
        en: "Game Class & Modularization",
        ja: "Gameクラスとモジュール化",
        zh: "Game类与模块化",
        ko: "Game 클래스와 모듈화",
        es: "Clase Game y Modularización"
    },
    "s13-title": {
        en: "Enhancements: Audio, Storage & Customization",
        ja: "拡張：音声、ストレージ、カスタマイズ",
        zh: "增强：音频、存储与自定义",
        ko: "향상: 오디오, 저장소, 커스터마이징",
        es: "Mejoras: Audio, Almacenamiento y Personalización"
    },
    "s14-title": {
        en: "Final Project Presentation",
        ja: "最終プロジェクト発表",
        zh: "期末项目展示",
        ko: "최종 프로젝트 발표",
        es: "Presentación del Proyecto Final"
    },
    "s15-title": {
        en: "Course Review & Reflection",
        ja: "コース総括と振り返り",
        zh: "课程回顾与反思",
        ko: "과정 리뷰 및 성찰",
        es: "Revisión y Reflexión del Curso"
    },

    // ========== BOT PORTAL ==========
    "bot-title": {
        en: "🤖 WP-200 Bot Portal",
        ja: "🤖 WP-200 ボットポータル",
        zh: "🤖 WP-200 助手门户",
        ko: "🤖 WP-200 봇 포털",
        es: "🤖 Portal del Bot WP-200"
    },
    "bot-chat-title": {
        en: "💬 WP-200 Course Bot",
        ja: "💬 WP-200 コースボット",
        zh: "💬 WP-200 课程助手",
        ko: "💬 WP-200 코스 봇",
        es: "💬 Bot del Curso WP-200"
    },
    "bot-welcome": {
        en: "Welcome! I'm your Web Programming course assistant. I can help you with:\n- Course content and assignments\n- HTML, CSS, and JavaScript questions\n- Game development guidance\n- Additional learning resources",
        ja: "ようこそ！ウェブプログラミングのコースアシスタントです。以下についてお手伝いできます：\n- 授業内容と課題\n- HTML、CSS、JavaScriptの質問\n- ゲーム開発のガイダンス\n- 追加の学習リソース",
        zh: "欢迎！我是你的网页编程课程助手。我可以帮助你：\n- 课程内容和作业\n- HTML、CSS和JavaScript问题\n- 游戏开发指导\n- 额外的学习资源",
        ko: "환영합니다! 저는 웹 프로그래밍 과정 도우미입니다. 다음을 도와드릴 수 있습니다:\n- 수업 내용과 과제\n- HTML, CSS, JavaScript 질문\n- 게임 개발 안내\n- 추가 학습 자료",
        es: "¡Bienvenido! Soy tu asistente del curso de Programación Web. Puedo ayudarte con:\n- Contenido del curso y tareas\n- Preguntas sobre HTML, CSS y JavaScript\n- Guía de desarrollo de juegos\n- Recursos de aprendizaje adicionales"
    },
    "bot-placeholder": {
        en: "Ask a question about the course...",
        ja: "コースについて質問してください...",
        zh: "请提问关于课程的问题...",
        ko: "과정에 대해 질문하세요...",
        es: "Haz una pregunta sobre el curso..."
    },
    "bot-send": {
        en: "Send",
        ja: "送信",
        zh: "发送",
        ko: "전송",
        es: "Enviar"
    },
    "bot-sending": {
        en: "Sending...",
        ja: "送信中...",
        zh: "发送中...",
        ko: "전송 중...",
        es: "Enviando..."
    },
    "bot-clear": {
        en: "Clear conversation",
        ja: "会話をクリア",
        zh: "清除对话",
        ko: "대화 지우기",
        es: "Borrar conversación"
    },

    // ========== SUBMISSIONS ==========
    "submissions-title": {
        en: "📤 Assignment Submissions",
        ja: "📤 課題提出",
        zh: "📤 作业提交",
        ko: "📤 과제 제출",
        es: "📤 Entrega de Tareas"
    },
    "submissions-desc": {
        en: "Select your assignment and paste your code below. The system will run automated checks and provide AI-assisted feedback. Your instructor will review and publish your final grade.",
        ja: "課題を選択し、コードを以下に貼り付けてください。自動チェックとAIによるフィードバックが提供されます。最終成績は講師が確認後に公開されます。",
        zh: "选择你的作业并在下方粘贴代码。系统将运行自动检查并提供AI辅助反馈。讲师审核后将公布最终成绩。",
        ko: "과제를 선택하고 아래에 코드를 붙여넣으세요. 시스템이 자동 검사를 실행하고 AI 피드백을 제공합니다. 강사가 검토 후 최종 성적을 공개합니다.",
        es: "Selecciona tu tarea y pega tu código abajo. El sistema ejecutará verificaciones automáticas y proporcionará retroalimentación asistida por IA. Tu instructor revisará y publicará tu calificación final."
    },
    "label-student-id": {
        en: "Student ID:",
        ja: "学生番号:",
        zh: "学号:",
        ko: "학번:",
        es: "ID de Estudiante:"
    },
    "label-assignment": {
        en: "Assignment:",
        ja: "課題:",
        zh: "作业:",
        ko: "과제:",
        es: "Tarea:"
    },
    "label-select-assignment": {
        en: "-- Select Assignment --",
        ja: "-- 課題を選択 --",
        zh: "-- 选择作业 --",
        ko: "-- 과제 선택 --",
        es: "-- Seleccionar Tarea --"
    },
    "label-your-code": {
        en: "Your Code:",
        ja: "コード:",
        zh: "你的代码:",
        ko: "코드:",
        es: "Tu Código:"
    },
    "label-upload-files": {
        en: "Or upload files:",
        ja: "またはファイルをアップロード:",
        zh: "或上传文件:",
        ko: "또는 파일 업로드:",
        es: "O subir archivos:"
    },
    "btn-submit": {
        en: "Submit Assignment",
        ja: "課題を提出",
        zh: "提交作业",
        ko: "과제 제출",
        es: "Entregar Tarea"
    },
    "grades-title": {
        en: "📊 My Grades",
        ja: "📊 成績確認",
        zh: "📊 我的成绩",
        ko: "📊 내 성적",
        es: "📊 Mis Calificaciones"
    },
    "btn-view-grades": {
        en: "View Published Grades",
        ja: "公開済み成績を表示",
        zh: "查看已发布成绩",
        ko: "공개된 성적 보기",
        es: "Ver Calificaciones Publicadas"
    },
    "grades-none": {
        en: "No published grades yet.",
        ja: "まだ公開された成績はありません。",
        zh: "暂无已发布的成绩。",
        ko: "아직 공개된 성적이 없습니다.",
        es: "Aún no hay calificaciones publicadas."
    },

    // ========== RESOURCES ==========
    "resources-title": {
        en: "📚 Resources",
        ja: "📚 リソース",
        zh: "📚 资源",
        ko: "📚 자료",
        es: "📚 Recursos"
    },
    "resources-mdn": {
        en: "MDN Tutorial",
        ja: "MDNチュートリアル",
        zh: "MDN教程",
        ko: "MDN 튜토리얼",
        es: "Tutorial MDN"
    },
    "resources-selfstudy": {
        en: "Self-Study",
        ja: "自習教材",
        zh: "自学资料",
        ko: "자습 자료",
        es: "Autoestudio"
    },
    "resources-tools": {
        en: "Development Tools",
        ja: "開発ツール",
        zh: "开发工具",
        ko: "개발 도구",
        es: "Herramientas de Desarrollo"
    },
    "resources-ai-policy": {
        en: "AI Policy",
        ja: "AI活用方針",
        zh: "AI使用政策",
        ko: "AI 정책",
        es: "Política de IA"
    },
    "ai-required": {
        en: "<strong>AI use is required</strong> in this course",
        ja: "本授業では<strong>AIの使用を必須</strong>とします",
        zh: "本课程<strong>要求使用AI</strong>",
        ko: "이 과정에서 <strong>AI 사용은 필수</strong>입니다",
        es: "El uso de IA es <strong>obligatorio</strong> en este curso"
    },
    "ai-complementary": {
        en: "AI is a complementary tool under instructor supervision",
        ja: "AIは教授の監督のもと補助ツールとして活用",
        zh: "AI是在讲师监督下的辅助工具",
        ko: "AI는 강사의 감독하에 보조 도구로 활용",
        es: "La IA es una herramienta complementaria bajo supervisión del instructor"
    },
    "ai-comply": {
        en: "All use must comply with university AI policies",
        ja: "大学のAIポリシーを遵守してください",
        zh: "所有使用必须遵守大学AI政策",
        ko: "모든 사용은 대학교 AI 정책을 준수해야 합니다",
        es: "Todo uso debe cumplir con las políticas de IA de la universidad"
    },

    // ========== ASSESSMENT ==========
    "assessment-title": {
        en: "📊 Assessment",
        ja: "📊 評価",
        zh: "📊 评估",
        ko: "📊 평가",
        es: "📊 Evaluación"
    },
    "assessment-grading": {
        en: "Grading",
        ja: "成績評価",
        zh: "评分",
        ko: "성적 평가",
        es: "Calificación"
    },
    "assessment-breakdown": {
        en: "<strong>100% - Continuous Assessment:</strong> Attendance, discussion participation, individual assignments (9 assignments throughout the course), and online quizzes",
        ja: "<strong>100% - 継続的評価:</strong> 出席、ディスカッション参加、個人課題（全9回）、オンラインクイズ",
        zh: "<strong>100% - 持续评估:</strong> 出勤、讨论参与、个人作业（全课程共9次）和在线测验",
        ko: "<strong>100% - 지속적 평가:</strong> 출석, 토론 참여, 개인 과제 (과정 전체 9회), 온라인 퀴즈",
        es: "<strong>100% - Evaluación Continua:</strong> Asistencia, participación en discusiones, tareas individuales (9 tareas a lo largo del curso) y cuestionarios en línea"
    },
    "assessment-format": {
        en: "<strong>Course Format:</strong> Face-to-face classes with live Zoom broadcast for students with online permission. All classes are recorded and available on Luna. Individual work only - no group projects.",
        ja: "<strong>授業方法:</strong> 対面授業形式。オンライン許可の学生にはZoomでライブ配信。全授業はLunaで録画視聴可能。個人課題のみ。",
        zh: "<strong>课程形式:</strong> 面对面授课，允许在线的学生可通过Zoom直播参与。所有课程均在Luna上录制可供观看。仅限个人作业，无小组项目。",
        ko: "<strong>수업 형식:</strong> 대면 수업, 온라인 허가 학생은 Zoom 라이브 방송 참여. 모든 수업은 Luna에서 녹화 시청 가능. 개인 과제만 - 그룹 프로젝트 없음.",
        es: "<strong>Formato del Curso:</strong> Clases presenciales con transmisión en vivo por Zoom para estudiantes con permiso en línea. Todas las clases se graban y están disponibles en Luna. Solo trabajo individual - sin proyectos grupales."
    },

    // ========== FOOTER ==========
    "footer-copyright": {
        en: "&copy; 2026 Kwansei Gakuin University - School of Policy Studies. All rights reserved.",
        ja: "著作権 &copy; 2026 関西学院大学 総合政策学部. 無断転載を禁じます。",
        zh: "&copy; 2026 关西学院大学 综合政策学部. 保留所有权利。",
        ko: "&copy; 2026 관서학원대학교 종합정책학부. 모든 권리 보유.",
        es: "&copy; 2026 Universidad Kwansei Gakuin - Facultad de Estudios de Políticas. Todos los derechos reservados."
    },

    // ========== LANGUAGE NAMES (for selector) ==========
    "lang-en": { en: "English", ja: "English", zh: "English", ko: "English", es: "English" },
    "lang-ja": { en: "日本語", ja: "日本語", zh: "日本語", ko: "日本語", es: "日本語" },
    "lang-zh": { en: "中文", ja: "中文", zh: "中文", ko: "中文", es: "中文" },
    "lang-ko": { en: "한국어", ja: "한국어", zh: "한국어", ko: "한국어", es: "한국어" },
    "lang-es": { en: "Español", ja: "Español", zh: "Español", ko: "Español", es: "Español" }
};

// ========== i18n Engine ==========

class I18n {
    constructor() {
        this.currentLang = localStorage.getItem('wp200_lang') || 'en';
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.applyLanguage(this.currentLang);
            this.setupLanguageSelector();
        });
    }

    setupLanguageSelector() {
        const selector = document.getElementById('language-selector');
        if (selector) {
            selector.value = this.currentLang;
            selector.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }
    }

    setLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('wp200_lang', lang);
        this.applyLanguage(lang);

        // Update bot language too
        const botLangToggle = document.getElementById('bot-language-toggle');
        if (botLangToggle) {
            botLangToggle.value = lang;
        }
        if (window.wp200BotChat) {
            window.wp200BotChat.currentLanguage = lang;
        }
    }

    applyLanguage(lang) {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation) {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = translation;
                } else {
                    el.innerHTML = translation;
                }
            }
        });

        // Update elements with data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation) {
                el.placeholder = translation;
            }
        });

        // Update document language
        document.documentElement.lang = lang;
    }

    t(key) {
        const entry = TRANSLATIONS[key];
        if (!entry) return null;
        return entry[this.currentLang] || entry['en'] || null;
    }
}

// Initialize
const i18n = new I18n();
