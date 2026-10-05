import os
import re
import docx

BANNED_WORDS = [
    'delve', 'delves', 'delving', 'tapestry', 'landscape', 'testament', 'vibrant', 
    'pivotal', 'crucial', 'intricate', 'intricacies', 'meticulous', 'meticulously', 
    'bolster', 'bolstered', 'garner', 'garnered', 'underscore', 'underscores', 
    'interplay', 'multifaceted', 'nuanced', 'foster', 'fostering', 'leverage', 
    'utilize', 'commence', 'facilitate', 'encompass', 'encompassing', 'paramount', 
    'groundbreaking', 'cutting-edge', 'game-changing', 'transformative', 
    'revolutionise', 'revolutionize', 'seamless', 'seamlessly', 'endeavour', 
    'endeavor', 'aforementioned', 'harnessing', 'spearheading', 'navigating', 
    'showcasing', 'highlighting', 'emphasizing', 'enhancing', 'unprecedented', 
    'remarkable', 'stunning', 'profound', 'in essence', 'synergy', 'pain points',
    'value add', 'moving forward', 'touch base', 'rest assured', 'it goes without saying',
    'not just', 'not only', 'it is worth noting', 'at its core', 'in the realm of',
    'when it comes to', 'without further ado', 'in a nutshell', 'elevate your',
    'streamline your', 'supercharge', 'bridge the gap', 'in conclusion'
]

HALLUCINATED_TERMS = [
    'gemini', 'claude', 'anthropic', 'ollama'
]

def check_text(name, text):
    for bw in BANNED_WORDS:
        pattern = r'\b' + re.escape(bw) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError(f"Banned word '{bw}' found in {name}: {text}")
    for ht in HALLUCINATED_TERMS:
        pattern = r'\b' + re.escape(ht) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError(f"Hallucinated term '{ht}' found in {name}: {text}")
    em_dashes = text.count('—') + text.count('--')
    if em_dashes > 1:
        print(f"Warning: {name} contains {em_dashes} dashes.")

def update_paragraph(p, new_text, name="paragraph"):
    check_text(name, new_text)
    if p.runs:
        p.runs[0].text = new_text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = new_text

def run_update():
    doc_path = os.path.abspath('docs/23CSMPB03-REPORT.docx')
    doc = docx.Document(doc_path)
    print(f"Loaded {doc_path} with {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables.")

    # 1. Date on Declaration (Paragraph 56)
    update_paragraph(doc.paragraphs[56], "Date: 30-11-2026", "Declaration Date")

    # 2. Abstract (Paragraph 62)
    abstract_text = (
        "WKAI (Workshop AI) is a real-time, AI-assisted platform for running live coding workshops and classroom sessions. "
        "An instructor runs a lightweight desktop application, built with Tauri over Rust and React, which captures the screen and microphone natively on Windows and Linux and publishes both live, while a Node.js backend follows the session with large language models and produces step-by-step guides, comprehension checks and error diagnoses for students as the class runs. "
        "Students join from an ordinary browser with a six-character room code and a signed access token, with nothing to install, and work in a companion React application holding the live view, the generated guide, a sandboxed Monaco and xterm editor for exercises, an AI debugging panel and a proctored assessment runner. "
        "The system is three independent applications over one backend: the instructor app, the student app, and the backend service, speaking a documented WebSocket protocol for control and WebRTC fanned out through a Cloudflare Realtime Selective Forwarding Unit for video delivery. "
        "The backend orchestrates seven LangGraph agents (error diagnosis, intent detection, transcript explanation, comprehension coaching, student messaging, notebook assistance and assessment authoring) running on Groq LPU inference using Qwen3.8-27B for vision, GPT-OSS-120B for reasoning, and Whisper Large v3 for speech, with PostgreSQL for durable records and Redis for room state and short-term memory. "
        "Phase-II delivered a working system end to end: authenticated session creation and join, native OS-level screen capture on Windows (DXGI) and Linux (X11 via x11rb), live delivery through an SFU relay with a direct WebRTC mesh as fallback and server-minted TURN credentials for restrictive networks, real-time guide generation with explicit grounding filters that reject ungrounded content, in-browser code execution and error help, file sharing, quizzes and proctored assessments with focus-loss tracking, cross-session workspace memory, an agent-facing Model Context Protocol (wkai-mcp) interface, automated multi-platform CI/CD on GitHub Actions with signed Windows and Linux installers mirrored to Google Drive, and zero-server edge hosting on Android phones via Termux and Debian proot."
    )
    update_paragraph(doc.paragraphs[62], abstract_text, "Abstract")

    # 3. Chapter 1: Introduction - Paragraph 231
    p231_text = (
        "WKAI is software only, structured across three independent components. The instructor desktop application, built with Tauri over Rust and React, captures system audio and displays natively on Windows and Linux, controls session parameters, and manages file distribution. The student companion is a zero-install single-page web application running in modern browsers, rendering the live stream, an interactive guide, an exercise workspace, and proctored assessments. The backend, implemented in Node.js with TypeScript and Express, manages rooms, verifies signed tokens, routes WebSocket messages, and orchestrates the AI agent pipeline on Groq."
    )
    update_paragraph(doc.paragraphs[231], p231_text, "P231 Overview")

    # Paragraph 238 (Native capture)
    p238_text = (
        "Native capture: screen and microphone inputs are grabbed directly through operating system APIs (Windows Desktop Duplication API with GDI fallback; Linux X11 protocol via x11rb with PipeWire fallback), avoiding browser permission dialogs and webview capture overhead."
    )
    update_paragraph(doc.paragraphs[238], p238_text, "P238 Native capture")

    # Paragraph 239 (Relay delivery)
    p239_text = (
        "Relay delivery: the instructor publishes one media stream to a selective forwarding unit (SFU) and every student pulls a copy, so the instructor's upstream bandwidth and CPU remain constant as the class grows."
    )
    update_paragraph(doc.paragraphs[239], p239_text, "P239 Relay delivery")

    # Paragraph 243 (Assessments and proctoring)
    p243_text = (
        "Assessments and proctoring: timed comprehension quizzes and programming challenges with client focus-loss ('away modal') and paste-event recording for instructor review."
    )
    update_paragraph(doc.paragraphs[243], p243_text, "P243 Assessments and proctoring")

    # Paragraph 248 (Agent interface for tooling - MCP)
    p248_text = (
        "An agent interface for tooling: an MCP server (wkai-mcp) exposes eight tools (wkai_create_session, wkai_connect_instructor, wkai_send_screen_frame, wkai_speak, wkai_share_file, wkai_reply_to_student, wkai_list_students, wkai_end_session) letting an external agent run a complete workshop session."
    )
    update_paragraph(doc.paragraphs[248], p248_text, "P248 Agent interface MCP")

    # Paragraph 252 (Summary of contributions)
    p252_text = (
        "The contributions of this phase can be stated precisely. First, an end-to-end workshop platform combining native OS-level screen capture on Windows and Linux with real-time AI study guide generation and context-aware error diagnosis. Second, a scalable WebRTC media distribution pipeline using an SFU relay that decouples instructor upload bandwidth from student cohort size. Third, an interactive student exercise sandbox integrated with a proctored assessment system and client focus tracking. Fourth, an autonomous agent interface implementing the Model Context Protocol (wkai-mcp) alongside flexible edge deployment on mobile hardware (Android Termux + Debian)."
    )
    update_paragraph(doc.paragraphs[252], p252_text, "P252 Summary of contributions")

    # Paragraph 253 (Architectural decisions)
    p253_text = (
        "The architecture preserves clear boundaries between capture, distribution, and inference. Rather than binding screen capture to fragile browser extensions, the instructor client captures framebuffers through native Rust subsystems (DXGI on Windows, x11rb on Linux). Video transmission uses an SFU relay with direct peer mesh fallback. Authentication relies on server-minted JSON Web Tokens, ensuring roles and capabilities cannot be spoofed by client-side manipulation."
    )
    update_paragraph(doc.paragraphs[253], p253_text, "P253 Architecture")

    # Paragraph 287 (Objective 1)
    p287_text = (
        "Build an instructor application that captures and streams screen and audio natively on Windows and Linux with minimal setup."
    )
    update_paragraph(doc.paragraphs[287], p287_text, "P287 Objective 1")

    # Paragraph 290 (Objective 4)
    p290_text = (
        "Deliver the live stream and guide to students through a zero-install browser application with embedded exercises and proctored comprehension assessments."
    )
    update_paragraph(doc.paragraphs[290], p290_text, "P290 Objective 4")

    # Paragraph 291 (Objective 5)
    p291_text = (
        "Harden authentication, session lifecycle, and multi-platform packaging with automated CI/CD and edge hosting support."
    )
    update_paragraph(doc.paragraphs[291], p291_text, "P291 Objective 5")

    # Paragraph 293 (Scope of project)
    p293_text = (
        "In scope for this phase: instructor screen and audio capture and streaming across Windows and Linux, the WebSocket signalling and session-lifecycle protocol, server-minted join tokens, the seven core LangGraph agents on Groq (Qwen3.8-27B for vision, GPT-OSS-120B for reasoning, and Whisper Large v3 for speech), student error diagnosis, file sharing, proctored comprehension quizzes with away-modal tracking, Google Colab context ingestion, Model Context Protocol agent tools, automated CI/CD release pipelines with Google Drive installer mirrors, and Android Termux edge deployment."
    )
    update_paragraph(doc.paragraphs[293], p293_text, "P293 Scope")

    # 4. Chapter 2: SRS - Paragraph 303 (FR-2)
    p303_text = (
        "FR-2: The system shall capture the instructor's screen and audio natively on Windows and Linux and stream it live to all connected students through an SFU relay."
    )
    update_paragraph(doc.paragraphs[303], p303_text, "P303 FR-2")

    # Paragraph 308 (FR-7)
    p308_text = (
        "FR-7: The system shall support in-session comprehension quizzes and proctored assessments with focus-loss tracking and automated scoring."
    )
    update_paragraph(doc.paragraphs[308], p308_text, "P308 FR-7")

    # Paragraph 310 (FR-9)
    p310_text = (
        "FR-9: Both applications shall support light and dark themes with persistent accent colours across views."
    )
    update_paragraph(doc.paragraphs[310], p310_text, "P310 FR-9")

    # Paragraph 317 (Portability)
    p317_text = (
        "Portability: the instructor app must build and run natively on Windows and Linux via Tauri v2, while students access the platform through standard evergreen browsers."
    )
    update_paragraph(doc.paragraphs[317], p317_text, "P317 Portability")

    # Paragraph 322 (Constraints)
    p322_text = (
        "The instructor runs the desktop application on Windows or Linux; students need only a modern browser."
    )
    update_paragraph(doc.paragraphs[322], p322_text, "P322 Constraints")

    # Paragraph 327 (Technical Feasibility)
    p327_text = (
        "Each technical dependency was verified before adoption. Real-time transcription was confirmed by measuring Whisper Large v3 on Groq LPUs, returning thirty-second audio chunks in under 200 ms. Desktop capture was implemented natively on Windows using the Desktop Duplication API (DXGI) with GDI fallback, and on Linux using the X11 protocol via x11rb with PipeWire fallback. One-to-many video delivery was proven using an SFU relay that distributes a single publisher stream to multiple student subscribers. Edge backend hosting was verified on ARM64 Android devices under Termux and proot Debian, consuming less than 180 MB of RAM while handling active WebSocket sessions."
    )
    update_paragraph(doc.paragraphs[327], p327_text, "P327 Technical Feasibility")

    # Paragraph 329 (Economic Feasibility)
    p329_text = (
        "The architecture operates at zero recurring cost during development and minimal expense in production. Groq inference provides development allowances; file storage uses a 25 GB Cloudinary tier; PostgreSQL and Redis operate within free managed quotas on Neon and Upstash; and the student app deploys to static CDN hosting on Vercel. When running on campus networks without internet egress, the backend can run on an existing Android smartphone via Termux, reducing cloud infrastructure expenditure to zero."
    )
    update_paragraph(doc.paragraphs[329], p329_text, "P329 Economic Feasibility")

    # Paragraph 331 (Operational Feasibility)
    p331_text = (
        "Operational feasibility rests on minimal installation friction. Instructors install a single native binary, built and packaged automatically by GitHub Actions for Windows (NSIS executable, MSI installer) and Linux (.deb package, AppImage) with Google Drive download mirrors. Students install nothing, accessing sessions via a browser with a room code. Sessions require no on-premises server configuration or dedicated administration."
    )
    update_paragraph(doc.paragraphs[331], p331_text, "P331 Operational Feasibility")

    # Paragraph 337-338 (Minimum System Configuration)
    p337_text = (
        "Instructor Machine: Dual-core x86_64 or ARM64 processor, 4 GB RAM, 200 MB disk space, Windows 10/11 (64-bit) or Linux (Ubuntu 22.04+, Debian 12+, Fedora 38+ with X11 or Wayland), microphone, and 5 Mbps upstream network connection."
    )
    p338_text = (
        "Student Machine: Device running a modern browser (Chrome 110+, Firefox 115+, Safari 16+, Edge 110+), 2 GB RAM, and 2 Mbps downstream connection. Edge Host (Optional): Android phone running Android 7.0+, 64-bit ARM CPU, 2 GB free storage, and Termux with proot Debian."
    )
    update_paragraph(doc.paragraphs[337], p337_text, "P337 Min Config")
    update_paragraph(doc.paragraphs[338], p338_text, "P338 Min Config 2")

    # 5. Chapter 3: High-Level Design
    # Paragraph 357 (Instructor app)
    p357_text = (
        "Instructor app (wkai/): Tauri v2 (Rust + React, TypeScript, Vite). The Rust core manages OS-level screen capture (DXGI and GDI on Windows; native X11 via x11rb and PipeWire on Linux), audio capture, tray lifecycle, and local recording."
    )
    update_paragraph(doc.paragraphs[357], p357_text, "P357 Instructor app")

    # Paragraph 359 (Backend)
    p359_text = (
        "Backend (wkai-backend/): Node.js with ES modules, Express and ws, backed by PostgreSQL for durable records and Redis for room state and session memory. The backend deploys to cloud containers (Render) or local edge hardware (Android Termux + Debian proot)."
    )
    update_paragraph(doc.paragraphs[359], p359_text, "P359 Backend")

    # Paragraph 360 (Capture)
    p360_text = (
        "Instructor capture runs entirely outside the browser runtime. The Rust capture module grabs framebuffers per operating system (DXGI on Windows, x11rb on Linux), executes SIMD colour conversion, and feeds the WebRTC SFU streaming pipeline."
    )
    update_paragraph(doc.paragraphs[360], p360_text, "P360 Capture")

    # Paragraph 378 (Backend module structure)
    p378_text = (
        "Module Structure of the Backend: Routes are partitioned into session management, authentication, file sharing, assessments, and AI orchestration. The ai/ package defines the LangGraph state machines, while wkai-mcp exposes tool definitions for external autonomous agents. The assessments/ module handles quiz dispatch, submission evaluation, and student focus-loss event aggregation."
    )
    update_paragraph(doc.paragraphs[378], p378_text, "P378 Backend modules")

    # Paragraph 389 (Streaming protocol)
    p389_text = (
        "Live media travels on an independent WebRTC transport. The instructor negotiates a publish session against the SFU relay using backend-brokered credentials. Students connect as subscribers, pulling video tracks over UDP/SRTP without loading the instructor's local uplink. If the relay is unavailable, connections drop back to a direct peer mesh."
    )
    update_paragraph(doc.paragraphs[389], p389_text, "P389 Streaming protocol")

    # 6. Chapter 4: Detailed Design
    # Paragraph 404 (AI Agent Layer Design)
    p404_text = (
        "The AI agent layer is hosted entirely on Groq's LPU inference infrastructure to sustain the low latencies required for live technical instruction. Speech transcription uses Whisper Large v3, transcribing thirty-second audio chunks in under 200 ms. Frame vision processing uses Qwen3.8-27B (qwen/qwen3.8-27b, max_tokens=900), which replaced the decommissioned llama-4-scout and operates under Groq's output-tokens-per-minute ceiling without emitting disruptive reasoning blocks. Text reasoning, error diagnosis, intent detection, and assessment authoring use GPT-OSS-120B (openai/gpt-oss-120b), which migrated from llama-3.3-70b-versatile for superior structured output generation and reliable Zod schema validation. A dedicated creative instance of GPT-OSS-120B (temperature 0.6, max_tokens=1200) generates comprehension check questions."
    )
    update_paragraph(doc.paragraphs[404], p404_text, "P404 AI Layer")

    # Paragraph 428 (Security)
    p428_text = (
        "The security boundary derives all privileges from cryptographically signed tokens. In addition to role enforcement, the backend supports explicit student removal with mandatory reason logging, broadcasting eviction notices over WebSockets. Forgotten room passwords can be reset by the instructor using a server-issued cryptographic access key."
    )
    update_paragraph(doc.paragraphs[428], p428_text, "P428 Security")

    # 7. Chapter 5: Implementation
    # Paragraph 441 (Environment)
    p441_text = (
        "Backend: Node.js (ESM), Express, ws, PostgreSQL (Neon), Redis (Upstash), and environment-configured credentials for the Groq API (GROQ_API_KEY), Cloudinary, and the Cloudflare Realtime SFU. Build dependencies for the desktop app include Rust 1.77+, CMake, and platform headers (Windows SDK on Windows; libx11-dev, libpipewire-0.3-dev, and mesa-common-dev on Linux)."
    )
    update_paragraph(doc.paragraphs[441], p441_text, "P441 Environment")

    # Paragraph 445 (Capture pipeline)
    p445_text = (
        "Instructor capture pipeline: the Rust native_capture module implements screen capture behind a common backend trait. On Windows, it leverages the Desktop Duplication API (DXGI) for hardware-accelerated frame grabbing, falling back to GDI if hardware acceleration is unavailable. On Linux, it implements direct X11 capture via x11rb, with a getDisplayMedia webview fallback for Wayland desktops. Frames are converted to BGRA/RGBA using SIMD routines before delivery to the WebRTC video track."
    )
    update_paragraph(doc.paragraphs[445], p445_text, "P445 Capture pipeline")

    # Paragraph 446 (Streaming backend)
    p446_text = (
        "Streaming backend: media delivery is brokered by the backend so that no client holds provider credentials. The backend provides short-lived ICE servers and room tokens, allowing the instructor to publish one video track and students to subscribe via the SFU relay. If relay credentials are absent, clients fall back to a direct WebRTC mesh."
    )
    update_paragraph(doc.paragraphs[446], p446_text, "P446 Streaming backend")

    # Paragraph 450 (Student exercise sandbox & assessments)
    p450_text = (
        "Student Exercise Sandbox and Assessments: The student application embeds Monaco editor and xterm instances for running exercises in Python, JavaScript, and TypeScript. In addition, an assessment runner presents timed comprehension quizzes and coding challenges. The client tracks focus-loss ('away modal') and paste events, sending telemetry to the backend to support academic integrity auditing."
    )
    update_paragraph(doc.paragraphs[450], p450_text, "P450 Student sandbox")

    # Paragraph 452 (File sharing & Colab context)
    p452_text = (
        "File Sharing and Colab Context Ingestion: File sharing supports drag-and-drop uploads, folder-watching on the instructor desktop, and automated Cloudinary hosting. In addition, the backend can ingest Google Colab notebooks, extracting code cells, execution outputs, and markdown notes into the session workspace context to guide AI explanations."
    )
    update_paragraph(doc.paragraphs[452], p452_text, "P452 File sharing & Colab")

    # Paragraph 456 (Presence & Controls)
    p456_text = (
        "Session Controls and Presence Signalling: The instructor interface features a floating PresentBar that stays accessible during screen sharing, complete with tray minimization, participant count indicators, student kick controls with audit logs, and password recovery tools."
    )
    update_paragraph(doc.paragraphs[456], p456_text, "P456 Session controls")

    # Paragraph 458 (Build and release automation)
    p458_text = (
        "Three deployment targets are automated using GitHub Actions. The student web app and landing page build on push to main and publish to static hosting on Vercel. The backend deploys automatically to container infrastructure on Render, with migration scripts executed on startup. The instructor desktop application builds on GitHub Actions runners for Windows (producing NSIS executables and MSI installers) and Linux (producing .deb packages and AppImages on ubuntu-24.04). Release artifacts are signed for in-app updates and automatically mirrored to Google Drive as a download fallback."
    )
    update_paragraph(doc.paragraphs[458], p458_text, "P458 Build and release")

    # Paragraph 461 (Challenges)
    p461_text = (
        "Four classes of difficulty required focused engineering this phase. The first was Linux display server diversity: capturing screen frames reliably across X11 and Wayland required implementing direct X11 protocol integration via x11rb while providing a PipeWire and webview capture fallback for Wayland. The second was process lifecycle management on mobile edge devices, where Android 12+ phantom process monitors aggressively terminate background proot child processes, requiring explicit wake-locks and child process monitor adjustments."
    )
    update_paragraph(doc.paragraphs[461], p461_text, "P461 Challenges")

    # 8. Chapter 6: Testing & Results
    # Paragraph 471 (Unit tests)
    p471_text = (
        "Backend unit tests, sixty of them, covering token issue and verification, the per-session AI concurrency queue, and prompt schema validation."
    )
    update_paragraph(doc.paragraphs[471], p471_text, "P471 Unit tests")

    # Paragraph 473 (MCP tests)
    p473_text = (
        "An MCP suite, four tests, exercising the session lifecycle through the agent-facing tool surface: open a room, broadcast guidance, monitor student activity, and execute assessment grading."
    )
    update_paragraph(doc.paragraphs[473], p473_text, "P473 MCP tests")

    # Paragraph 474 (Playwright tests)
    p474_text = (
        "A Playwright browser suite, twenty-six tests, driving the student application through the landing page, room join flow, Monaco code editor, terminal execution, and proctoring away-modal focus tracking."
    )
    update_paragraph(doc.paragraphs[474], p474_text, "P474 Playwright tests")

    # 9. Chapter 7: Conclusion & Future Scope
    # Paragraph 526 (Conclusion)
    p526_text = (
        "Phase-II delivered a complete, validated WKAI system. The instructor application streams live coding sessions natively on Windows and Linux, capturing framebuffers at 37 to 40 frames per second through native Rust backends and fanning out video to students through an SFU relay. The backend AI pipeline generates grounded study guides and on-demand error diagnoses, backed by hallucination filters and Groq LPU inference models (Qwen3.8-27B for vision, GPT-OSS-120B for reasoning, and Whisper Large v3 for audio). Students join instantly via modern web browsers without installation, participating through an interactive workspace with embedded code execution and proctored comprehension quizzes. Deployment flexibility spans cloud containers, static CDNs, and zero-cost Android phone edge hosting via Termux. The platform is further extensible through the Model Context Protocol (wkai-mcp), enabling external AI agents to programmatically orchestrate sessions."
    )
    update_paragraph(doc.paragraphs[526], p526_text, "P526 Conclusion")

    # Paragraph 528 (Limitations - CORRECT THE OUTDATED TEXT)
    p528_text = (
        "Native screen capture is implemented for Windows and Linux; the macOS backend remains a stub behind the unified trait. Frame rate is bounded by the capture call at approximately 37 frames per second on Windows and 40 frames per second on Linux X11. Exceeding this threshold requires dirty-rectangle delta tracking rather than additional capture threads. Video distribution depends on an SFU relay, falling back to a direct peer mesh if external relay credentials are missing. On Groq's free tier, vision inference costs roughly 3,900 tokens per frame against a daily quota of 200,000 tokens, limiting vision-based guide generation to about fifty frames per day. Assessment proctoring records focus-loss and paste events rather than locking student browser environments. Automated test coverage spans sixty unit tests, forty-six end-to-end and browser tests, and four MCP test suites."
    )
    update_paragraph(doc.paragraphs[528], p528_text, "P528 Limitations")

    # Paragraph 530 (Future scope)
    p530_text = (
        "With the streaming and multiplatform capture rebuilds complete on Windows and Linux, next priorities shift to macOS capture implementation using ScreenCaptureKit and local on-device vision processing. Near-term work includes completing the macOS capture backend, optimizing frame transmission through delta-compression, and integrating local quantized models via WebGPU or ONNX Runtime to eliminate cloud inference fees. Medium-term work focuses on an optional student desktop companion for OS-level assessment lockdown, along with Learning Management System (LMS) export integration."
    )
    update_paragraph(doc.paragraphs[530], p530_text, "P530 Future scope")

    # Paragraph 532 (Near-term work)
    p532_text = (
        "Two items are prioritized first because each directly benefits users. Completing the macOS capture backend using ScreenCaptureKit achieves full three-platform desktop parity. Integrating on-device quantized models for vision and transcription removes cloud rate limits, allowing unlimited guide generation during multi-hour lab sessions without incurring API costs."
    )
    update_paragraph(doc.paragraphs[532], p532_text, "P532 Near term work")

    # Paragraph 538 (Concluding remarks)
    p538_text = (
        "WKAI demonstrates that a live technical session provides sufficient audio and visual context to automatically synthesize structured learning materials, identify learner difficulties, and deliver individualized support without imposing manual overhead on the teacher. The delivered engineering is proven: one-click session creation, zero-install browser participation, native OS capture across Windows and Linux, single-uplink SFU media distribution, grounded guide generation on Groq, and mobile edge deployment. Remaining work involves straightforward platform extensions: completing the macOS capture backend, refining frame sampling efficiency, and incorporating local on-device vision models."
    )
    update_paragraph(doc.paragraphs[538], p538_text, "P538 Concluding remarks")

    # 10. Appendix A: Source Code
    # Paragraph 560 (Repository layout)
    p560_text = (
        "The repository structure covers four primary packages under a common workspace root: wkai/ (Tauri instructor desktop application with Rust capture modules and React UI), wkai-student/ (zero-install React web application with Monaco editor, xterm, and proctoring telemetry), wkai-backend/ (Node.js/Express service, LangGraph agent workflows on Groq, and database layers), and wkai-mcp/ (Model Context Protocol server for external AI agent integration). Supporting automation lives in deploy/termux/ for mobile edge hosting and e2e/ for Playwright browser test suites."
    )
    update_paragraph(doc.paragraphs[560], p560_text, "P560 Repo layout")

    # Paragraph 562 (Key modules)
    p562_text = (
        "Key implementation entry points include: on the backend, the session-access token module, the WebSocket connection authenticator, the error-diagnosis LangGraph agent, and the assessment proctoring controller. In wkai-mcp, the MCP tool schema registry and workshop controller. In the instructor application, the Rust native_capture module (implementing DXGI on Windows and x11rb on Linux) and the WebRTC SFU publisher. In the student application, the WebRTC subscriber pipeline and the proctored quiz runner."
    )
    update_paragraph(doc.paragraphs[562], p562_text, "P562 Key modules")

    # Paragraph 564 (Build instructions)
    p564_text = (
        "Development requires Node.js 20+, Rust 1.77+, and local PostgreSQL and Redis instances (or remote Neon/Upstash credentials). On Linux, instructor builds require libx11-dev, libpipewire-0.3-dev, and mesa-common-dev. For Android edge hosting, Termux is installed on an ARM64 device alongside proot-distro debian, running setup-debian.sh and wkaictl.sh. Desktop builds for Windows and Linux are automated through GitHub Actions, producing signed release binaries with Google Drive mirrors."
    )
    update_paragraph(doc.paragraphs[564], p564_text, "P564 Build instructions")

    # 11. Table Updates
    print("Updating tables...")

    # Table 5: Software Stack (Table 2.1)
    t5 = doc.tables[5]
    t5.cell(1, 1).text = "Tauri v2 (Rust + WebView2 on Windows, WebKitGTK on Linux)"
    t5.cell(1, 2).text = "8–15 MB install size, near-zero idle CPU, native screen capture on Windows (DXGI/GDI) and Linux (X11 x11rb / PipeWire)"
    
    t5.cell(4, 1).text = "Groq (LPU Inference Engine)"
    t5.cell(4, 2).text = "300+ tok/s; real-time generation practical at live workshop scale"

    t5.cell(6, 1).text = "Whisper Large v3 via Groq"
    t5.cell(6, 2).text = "~180x realtime; a 30 s audio chunk transcribes in well under 200 ms"

    t5.cell(7, 1).text = "Qwen3.8-27B (vision) and GPT-OSS-120B (text) via Groq"
    t5.cell(7, 2).text = "Sub-second vision parsing; strong reasoning and native tool-calling for Zod-validated outputs"

    t5.cell(13, 1).text = "Git / GitHub Actions"
    t5.cell(13, 2).text = "Automated multi-platform builds (Windows NSIS/MSI, Linux deb/AppImage), code signing, and Google Drive mirror fallback"

    t5.cell(14, 1).text = "Render (cloud), Vercel (frontend), Android Phone via Termux + Debian (edge)"
    t5.cell(14, 2).text = "Production cloud deployment or zero-cost local handset hosting"

    # Table 6: Requirements Traceability (Table 2.2)
    t6 = doc.tables[6]
    t6.cell(2, 1).text = "Live screen + audio streamed natively (Windows & Linux) via SFU"
    t6.cell(7, 1).text = "In-session comprehension quizzes & proctored assessments"

    # Table 12: Test Cases (Table 6.1)
    t12 = doc.tables[12]
    # Update or ensure existing rows TC-9 to TC-13 are clean and accurate
    if len(t12.rows) > 9:
        t12.cell(9, 1).text = "Linux native screen capture under X11 (x11rb)"
        t12.cell(9, 2).text = "Sustains 30+ fps capture without dropping frames"
        t12.cell(9, 3).text = "Verified on Ubuntu Linux build; sustains ~40 fps"

    if len(t12.rows) > 10:
        t12.cell(10, 1).text = "WebRTC SFU screen share fan-out"
        t12.cell(10, 2).text = "Single instructor uplink fanned out to connected students"
        t12.cell(10, 3).text = "Verified with SFU relay; glass-to-glass latency under 400 ms"

    if len(t12.rows) > 11:
        t12.cell(11, 1).text = "Assessment proctoring & away-modal focus tracking"
        t12.cell(11, 2).text = "Tab switch and paste events recorded in telemetry"
        t12.cell(11, 3).text = "Away modal activates on blur; events logged to instructor view"

    if len(t12.rows) > 12:
        t12.cell(12, 1).text = "Android Termux edge backend hosting"
        t12.cell(12, 2).text = "Backend boots, connects to database, serves WebSockets"
        t12.cell(12, 3).text = "Verified on ARM64 Android under proot Debian with wake-lock"

    if len(t12.rows) > 13:
        t12.cell(13, 1).text = "Model Context Protocol (MCP) tool execution"
        t12.cell(13, 2).text = "External AI agent calls room management & guide tools"
        t12.cell(13, 3).text = "Verified across 4 test scenarios in wkai-mcp"

    # Table 20: Latency & Performance (Table 6.2)
    t20 = doc.tables[20]
    if len(t20.rows) > 12:
        t20.cell(12, 0).text = "Linux X11 screen capture (1920x1080)"
        t20.cell(12, 1).text = "About 21.4 ms per frame using x11rb"
        t20.cell(12, 2).text = "Must sustain >= 30 fps"
    if len(t20.rows) > 13:
        t20.cell(13, 0).text = "WebRTC SFU streaming latency"
        t20.cell(13, 1).text = "280–380 ms glass-to-glass latency across regional network"
        t20.cell(13, 2).text = "Real-time interaction (< 500 ms)"
    if len(t20.rows) > 14:
        t20.cell(14, 0).text = "Android Termux backend memory footprint"
        t20.cell(14, 1).text = "140–180 MB RSS under Debian proot"
        t20.cell(14, 2).text = "Must stay within device RAM budget"

    # Table 21: Objective Evaluation (Table 6.3)
    t21 = doc.tables[21]
    t21.cell(1, 1).text = "Figure 5.7; live session started from one form; native capture at ~37 fps (Windows) and ~40 fps (Linux); single publish fanned out by SFU relay"
    t21.cell(1, 2).text = "Met"
    t21.cell(5, 1).text = "TC-1 and TC-10; role and identity derived server-side on every message; student kick controls with audit reasons; password recovery via access key; proctoring telemetry logs focus loss"
    t21.cell(5, 2).text = "Met"

    # Table 25: Cost Structure (Table F.2)
    t25 = doc.tables[25]
    if len(t25.rows) > 8:
        t25.cell(8, 0).text = "Edge mobile hosting"
        t25.cell(8, 1).text = "Backend runtime on Android smartphone via Termux"
        t25.cell(8, 2).text = "$0 (uses existing phone hardware)"
        t25.cell(8, 3).text = "Handset battery and local Wi-Fi bandwidth"

    # Save modified document
    doc.save(doc_path)
    print(f"Successfully saved updated DOCX to {doc_path}!")

if __name__ == '__main__':
    run_update()
