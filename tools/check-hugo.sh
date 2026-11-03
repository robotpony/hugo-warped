#!/bin/bash
# Checks this machine's Hugo against the site's .hugo-version, so a machine
# that has fallen behind another can't build or publish the site unnoticed.
#
#     themes/hugo-warped/tools/check-hugo.sh
#
# Run from the site root, before Hugo. Exits 1 when Hugo is missing, below
# min, or not extended when the site needs that; a Hugo that differs from
# tested is only a warning. Prints nothing when all is well. No network.
#
#     # .hugo-version
#     min = 0.165.0      # refuse anything older
#     tested = 0.169.0   # warn on anything else
#     extended = true    # optional: refuse a build that isn't extended

FILE=.hugo-version

refuse() {
  printf 'check-hugo: %s\n' "$@" >&2
  exit 1
}

warn() {
  printf 'check-hugo: warning: %s\n' "$@" >&2
}

is_version() {
  [[ $1 =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]
}

# Prints -1, 0 or 1 for a below, equal to or above b, comparing numerically
# so 0.99 is below 0.163. A missing patch number counts as 0.
compare() {
  local a b i x y
  IFS=. read -r -a a <<< "$1"
  IFS=. read -r -a b <<< "$2"
  for i in 0 1 2; do
    x=$((10#${a[i]:-0}))
    y=$((10#${b[i]:-0}))
    if ((x < y)); then echo -1; return; fi
    if ((x > y)); then echo 1; return; fi
  done
  echo 0
}

[[ -f $FILE ]] || refuse "no $FILE in $PWD. Run this from the site root."

min=
tested=
extended=
while IFS= read -r line || [[ -n $line ]]; do
  line=${line%%#*}
  [[ $line =~ ^[[:space:]]*$ ]] && continue
  if [[ ! $line =~ ^[[:space:]]*([a-z]+)[[:space:]]*=[[:space:]]*([^[:space:]]+)[[:space:]]*$ ]]; then
    refuse "can't read this line of $FILE: $line"
  fi
  key=${BASH_REMATCH[1]}
  value=${BASH_REMATCH[2]}
  case $key in
    min) min=$value ;;
    tested) tested=$value ;;
    extended) extended=$value ;;
    *) refuse "unknown key in $FILE: $key" ;;
  esac
done < "$FILE"

is_version "$min" || refuse "$FILE needs min = a version, like 0.165.0; it has '$min'."
is_version "$tested" || refuse "$FILE needs tested = a version, like 0.169.0; it has '$tested'."
[[ -z $extended || $extended == true || $extended == false ]] ||
  refuse "$FILE has extended = '$extended'; it can only be true or false."
[[ $(compare "$min" "$tested") != 1 ]] || refuse "$FILE has min $min above tested $tested."

command -v hugo > /dev/null ||
  refuse "Hugo isn't installed; this site needs $min or newer. Run: brew install hugo"

output=$(hugo version 2>&1)
if [[ $output =~ v?([0-9]+\.[0-9]+(\.[0-9]+)?) ]]; then
  installed=${BASH_REMATCH[1]}
else
  refuse "can't read a version from 'hugo version': $output"
fi

if [[ $(compare "$installed" "$min") == -1 ]]; then
  refuse "Hugo $installed on this machine is below $min, the minimum in $FILE." \
    "This machine has probably fallen behind another one you've worked on. Run: brew upgrade hugo"
fi

if [[ $extended == true && $output != *+extended* ]]; then
  refuse "Hugo $installed on this machine isn't the extended build, which $FILE requires." \
    "Homebrew's is extended. Run: brew install hugo"
fi

case $(compare "$installed" "$tested") in
  -1)
    warn "Hugo $installed on this machine is older than $tested, the version in $FILE that this site was last tested on." \
      "This machine has probably fallen behind another one you've worked on. Run: brew upgrade hugo"
    ;;
  1)
    warn "Hugo $installed on this machine is newer than $tested, the version in $FILE that this site was last tested on." \
      "Check the build, then set tested = $installed there, so your other machines hear about it."
    ;;
esac

exit 0
