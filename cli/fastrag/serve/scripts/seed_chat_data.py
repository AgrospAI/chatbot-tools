import random

from faker import Faker
from sqlalchemy.orm import Session

from fastrag.config.settings import settings
from fastrag.serve.db import get_db
from fastrag.serve.db.models import Chat, ChatMessage

fake = Faker()

engine, SessionLocal, _ = get_db(settings)

ROLES = ["user", "assistant", "system"]


def seed_chats(
    db: Session,
    num_chats: int = 50,
    min_messages: int = 3,
    max_messages: int = 15,
):
    print(f"Seeding {num_chats} chats...")
    chats = []
    total_messages = 0

    for i in range(num_chats):
        chat = Chat(
            ip=fake.ipv4(),
            country=fake.country(),
        )
        num_messages = random.randint(min_messages, max_messages)
        for _ in range(num_messages):
            message = ChatMessage(
                role=random.choice(ROLES),
                content=fake.paragraph(nb_sentences=3),
                sources=[fake.url() for _ in range(random.randint(0, 3))] or None,
            )
            chat.messages.append(message)
        chats.append(chat)
        total_messages += num_messages
        # Print progress every 10 chats or at the end
        if (i + 1) % 10 == 0 or (i + 1) == num_chats:
            print(f"  Progress: {i + 1}/{num_chats} chats seeded...")

    db.add_all(chats)
    db.commit()
    print(f"Seeding completed: {len(chats)} chats and {total_messages} messages added.")


if __name__ == "__main__":
    print("Starting chat data seeding script...")
    db = SessionLocal()
    try:
        seed_chats(db)
    finally:
        db.close()
    print("Database session closed. Script finished.")
