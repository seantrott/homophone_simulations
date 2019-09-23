nohup python3 src/generate_artificial_lexicon.py &
echo 'Beginning process:' > logs/homophone_status.txt
echo $! >> logs/homophone_status.txt
wait
echo 'All background processes have finished.' >> logs/homophone_status.txt