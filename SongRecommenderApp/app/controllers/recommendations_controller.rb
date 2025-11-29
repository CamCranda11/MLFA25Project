# Requirement statements.
require 'open3'
require 'json'
require 'shellwords'

class RecommendationsController < ApplicationController
  # Main action to search and recommend.
  def search
    # Initialize instance variables for view template.
    @matches = []
    @recommendations = []

    # Check for empty input.
    if params[:song_name].blank? && params[:artist_name].blank? && params[:selected_song_name].blank?
      return
    end

    # Recommendation logic.
    if params[:selected_song_name].present?
      # Capture the song and/or artist from the search.
      song_name = params[:selected_song_name]
      artist_name = params[:selected_artist_name]
      # Rails.logger.debug "DEBUG: Recommending based on '#{song_name}' by '#{artist_name}'..."
    
      # Execute the recommendations Python script in recommend.py.
      stdout, stderr, status = Open3.capture3("python3", "recommend.py", "recommend", song_name, artist_name)

      if status.success?
        begin
          # Attempt to parse the JSON output.
          result = JSON.parse(stdout)
          if result.is_a?(Hash) && result['error'] # Check for structured error.
            flash.now[:alert] = result['error']
          else
            @recommendations = result # Store the list of recommendations.
          end
        rescue JSON::ParserError
          # Handle cases when the script output is not JSON.
          Rails.logger.error "Python Output was not JSON: #{stdout}"
          flash.now[:error] = "System Error: Could not parse recommendations."
        end
      else
        # Handle errors in the Python script.
        Rails.logger.error "Recommendation Script Failed: #{stderr}"
        flash.now[:error] = "An error occurred while generating recommendations."
      end

    # Search logic.
    elsif params[:song_name].present? || params[:artist_name].present?
      # Set search variables, default to an empty string if there's no input.
      song_name = params[:song_name] || ""
      artist_name = params[:artist_name] || "" 
      
      # Rails.logger.debug "DEBUG: Searching for Song: '#{song_name}' | Artist: '#{artist_name}'"
      
      # Execute the search Python script in recommend.py.
      stdout, stderr, status = Open3.capture3("python3", "recommend.py", "search", song_name, artist_name)

      if status.success?
        begin
          # Attempt to parse the JSON output.
          result = JSON.parse(stdout)
          if result.is_a?(Hash) && result['error'] # Check for structured error.
            flash.now[:alert] = result['error']
          else
            @matches = result # Store the list of results.
          end
        rescue JSON::ParserError
          # Handle cases where the script output is not JSON.
          Rails.logger.error "Python Output was not JSON: #{stdout}"
          flash.now[:error] = "System Error: Could not parse search results."
        end
      else
        # Handle errors in the Python script.
        Rails.logger.error "Search Script Failed: #{stderr}"
        flash.now[:error] = "An error occurred while searching."
      end
    end
  
    # Render the search view template.
    render :search
  end
end
