
function wait_for_service {
  while : ; do
    exec 6<>/dev/tcp/$1/$2
    if [[ $? -eq 0 ]]; then
      break
    fi
    sleep 1
  done

  exec 6>&- # close output connection
  exec 6<&- # close input connection
}

function wait_for_lock {
  while [ -f $1 ]; do
    sleep 1
  done
}
