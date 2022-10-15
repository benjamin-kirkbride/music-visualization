#!/bin/bash

# $1: project dir
# $2: fqbn
# $3: file ext to upload

set -o errexit
set -o pipefail
set -o nounset

# get the directory this is located in
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SCRIPT_NAME=$0

function isodate {
  date +"%Y-%m-%dT%H:%M:%S%z"
}


function log {
  echo "$SCRIPT_NAME:$(isodate): $1"
}

function main {
  slashless_project=$(echo $1 | sed 's/\///')
  dotted_fqbn=$(echo $2 | sed 's/:/./g')
  
  log "starting compilation of $1"
  log "arduino-cli compile -b $2 $1"
  arduino-cli compile -b $2 $1
  
  log "transferring compiled hex to jukebox"
  log "$__dir/$slashless_project/build/$dotted_fqbn/$slashless_project.ino.$3"
  scp \
    "$__dir/$slashless_project/build/$dotted_fqbn/$slashless_project.ino.$3" \
    "jukebox.caverage.lan:/tmp/$slashless_project.ino.$3"
  ssh jukebox.caverage.lan \
    "teensy_loader_cli -v -s --mcu=imxrt1062 -w /tmp/$slashless_project.ino.$3"
}

main $1 $2 $3
