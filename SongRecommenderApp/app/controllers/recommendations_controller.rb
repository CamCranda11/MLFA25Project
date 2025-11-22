require 'open3'
require 'json'
require 'shellwords'

class RecommendationsController < ApplicationController
  def search
    @matches = []
    @recommendations = []

    if params[:selected_song_name].present?
      song_name = params[:selected_song_name]
      artist_name = params[:selected_artist_name]
      Rails.logger.debug "DEBUG: Recommending based on '#{song_name}' by '#{artist_name}'..."
    
      stdout, stderr, status = Open3.capture3("python3", "recommend.py", "recommend", song_name, artist_name)

      if status.success?
        begin
          result = JSON.parse(stdout)
          if result.is_a?(Hash) && result['error']
            flash.now[:alert] = result['error']
          else
            @recommendations = result
          end
        rescue JSON::ParserError
          Rails.logger.error "Python Output was not JSON: #{stdout}"
          flash.now[:error] = "System Error: Could not parse recommendations."
        end
      else
        Rails.logger.error "Recommendation Script Failed: #{stderr}"
        flash.now[:error] = "An error occurred while generating recommendations."
      end

    elsif params[:song_name].present?
      song_name = params[:song_name]
      Rails.logger.debug "DEBUG: Searching for '#{song_name}'..."
    
      stdout, stderr, status = Open3.capture3("python3", "recommend.py", "search", song_name)

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
        flash.now[:error] = "An error occurred while searching."
      end
    end
  
    render :search
  end
end
