class FlexibleCancellationPolicy < CancellationPolicy
  def cancellable?(_booking, at:)
    true
  end

  def refund_amount(booking, at:)
    booking.amount_to_pay
  end
end
