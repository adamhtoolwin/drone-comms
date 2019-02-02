class NetController < ApplicationController
  def ssh
    require 'net/ssh'

    host = ssh_params[:ipaddr]
    user = 'adam'
    password = 'sfsfsfsf'

    result = ''


    # Net::SSH.start(host, user, password: "") do |ssh|
    #   # capture all stderr and stdout output from a remote process
    #   # puts ssh.exec!("source ~/.bashrc; echo $PATH")
    #   # output = ssh.exec!("source ~/.bashrc; python ~/drone/drone-comms/drone/arming.py udp:127.0.0.1:14551")
    #   # puts output
    #
    #   channel = ssh.open_channel do |ch|
    #     ch.exec "source ~/pyenv-path.sh; echo $PATH; python ~/drone/drone-comms/drone/arming.py udp:127.0.0.1:14551" do |ch, success|
    #       raise "could not execute command" unless success
    #
    #       # "on_data" is called when the process writes something to stdout
    #       ch.on_data do |c, data|
    #         puts "got stdout: #{data}"
    #         # $stdout.print data
    #       end
    #
    #       # "on_extended_data" is called when the process writes something to stderr
    #       ch.on_extended_data do |c, type, data|
    #         puts "got error: #{data}"
    #         # $stderr.print data
    #       end
    #
    #       ch.on_close { puts "done!" }
    #     end
    #   end
    #
    #   ssh.loop
    #   # result = output
    # end

    redirect_to root_path
  end

  def ping
  end

  def ssh_params
    params.permit(:ipaddr)
  end
end
