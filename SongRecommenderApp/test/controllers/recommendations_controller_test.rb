require "test_helper"

class RecommendationsControllerTest < ActionDispatch::IntegrationTest
  test "should get search" do
    get recommendations_search_url
    assert_response :success
  end
end
