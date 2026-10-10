class AdditionalServicePricing
  def self.total(services)
    services.sum { |service| service.subtotal }
  end
end
