# CarbonPilot AI - Frontend

The frontend is a modern Next.js 14 application built with React and TailwindCSS. It provides a dynamic, accessible, and highly responsive user interface for uploading utility bills, simulating climate scenarios, and chatting with the AI coach.

## Prerequisites
- Node.js 18+
- npm, yarn, pnpm, or bun

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Variables
Create a `.env.local` file in the `frontend` directory (if needed for any future integrations). Currently, the frontend connects directly to the local backend API.

### 3. Run the Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure
- `src/app/`: Next.js App Router pages and layouts.
- `src/components/`: Reusable React components.
- `src/lib/`: Helper functions and utilities.

## Features
- **OCR Upload**: Drag-and-drop interface for uploading utility bills.
- **Interactive Simulator**: Real-time evaluation of stacked lifestyle changes.
- **AI Chat Coach**: Context-aware chat interface for personalized sustainability advice.
