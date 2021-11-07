#!/bin/bash

cd "$( dirname "$0" )/.."
app_root_dir="$( pwd )"

secrets_env_file="$app_root_dir/config/.secrets.env"
app_env_file="$app_root_dir/config/asana_extensions.env"
source $secrets_env_file
source $app_env_file

log=0

while getopts "l" opt; do
    case "$opt" in
    l) log=1 ;;
    esac
done

out_log="/tmp/asana_extensions_stdout.log"
err_log="/tmp/asana_extensions_stderr.log"

script="-m asana_extensions"
script_opts="-e -m all"
tmp_log="1>$out_log 2>$err_log"

log_stdout="logger -s -t '[asana_extensions]' -p local7.info < $out_log"
log_stderr="logger -s -t '[asana_extensions]' -p local7.warn < $err_log"

rm_stdout="rm $out_log"
rm_stderr="rm $err_log"

if [ $log -eq 1 ]; then
  eval $PYTHON_BIN $script $script_opts $tmp_log
  eval $log_stdout
  eval $log_stderr

  if [ -s $err_log ]; then
    sendemail=/usr/bin/sendemail

    date=`date +"%B %-d, %Y"`
    subject="Error in Asana Extensions for $date"
    message="There was a fatal error in running Asana Extensions.<br \>"
    message="$message<br \><br \>Error log:<br \><br \>"
    err_message=`cat $err_log |  sed ':a;s|^\([[:space:]]*\)[[:space:]]|\1\&nbsp\;|;ta' |  sed ':a;N;$!ba;s|\n|<br />|g'`
    message="$message $err_message"

    $sendemail -f "$EMAIL_SENDER_NAME_AND_ADDR" \
               -t "$EMAIL_ADMIN_RECIPIENT_NAME_AND_ADDR" \
               -s "$EMAIL_SERVER_HOST:$EMAIL_SERVER_PORT" \
               -o tls=yes \
               -xu "$EMAIL_USERNAME" \
               -xp "$EMAIL_PASSWORD" \
               -u "$subject" \
               -m "$message" \
               -o message-content-type=html
  fi

  eval $rm_stdout
  eval $rm_stderr
else

  eval $PYTHON_BIN $script $script_opts
fi
