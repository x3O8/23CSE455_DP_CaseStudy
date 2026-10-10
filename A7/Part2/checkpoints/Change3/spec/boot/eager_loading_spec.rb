require "rails_helper"

RSpec.describe "Evolved application boot" do
  it "eager loads the application and payment engine without unresolved constants" do
    expect { Rails.application.eager_load! }.not_to raise_error
  end
end
