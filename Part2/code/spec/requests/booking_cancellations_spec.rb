require "rails_helper"

RSpec.describe "Rails booking cancellation", type: :request do
  include Devise::Test::IntegrationHelpers

  let(:user) { create(:user_1) }
  let(:room) { create(:room_1, user: user, day_price: 100) }
  let(:booking) { create(:booking_1, user: user, room: room, start_date: Date.new(2026, 11, 10), end_date: Date.new(2026, 11, 13)) }

  around do |example|
    original = Rails.application.config.x.cancellation_policy
    example.run
  ensure
    Rails.application.config.x.cancellation_policy = original
  end

  it "uses the configured Strategy through the real POST route" do
    Rails.application.config.x.cancellation_policy = -> { PartialRefundCancellationPolicy.new }
    sign_in user
    post cancel_booking_path(booking, locale: :fr)
    expect(response).to redirect_to(booking_path(booking, locale: :fr))
    expect(booking.reload).to be_canceled
    expect(booking.cancellation_refund_amount).to eq(180)
    expect(flash[:notice]).to include("180")
  end

  it "uses flexible cancellation by default" do
    sign_in user
    post cancel_booking_path(booking, locale: :fr)
    expect(booking.reload.cancellation_refund_amount).to eq(360)
  end

  it "does not let request parameters choose a more generous policy" do
    Rails.application.config.x.cancellation_policy = -> { NoRefundCancellationPolicy.new }
    sign_in user
    post cancel_booking_path(booking, locale: :fr), params: { policy: "flexible" }
    expect(booking.reload.cancellation_refund_amount).to eq(0)
  end

  it "does not cancel another user's booking" do
    other = create(:user_1, email: "other@example.test")
    booking
    sign_in other
    post cancel_booking_path(booking, locale: :fr)
    expect(response).to have_http_status(:not_found)
    expect(booking.reload).not_to be_canceled
  end

  it "redirects guests to authentication without canceling" do
    post cancel_booking_path(booking, locale: :fr)
    expect(response).to redirect_to(new_user_session_path(locale: :fr))
    expect(booking.reload).not_to be_canceled
  end

  it "reports repeated cancellation without changing the refund" do
    sign_in user
    post cancel_booking_path(booking, locale: :fr)
    post cancel_booking_path(booking, locale: :fr)
    expect(response).to be_redirect
    expect(flash[:alert]).to be_present
    expect(booking.reload.cancellation_refund_amount).to eq(360)
  end
end
