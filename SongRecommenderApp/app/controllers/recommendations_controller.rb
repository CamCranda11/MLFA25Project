require 'open3'
require 'json'

class RecommendationsController < ApplicationController
  def search
    @recommendations = []
    @error = nil
    
    if params[:song_name].present? && params[:artist_name].present?
      song_name = params[:song_name]
      artist_name = params[:artist_name]
      
      venv_python = "/home/MLFA25Project/SongRecommenderApp/.venv/bin/python"
      script_path = Rails.root.join("recommend.py").to_s
      full_command = "#{venv_python} #{script_path} #{song_name} #{artist_name}"
      
      command = ["/bin/sh", "-c", full_command]
      
      stdout, stderr, status = Open3.capture3(*command)
      
      if status.success?
        begin
          results = JSON.parse(stdout)
          
          if results.is_a?(Hash) && results['error']
            @error = results['error']
          else
            @recommendations = results
            
            if @recommendations.empty?
              @error = "No similar songs were found."
            end
          end
        rescue JSON::ParserError
          @error = "Error parsing Python script output. Raw output: #{stdout}"
        end
      else
        @error = "Failed to run recommendation script. Check Python/library installations. Error: #{stderr}"
      end
    end
  end
end
