import subprocess

for i in range(1, 6):
    print("current stage: " + str(i))
    cmd_str = F"python -m mlgame -1 -i ml/ml_play_ai.py ./ --map {i} --game_type PRACTICE --time_to_play 4500 --sensor_num 5 --sound off"
    subprocess.run(cmd_str, shell=True)

for i in range(1, 6):
    print("current stage: " + str(i))
    cmd_str = F"python -m mlgame -1 -i ml/ml_play_ai.py ./ --map {i} --game_type MAZE --time_to_play 4500 --sensor_num 5 --sound off"
    subprocess.run(cmd_str, shell=True)

for i in range(1, 5):
    print("current stage: " + str(i))
    cmd_str = F"python -m mlgame -1 -i ml/ml_play_ai.py ./ --map {i} --game_type MOVE_MAZE --time_to_play 4500 --sensor_num 5 --sound off"
    subprocess.run(cmd_str, shell=True)