# AGENTS.md - Development Guidelines

## Build/Lint/Test Commands
- **Build**: `npm run build` (Vite production build)
- **Dev Server**: `npm run dev` (Vite dev server with HMR)
- **Lint**: `npm run lint` (ESLint with React hooks & refresh plugins)
- **Preview**: `npm run preview` (Preview production build)
- **Single Test**: No test framework configured yet

## Code Style Guidelines
- **Language**: Modern JavaScript (ES2020+) with JSX
- **Imports**: React imports first, then utilities, then components
- **Naming**: camelCase for variables/functions, PascalCase for components
- **Components**: Functional components with hooks (useState, useEffect, useRef)
- **Styling**: TailwindCSS with cyberpunk theme (cyan/fuchsia/black palette)
- **Error Handling**: Try/catch blocks with user-friendly cyberpunk-themed messages
- **Formatting**: ESLint auto-fixable rules, 2-space indentation
- **Types**: No TypeScript, use JSDoc for complex functions

## Project Structure
- **Framework**: React 18.1.1 + Vite 7.1.2 with SWC
- **Styling**: TailwindCSS v4 with PostCSS & Autoprefixer
- **Linting**: ESLint v9 with React hooks and refresh plugins
- **Build Tool**: Vite with @vitejs/plugin-react-swc

## Development Workflow
1. Run `npm run dev` for development (cd toollama/)
2. Use `npm run lint` before commits
3. Test in browser with `npm run preview` after build
4. Follow cyberpunk theme: cyan-400/fuchsia-500 borders, Orbitron font