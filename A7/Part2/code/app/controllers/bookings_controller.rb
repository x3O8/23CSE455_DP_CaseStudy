class BookingsController < ApplicationController
  include ::CrudConcern

  before_action :stripe_init_intent, only: [:show]
  before_action :authenticate_user!, only: [:cancel]

  def cancel
    set_object
    return if performed?

    authorize @object

    policy = Rails.application.config.x.cancellation_policy.call
    result = CancellationService.new(@object, policy: policy).call
    flash[:notice] = "Booking canceled. Calculated refund: #{result[:refund_amount]}"

    redirect_to_show(@object)
  rescue ArgumentError => e
    flash[:alert] = e.message
    redirect_to_show(@object)
  end

  private

  def base_class
    ::Booking
  end

  def object_class
    return base_class.none if current_user.nil?

    base_class.where(user_id: current_user.id)
  end

  def strong_params
    [
      :start_date, :end_date, :num_guests, :room_id
    ]
  end

  def model_params
    :booking
  end

  def use_slug?
    false
  end

  def stripe_init_intent
    return unless @object.payment_pending?

    @object.payment.stripe_init_intent
  end
end
