Rails.application.routes.draw do
  # Set the root URL to the search action.
  root 'recommendations#search'
  # Define a GET route for the search.
  get 'recommendations/search'
end
