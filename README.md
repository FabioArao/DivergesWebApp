# DivergesApp - Educational Portal

## Overview

DivergesApp is a comprehensive educational platform designed to facilitate learning and interaction between students, teachers, and guardians.

## Prerequisites

- Docker and Docker Compose
- Firebase Project
- Node.js 18+
- Python 3.10+

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/DivergesApp.git
cd DivergesApp
```

### 2. Firebase Configuration

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Go to Project Settings
3. Navigate to Service Accounts
4. Generate a new private key (download JSON)

### 3. Environment Configuration

#### Frontend Environment
```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env` and fill in your Firebase configuration:
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- Other Firebase-related variables

#### Backend Environment
```bash
cd ../backend
cp .env.example .env
```

Edit `backend/.env` and configure:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY` (from Firebase service account JSON)
- `FIREBASE_CLIENT_EMAIL`
- Database and other settings

### 4. Running the Application

#### Option 1: Docker Deployment (Recommended)
```bash
# Ensure you're in the project root directory
docker-compose up --build
```

#### Option 2: Local Development

##### Backend Terminal
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

##### Frontend Terminal
```bash
cd frontend
npm install
npm run dev
```

## Application Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Verify all environment variables are set
   - Check available disk space
   - Update Docker and Docker Compose

2. **Firebase Configuration**
   - Double-check Firebase project settings
   - Ensure private key is correctly formatted
   - Verify service account permissions

3. **No Space Left on Device**
   ```bash
   # Clear Docker cache
   docker system prune -a
   ```

### Debugging

- Check Docker logs: `docker-compose logs`
- Verify environment variables
- Ensure Firebase credentials are correct

## Technology Stack

### Backend
- Framework: FastAPI
- ORM: SQLAlchemy
- Database: PostgreSQL
- Authentication: Firebase Admin SDK

### Frontend
- Framework: Next.js
- State Management: React Context
- Authentication: Firebase
- Styling: Tailwind CSS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
