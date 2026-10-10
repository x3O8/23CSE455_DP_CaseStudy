class PartialRefundCancellationPolicy < CancellationPolicy
  def initialize(rate: 0.5)
    @rate = BigDecimal(rate.to_s)
    raise ArgumentError, "Refund rate must be between zero and one" unless @rate.finite? && @rate.between?(0, 1)
  end

  def cancellable?(_booking, at:)
    true
  end

  def refund_amount(booking, at:)
    (booking.amount_to_pay * @rate).round(2)
  end
end
