#!/bin/bash

SESSION_DIR="/tmp/pycore.1"
PROJECT_DIR="/volume/cc-tp2"

start_all() {
    run_in_node() {
        local node=$1
        local cmd=$2
        echo "Starting $node"
        vcmd -c $SESSION_DIR/$node -- bash -c "cd $PROJECT_DIR && $cmd" &
    }
    
    # rotas nave-mãe (config)
    echo "Configuring routes."
    vcmd -c $SESSION_DIR/nave-mae -- bash -c "cd $PROJECT_DIR && bash config/mother_route_setup.sh"
    sleep 3
    
    # nave-mãe
    echo "Starting mother."
    run_in_node "nave-mae" "python -m mother -l"
    sleep 2
    
    # 3. Iniciar rovers com espaçamento
    echo "Starting rovers."
    for rover in rover-01 rover-02 rover-03 rover-04; do
        run_in_node "$rover" "python -m rover -l"
        sleep 1
    done
    
    # 4. Iniciar ground control
    sleep 2
    echo "4. Starting ground."
    run_in_node "ground-control" "cd ground && python -m http.server 8000"

    echo ""
    echo "Started."
    echo "To stop: $0 stop"
    wait
}

stop_all() {
    for node in nave-mae rover-01 rover-02 rover-03 rover-04 ground-control; do
        echo -n "  $node:"
        vcmd -c $SESSION_DIR/$node -- pkill -f "python" 2>/dev/null
        sleep 0.3
        echo "stopped"
    done
    
    echo ""
    echo "Processes stopped."
}

case "$1" in
    start) start_all;;
    stop)  stop_all;;
    *)
        echo "  start - start mother, rovers, ground"
        echo "  stop - stop processes"
        exit 1
        ;;
esac