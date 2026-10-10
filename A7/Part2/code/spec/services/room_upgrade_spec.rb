require "rails_helper"

RSpec.describe RoomUpgrade, type: :model do
  let(:user) { create(:user_1) }
  let(:room) { create(:room_1, user: user, day_price: 100) }
  let(:target) { create(:room_1, user: user, title: "Upgrade", slug: "upgrade", day_price: 150) }
  let(:booking) { create(:booking_1, user: user, room: room, start_date: Date.new(2026, 11, 10), end_date: Date.new(2026, 11, 13)) }

  it "rejects overlapping reservations without changing persisted room or totals" do
    create(:booking_1, user: user, room: target, start_date: Date.new(2026, 11, 12), end_date: Date.new(2026, 11, 14))
    result = described_class.new(booking, target).call
    expect(result).not_to be_success
    expect(result.error).to be_present
    expect(booking.reload.room).to eq(room)
    expect(booking.total_ht).to eq(300)
    expect(booking.total_ttc).to eq(360)
    expect(booking.upgraded_from_room).to be_nil
  end

  it "persists an available room, its original room and the independently calculated difference" do
    result = described_class.new(booking, target).call
    expect(result).to be_success
    expect(result.difference).to eq(150)
    expect(booking.reload.room).to eq(target)
    expect(booking.upgraded_from_room).to eq(room)
    expect(booking.total_ht).to eq(450)
    expect(booking.total_ttc).to eq(540)
    expect(booking.payment.amount).to eq(540)
  end

  it "allows adjacent checkout/check-in dates" do
    create(:booking_1, user: user, room: target, start_date: Date.new(2026, 11, 13), end_date: Date.new(2026, 11, 14))
    expect(described_class.new(booking, target).call).to be_success
  end

  it "ignores canceled reservations in the target room" do
    occupied = create(:booking_1, user: user, room: target, start_date: booking.start_date, end_date: booking.end_date)
    occupied.cancel!
    expect(described_class.new(booking, target).call).to be_success
  end

  it "retains service charges when the room price changes" do
    booking.add_service(BreakfastPackage.new, quantity: 2)
    result = described_class.new(booking, target).call
    expect(result.difference).to eq(150)
    expect(booking.reload.total_ht).to eq(510)
    expect(booking.total_ttc).to eq(612)
  end

  it "preserves the first original room across multiple upgrades" do
    described_class.new(booking, target).call
    second = create(:room_1, user: user, title: "Suite", slug: "suite", day_price: 200)
    expect(described_class.new(booking, second).call).to be_success
    expect(booking.reload.upgraded_from_room).to eq(room)
    expect(booking.room).to eq(second)
  end

  it "restores the original persisted state when validation fails" do
    booking.update_column(:end_date, booking.start_date)
    result = described_class.new(booking, target).call
    expect(result).not_to be_success
    expect(booking.reload.room).to eq(room)
    expect(booking.upgraded_from_room).to be_nil
    expect(booking.total_ttc).to eq(360)
  end

  it "rejects upgrades of a canceled booking" do
    booking.cancel!
    expect(described_class.new(booking, target).call).not_to be_success
    expect(booking.reload.room).to eq(room)
  end
end
