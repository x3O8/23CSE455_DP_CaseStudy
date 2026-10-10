class AirportTransfer < AdditionalService
  def initialize(unit_price: 40)
    super(name: "Airport transfer", unit_price: unit_price)
  end
end
