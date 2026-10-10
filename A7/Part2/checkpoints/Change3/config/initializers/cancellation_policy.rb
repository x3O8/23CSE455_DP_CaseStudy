# Policy selection is server configuration, never a client-supplied parameter.
policy_classes = {
  "flexible" => "FlexibleCancellationPolicy",
  "partial" => "PartialRefundCancellationPolicy",
  "no_refund" => "NoRefundCancellationPolicy"
}.freeze

Rails.application.config.x.cancellation_policy = lambda do
  policy_classes.fetch(ENV.fetch("CANCELLATION_POLICY", "flexible")).constantize.new
end
