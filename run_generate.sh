nohup python3 main.py --mode=generate &
echo 'Beginning process:' > logs/homophone_status.txt
echo $! >> logs/homophone_status.txt
wait
echo 'All background processes have finished.' >> logs/homophone_status.txt