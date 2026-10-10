class CancellationService
  def initialize(booking, policy:)
    @booking = booking
    @policy = policy
  end

  def call(at: Time.current)
    @booking.with_lock do
      raise ArgumentError, "Booking is already canceled" if @booking.canceled?
      raise ArgumentError, "Cancellation is not permitted" unless @policy.cancellable?(@booking, at: at)

      refund = @policy.refund_amount(@booking, at: at)
      @booking.update!(canceled_at: at, cancellation_refund_amount: refund)
      { booking: @booking, refund_amount: refund }
    end
  end
end
