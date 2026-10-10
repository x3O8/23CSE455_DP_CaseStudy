class BreakfastPackage < AdditionalService
  def initialize(unit_price: 30)
    super(name: "Breakfast package", unit_price: unit_price)
  end
end
