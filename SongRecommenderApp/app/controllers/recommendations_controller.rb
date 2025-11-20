require 'open3'
require 'json'
require 'shellwords'

class RecommendationsController < ApplicationController
  def search
    song_name = params[:song_name]
  
    @matches = [] 
  
    if song_name.blank?
      return
    end

    Rails.logger.debug "DEBUG: Searching for '#{song_name}'..."

    stdout, stderr, status = Open3.capture3("python3", "recommend.py", song_name)

    if status.success?
      begin
        result = JSON.parse(stdout)
      
        if result.is_a?(Hash) && result['error']
          flash.now[:alert] = result['error']
        else
          @matches = result
        end
      rescue JSON::ParserError
        Rails.logger.error "Python Output was not JSON: #{stdout}"
        flash.now[:error] = "System Error: Could not parse search results."
      end
    else
      Rails.logger.error "Search Script Failed: #{stderr}"
      flash.now[:error] = "An error occurred while searching. Please try again."
    end
  
    render :search
  end
end
