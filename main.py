# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#93E9BE",  # TODO: Choose color
        "head": "nr-rocket",  # TODO: Choose head
        "tail": "coffee",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    # board_width = game_state['board']['width']
    # board_height = game_state['board']['height']

    check_wall(my_head, game_state, is_move_safe)
    print(f"step 1 {is_move_safe}")
  
    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    check_self(my_neck, my_body, my_head, is_move_safe)
    print(f"step 2 {is_move_safe}")

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']
    for snake in opponents:
      body = snake["body"]
      check_moves(body, my_head, is_move_safe)
    print(f"step 3 {is_move_safe}")
    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    new_safe_moves = {"up": True, "down": True, "left": True, "right": True}
    check_moves(safe_moves, my_head, new_safe_moves)
    # TODO: 
  
    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer

    # TODO: Step 5 check 1 move before
    food = game_state['board']['food']
    if not food:
        return {"move": next_move}

    # Target the food closest to the snake head
    target_food = (food[0]["x"], food[0]["y"])
    for f in food[1:]:
        x_diff = max(my_head["x"], f["x"]) - min(my_head["x"], f["x"])
        y_diff = max(my_head["y"], f["y"]) - min(my_head["y"], f["y"])

        if (x_diff, y_diff) < target_food:
            target_food = (f["x"], f["y"])
    
    # Move closer towards food location if safe
    if target_food[0] > my_head["x"] and is_move_safe["right"]:
        next_move = "right"
    elif target_food[0] < my_head["x"] and is_move_safe["left"]:
        next_move = "left"
    elif target_food[1] > my_head["y"] and is_move_safe["up"]:
        next_move = "up"
    elif target_food[1] < my_head["y"] and is_move_safe["down"]:
        next_move = "down"
    
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


def check_moves(moves, my_head, my_neck, my_body, game_state, is_move_safe):
  dict = {}
  for move in moves:
    if move == "up":
      new_head = {"x": my_head["x"], "y":  my_head["y"]+1}
    if move == "down":
      new_head = {"x": my_head["x"], "y":  my_head["y"]-1}
    if move == "left":
      new_head = {"x": my_head["x"]-1, "y":  my_head["y"]}
    if move == "right":
      new_head = {"x": my_head["x"]+1, "y":  my_head["y"]}
  
    new_body = my_body.copy()
    new_body.pop()
    new_body.insert(0, new_head)
    check_wall(new_body[0], game_state, is_move_safe)
    check_self(new_body[1], new_body, new_body[0], is_move_safe)
    
    opponents = game_state['board']['snakes']
    for snake in opponents:
      body = snake["body"]
      check_others(body, my_head, is_move_safe)
      
    dict[move]=len(is_move_safe)

  return dict
    


def check_others(moves: typing.Dict, my_head: typing.Dict, is_move_safe: typing.Dict):
      for cell in moves:
        if cell["x"] == my_head["x"] + 1 and cell["y"] == my_head["y"]:
          is_move_safe["right"] = False
        if cell["x"] == my_head["x"] - 1 and cell["y"] == my_head["y"]:
          is_move_safe["left"] = False
        if cell["y"] == my_head["y"] + 1 and cell["x"] == my_head["x"]:
          is_move_safe["up"] = False
        if cell["y"] == my_head["y"] - 1 and cell["x"] == my_head["x"]:
          is_move_safe["down"] = False


def check_self(my_neck, my_body, my_head, is_move_safe):
   for cell in my_body:
      if cell["x"] == my_head["x"] - 1 and cell["y"] == my_head["y"]:  # Body cell is left of head, don't move left
          is_move_safe["left"] = False

      if cell["x"] == my_head["x"] + 1 and cell["y"] == my_head["y"]:  # Body cell is right of head, don't move right
          is_move_safe["right"] = False

      if cell["x"] == my_head["x"] and cell["y"] == my_head["y"] - 1:  # Body cell is below head, don't move down
          is_move_safe["down"] = False

      if cell["x"] == my_head["x"] and cell["y"] == my_head["y"] + 1:  # Body cell is above head, don't move up
          is_move_safe["up"] = False


def check_wall(my_head, game_state, is_move_safe):
  if my_head["x"] == 0:
      is_move_safe["left"] = False
  if my_head["x"] == game_state['board']['width'] -1:
      is_move_safe["right"] = False
  if my_head["y"] == 0:
      is_move_safe["down"] = False
  if my_head["y"] == game_state['board']['height'] -1:
      is_move_safe["up"] = False
  print(f"step 1 {is_move_safe}")

        
# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
