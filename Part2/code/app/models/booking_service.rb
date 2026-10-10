class BookingService < ApplicationRecord
  belongs_to :booking

  validates :service_type, inclusion: { in: %w[BreakfastPackage AirportTransfer] }
  validates :quantity, numericality: { only_integer: true, greater_than: 0 }
  validates :unit_price, numericality: { greater_than_or_equal_to: 0 }

  after_save :refresh_booking_prices
  after_destroy :refresh_booking_prices

  def subtotal
    unit_price * quantity
  end

  private

  def refresh_booking_prices
    return if destroyed_by_association

    booking.with_lock do
      booking.booking_services.reset
      booking.save!
    end
  end
end
