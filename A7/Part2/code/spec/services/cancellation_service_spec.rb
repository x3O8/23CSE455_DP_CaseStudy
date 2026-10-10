require "rails_helper"

RSpec.describe CancellationService, type: :model do
  let(:user) { create(:user_1) }
  let(:room) { create(:room_1, user: user, day_price: 100) }
  let(:booking) { create(:booking_1, user: user, room: room, start_date: Date.new(2026, 11, 10), end_date: Date.new(2026, 11, 13)) }
  let(:at) { Time.zone.local(2026, 10, 10, 12, 0, 0) }

  [[FlexibleCancellationPolicy, 360], [PartialRefundCancellationPolicy, 180], [NoRefundCancellationPolicy, 0]].each do |policy_class, refund|
    it "calculates and persists #{refund} with #{policy_class}" do
      result = described_class.new(booking, policy: policy_class.new).call(at: at)
      expect(result[:refund_amount]).to eq(refund)
      expect(booking.reload.canceled_at).to eq(at)
      expect(booking.cancellation_refund_amount).to eq(refund)
    end
  end

  it "includes optional service charges in the refund basis" do
    booking.add_service(AirportTransfer.new)
    result = described_class.new(booking, policy: FlexibleCancellationPolicy.new).call(at: at)
    expect(result[:refund_amount]).to eq(408)
    expect(booking.reload.cancellation_refund_amount).to eq(408)
  end

  it "supports a non-default partial refund rate" do
    result = described_class.new(booking, policy: PartialRefundCancellationPolicy.new(rate: 0.25)).call(at: at)
    expect(result[:refund_amount]).to eq(90)
  end

  it "leaves a denied booking uncanceled" do
    denied_policy = Class.new(CancellationPolicy) do
      def cancellable?(_booking, at:); false; end
    end.new
    expect { described_class.new(booking, policy: denied_policy).call(at: at) }.to raise_error(ArgumentError)
    expect(booking.reload).not_to be_canceled
    expect(booking.cancellation_refund_amount).to be_nil
  end

  it "rejects repeated cancellation without replacing the original audit record" do
    described_class.new(booking, policy: FlexibleCancellationPolicy.new).call(at: at)
    expect { described_class.new(booking, policy: NoRefundCancellationPolicy.new).call(at: at + 1.day) }.to raise_error(ArgumentError)
    expect(booking.reload.canceled_at).to eq(at)
    expect(booking.cancellation_refund_amount).to eq(360)
  end

  it "rejects invalid partial refund rates" do
    [-0.1, 1.1].each do |rate|
      expect { PartialRefundCancellationPolicy.new(rate: rate) }.to raise_error(ArgumentError)
    end
  end

  it "preserves a paid payment record when canceling" do
    payment = booking.payment
    payment.update!(status: :paid, paid_at: at - 1.day)
    described_class.new(booking, policy: FlexibleCancellationPolicy.new).call(at: at)
    expect(booking.reload.payment.id).to eq(payment.id)
    expect(booking.payment).to be_paid
    expect(booking.payment.amount).to eq(360)
  end
end
