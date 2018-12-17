require 'test_helper'

class NetControllerTest < ActionDispatch::IntegrationTest
  test "should get ssh" do
    get net_ssh_url
    assert_response :success
  end

  test "should get ping" do
    get net_ping_url
    assert_response :success
  end

end
