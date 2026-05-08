# Imports
from RealtimeSTT import AudioToTextRecorder
from chesslogic import ChessGame
from chessUI import ChessUI
import tkinter
import queue
import threading
import pyttsx3


# Function to thread STT component
def listen(recorder, q):
        try:
            # Process the recorded audio
            game_command = recorder.text()
            # Enqueue the command
            q.put(("command", game_command))
        except Exception as e:
            print(f"Error in listen thread: {e}")

def button_release(recorder,q):
    #Stop recording
    recorder.stop()
    # Create thread to process speech, update UI.
    threading.Thread(target=listen, args=(recorder, command_q), daemon=True).start()

# Game logic
def game_loop(root, ui, game, q):
    try:
        # DQ latest command
        header, game_command = q.get_nowait()
        if header == "command":
            # Process game command
            result = game.handle_command(game_command)
            result_msg = result.message
            # Hide / reveal board logic
            if result.type == "hide":
                ui.hide_board()
            elif result.type == "reveal":
                ui.reveal_board()
            # feedback to console
            ui.update_console(game_command, result_msg)
            # update the chessboard ui
            ui.update_chessboard(result.state.board)
            # Speak the user input and result
            pyttsx3.speak(game_command)
            pyttsx3.speak(result_msg)
            if game.winner is None:
                # Schedule next queue check
                root.after(100, game_loop, root, ui, game, q)
            else:
                # Declare Winner
                pyttsx3.speak(f"Game over! Winner: {game.winner}")
                print("Game over! Winner: ", game.winner)
                root.quit()
    except queue.Empty:
        # Queue is empty, check again soon
        if game.winner is None:
            # Schedule next queue check
            root.after(100, game_loop, root, ui, game, q)

if __name__ == '__main__':
    # Initializing Game components
    recorder = AudioToTextRecorder()
    game = ChessGame()
    root = tkinter.Tk()
    ui = ChessUI(root)
    command_q = queue.Queue()
    transcription = ""
    # Setting up default state of board
    ui.update_chessboard(game.board)
    ui.hide_board()

    # Bind Functions to buttons, pressing starts the recording process
    # A release function stops recording and creates a thread to process the audio and update the UI.
    ui.button.bind("<ButtonPress-1>", lambda e: recorder.start())
    ui.button.bind("<ButtonRelease-1>", lambda e: button_release(recorder, command_q))
    # update UI
    root.after(100, game_loop, root, ui, game, command_q)
    # main loop
    root.mainloop()