# This script is to be called by the web app

require 'net/ssh'

host = "localhost"
# Will PROBABLY always be pi
user = 'pi'
password = '1234'

puts "Starting connection to #{host} with user #{user}"
Net::SSH.start(host, user, port:2211, password: password) do |ssh|
    
      channel = ssh.open_channel do |ch|
        # For now using usb by serial - testing purposes
        ch.exec "python ~/Desktop/Drone_Base_python_codes/open_door.py" do |ch, success|
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