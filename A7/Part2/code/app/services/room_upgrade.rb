class RoomUpgrade
  Result = Struct.new(:success?, :booking, :difference, :error, keyword_init: true)

  def initialize(booking, target_room)
    @booking = booking
    @target_room = target_room
  end

  def call
    @target_room.with_lock do
      @booking.with_lock do
        if @booking.canceled?
          failure("Canceled bookings cannot be upgraded")
        elsif !available?
          failure("Target room is unavailable for the booking dates")
        else
          difference = price_difference
          @booking.upgraded_from_room ||= @booking.room
          @booking.room = @target_room
          @booking.save!
          Result.new(success?: true, booking: @booking, difference: difference, error: nil)
        end
      end
    end
  rescue ActiveRecord::RecordInvalid => e
    @booking.reload
    failure(e.message)
  end

  private

  def available?
    @target_room.bookings.active.where.not(id: @booking.id).where("(? < end_date) AND (? > start_date)", @booking.start_date, @booking.end_date).none?
  end

  def price_difference
    nights = (@booking.end_date - @booking.start_date).to_i
    (@target_room.day_price - @booking.room.day_price) * nights
  end

  def failure(message)
    Result.new(success?: false, booking: @booking, difference: 0, error: message)
  end
end
