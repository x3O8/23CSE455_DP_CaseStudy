class NoRefundCancellationPolicy < CancellationPolicy
  def cancellable?(_booking, at:)
    true
  end

  def refund_amount(_booking, at:)
    0
  end
end
