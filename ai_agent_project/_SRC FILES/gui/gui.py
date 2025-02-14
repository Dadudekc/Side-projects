# gui.py

"""
GUI for AI Agent Interaction using Dear PyGui

This module defines the graphical user interface (GUI) using Dear PyGui.
The GUI allows users to send messages to the AI agent, view responses,
maintain a chat history, and utilize additional features like saving and
clearing the chat.
"""

import dearpygui.dearpygui as dpg
import threading
import datetime
import logging
import os

class AIAgentGUI:
    def __init__(self, agent):
        """
        Initialize the GUI with the AI agent instance.

        Args:
            agent (AIAgentWithMemory): The AI agent to interact with.
        """
        self.agent = agent

        # Initialize chat history storage
        self.chat_history = []

        # Configure logging
        if not os.path.exists("logs"):
            os.makedirs("logs")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler("logs/gui.log"),
                logging.StreamHandler()
            ]
        )
        logging.info("Initialized GUI for AI Agent.")

    def send_message(self, sender, app_data):
        """
        Callback function to send the user's message to the AI agent and display the response.

        Args:
            sender: The widget ID that triggered the callback.
            app_data: Additional data from the widget (unused).
        """
        user_message = dpg.get_value("Input")
        if user_message.strip():
            # Display user's message in the chat area
            self.display_message(f"You: {user_message}", "user")

            # Clear the input box for the next message
            dpg.set_value("Input", "")

            # Show loading indicator
            dpg.configure_item("LoadingIndicator", show=True)

            # Get the AI's response in a separate thread to avoid freezing the GUI
            threading.Thread(target=self.get_ai_response, args=(user_message,)).start()

    def get_ai_response(self, user_message):
        """
        Get the AI's response to the user input and display it.

        Args:
            user_message (str): The user's message to the AI.
        """
        try:
            ai_response = self.agent.chat(user_message)
            # Update the GUI after receiving the response (on the main thread)
            dpg.configure_item("LoadingIndicator", show=False)
            self.display_message(f"{self.agent.name}: {ai_response}", "ai")
            logging.info(f"AI Response: {ai_response}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            dpg.configure_item("LoadingIndicator", show=False)
            self.display_message(error_msg, "error")
            logging.error(f"AI Interaction Error: {str(e)}")

    def display_message(self, message, sender_type):
        """
        Display a message in the chat display area with appropriate styling.

        Args:
            message (str): The message to display.
            sender_type (str): Type of sender ('user', 'ai', 'error') to apply styling.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Append to chat history
        self.chat_history.append(formatted_message)

        # Determine text color based on sender type
        if sender_type == "user":
            color = (0, 0, 255)  # Blue
        elif sender_type == "ai":
            color = (0, 128, 0)  # Green
        elif sender_type == "error":
            color = (255, 0, 0)  # Red
        else:
            color = (255, 255, 255)  # White as default

        # Add text to the chat display with specified color
        dpg.add_text(formatted_message, color=color, parent="ChatDisplay")

        # Scroll to the bottom of the chat display
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """
        Scroll to the bottom of the chat display.
        """
        # Get the total scroll height of the chat display
        total_scroll_y = dpg.get_y_scroll_max("ChatDisplay")

        # Set the scroll to the maximum (bottom)
        dpg.set_y_scroll("ChatDisplay", total_scroll_y)

    def clear_chat(self):
        """
        Clear the chat history.
        """
        self.chat_history = []
        # Remove all children from the chat display
        children = dpg.get_item_children("ChatDisplay", slot=0)
        for child in children:
            dpg.delete_item(child)
        logging.info("Chat history cleared.")

    def save_chat(self):
        """
        Save the current chat history to a text file.
        """
        if not self.chat_history:
            dpg.set_value("StatusText", "No chat history to save.")
            return

        # Create chat_logs directory if it doesn't exist
        if not os.path.exists("chat_logs"):
            os.makedirs("chat_logs")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_logs/chat_history_{timestamp}.txt"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                for message in self.chat_history:
                    f.write(message + "\n")
            dpg.set_value("StatusText", f"Chat history saved to {filename}.")
            logging.info(f"Chat history saved to {filename}.")
        except Exception as e:
            dpg.set_value("StatusText", f"Failed to save chat history: {str(e)}")
            logging.error(f"Failed to save chat history: {str(e)}")

    def run(self):
        """
        Start the Dear PyGui main loop with the enhanced GUI layout.
        """
        # Build the UI layout
        dpg.create_context()

        with dpg.window(label=f"{self.agent.name} - AI Chat", width=700, height=600, pos=(100, 100)):
            # Menu Bar
            with dpg.menu_bar():
                with dpg.menu(label="Options"):
                    dpg.add_menu_item(label="Clear Chat", callback=self.clear_chat)
                    dpg.add_menu_item(label="Save Chat History", callback=self.save_chat)
                    dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

            # Chat Display Area within a child window for scrolling
            dpg.add_text(f"Chat with {self.agent.name}", bullet=True)
            with dpg.child_window(label="Chat History", tag="ChatDisplay", width=680, height=450, autosize_x=False, autosize_y=False, border=True):
                pass  # Messages will be added here dynamically

            # Loading Indicator (hidden by default)
            dpg.add_text("Loading...", tag="LoadingIndicator", color=(255, 165, 0), show=False)

            # Status Text
            dpg.add_text("", tag="StatusText")

            # Input Box and Send Button
            with dpg.group(horizontal=True):
                dpg.add_input_text(
                    label="",
                    tag="Input",
                    hint="Type your message here...",
                    width=600,
                    callback=self.send_message,
                    on_enter=True
                )
                dpg.add_button(label="Send", width=80, callback=self.send_message)

        dpg.create_viewport(title="AI Agent Chat", width=700, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
