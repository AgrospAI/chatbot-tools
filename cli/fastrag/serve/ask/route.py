import time
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse

from fastrag.llms.llm import ILLM
from fastrag.logging import logger
from fastrag.serve.ask.dependencies import get_llm
from fastrag.serve.ask.schemas import QuestionRequest, QuestionResponse
from fastrag.serve.chats.deps import get_chat_service
from fastrag.serve.chats.interfaces import IChatService
from fastrag.serve.chats.schemas import ChatMessageCreate
from fastrag.serve.geolocalization.deps import ClientInfo, get_client_info
from fastrag.serve.prompt_builder.deps import get_prompt_builder
from fastrag.serve.prompt_builder.interfaces import IPromptBuilder
from fastrag.serve.rate_limiting import limiter
from fastrag.serve.telemetry.metrics import llm_time_to_first_token

router = APIRouter(
    prefix="/ask",
    tags=["ask"],
)


@router.post(
    "/",
    response_class=StreamingResponse,
)
@limiter.limit("5/minute")
async def ask_question(
    request: Request,  # Required by slowapi limiter
    req: QuestionRequest,
    llm: Annotated[ILLM, Depends(get_llm)],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
    client_info: Annotated[ClientInfo, Depends(get_client_info)],
    response_builder: Annotated[IPromptBuilder, Depends(get_prompt_builder)],
    background_tasks: BackgroundTasks,
):
    active_chat_id = req.chat_id or uuid.uuid4()

    # Save the received user message in the background
    background_tasks.add_task(
        chat_service.save_message,
        data=ChatMessageCreate(
            chat_id=active_chat_id,
            content=req.question,
            role="user",
        ),
        ip=client_info.ip,
        country=client_info.country,
    )

    async def generate_answer():
        start_time = time.monotonic()
        answer_chunks: list[str] = []
        context = await response_builder.get_context(req.question)

        logger.info("Context %s", context)

        yield QuestionResponse(type="sources", data=context.sources)

        stream = llm.stream(context.prompt)
        try:
            # Get the first chunk to calculate timedelta
            first_chunk = await stream.__anext__()
            answer_chunks.append(first_chunk)

            llm_time_to_first_token.record(time.monotonic() - start_time, {})

            yield QuestionResponse(type="token", data=first_chunk)

            # Consume the rest of the generator
            async for token in stream:
                answer_chunks.append(token)
                yield QuestionResponse(type="token", data=token)

        except StopAsyncIteration:
            pass

        finally:
            full_answer = "".join(answer_chunks)
            background_tasks.add_task(
                chat_service.save_message,
                data=ChatMessageCreate(
                    chat_id=active_chat_id,
                    content=full_answer,
                    role="assistant",
                    sources=context.sources,
                ),
            )

    return StreamingResponse(
        content=generate_answer(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
