from RealtimeSTT import AudioToTextRecorder
from chesslogic import ChessGame
from chessUI import ChessUI
import tkinter
import threading
def process_text(text):
    print(text)

if __name__ == '__main__':
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()
    game = ChessGame()
    root = tkinter.Tk()
    ui = ChessUI(root)
    turn = 0;
    #Load / Create Window
    #Game Process
    # Load the initial game state into UI. Board is hidden by default.
    ui.update_chessboard(game.board);
    ui.hide_board();
    while game.winner is None:
        game_command = recorder.text();
        result = game.handle_command(game_command);
        game_msg = result.message
        # Updating the UI based on the result.
        if result.type == "hide":
            ui.hide_board();
        elif result.type == "reveal":
            ui.reveal_board();
        if result.success is True:
            turn +=1;
        ui.update_console(game_command, game_msg);
        ui.update_chessboard(result.state.board);
        current_move = result.state.turn;
        print(result.state.turn, " | TURN"); # Whose turn
        print(turn);
        root.update();
        # recorder.text(process_text)
    root.quit();
    print("Game over! Winner: ", game.winner);