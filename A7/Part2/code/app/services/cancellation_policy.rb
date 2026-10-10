class CancellationPolicy
  def cancellable?(_booking, at:)
    raise NotImplementedError
  end

  def refund_amount(_booking, at:)
    raise NotImplementedError
  end
end
