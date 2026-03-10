"""
Telegram Interface — entrypoint for Phase 1.

Runs a long-polling bot that routes messages to the Orchestrator via Guardrails.
"""

import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from guardrails.validator import ValidationError
from core.orchestrator import Orchestrator, UserInputError

logger = logging.getLogger(__name__)


class TelegramInterface:
    """
    Telegram Bot interface.

    Responsibilities:
    - Listen for Telegram messages.
    - Pass input through Validator.
    - Call Orchestrator if valid.
    - Return output to user.
    """

    def __init__(self, token: str, orchestrator: Orchestrator) -> None:
        if not token:
            raise ValueError("Telegram Bot Token is required.")
            
        self._app = Application.builder().token(token).build()
        self._orchestrator = orchestrator

        # Register handlers
        self._app.add_handler(CommandHandler("start", self._start_command))
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        msg = (
            "Xin chào! Tôi là Personal AI Orchestrator.\n"
            "Tôi có thể giúp bạn:\n"
            "- Thêm / Xem chi tiêu\n"
            "- Tạo / Xem lịch trình\n"
            "Hãy gửi tin nhắn cho tôi!"
        )
        if update.message:
            await update.message.reply_text(msg)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages."""
        if not update.message or not update.message.text:
            return

        user_input = update.message.text
        logger.info(f"Received message: {user_input!r}")

        try:
            # Orchestrator handles validation, routing, dispatch and LLM fallback.
            # Using to_thread guarantees we don't block the main asyncio loop.
            response = await asyncio.to_thread(self._orchestrator.handle, user_input)

            # Reply
            await update.message.reply_text(response)

        except UserInputError as exc:
            logger.warning(f"Validation error: {exc}")
            await update.message.reply_text("Xin lỗi, tin nhắn không hợp lệ.")
            
        except Exception as exc:
            logger.error(f"Orchestrator error: {exc}", exc_info=True)
            await update.message.reply_text("Xin lỗi, có lỗi hệ thống xảy ra.")

    def run(self) -> None:
        """Start the bot in polling mode."""
        logger.info("Starting Telegram Bot...")
        self._app.run_polling(allowed_updates=Update.ALL_TYPES)
