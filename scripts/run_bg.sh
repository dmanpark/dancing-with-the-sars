set -euo pipefail
source ~/miniforge3/etc/profile.d/conda.sh
conda activate dwts
cd "$(dirname "$0")/.."
: "${DWTS_OUT:=$HOME/dwts-out}"
mkdir -p "$DWTS_OUT/logs"
tag=$1; shift
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-2} MKL_NUM_THREADS=${MKL_NUM_THREADS:-2}
setsid nohup /usr/bin/time -v python -m dwts.run "$@" > "$DWTS_OUT/logs/$tag.log" 2>&1 < /dev/null &
echo "started $tag pid $!"
sleep 3
