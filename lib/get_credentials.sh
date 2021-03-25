# -u, --dry-run: do not create anything; merely print a name
env_var_pipe=$(mktemp -u)
# We use a named pipe (FIFO special file) instead of a regular file because it has
# no contents on the filesystem; the filesystem entry merely serves as a reference
# point so that processes can access the pipe using a name in the filesystem.
mkfifo ${env_var_pipe}
chmod 600 ${env_var_pipe}

# Use next available file descriptor
# https://www.gnu.org/software/bash/manual/html_node/Redirections.html
# Each redirection that may be preceded by a file descriptor number may instead
# be preceded by a word of the form {varname}. In this case, for each redirection
# operator except >&- and <&-, the shell will allocate a file descriptor greater
# than 10 and assign it to {varname}.
exec {pipe_fd}<>${env_var_pipe}

# This is to make sure the file is deleted after use. Since it is open, the 
# descriptor is still available for the current process (and subprocesses). The
# filesystem entry will be deleted by the filesystem on close. Even if we don't
# close if explicitly, the kernel will do this automatically when the process
# exits (including kills and crashes).
rm $env_var_pipe

"${HOME}/.cache/venv/mikrotik-tools-py3/bin/python3" \
  ${script_dir}/lib/get_credentials.py --env-var-pipe-handle ${pipe_fd}
if [ $? -ne 0 ]; then return; fi

# Write an empty line to the end of the pipe in case child process has crashed
# and has never got a chance to write to the pipe. This will prevent current
# shell from hanging.
echo '' >&${pipe_fd}

read env_var_value <&${pipe_fd}
if [ "${env_var_value}" != "" ]; then
  declare -x "$1=${env_var_value}"
fi

eval "exec ${pipe_fd}>&-"
