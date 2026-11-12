from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media,
    list_audio_messages as whatsapp_list_audio_messages,
)
import json
import os
import subprocess

# Initialize FastMCP server
mcp = FastMCP("whatsapp")

MACPARAKEET_CLI = os.environ.get(
    "MACPARAKEET_CLI", "/Applications/MacParakeet.app/Contents/MacOS/macparakeet-cli"
)
# Transcripts go to this database unless save_to_library is set, so the MacParakeet library
# doesn't fill up with copies of WhatsApp audio.
TRANSCRIPTS_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "whatsapp-bridge", "store", "transcripts.db"
)

@mcp.tool()
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@mcp.tool()
def list_messages(
    after: Optional[str] = None,
    before: Optional[str] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        after: Optional ISO-8601 formatted string to only return messages after this date
        before: Optional ISO-8601 formatted string to only return messages before this date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    messages = whatsapp_list_messages(
        after=after,
        before=before,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    return messages

@mcp.tool()
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@mcp.tool()
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@mcp.tool()
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@mcp.tool()
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@mcp.tool()
def get_last_interaction(jid: str) -> str:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@mcp.tool()
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    return context

@mcp.tool()
def send_message(
    recipient: str,
    message: str
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
    
    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }
    
    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_file(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send a file such as a picture, raw audio, video or document via WhatsApp to the specified recipient. For group messages use the JID.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the media file to send (image, video, document)
    
    Returns:
        A dictionary containing success status and a status message
    """
    
    # Call the whatsapp_send_file function
    success, status_message = whatsapp_send_file(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def send_audio_message(recipient: str, media_path: str) -> Dict[str, Any]:
    """Send any audio file as a WhatsApp audio message to the specified recipient. For group messages use the JID. If it errors due to ffmpeg not being installed, use send_file instead.
    
    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        media_path: The absolute path to the audio file to send (will be converted to Opus .ogg if it's not a .ogg file)
    
    Returns:
        A dictionary containing success status and a status message
    """
    success, status_message = whatsapp_audio_voice_message(recipient, media_path)
    return {
        "success": success,
        "message": status_message
    }

@mcp.tool()
def download_media(message_id: str, chat_jid: str) -> Dict[str, Any]:
    """Download media from a WhatsApp message and get the local file path.
    
    Args:
        message_id: The ID of the message containing the media
        chat_jid: The JID of the chat containing the message
    
    Returns:
        A dictionary containing success status, a status message, and the file path if successful
    """
    file_path = whatsapp_download_media(message_id, chat_jid)
    
    if file_path:
        return {
            "success": True,
            "message": "Media downloaded successfully",
            "file_path": file_path
        }
    else:
        return {
            "success": False,
            "message": "Failed to download media"
        }

@mcp.tool()
def list_audio_messages(chat_jid: str, limit: int = 10, from_me: Optional[bool] = None) -> List[Dict[str, Any]]:
    """List a chat's audio messages and voice notes, newest first.

    Args:
        chat_jid: The chat's JID (a phone-number JID or an @lid JID; check both for one person)
        limit: Maximum number of messages to return (default 10)
        from_me: True for only audio you sent, False for only audio you received, None for both

    Returns:
        A list with message_id, timestamp, is_from_me, sender, file_bytes, and approx_minutes
        (an estimate from the file size; the transcript reports the exact duration)
    """
    return whatsapp_list_audio_messages(chat_jid, limit, from_me)


@mcp.tool()
def transcribe_audio_message(
    message_id: str,
    chat_jid: str,
    engine: str = "parakeet",
    language: Optional[str] = None,
    save_to_library: bool = False,
) -> Dict[str, Any]:
    """Download a WhatsApp audio message and transcribe it locally with MacParakeet.

    Nothing leaves this Mac. Parakeet is fastest; it detects the language itself but can
    drift into English on fast non-English speech. For non-English audio, Whisper with an
    explicit language is more accurate.

    Args:
        message_id: The audio message's ID (from list_audio_messages or list_messages)
        chat_jid: The JID of the chat that contains the message
        engine: "parakeet" (default, fastest) or "whisper" (pass language for non-English audio)
        language: Language code for Whisper, such as "es" or "en". Parakeet ignores it.
        save_to_library: Also save the transcript to the MacParakeet app's library (default False)

    Returns:
        success, transcript, duration_seconds, engine, language, and the local audio file_path
    """
    if engine not in ("parakeet", "whisper"):
        return {"success": False, "message": "engine must be 'parakeet' or 'whisper'"}
    file_path = whatsapp_download_media(message_id, chat_jid)
    if not file_path:
        return {"success": False, "message": "Failed to download the audio; is the bridge running?"}

    command = [MACPARAKEET_CLI, "transcribe", file_path, "--engine", engine,
               "--speaker-detection", "off", "-f", "json"]
    if engine == "whisper" and language:
        command += ["--language", language]
    if not save_to_library:
        command += ["--database", TRANSCRIPTS_DB]
    try:
        run = subprocess.run(
            command, capture_output=True, text=True, timeout=1800,
            env={**os.environ, "MACPARAKEET_TELEMETRY": "0"},
        )
    except FileNotFoundError:
        return {"success": False, "message": f"MacParakeet CLI not found at {MACPARAKEET_CLI}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Transcription timed out after 30 minutes"}
    if run.returncode != 0:
        return {"success": False, "message": (run.stderr or run.stdout).strip()[-1000:]}
    try:
        result = json.loads(run.stdout)
    except json.JSONDecodeError:
        return {"success": False, "message": "MacParakeet returned output that isn't JSON"}
    return {
        "success": True,
        "transcript": result.get("rawTranscript", ""),
        "duration_seconds": round((result.get("durationMs") or 0) / 1000),
        "engine": f"{result.get('engine')} {result.get('engineVariant')}",
        "language": result.get("language"),
        "file_path": file_path,
    }


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')