class NetController < ApplicationController
  def ssh
    require 'net/ssh'

    host = ssh_params[:ipaddr]
    user = 'pi'
    password = 'sfsfsfsf'

    result = ''

    Net::SSH.start(host, user, password: "sfsfsfsf") do |ssh|
      # capture all stderr and stdout output from a remote process
      output = ssh.exec!("ls -a")
      puts output

      result = output
    end

    redirect_to root_path
  end

  def ping
  end

  def ssh_params
    params.permit(:ipaddr)
  end
end
