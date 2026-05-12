"""
Streaming with Anthropic Claude via AWS Bedrock

This module demonstrates two approaches to streaming responses from Claude:
1. Low-level event streaming with manual event handling
2. High-level streaming with automatic text extraction
"""

import logging
from anthropic import AnthropicBedrockMantle
from anthropic.types import Message

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeStreaming:
    """
    A class demonstrating streaming patterns with Claude via AWS Bedrock.

    This class provides examples of both raw event streaming and simplified
    text streaming approaches for real-time AI responses.
    """

    def __init__(self, model: str = "anthropic.claude-opus-4-7"):
        """
        Initialize the streaming tutorial with an Anthropic Bedrock client.

        Args:
            model: The Claude model identifier to use for streaming.
                  Default is "anthropic.claude-opus-4-7".
        """
        self.client = AnthropicBedrockMantle()
        self.model = model
        logger.info(f"Initialized ClaudeStreamingTutorial with model: {model}")

    def stream_with_raw_events(self, prompt: str, max_tokens: int = 256) -> None:
        """
        Demonstrate low-level streaming with raw event handling.

        This method shows how to process individual streaming events, giving you
        fine-grained control over the streaming lifecycle. Useful when you need
        to handle specific events differently or track detailed streaming metrics.

        Event Flow:
            1. RawMessageStartEvent - Contains message ID, model, initial usage stats
            2. RawContentBlockStartEvent - Signals new content block (text/tool_use)
            3. RawContentBlockDeltaEvent - Multiple events with incremental text chunks
            4. RawContentBlockStopEvent - Signals content block completion
            5. RawMessageDeltaEvent - Contains stop_reason and final usage stats
            6. RawMessageStopEvent - Final event signaling stream end

        Args:
            prompt: The user prompt to send to Claude.
            max_tokens: Maximum tokens to generate in the response.

        Example:
            >>> tutorial = ClaudeStreamingTutorial()
            >>> tutorial.stream_with_raw_events("Write me a story")
        """
        logger.info("Starting raw event streaming...")

        stream = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        print("\n" + "="*70)
        print("RAW EVENT STREAMING")
        print("="*70 + "\n")

        for event in stream:
            event_type = type(event).__name__
            print(f"📦 Event Type: {event_type}")
            print(f"   Data: {event}")
            print("-" * 70)

        logger.info("Raw event streaming completed")

    def stream_with_text_extraction(self, prompt: str, max_tokens: int = 256) -> Message:
        """
        Demonstrate high-level streaming with automatic text extraction.

        This method uses the context manager approach to automatically handle
        event processing and extract only the text content. This is the recommended
        approach for most use cases where you just need the generated text.

        The context manager:
            - Automatically handles connection lifecycle
            - Provides a clean text_stream iterator
            - Accumulates the final message for post-processing
            - Ensures proper cleanup even if errors occur

        Args:
            prompt: The user prompt to send to Claude.
            max_tokens: Maximum tokens to generate in the response.

        Returns:
            Message: The final complete message object containing all metadata,
                    usage statistics, and the full generated content.

        Example:
            >>> tutorial = ClaudeStreamingTutorial()
            >>> message = tutorial.stream_with_text_extraction("Write me a story")
            >>> print(f"Tokens used: {message.usage.output_tokens}")
        """
        logger.info("Starting text stream extraction...")

        print("\n" + "="*70)
        print("HIGH-LEVEL TEXT STREAMING")
        print("="*70 + "\n")

        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            print("📝 Streaming text: ", end="", flush=True)

            for text in stream.text_stream:
                print(text, end="", flush=True)

            print("\n")  # New line after streaming completes

        # Access the final message after the context manager closes
        final_message = stream.get_final_message()

        logger.info(f"Text streaming completed. Tokens used: {final_message.usage.output_tokens}")
        return final_message

    def compare_streaming_methods(self, prompt: str) -> None:
        """
        Run both streaming methods sequentially for comparison.

        This method demonstrates the differences between raw event handling
        and simplified text streaming, helping you choose the right approach
        for your use case.

        Use raw events when:
            - You need to handle tool use events
            - You want to track detailed streaming metrics
            - You need custom logic for different event types

        Use text streaming when:
            - You only need the generated text
            - You want simpler, more readable code
            - You're building chat interfaces or text generation apps

        Args:
            prompt: The user prompt to send to Claude.

        Example:
            >>> tutorial = ClaudeStreamingTutorial()
            >>> tutorial.compare_streaming_methods("Explain quantum computing")
        """
        print("\n" + "🔄 COMPARING STREAMING METHODS ".center(70, "="))

        # Method 1: Raw events
        self.stream_with_raw_events(prompt, max_tokens=150)

        # Method 2: Text extraction
        final_message = self.stream_with_text_extraction(prompt, max_tokens=150)

        # Display final message details
        print("\n" + "="*70)
        print("FINAL MESSAGE DETAILS")
        print("="*70)
        print(f"Message ID: {final_message.id}")
        print(f"Model: {final_message.model}")
        print(f"Stop Reason: {final_message.stop_reason}")
        print(f"Input Tokens: {final_message.usage.input_tokens}")
        print(f"Output Tokens: {final_message.usage.output_tokens}")
        print("="*70 + "\n")


def main():
    """
    Main function demonstrating the streaming tutorial.

    This function creates a tutorial instance and runs examples of both
    streaming methods, providing a complete overview of streaming capabilities.
    """
    # Initialize the tutorial
    tutorial = ClaudeStreaming()

    # Example 1: Raw event streaming
    print("\n🎯 EXAMPLE 1: Raw Event Streaming")
    tutorial.stream_with_raw_events("Write me a short story in 200 words.")

    # Example 2: Text streaming
    print("\n🎯 EXAMPLE 2: Text Streaming")
    message = tutorial.stream_with_text_extraction("Write me a short story in 200 words.")

    # Example 3: Compare both methods
    print("\n🎯 EXAMPLE 3: Comparing Both Methods")
    tutorial.compare_streaming_methods("Tell me a short joke")


if __name__ == "__main__":
    main()