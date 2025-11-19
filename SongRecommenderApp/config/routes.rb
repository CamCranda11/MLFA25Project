Rails.application.routes.draw do
  root 'recommendations#search'
  get 'recommendations/search'
end
