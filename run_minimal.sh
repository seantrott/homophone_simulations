nohup python3 src/minimal_pairs.py &
echo 'Beginning process:' > logs/mp_status.txt
echo $! > logs/mp_status.txt
wait
echo 'All background processes have finished.' >> logs/mp_status.txt