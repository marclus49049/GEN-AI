# Todo App Frontend

A React TypeScript application for managing public and private todos with Material-UI.

## Features

- **Public Todos**: Accessible without authentication
- **Private Todos**: Secure personal todos with JWT authentication
- **User Authentication**: Register and login functionality
- **Material-UI**: Professional and responsive design
- **TypeScript**: Type-safe development
- **React Query**: Efficient server state management

## Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` if your backend runs on a different port

## Development

Run the development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
src/
├── api/          # API service layer
├── components/   # Reusable components
├── contexts/     # React contexts (Auth)
├── hooks/        # Custom React hooks
├── pages/        # Page components
├── theme/        # MUI theme configuration
├── types/        # TypeScript types
└── utils/        # Utility functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint