class AddRoomUpgradeFieldsToBookings < ActiveRecord::Migration[7.0]
  def change
    add_reference :bookings, :upgraded_from_room, foreign_key: { to_table: :rooms }, null: true
  end
end
