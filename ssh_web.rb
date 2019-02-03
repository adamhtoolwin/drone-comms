# This script is to be called by the web app

require 'net/ssh'

if !ARGV.any?
    raise "Empty address!"
end

host = "#{ARGV.first}"
# Will PROBABLY always be pi
user = 'pi'
password = 'sfsfsfsf'

puts "Starting connection to #{host} with user #{user}"
Net::SSH.start(host, user, password: password) do |ssh|
    
      channel = ssh.open_channel do |ch|
        # For now using usb by serial - testing purposes
        ch.exec "source ~/drone-comms/pyenv-path.sh; echo $PATH; python ~/drone-comms/drone/arming.py /dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00" do |ch, success|
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