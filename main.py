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
import copy
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

  my_head = game_state["you"]["body"][0]  # Coordinates of your head
  my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"
  my_health = game_state["you"]["health"]
  my_id = game_state["you"]["id"]
  eat = False
  
  check_wall(my_head, game_state, is_move_safe)
  print(f"step 1 {is_move_safe}")

  # Step 2 - Prevent your Battlesnake from colliding with itself
  my_body = game_state['you']['body']
  check_self(my_neck, my_body, my_head, is_move_safe)
  print(f"step 2 {is_move_safe}")

  # Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
  opponents = game_state['board']['snakes']
  others_heads = {}
  others_cells = []
  for i in range(0, len(opponents)):
    snake = opponents[i]
    id = snake["id"] 
    if id != my_id:
      body = snake["body"]
      others_heads[i] = snake["head"]
      for cell in body[:-2]:
        others_cells.append(cell)
      check_others(body[:-1], my_head, is_move_safe)
  print(f"step 3 {is_move_safe}")

  # Are there any safe moves left?
  safe_moves = []
  for move, isSafe in is_move_safe.items():
    if isSafe:
      safe_moves.append(move)

  if len(safe_moves) == 0:
    print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
    return {"move": "down"}

  # Secondary check to prioritize the most safe moves
  dict1 = check_moves(safe_moves, my_head, my_neck, my_body, game_state, others_heads)
  print(f"dict1 {dict1}")
  
  priority_moves = sorted(dict1, key=dict1.get, reverse=True)
  
  print(f"priority {priority_moves}")
  # Choose the safest moves from the ones available
  fst_choice  = priority_moves[0]
  fst_head = move_position(fst_choice, my_head)
  snd_choice = None
  thd_choice = None
  snd_head = None
  thd_head = None
  if len(priority_moves) > 1:
    snd_choice = priority_moves[1]
    snd_head = move_position(snd_choice, my_head)
  if len(priority_moves) > 2:
    thd_choice = priority_moves[2]
    thd_head = move_position(snd_choice, my_head)
    
  next_move = fst_choice

    # if dict1[next_move] == dict1[snd_choice] and next_move != snd_choice and next_move == "up":
    #   next_move = snd_choice

  # Step 4 - Move towards food to regain health and survive longer
  food = game_state['board']['food']
  if len(food) > 0:
    food_dict={}
    for i in range(0, len(food)):
      f = food[i]
      f_dis = abs(f["x"] - my_head["x"]) + abs(f["y"] - my_head["y"])
      food_dict[i] = f_dis
          
    food_dict = sorted(food_dict, key=food_dict.get)
    target_food_index = food_dict[0]
    target_food = food[target_food_index]
  
    BUFFER = 35
    if my_health <= (food_dict[target_food_index] + BUFFER) or my_health < 40:
      eat = True
      food_move = move_towards_food(target_food, my_head, is_move_safe, dict1)
      if food_move is not None:
        next_move = food_move
      elif len(food_dict) > 1:
        snd_food_index = food_dict[1]
        if my_health <= food_dict[snd_food_index]: 
          snd_food = food[snd_food_index]
          food_move = move_towards_food(snd_food, my_head, is_move_safe, dict1)
          if food_move is not None:
            target_food = snd_food
            next_move = food_move
      print(f"food:{target_food}, move:{food_move}")

    #avoid food or near food
    new_head = move_position(next_move, my_head) 
    for fd in food:
      if (not eat and my_health > 40 and 
          ((new_head["x"] == fd["x"] and new_head["y"] == fd["y"]))):
            #or is_next_to(new_head, fd, 1)
        if next_move != snd_choice and snd_head is not None and dict1[snd_choice] >= dict1[next_move]:
          next_move = snd_choice
          print(f"145 next: {next_move}")
        elif next_move != thd_choice and thd_head is not None and dict1[thd_choice] >= dict1[next_move]:
          next_move = thd_choice
          print(f"147 next: {next_move}")
        
  # avoid move into corner
  if not eat and snd_head is not None and dict1[snd_choice] == dict1[fst_choice]:
    corner_avoid = {"up": False, "down": False, "left": False, "right": False}
    fst_position = {"up": False, "down": False, "left": False, "right": False}
    snd_position = {"up": False, "down": False, "left": False, "right": False}
    thd_position = {"up": False, "down": False, "left": False, "right": False}
    snd_ok = False
    thd_ok = False
    new_head = move_position(next_move, my_head)
    if 0 <=new_head["x"] < 2:  
      corner_avoid["right"] = True
    if 9 <=new_head["x"] < game_state['board']['width']:
      corner_avoid["left"] = True
    if 0 <=new_head["y"] < 2:
      corner_avoid["up"] = True
    if 9 <=new_head["y"] < game_state['board']['height']:
      corner_avoid["down"] = True
    print(f"coner_avoid: {corner_avoid}")

    if next_move != fst_choice:
      if fst_head["x"] > new_head["x"]: #fst is on the right of current option
        fst_position["right"] = True
      if fst_head["x"] < new_head["x"]:
        fst_position["left"] = True
      if fst_head["y"] < new_head["y"]:
        fst_position["down"] = True
      if fst_head["y"] > new_head["y"]:
        fst_position["up"] = True
      print(f"fst_position: {fst_position}")
    
    if next_move != snd_choice:
      snd_ok = True
      if snd_head["x"] > new_head["x"]: #snd is on the right of current option
        snd_position["right"] = True
      if snd_head["x"] < new_head["x"]:
        snd_position["left"] = True
      if snd_head["y"] < new_head["y"]:
        snd_position["down"] = True
      if snd_head["y"] > new_head["y"]:
        snd_position["up"] = True
      print(f"snd_position: {snd_position}")
      

    if thd_choice is not None and next_move != thd_choice and dict1[thd_choice] == dict1[next_move]:
      thd_ok = True
      if thd_head["x"] > new_head["x"]: #thd is on the right of current option
        thd_position["right"] = True
      if thd_head["x"] < new_head["x"]:
        thd_position["left"] = True
      if thd_head["y"] < new_head["y"]:
        thd_position["down"] = True
      if thd_head["y"] > new_head["y"]:
        thd_position["up"] = True
      print(f"thd_position: {thd_position}")

    snd_cnt = 0
    thd_cnt = 0
    fst_cnt = 0
    for move, need in corner_avoid.items():
      if need: # see if need to move to this direction
        if next_move != fst_choice and fst_position[move]:
          fst_cnt += 1
        if snd_ok and snd_position[move]:
          snd_cnt += 1
        if thd_ok and thd_position[move]:
          thd_cnt += 1
    print(f"snd_cnt: {snd_cnt} thd_cnt:{thd_cnt}")

    # also avoid close to others
    snd_others_cnt = 0
    thd_others_cnt = 0
    fst_others_cnt = 0

    for c in others_cells:
        if is_next_to(fst_head, c, 2):
          fst_others_cnt += 1
    
    if snd_ok:
      for c in others_cells:
        if is_next_to(snd_head, c, 2):
          snd_others_cnt += 1

    if thd_ok:
      for c in others_cells:
        if is_next_to(thd_head, c, 2):
          thd_others_cnt += 1
    if fst_others_cnt < snd_others_cnt:
      next_move = fst_choice
    elif snd_ok and snd_others_cnt < thd_others_cnt:
      next_move = snd_choice
      print(f"220 next: {next_move}")
    elif thd_ok and snd_others_cnt > thd_others_cnt:
      next_move = thd_choice
      print(f"223 next: {next_move}")
    elif snd_others_cnt == thd_others_cnt and snd_cnt > thd_cnt:
      next_move = snd_choice
      print(f"226 next: {next_move}")
    elif thd_cnt > 0 and snd_others_cnt == thd_others_cnt and snd_cnt >= thd_cnt:
      next_move = thd_choice
      print(f"223 next: {next_move}")
            
  print(f"health:{my_health}")
  print(f"MOVE {game_state['turn']}: {next_move}")
  print('---------------------------------------')
  return {"move": next_move}

# Helper function that moves snake towards food target

def move_towards_food(target_food, my_head, is_move_safe, dict1):
  next_move = None
  if target_food["x"] > my_head["x"] and is_move_safe["right"] and "right" in dict1.keys() and dict1["right"] > 1:
    next_move = "right"
  elif target_food["x"] < my_head["x"] and is_move_safe["left"] and "left" in dict1.keys() and dict1["left"] > 1:
    next_move = "left"
  elif target_food["y"] > my_head["y"] and is_move_safe["up"] and "up" in dict1.keys() and dict1["up"] > 1:
    next_move = "up"
  elif target_food["y"] < my_head["y"] and is_move_safe["down"] and "down" in dict1.keys() and dict1["down"] > 1:
    next_move = "down"

  return next_move


def move_position(move_str, my_head):
  if move_str == "up":
      new_head = {"x": my_head["x"], "y": my_head["y"] + 1}
  if move_str == "down":
      new_head = {"x": my_head["x"], "y": my_head["y"] - 1}
  if move_str == "left":
      new_head = {"x": my_head["x"] - 1, "y": my_head["y"]}
  if move_str == "right":
      new_head = {"x": my_head["x"] + 1, "y": my_head["y"]}

  return new_head

# Helper function that scores the safety of each potential move
def check_moves(moves, my_head, my_neck, my_body, game_state, others_heads):
  dict = {}
  for move in moves:
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}
    new_head = move_position(move, my_head)
    new_body = copy.deepcopy(my_body)
    new_body.pop()
    new_body.insert(0, new_head)
    check_wall(new_body[0], game_state, is_move_safe)
    check_self(new_body[1], new_body, new_head, is_move_safe)

    opponents = game_state['board']['snakes']
    for snake in opponents:
      id = snake["id"] 
      if id != game_state["you"]["id"]:
        body = snake["body"]
        check_others(body[:-1], my_head, is_move_safe)

    danger = False
    for index, head in others_heads.items():
      op_len = opponents[index]["length"]
      me_len = game_state["you"]["length"]
      if is_next_to(new_head, head, 1) and op_len >= me_len:
        print(f"op:{op_len} vs me:{me_len}")
        danger = True
      # cnt len
      cnt = 0
      for drct, is_safe in is_move_safe.items():
        if is_safe:
          cnt += 1
    if not danger:
      dict[move] = cnt
    else:
      dict[move] = cnt - 4 #-1 ~ -4
    
    # is_safe_dict[move] = is_move_safe
    
  return dict


def is_next_to(self, next, dis):
  if (self["x"] == next["x"] and  abs(self["y"] - next["y"]) == dis) or (self["y"] == next["y"] and  abs(self["x"] - next["x"]) == dis):
    return True
  else:
    return False


# Helper function that prevents snake from colliding with opponents
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
    # print(f"cell{cell} is_safe: {is_move_safe}")


# Helper function that prevents snake from colliding with itself
def check_self(my_neck, my_body, my_head, is_move_safe):
  for cell in my_body[:-1]: # skip tail
    if cell["x"] == my_head["x"] - 1 and cell["y"] == my_head[
        "y"]:  # Body cell is left of head, don't move left
      is_move_safe["left"] = False

    if cell["x"] == my_head["x"] + 1 and cell["y"] == my_head[
        "y"]:  # Body cell is right of head, don't move right
      is_move_safe["right"] = False

    if cell["x"] == my_head["x"] and cell[
        "y"] == my_head["y"] - 1:  # Body cell is below head, don't move down
      is_move_safe["down"] = False

    if cell["x"] == my_head["x"] and cell[
        "y"] == my_head["y"] + 1:  # Body cell is above head, don't move up
      is_move_safe["up"] = False


# Helper function that prevents snake from colliding with wall
def check_wall(my_head, game_state, is_move_safe):
  if my_head["x"] == 0:
    is_move_safe["left"] = False
  if my_head["x"] == game_state['board']['width'] - 1:
    is_move_safe["right"] = False
  if my_head["y"] == 0:
    is_move_safe["down"] = False
  if my_head["y"] == game_state['board']['height'] - 1:
    is_move_safe["up"] = False
  # print(f"step 1 {is_move_safe}")


# Start server when `python main.py` is run
if __name__ == "__main__":
  from server import run_server

  run_server({"info": info, "start": start, "move": move, "end": end})