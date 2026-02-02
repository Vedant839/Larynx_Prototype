#!/usr/bin/env python3
"""
Text Buffer for Larynx ASR Tool.

Manages transcription text accumulation with proper handling of
partial and final results, text formatting, and thread-safe operations.
"""

import threading
import re

class TextBuffer:
    """
    Thread-safe text buffer for managing ASR transcription results.

    Handles partial results (real-time updates) and final results (confirmed text),
    with automatic formatting and deduplication.
    """

    def __init__(self):
        """Initialize the text buffer."""
        self.lock = threading.Lock()
        self.final_text = ""  # Confirmed, immutable text
        self.partial_text = ""  # Current partial result (may change)
        self.last_partial_length = 0  # Track partial text length for deduplication

    def add_partial_text(self, text):
        """
        Update the current partial transcription text.

        Args:
            text (str): New partial text from ASR engine
        """
        with self.lock:
            if text:
                # Clean and format the partial text
                cleaned = self._clean_text(text)
                self.partial_text = cleaned
            else:
                self.partial_text = ""

    def add_final_text(self, text):
        """
        Add confirmed final text to the buffer.

        Args:
            text (str): Confirmed final text from ASR engine
        """
        with self.lock:
            if text:
                cleaned = self._clean_text(text)
                self.final_text += cleaned + " "
                # Clear partial after committing
                self.partial_text = ""

    def get_full_text(self):
        """
        Get the complete formatted transcription text.

        Returns:
            str: All final text plus current partial text
        """
        with self.lock:
            full_text = self.final_text + self.partial_text
            return self._format_text(full_text.strip())

    def get_final_text_only(self):
        """
        Get only the confirmed final text (without partial).

        Returns:
            str: Formatted final text only
        """
        with self.lock:
            return self._format_text(self.final_text.strip())

    def get_partial_text_only(self):
        """
        Get only the current partial text.

        Returns:
            str: Current partial text
        """
        with self.lock:
            return self.partial_text

    def clear(self):
        """Clear all text from the buffer."""
        with self.lock:
            self.final_text = ""
            self.partial_text = ""
            self.last_partial_length = 0

    def _clean_text(self, text):
        """
        Clean raw text from ASR engine.

        Args:
            text (str): Raw text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())

        # Remove common ASR artifacts (if any)
        # Add more cleaning rules as needed

        return cleaned

    def _format_text(self, text):
        """
        Format text for display: capitalization, punctuation, etc.

        Args:
            text (str): Raw text

        Returns:
            str: Formatted text
        """
        if not text:
            return ""

        # Ensure single space between words
        formatted = re.sub(r'\s+', ' ', text.strip())

        # Capitalize first letter of text
        if formatted:
            formatted = formatted[0].upper() + formatted[1:]

        # Capitalize after sentence endings
        formatted = re.sub(r'([.!?]\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(), formatted)

        return formatted

    def get_word_count(self):
        """
        Get the total word count of final text.

        Returns:
            int: Number of words in final text
        """
        with self.lock:
            return len(self.final_text.split())

    def is_empty(self):
        """
        Check if buffer is empty.

        Returns:
            bool: True if no text in buffer
        """
        with self.lock:
            return not self.final_text and not self.partial_text


# Test function for standalone testing
def test_text_buffer():
    """Test the text buffer functionality."""
    print("Testing TextBuffer...")

    buffer = TextBuffer()

    # Test partial text
    print("Adding partial text: 'hello'")
    buffer.add_partial_text("hello")
    print(f"Full text: '{buffer.get_full_text()}'")

    print("Adding partial text: 'hello world'")
    buffer.add_partial_text("hello world")
    print(f"Full text: '{buffer.get_full_text()}'")

    # Test final text
    print("Adding final text: 'hello world'")
    buffer.add_final_text("hello world")
    print(f"Full text: '{buffer.get_full_text()}'")

    # Test more text
    print("Adding partial text: 'how are'")
    buffer.add_partial_text("how are")
    print(f"Full text: '{buffer.get_full_text()}'")

    print("Adding final text: 'how are you'")
    buffer.add_final_text("how are you")
    print(f"Full text: '{buffer.get_full_text()}'")

    # Test formatting
    print("Adding final text: 'this is a test. hello world'")
    buffer.add_final_text("this is a test. hello world")
    print(f"Formatted text: '{buffer.get_full_text()}'")

    print(f"Word count: {buffer.get_word_count()}")

    print("Clearing buffer...")
    buffer.clear()
    print(f"After clear: '{buffer.get_full_text()}'")

    print("TextBuffer test complete")


if __name__ == "__main__":
    test_text_buffer()