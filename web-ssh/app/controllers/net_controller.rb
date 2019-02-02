class NetController < ApplicationController
  def ssh
    require 'net/ssh'

    host = ssh_params[:ipaddr]

    puts "Executing command 'ruby ~/drone/drone-comms/ssh_web.rb #{host}'"
    child_pid = spawn("ruby ~/drone/drone-comms/ssh_web.rb #{host}")
    Process.detach(child_pid)

    redirect_to root_path
  end

  def ping
  end

  def ssh_params
    params.permit(:ipaddr)
  end
end
