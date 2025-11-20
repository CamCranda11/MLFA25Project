require 'open3'
require 'json'
require 'shellwords'

class RecommendationsController < ApplicationController
  def search
    @matches = []
    @error = nil

    if params[:song_name].present? && !params[:selected_song].present? # Only run if search button is clicked

      python_executable = "/usr/bin/python3" 
      script_path = Rails.root.join("recommend.py").to_s
      safe_song_name = Shellwords.escape(params[:song_name])

      command = [python_executable, script_path, safe_song_name] 

      stdout, stderr, status = Open3.capture3(*command)

      if status.success?
        begin
          results = JSON.parse(stdout)

          if results.is_a?(Hash) && results['error']
            @error = results['error']
          else
            @matches = results # Store matches in a new instance variable
          end
        rescue JSON::ParserError
          @error = "Error parsing Python script output. Raw output: #{stdout}"
        end
      else
        @error = "Failed to run search script. Error: #{stderr}"
      end
    end
  end
end
