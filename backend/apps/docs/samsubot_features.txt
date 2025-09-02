SamsuBot is a chatbot framework designed for intelligent conversations,
retrieval-augmented generation (RAG), and system integrations.

Key Features:
- Natural language understanding
- Knowledge base integration
- Multi-database support (Postgres, MongoDB, Chroma)
- Secure authentication with JWT

System Requirements

Docker & Docker Compose

Python 3.10+

2GB RAM minimum

Stable internet connection

Installation

Clone repo: git clone https://github.com/your-repo/samsubot.git

Configure .env.dev

Start services: docker-compose up --build

API available at: http://localhost:8000/api/v2

Using SamsuBot

Health check: /api/v2/heartbeat

Send chat messages: /api/v2/chat

Manage users: JWT authentication

Store logs: Postgres/MongoDB integration

Knowledge base queries: Chroma vector DB

Benefits

Business efficiency with 24/7 automated support

Context-aware responses with RAG

Easy deployment and scaling

Secure and customizable

Troubleshooting & FAQ

API not responding? → Check if containers are running.

Auth errors? → Verify JWT_SECRET in .env.dev.

Database not connecting? → Ensure Postgres & MongoDB services are healthy.

Contact
For support, reach out to:
Nurul Islam Choudhury
📧 tutulbims@gmail.com
 | 📞 +91 9741546661