nohup python3 src/minimal_pairs.py &
echo $! > logs/mp_status.txt
wait
echo 'All background processes have finished.' >> logs/mp_status.txt