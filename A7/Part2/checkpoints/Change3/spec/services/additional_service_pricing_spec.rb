require "rails_helper"

RSpec.describe AdditionalServicePricing, type: :model do
  let(:user) { create(:user_1) }
  let(:room) { create(:room_1, user: user, day_price: 100) }
  let(:booking) { create(:booking_1, user: user, room: room, start_date: Date.new(2026, 11, 10), end_date: Date.new(2026, 11, 13)) }

  it "includes captured breakfast and transfer charges in saved booking and payment totals" do
    booking.add_service(BreakfastPackage.new, quantity: 2)
    booking.add_service(AirportTransfer.new)
    expect(booking.booking_services.pluck(:service_type)).to contain_exactly("BreakfastPackage", "AirportTransfer")
    expect(described_class.total(booking.booking_services)).to eq(100)
    expect(booking.reload.total_ht).to eq(400)
    expect(booking.total_ttc).to eq(480)
    expect(booking.payment.amount).to eq(480)
  end

  it "recalculates prices after quantity updates and removal without changing dates" do
    selection = booking.add_service(BreakfastPackage.new, quantity: 2)
    selection.update!(quantity: 3)
    expect(booking.reload.total_ht).to eq(390)
    expect(booking.total_ttc).to eq(468)
    selection.destroy!
    expect(booking.reload.total_ht).to eq(300)
    expect(booking.total_ttc).to eq(360)
    expect(booking.payment.amount).to eq(360)
  end

  it "keeps the captured unit price independent of later catalogue prices" do
    selection = booking.add_service(BreakfastPackage.new(unit_price: "30.10"), quantity: 2)
    expect(selection.reload.unit_price).to eq(BigDecimal("30.10"))
    expect(booking.reload.total_ht).to eq(BigDecimal("360.20"))
    expect(BreakfastPackage.new(unit_price: 40).price).to eq(40)
    expect(selection.reload.subtotal).to eq(BigDecimal("60.20"))
  end

  it "rejects zero and negative quantities without altering the booking total" do
    [0, -1].each do |quantity|
      expect { booking.add_service(BreakfastPackage.new, quantity: quantity) }.to raise_error(ActiveRecord::RecordInvalid)
    end
    expect(booking.reload.total_ttc).to eq(360)
    expect(booking.booking_services.count).to eq(0)
  end

  it "rejects negative unit prices and unrecognized service types" do
    expect { booking.add_service(BreakfastPackage.new(unit_price: -1)) }.to raise_error(ActiveRecord::RecordInvalid)
    expect { booking.booking_services.create!(service_type: "Unknown", unit_price: 1, quantity: 1) }.to raise_error(ActiveRecord::RecordInvalid)
    expect(booking.reload.total_ht).to eq(300)
  end

  it "keeps the original room-only total when no services are selected" do
    expect(described_class.total(booking.booking_services)).to eq(0)
    expect(booking.total_ht).to eq(300)
    expect(booking.total_ttc).to eq(360)
  end

  it "updates the existing pending payment rather than creating a replacement" do
    payment_id = booking.payment.id
    booking.add_service(AirportTransfer.new)
    expect(booking.reload.payment.id).to eq(payment_id)
    expect(booking.payment.amount).to eq(408)
  end
end
