from RealtimeSTT import AudioToTextRecorder
from chesslogic import ChessGame
from chessUI import ChessUI
import tkinter
import queue
import threading

def process_text(text):
    print(text)

def listen(recorder, q):
    while True:
        try:
            game_command = recorder.text()
            q.put(("command", game_command))
        except Exception as e:
            print(f"Error in listen thread: {e}")
            break

def game_loop(root, ui, game, q):
    try:
        header, game_command = q.get_nowait()
        if header == "command":
            result = game.handle_command(game_command)
            result_msg = result.message
            if result.type == "hide":
                ui.hide_board()
            elif result.type == "reveal":
                ui.reveal_board()
            ui.update_console(game_command, result_msg)
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
            root.after(100, game_loop, root, ui, game, q)

if __name__ == '__main__':
    recorder = AudioToTextRecorder()
    game = ChessGame()
    root = tkinter.Tk()
    ui = ChessUI(root)
    command_q = queue.Queue()
    
    ui.update_chessboard(game.board)
    ui.hide_board()

    thread = threading.Thread(target=listen, args=(recorder, command_q), daemon=True)
    ui.button.bind("<Button-1>", lambda e: thread.start())
    root.after(100, game_loop, root, ui, game, command_q)
    root.mainloop()