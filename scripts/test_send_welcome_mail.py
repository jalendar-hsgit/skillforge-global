import asyncio
from app.services.email_service import email_service

async def main():
    to = "test@example.com"  # replace with desired recipient or use Mailhog
    name = "Smoke Tester"
    ok = await email_service.send_welcome_email(to, name)
    print("send_welcome_email returned:", ok)

if __name__ == '__main__':
    asyncio.run(main())
