Describe what you did, how you did it, what challenges you encountered, and how you solved them.

We have developed an application that allows one to play chess (optionally) blind. The entire game works through voice commands. We used python and various modules, such as RealtimeSTT, tkinter, threading, and dataclasses. There is a UI component where the player can observe the game. 

Challenges:

D: I was learning Tkinter from scratch, so there was a lot of time spent looking at guides and screwing around until it worked well enough. I thought the scroll bar would have been difficult, but it turns out the Push and Hold Button bested me.

M: The main challenge was debugging some of the complicated chess rules and piece interactions, as well as ensuring that the game had enough interpretability in the inputs to allow for ease of verbal user interactions.

Please answer any questions found throughout the narrative of this assignment.
If collaboration with a buddy was permitted, did you work with a buddy on this assignment? 
Yes.
If so, who? 
Michael and Devin worked together.

If not, do you certify that this submission represents your own original work?
Please identify any and all portions of your submission that were not originally written by you (for example, code originally written by your buddy, or anything taken or adapted from a non-classroom resource). It is always OK to use your textbook and instructor notes; however, you are certifying that any portions not designated as coming from an outside person or source are your own original work.

chesslogic.py is entirely Michael's Work.
game.py, chessUI.py are entirely Devin's work.

Approximately how many hours it took you to finish this assignment (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?

D: My portions took at least 8-12 hours total. I was learning tkinter from scratch (It should show in the product) and had a difficult time wrapping my head around how UI development works. I get the boxes-within-boxes approach, but I can't say I like how tkinter sizes things (based on content). I thought it a good challenge nonetheless.

M: The chess logic portion took around 6-8 hours of work. I had previously made an incomplete chess game in java, so I had a foundation that I was able to build upon, but implementing some of the more fringe chess rules (en passant, castling) took quite some time and required a good amount of tinkering and debugging. Another time sink was establishing interpretable textual move input, as all of the interactions with the game would be through transcribed verbal inputs.

Your overall impression of the assignment. Did you love it, hate it, or were you neutral? One word answers are fine, but if you have any suggestions for the future let me know.

D: I had fun doing this yea.

M: I enjoyed writing the chess logic, and it was satisfying to build upon a project that I had left incomplete in the past.

Using the grading specifications on this page, discuss briefly the grade you would give yourself and why. Discuss each item in the grading specification.

D: For me, I think an A. I  managed to make a product that does almost exactly what we had set out to do. While the embellishments are missing, such cosmetic features would be no challenge to implement in future. My biggest grievance is the button. That took the longest to get working, which I did not expect. Some feedback, such as changing the display names for pieces, was incorporated. In the future, those could be swapped out for pictures.

M: I beleive that we deserve an A for our efforts. We accomplished the main goals of our design plan, as I beleive that anyone of any visual capabilites would be able to play this game. I am very proud of our final product, and I believe that we adapted it to comments on the design very well; my part in responding to comments was the addition of the chess rules that I had neglected to include originally as well as increasing the interpretability of the chess game logic with regular expressions. 

Any other concerns that you have. For instance, if you have a bug that you were unable to solve but you made progress, write that here. The more you articulate the problem the more partial credit you will receive (it is fine to leave this blank).

D: While my button works, it is not a push to talk (hold it down, machine listens, release, process speech) button. It instead starts the program and STT thread, which is a fine use, but not exactly what I had hoped to do. -- Edit: I managed to get the button working as intended.

M: My main concern is that there could potentially be certain game states that may result in errors in the chess games logic. I was able to both write quick tests within the chesslogic.py script and test out our final product for most important game states. However, there is so much variation that is very hard to account for, so there does exist the possibility that a bug may emerge upon extensive use of the product. 