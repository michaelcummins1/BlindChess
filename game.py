from RealtimeSTT import AudioToTextRecorder
from chesslogic import ChessGame
from chessUI import ChessUI
import tkinter
import queue
import threading
# Function to thread STT component
def listen(recorder, q):
    while True:
        try:
            game_command = recorder.text()
            # Enqueue the command
            q.put(("command", game_command))
        except Exception as e:
            print(f"Error in listen thread: {e}")
            break
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
            if game.winner is None:
                # Schedule next queue check
                root.after(100, game_loop, root, ui, game, q)
            else:
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
    # Setting up default state of board.
    ui.update_chessboard(game.board)
    ui.hide_board()
    # Init thread as variable
    thread = threading.Thread(target=listen, args=(recorder, command_q), daemon=True)
    # Bind thread to button
    ui.button.bind("<Button-1>", lambda e: thread.start())
    # update UI
    root.after(100, game_loop, root, ui, game, command_q)
    # main loop
    root.mainloop()