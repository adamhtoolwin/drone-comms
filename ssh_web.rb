# This script is to be called by the web app

require 'net/ssh'

if !ARGV.any?
    raise "Empty address!"
end

host = "#{ARGV.first}"
# Will PROBABLY always be pi
# TODO
user = 'pi'

puts "Starting connection to #{host} with user #{user}"
# TODO put password
Net::SSH.start(host, user, password: "") do |ssh|
    
      channel = ssh.open_channel do |ch|
        ch.exec "source ~/pyenv-path.sh; echo $PATH; python ~/drone/drone-comms/drone/arming.py udp:127.0.0.1:14551" do |ch, success|
          raise "could not execute command" unless success
    
          # "on_data" is called when the process writes something to stdout
          ch.on_data do |c, data|
            puts "got stdout: #{data}"
            # $stdout.print data
          end
    
          # "on_extended_data" is called when the process writes something to stderr
          ch.on_extended_data do |c, type, data|
            puts "got error: #{data}"
            # $stderr.print data
          end
    
          ch.on_close { puts "done!" }
        end
      end
    
      ssh.loop
end