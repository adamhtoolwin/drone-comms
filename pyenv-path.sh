# The dronekit needs the PATH here because it's installed with pyenv.
# Always source this file when running commands remotely with 'source pyenv-path.sh'

export PATH="$HOME/.rbenv/bin:$PATH"
# eval "$(rbenv init -)"
export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi

export PYTHONPATH="${PYTHONPATH}:/home/pi/drone/mavlink"
export PATH=/home/pi/.pyenv/shims:/home/pi/.pyenv/bin:/home/pi/.rbenv/plugins/ruby-build/bin:/home/pi/.rbenv/shims:/home/pi/.rbenv/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/pi/.local/bin
