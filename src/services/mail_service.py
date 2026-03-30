"""Async email service for sending library notifications via SMTP."""

import asyncio
import logging
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import load_settings

logger = logging.getLogger(__name__)


def _get_mail_cfg() -> dict:
    """Load the current mail settings from settings.yml."""
    settings = load_settings()
    return settings.get("mail", {})


def _send(to: str, subject: str, html_body: str) -> None:
    """Send an email synchronously (called from a thread)."""
    cfg = _get_mail_cfg()
    if not cfg.get("host") or not cfg.get("from_address"):
        logger.warning("Mail not configured — skipping send to %s", to)
        return
    if not to:
        logger.warning("No recipient address — skipping mail '%s'", subject)
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = cfg["from_address"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    host = cfg["host"]
    port = int(cfg.get("port", 587))
    username = cfg.get("username", "")
    password = cfg.get("password", "")
    use_tls = cfg.get("use_tls", True)

    with smtplib.SMTP(host, port, timeout=15) as server:
        if use_tls:
            server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)
    logger.info("Mail sent to %s: %s", to, subject)


async def send_async(to: str, subject: str, html_body: str) -> None:
    """Send an email in a background thread so we don't block the event loop."""
    try:
        await asyncio.to_thread(_send, to, subject, html_body)
    except Exception:
        logger.exception("Failed to send email to %s", to)


class MailService:
    """High-level email operations for library notifications."""

    # ── Welcome ──────────────────────────────────────────────────────

    async def send_welcome_user(self, display_name: str, username: str, email: str) -> None:
        """Send a welcome email to a newly created application user."""
        html = f"""
        <h2>Welcome to Library Manager, {display_name or username}!</h2>
        <p>Your account has been created.</p>
        <ul>
            <li><strong>Username:</strong> {username}</li>
        </ul>
        <p>Please log in and change your password at your earliest convenience.</p>
        """
        await send_async(email, "Welcome to Library Manager", html)

    # ── Rental confirmation ──────────────────────────────────────────

    async def send_rental_confirmation(self, client_name: str, client_email: str,
                                       book_title: str, due_date: str) -> None:
        """Notify a client that they have rented a book."""
        html = f"""
        <h2>Rental Confirmation</h2>
        <p>Dear {client_name},</p>
        <p>You have rented the following book:</p>
        <ul>
            <li><strong>Book:</strong> {book_title}</li>
            <li><strong>Due date:</strong> {due_date}</li>
        </ul>
        <p>Please return it on or before the due date. Thank you!</p>
        """
        await send_async(client_email, f"Rental Confirmation: {book_title}", html)

    # ── Return confirmation ──────────────────────────────────────────

    async def send_return_confirmation(self, client_name: str, client_email: str,
                                       book_title: str) -> None:
        """Notify a client that their book has been returned."""
        html = f"""
        <h2>Book Returned</h2>
        <p>Dear {client_name},</p>
        <p>The following book has been returned successfully:</p>
        <ul>
            <li><strong>Book:</strong> {book_title}</li>
        </ul>
        <p>Thank you for using our library!</p>
        """
        await send_async(client_email, f"Book Returned: {book_title}", html)

    # ── Due-date reminders ───────────────────────────────────────────

    async def send_due_reminder(self, client_name: str, client_email: str,
                                book_title: str, due_date: str) -> None:
        """Remind a client their book is due in 2 days."""
        html = f"""
        <h2>Rental Due Soon</h2>
        <p>Dear {client_name},</p>
        <p>This is a friendly reminder that your rental is due soon:</p>
        <ul>
            <li><strong>Book:</strong> {book_title}</li>
            <li><strong>Due date:</strong> {due_date}</li>
        </ul>
        <p>Please return it on time to avoid overdue notices.</p>
        """
        await send_async(client_email, f"Reminder: \"{book_title}\" due on {due_date}", html)

    async def send_overdue_notice(self, client_name: str, client_email: str,
                                  book_title: str, due_date: str) -> None:
        """Notify a client their book is overdue."""
        html = f"""
        <h2>Book Overdue</h2>
        <p>Dear {client_name},</p>
        <p>The following book is <strong>overdue</strong>:</p>
        <ul>
            <li><strong>Book:</strong> {book_title}</li>
            <li><strong>Was due:</strong> {due_date}</li>
        </ul>
        <p>Please return it as soon as possible.</p>
        """
        await send_async(client_email, f"OVERDUE: \"{book_title}\" was due {due_date}", html)

    # ── Batch check (called periodically) ────────────────────────────

    async def check_and_send_reminders(self, rentals: list) -> None:
        """Scan active rentals and send due-soon / overdue emails.

        Args:
            rentals: List of active Rental entities (with book and client loaded).
        """
        today = date.today()
        reminder_date = (today + timedelta(days=2)).isoformat()

        for rental in rentals:
            if not rental.due_date or not rental.client.email:
                continue
            if rental.due_date < today.isoformat():
                await self.send_overdue_notice(
                    rental.client.name, rental.client.email,
                    rental.book.title, rental.due_date)
            elif rental.due_date <= reminder_date:
                await self.send_due_reminder(
                    rental.client.name, rental.client.email,
                    rental.book.title, rental.due_date)
