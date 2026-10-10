class AdditionalService
  attr_reader :name, :unit_price

  def initialize(name:, unit_price:)
    @name = name
    @unit_price = BigDecimal(unit_price.to_s)
  end

  def price(quantity: 1)
    unit_price * quantity
  end
end
