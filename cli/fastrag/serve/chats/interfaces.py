from abc import ABC, abstractmethod
from uuid import UUID

from fastrag.serve.chats.model import Chat, ChatMessage
from fastrag.serve.chats.schemas import ChatMessageCreate
from fastrag.serve.paging import Page, PageParameters


class IChatService(ABC):
    @abstractmethod
    async def get_chat(
        self,
        id: UUID,
        include_messages: bool = False,
    ) -> Chat | None:
        """Get chat from ID

        Args:
            id (UUID): chat id
            include_messagess (bool): include the chat messages. Defaults to True.

        Returns:
            Chat | None: chat if found
        """

    @abstractmethod
    async def get_page(
        self,
        page_parameters: PageParameters,
    ) -> Page[Chat]:
        """Get page of chats

        Args:
            page_parameters (PageParameters): Pagination parameters

        Returns:
            Page[Chat]: Page of chats
        """

    @abstractmethod
    async def save_message(
        self,
        data: ChatMessageCreate,
        ip: str | None = None,
        country: str | None = None,
    ) -> ChatMessage:
        """Save a message

        Args:
            data (ChatMessageCreate): New chat message data
            ip (str | None, optional): User IP. Defaults to None.
            country (str | None, optional): User country. Defaults to None.

        Returns:
            ChatMessage: the created message.
        """


class IChatRepository(ABC):
    @abstractmethod
    async def get_chat(
        self,
        id: UUID,
        include_messages: bool = True,
    ) -> Chat | None:
        """Get chat from ID

        Args:
            id (UUID): chat id
            include_messagess (bool): include the chat messages. Defaults to True.

        Returns:
            Chat | None: chat if found
        """

    @abstractmethod
    async def save_message(
        self,
        message: ChatMessageCreate,
        ip: str | None = None,
        country: str | None = None,
    ) -> ChatMessage:
        """Save a new message to the database

        Args:
            message (ChatMessageCreate): to be saved
            ip (str | None, optional): User IP. Defaults to None.
            country (str | None, optional): User country. Defaults to None.

        Returns:
            ChatMessage: the created message.
        """

    @abstractmethod
    async def get_chats(
        self,
        pagination: PageParameters,
    ) -> Page[Chat]:
        """Get a page of chats

        Args:
            pagination (PageParameters): pagination parameters

        Returns:
            Page[Chat]: page of chats
        """
