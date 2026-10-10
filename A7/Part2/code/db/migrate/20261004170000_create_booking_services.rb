class CreateBookingServices < ActiveRecord::Migration[7.0]
  def change
    create_table :booking_services do |t|
      t.references :booking, null: false, foreign_key: true
      t.string :service_type, null: false
      t.integer :quantity, null: false, default: 1
      t.decimal :unit_price, precision: 10, scale: 2, null: false
      t.timestamps
    end
  end
end
