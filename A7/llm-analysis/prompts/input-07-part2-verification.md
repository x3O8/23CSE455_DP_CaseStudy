# Frozen input context for experiment 07
Captured current repository files for a new read-only experiment. Test receipts are prior executed evidence, not new model-run tests. Repository HEAD ce01bfaa2cb38a27896c7cd0b23626b7745db2d2.

## Part2/changes/Change1/diff.md (SHA-256 01b81d4b00c6d8e307c980de3faee9465a2a11b468c9222578619cae4ecc6eeb)
1: # Change1: additional services
2: 
3: The machine-applicable diff is `diff.patch`, from `Part2/checkpoints/original/` to `Part2/checkpoints/Change1/`. This is a reconstructed review stage, not a historical commit. Bundle/platform and eager-loading support are assigned to this first runnable evolved stage. The copied provenance note is removed from evolved checkpoints; baseline provenance remains retained. Test counts below describe the feature specification; consult fresh stage receipts for executed results.
4: 
5: + app/models/additional_service.rb
6: + app/models/breakfast_package.rb
7: + app/models/airport_transfer.rb
8: + app/models/booking_service.rb
9: + app/services/additional_service_pricing.rb
10: + db/migrate/20261004170000_create_booking_services.rb
11: + Booking has_many :booking_services, dependent: :destroy
12: + Booking#add_service captures service type, unit price and quantity.
13: + Booking#compute_price_ht adds optional services to the room subtotal.
14: + BookingService save/destroy callbacks recalculate booking totals under a lock.
15: + HasPriceConcern refreshes totals on save; pending payments retain their identity and get the new amount, while paid amounts remain unchanged.
16: + spec/services/additional_service_pricing_spec.rb: seven database-backed examples.
17: 
18: Refactoring effect: optional-service pricing is moved away from controller branching into a small domain/service layer.

## Part2/code/app/services/additional_service_pricing.rb (SHA-256 d5466c57ccac705bfdc152831ad7e6d8b18988673838a6689ada1d522a490561)
1: class AdditionalServicePricing
2:   def self.total(services)
3:     services.sum { |service| service.subtotal }
4:   end
5: end

## code/app/controllers/bookings_controller.rb (SHA-256 9401eb2d86caf416cd122fa2da0708e38236774fce0190a70867819131d161ef)
1: class BookingsController < ApplicationController
2:   include ::CrudConcern
3: 
4:   before_action :stripe_init_intent, only: [:show]
5: 
6:   def cancel
7:     set_object
8: 
9:     authorize @object
10: 
11:     @object.cancel!
12: 
13:     redirect_to_show(@object)
14:   end
15: 
16:   private
17: 
18:   def base_class
19:     ::Booking
20:   end
21: 
22:   def object_class
23:     return base_class.none if current_user.nil?
24: 
25:     base_class.where(user_id: current_user.id)
26:   end
27: 
28:   def strong_params
29:     [
30:       :start_date, :end_date, :num_guests, :room_id
31:     ]
32:   end
33: 
34:   def model_params
35:     :booking
36:   end
37: 
38:   def use_slug?
39:     false
40:   end
41: 
42:   def stripe_init_intent
43:     return unless @object.payment_pending?
44: 
45:     @object.payment.stripe_init_intent
46:   end
47: end

## code/app/models/booking.rb (SHA-256 ca5fd15dbf3d42bf0137ebef14a1d83840424bd68782cf554e7478f7a925ebff)
1: class Booking < ApplicationRecord
2:   include ::Payify::HasPaymentConcern
3: 
4:   include ::HasOwnerConcern
5:   include ::HasPriceConcern
6: 
7:   after_save :create_payment
8:   after_create :notify_booking
9: 
10:   belongs_to :user
11:   belongs_to :room
12: 
13:   validates :start_date, :end_date, :room_id, :user_id, presence: true
14:   validate :end_date_greater_than_start_date
15:   validate :dates_are_available
16: 
17:   def end_date_greater_than_start_date
18:     errors.add(:end_date, I18n.t("activerecord.errors.models.booking.invalid_dates")) if end_date && start_date && end_date <= start_date
19:   end
20: 
21:   def dates_are_available
22:     conflicting_bookings = room.bookings.where.not(id: id).where("(? < end_date) AND (? > start_date)", start_date, end_date)
23: 
24:     errors.add(:base, I18n.t("activerecord.errors.models.booking.unavailable_dates")) if conflicting_bookings.exists?
25:   end
26: 
27:   def self.default_sort
28:     "created_at desc"
29:   end
30: 
31:   def start_formated
32:     I18n.l(start_date, format: :long)
33:   end
34: 
35:   def end_formated
36:     I18n.l(end_date, format: :long)
37:   end
38: 
39:   def formated_dates
40:     "#{start_formated} - #{end_formated}"
41:   end
42: 
43:   def start_or_end_changed?
44:     start_date_changed? || end_date_changed?
45:   end
46: 
47:   def canceled?
48:     canceled_at.present?
49:   end
50: 
51:   def payment_pending?
52:     !canceled? && payment&.status == "pending"
53:   end
54: 
55:   def paid?
56:     payment&.paid?
57:   end
58: 
59:   def cancel!
60:     update_attribute :canceled_at, Time.now
61:   end
62: 
63:   def amount_to_pay
64:     total_ttc
65:   end
66: 
67:   def notify_booking
68:     return unless Integromat.config.web_hooks.key?(:booking)
69: 
70:     Integromat::Webhook.new(:booking).trigger(start: start_date, end: end_date, guests: num_guests, room: room.title, user: user.email, total_ht: total_ht)
71:   end
72: end

## Part2/code/app/services/room_upgrade.rb (SHA-256 bbda4dfdb2a3aef6c01f7f456bef36118c383509122a620fdca9d58a705b9503)
1: class RoomUpgrade
2:   Result = Struct.new(:success?, :booking, :difference, :error, keyword_init: true)
3: 
4:   def initialize(booking, target_room)
5:     @booking = booking
6:     @target_room = target_room
7:   end
8: 
9:   def call
10:     @target_room.with_lock do
11:       @booking.with_lock do
12:         if @booking.canceled?
13:           failure("Canceled bookings cannot be upgraded")
14:         elsif !available?
15:           failure("Target room is unavailable for the booking dates")
16:         else
17:           difference = price_difference
18:           @booking.upgraded_from_room ||= @booking.room
19:           @booking.room = @target_room
20:           @booking.save!
21:           Result.new(success?: true, booking: @booking, difference: difference, error: nil)
22:         end
23:       end
24:     end
25:   rescue ActiveRecord::RecordInvalid => e
26:     @booking.reload
27:     failure(e.message)
28:   end
29: 
30:   private
31: 
32:   def available?
33:     @target_room.bookings.active.where.not(id: @booking.id).where("(? < end_date) AND (? > start_date)", @booking.start_date, @booking.end_date).none?
34:   end
35: 
36:   def price_difference
37:     nights = (@booking.end_date - @booking.start_date).to_i
38:     (@target_room.day_price - @booking.room.day_price) * nights
39:   end
40: 
41:   def failure(message)
42:     Result.new(success?: false, booking: @booking, difference: 0, error: message)
43:   end
44: end

## Part2/checkpoints/Change2/app/models/booking.rb (SHA-256 33c545149828c042d786d91a808a4b6fe4fb9222d8cdb36ad338085057354bec)
1: class Booking < ApplicationRecord
2:   include ::Payify::HasPaymentConcern
3: 
4:   include ::HasOwnerConcern
5:   include ::HasPriceConcern
6: 
7:   after_save :create_payment
8:   after_create :notify_booking
9: 
10:   belongs_to :user
11:   belongs_to :room
12:   belongs_to :upgraded_from_room, class_name: "Room", optional: true
13:   has_many :booking_services, dependent: :destroy
14: 
15:   scope :active, -> { where(canceled_at: nil) }
16: 
17:   validates :start_date, :end_date, :room_id, :user_id, presence: true
18:   validate :end_date_greater_than_start_date
19:   validate :dates_are_available
20: 
21:   def end_date_greater_than_start_date
22:     errors.add(:end_date, I18n.t("activerecord.errors.models.booking.invalid_dates")) if end_date && start_date && end_date <= start_date
23:   end
24: 
25:   def dates_are_available
26:     return if room.nil? || start_date.nil? || end_date.nil? || canceled?
27: 
28:     conflicting_bookings = room.bookings.active.where.not(id: id).where("(? < end_date) AND (? > start_date)", start_date, end_date)
29: 
30:     errors.add(:base, I18n.t("activerecord.errors.models.booking.unavailable_dates")) if conflicting_bookings.exists?
31:   end
32: 
33:   def self.default_sort
34:     "created_at desc"
35:   end
36: 
37:   def start_formated
38:     I18n.l(start_date, format: :long)
39:   end
40: 
41:   def end_formated
42:     I18n.l(end_date, format: :long)
43:   end
44: 
45:   def formated_dates
46:     "#{start_formated} - #{end_formated}"
47:   end
48: 
49:   def start_or_end_changed?
50:     start_date_changed? || end_date_changed?
51:   end
52: 
53:   def canceled?
54:     canceled_at.present?
55:   end
56: 
57:   def payment_pending?
58:     !canceled? && payment&.status == "pending"
59:   end
60: 
61:   def paid?
62:     payment&.paid?
63:   end
64: 
65:   def cancel!
66:     update_attribute :canceled_at, Time.now
67:   end
68: 
69:   def amount_to_pay
70:     total_ttc
71:   end
72: 
73:   def compute_price_ht
74:     super + AdditionalServicePricing.total(booking_services)
75:   end
76: 
77:   def add_service(service, quantity: 1)
78:     booking_services.create!(service_type: service.class.name, unit_price: service.unit_price, quantity: quantity)
79:   end
80: 
81:   def create_payment
82:     return payment if canceled?
83: 
84:     if payment
85:       payment.update!(amount: amount_to_pay) if payment.pending? && !payment.paid?
86:       payment
87:     else
88:       build_payment(amount: amount_to_pay).tap(&:save!)
89:     end
90:   end
91: 
92:   def notify_booking
93:     return unless Integromat.config.web_hooks.key?(:booking)
94: 
95:     Integromat::Webhook.new(:booking).trigger(start: start_date, end: end_date, guests: num_guests, room: room.title, user: user.email, total_ht: total_ht)
96:   end
97: end

## Part2/code/app/services/cancellation_service.rb (SHA-256 3927fab03617807b83e7a376060952b85416eead321016c73ac476857fd64399)
1: class CancellationService
2:   def initialize(booking, policy:)
3:     @booking = booking
4:     @policy = policy
5:   end
6: 
7:   def call(at: Time.current)
8:     @booking.with_lock do
9:       raise ArgumentError, "Booking is already canceled" if @booking.canceled?
10:       raise ArgumentError, "Cancellation is not permitted" unless @policy.cancellable?(@booking, at: at)
11: 
12:       refund = @policy.refund_amount(@booking, at: at)
13:       @booking.update!(canceled_at: at, cancellation_refund_amount: refund)
14:       { booking: @booking, refund_amount: refund }
15:     end
16:   end
17: end

## Part2/code/app/services/cancellation_policy.rb (SHA-256 276d9f37c8a238a496f53d0d3001e3bfab601efda0ed2055e2efa25960360689)
1: class CancellationPolicy
2:   def cancellable?(_booking, at:)
3:     raise NotImplementedError
4:   end
5: 
6:   def refund_amount(_booking, at:)
7:     raise NotImplementedError
8:   end
9: end

## Part2/code/app/services/flexible_cancellation_policy.rb (SHA-256 9278d501836795ec8b31c11eb7defe47deb80299f82dbe05177e3d35ed8de1e0)
1: class FlexibleCancellationPolicy < CancellationPolicy
2:   def cancellable?(_booking, at:)
3:     true
4:   end
5: 
6:   def refund_amount(booking, at:)
7:     booking.amount_to_pay
8:   end
9: end

## Part2/code/app/services/partial_refund_cancellation_policy.rb (SHA-256 cc8b30896f309f0e81bf98049981b36cd08beb723b9a88d89f20feebc473dfca)
1: class PartialRefundCancellationPolicy < CancellationPolicy
2:   def initialize(rate: 0.5)
3:     @rate = BigDecimal(rate.to_s)
4:     raise ArgumentError, "Refund rate must be between zero and one" unless @rate.finite? && @rate.between?(0, 1)
5:   end
6: 
7:   def cancellable?(_booking, at:)
8:     true
9:   end
10: 
11:   def refund_amount(booking, at:)
12:     (booking.amount_to_pay * @rate).round(2)
13:   end
14: end

## Part2/code/app/services/no_refund_cancellation_policy.rb (SHA-256 c3065dcc7238a63da1fa453deef62f9133cf157d95ca51d085d59aae81976e8d)
1: class NoRefundCancellationPolicy < CancellationPolicy
2:   def cancellable?(_booking, at:)
3:     true
4:   end
5: 
6:   def refund_amount(_booking, at:)
7:     0
8:   end
9: end

## Part2/code/app/controllers/bookings_controller.rb (SHA-256 80c0786ad3598be9bec4289d29999afbd0a86a0a4ddd834f3c2abce388135dd5)
1: class BookingsController < ApplicationController
2:   include ::CrudConcern
3: 
4:   before_action :stripe_init_intent, only: [:show]
5:   before_action :authenticate_user!, only: [:cancel]
6: 
7:   def cancel
8:     set_object
9:     return if performed?
10: 
11:     authorize @object
12: 
13:     policy = Rails.application.config.x.cancellation_policy.call
14:     result = CancellationService.new(@object, policy: policy).call
15:     flash[:notice] = "Booking canceled. Calculated refund: #{result[:refund_amount]}"
16: 
17:     redirect_to_show(@object)
18:   rescue ArgumentError => e
19:     flash[:alert] = e.message
20:     redirect_to_show(@object)
21:   end
22: 
23:   private
24: 
25:   def base_class
26:     ::Booking
27:   end
28: 
29:   def object_class
30:     return base_class.none if current_user.nil?
31: 
32:     base_class.where(user_id: current_user.id)
33:   end
34: 
35:   def strong_params
36:     [
37:       :start_date, :end_date, :num_guests, :room_id
38:     ]
39:   end
40: 
41:   def model_params
42:     :booking
43:   end
44: 
45:   def use_slug?
46:     false
47:   end
48: 
49:   def stripe_init_intent
50:     return unless @object.payment_pending?
51: 
52:     @object.payment.stripe_init_intent
53:   end
54: end

## Part2/code/config/initializers/cancellation_policy.rb (SHA-256 98818378e407cc680fc024d2909f4d46192b202992b5ee8351e4b6df06a083f2)
1: # Policy selection is server configuration, never a client-supplied parameter.
2: policy_classes = {
3:   "flexible" => "FlexibleCancellationPolicy",
4:   "partial" => "PartialRefundCancellationPolicy",
5:   "no_refund" => "NoRefundCancellationPolicy"
6: }.freeze
7: 
8: Rails.application.config.x.cancellation_policy = lambda do
9:   policy_classes.fetch(ENV.fetch("CANCELLATION_POLICY", "flexible")).constantize.new
10: end

## code/app/controllers/concerns/crud_concern.rb (SHA-256 41e22a529003b85fe4e2eabfc63f277a2b7ae7391e88e76089786e7c716d2662)
1: module CrudConcern
2:   extend ActiveSupport::Concern
3: 
4:   included do
5:     before_action :set_object, only: %i[edit update destroy show undelete]
6:   end
7: 
8:   def index
9:     authorize base_class
10: 
11:     init_pagination
12: 
13:     @objects = objects_paginated
14:   end
15: 
16:   def show
17:     return redirect_to_list unless @object
18: 
19:     authorize @object
20:   end
21: 
22:   def new
23:     authorize object_class
24: 
25:     @object = object_class.new(initial_value)
26:   end
27: 
28:   def create
29:     authorize object_class
30: 
31:     @object = object_class.new(form_values)
32: 
33:     if @object.valid?
34:       @object.save!
35: 
36:       redirect_to_show(@object)
37:     else
38:       render :new, status: :unprocessable_entity
39:     end
40:   end
41: 
42:   def edit
43:     authorize @object
44: 
45:     render "new"
46:   end
47: 
48:   def update
49:     authorize @object
50: 
51:     @object.assign_attributes(form_values)
52: 
53:     if @object.valid?
54:       @object.save!
55: 
56:       redirect_to_show(@object)
57:     else
58:       render :new, status: :unprocessable_entity
59:     end
60:   end
61: 
62:   def destroy
63:     authorize @object
64: 
65:     @object.destroy
66: 
67:     redirect_to_list
68:   end
69: 
70:   private
71: 
72:   def redirect_to_list
73:     redirect_to polymorphic_path(base_class)
74:   end
75: 
76:   def redirect_to_show(object)
77:     redirect_to polymorphic_path(object, locale: @page_lang)
78:   end
79: 
80:   def initial_value
81:     {}
82:   end
83: 
84:   def total_objects
85:     objects_query.count.to_f
86:   end
87: 
88:   def init_pagination
89:     @per_page     = per_page
90:     @page         = params[:page].present? ? params[:page].to_i : 1
91:     @total_pages  = (total_objects / @per_page.to_f).ceil
92:     @data         = url_params.select { |_, value| !value.nil? && !value.empty? }
93: 
94:     set_page_url
95:   end
96: 
97:   def set_page_url
98:     @page_url = "#{@page_url}?#{@data.to_query}"
99:   end
100: 
101:   def model_params
102:   end
103: 
104:   def url_allowed_params
105:     [:page, :q]
106:   end
107: 
108:   def url_params
109:     params.permit(url_allowed_params).to_hash
110:   end
111: 
112:   def form_values
113:     params.require(model_params).permit(strong_params).to_hash
114:   end
115: 
116:   def per_page
117:     20
118:   end
119: 
120:   def objects_query
121:     object_class.all.order(base_class.default_sort)
122:   end
123: 
124:   def objects_paginated
125:     objects = objects_query
126: 
127:     objects.page(@page).per(@per_page)
128:   end
129: 
130:   def base_class
131:     raise NotImplementedError
132:   end
133: 
134:   def object_class
135:     raise NotImplementedError
136:   end
137: 
138:   def use_slug?
139:     true
140:   end
141: 
142:   def set_object
143:     return @object = object_class.find_by(slug: params[:slug]) if use_slug?
144: 
145:     @object = object_class.find params[:id]
146:   rescue ActiveRecord::RecordNotFound
147:     head :not_found
148:   end
149: end

## Part2/verification/Change1_rails.txt (SHA-256 ae2372888ec2bff67c9141f78a9128c710b57221439f1e4e607e090b3601e57d)
1: Checkpoint: Change1
2: Source: C:\Users\abhij\Desktop\A7\A7\Part2\checkpoints\Change1
3: Database: a7_part2_Change1_test
4: Executed at: 2026-10-11T00:28:15.9150119+05:30
5: Runtime: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/bin/ruby.exe
6: Bundle: checkpoint's own Gemfile/lockfile
7: Command: ruby bin/rails db:create
8: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
9: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
10: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
11: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
12: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
13: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
14: Created database 'a7_part2_Change1_test'
15: Exit code: 0
16: Command: ruby bin/rails db:migrate
17: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
18: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
19: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
20: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
21: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
22: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
23: == 20230518121724 DeviseCreateUsers: migrating ================================
24: -- create_table(:users)
25:    -> 0.0109s
26: -- add_index(:users, :email, {:unique=>true})
27:    -> 0.0037s
28: -- add_index(:users, :reset_password_token, {:unique=>true})
29:    -> 0.0037s
30: == 20230518121724 DeviseCreateUsers: migrated (0.0185s) =======================
31: 
32: == 20230521044444 CreateRooms: migrating ======================================
33: -- create_table(:rooms)
34:    -> 0.0158s
35: == 20230521044444 CreateRooms: migrated (0.0158s) =============================
36: 
37: == 20230521044712 CreateBooking: migrating ====================================
38: -- create_table(:bookings)
39:    -> 0.0128s
40: == 20230521044712 CreateBooking: migrated (0.0129s) ===========================
41: 
42: == 20230531042741 CreateActiveStorageTables: migrating ========================
43: -- create_table(:active_storage_blobs, {:id=>:primary_key})
44:    -> 0.0122s
45: -- create_table(:active_storage_attachments, {:id=>:primary_key})
46:    -> 0.0186s
47: -- create_table(:active_storage_variant_records, {:id=>:primary_key})
48:    -> 0.0135s
49: == 20230531042741 CreateActiveStorageTables: migrated (0.0445s) ===============
50: 
51: == 20230608045813 AddTotalPriceToBooking: migrating ===========================
52: -- add_column(:bookings, :total_ht, :decimal, {:default=>0.0})
53:    -> 0.0053s
54: -- add_column(:bookings, :total_ttc, :decimal, {:default=>0.0})
55:    -> 0.0006s
56: == 20230608045813 AddTotalPriceToBooking: migrated (0.0059s) ==================
57: 
58: == 20230609044940 AddCancelToBooking: migrating ===============================
59: -- add_column(:bookings, :canceled_at, :datetime, {:null=>true})
60:    -> 0.0005s
61: == 20230609044940 AddCancelToBooking: migrated (0.0005s) ======================
62: 
63: == 20230610114044 CreateSettingsTable: migrating ==============================
64: -- create_table(:settings)
65:    -> 0.0122s
66: == 20230610114044 CreateSettingsTable: migrated (0.0123s) =====================
67: 
68: == 20230618133900 CreatePayment: migrating ====================================
69: -- create_table(:payify_payments)
70:    -> 0.0105s
71: == 20230618133900 CreatePayment: migrated (0.0105s) ===========================
72: 
73: == 20230618133901 AddStripePaymentIntentId: migrating =========================
74: -- add_column(:payify_payments, :stripe_payment_inent_id, :string)
75:    -> 0.0008s
76: -- add_column(:payify_payments, :stripe_client_secret, :string)
77:    -> 0.0004s
78: == 20230618133901 AddStripePaymentIntentId: migrated (0.0012s) ================
79: 
80: == 20261004170000 CreateBookingServices: migrating ============================
81: -- create_table(:booking_services)
82:    -> 0.0142s
83: == 20261004170000 CreateBookingServices: migrated (0.0142s) ===================
84: 
85: Exit code: 0
86: Command: ruby -rbundler/setup -e load Gem.bin_path("rspec-core", "rspec") -- spec --format documentation
87: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
88: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
89: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
90: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
91: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
92: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
93: 
94: Evolved application boot
95:   eager loads the application and payment engine without unresolved constants
96: 
97: Booking
98:   When checking the booking price
99:     Book a room and check price
100:   When checking booking dates
101:     Should require start and end dates
102:     should be valid if there are no conflicting bookings
103:     should be invalid if there are conflicting bookings
104: 
105: Room
106:   Create a room
107: 
108: AdditionalServicePricing
109:   includes captured breakfast and transfer charges in saved booking and payment totals
110:   recalculates prices after quantity updates and removal without changing dates
111:   keeps the captured unit price independent of later catalogue prices
112:   rejects zero and negative quantities without altering the booking total
113:   rejects negative unit prices and unrecognized service types
114:   keeps the original room-only total when no services are selected
115:   updates the existing pending payment rather than creating a replacement
116: 
117: Finished in 7.94 seconds (files took 13.86 seconds to load)
118: 13 examples, 0 failures
119: 
120: Exit code: 0

## Part2/verification/Change2_rails.txt (SHA-256 9a5b08c4fda776b919847cf89ed1444c8f80b741ee5af2ff6b5e9683e8f0b123)
1: Checkpoint: Change2
2: Source: C:\Users\abhij\Desktop\A7\A7\Part2\checkpoints\Change2
3: Database: a7_part2_Change2_test
4: Executed at: 2026-10-11T00:29:11.1517123+05:30
5: Runtime: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/bin/ruby.exe
6: Bundle: checkpoint's own Gemfile/lockfile
7: Command: ruby bin/rails db:create
8: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
9: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
10: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
11: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
12: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
13: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
14: Database 'a7_part2_Change2_test' already exists
15: Exit code: 0
16: Command: ruby bin/rails db:migrate
17: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
18: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
19: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
20: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
21: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
22: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
23: Exit code: 0
24: Command: ruby -rbundler/setup -e load Gem.bin_path("rspec-core", "rspec") -- spec --format documentation
25: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
26: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
27: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
28: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
29: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
30: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
31: 
32: Evolved application boot
33:   eager loads the application and payment engine without unresolved constants
34: 
35: Booking
36:   When checking the booking price
37:     Book a room and check price
38:   When checking booking dates
39:     Should require start and end dates
40:     should be valid if there are no conflicting bookings
41:     should be invalid if there are conflicting bookings
42: 
43: Room
44:   Create a room
45: 
46: AdditionalServicePricing
47:   includes captured breakfast and transfer charges in saved booking and payment totals
48:   recalculates prices after quantity updates and removal without changing dates
49:   keeps the captured unit price independent of later catalogue prices
50:   rejects zero and negative quantities without altering the booking total
51:   rejects negative unit prices and unrecognized service types
52:   keeps the original room-only total when no services are selected
53:   updates the existing pending payment rather than creating a replacement
54: 
55: RoomUpgrade
56:   rejects overlapping reservations without changing persisted room or totals
57:   persists an available room, its original room and the independently calculated difference
58:   allows adjacent checkout/check-in dates
59:   ignores canceled reservations in the target room
60:   retains service charges when the room price changes
61:   preserves the first original room across multiple upgrades
62:   restores the original persisted state when validation fails
63:   rejects upgrades of a canceled booking
64: 
65: Finished in 7.9 seconds (files took 15.99 seconds to load)
66: 21 examples, 0 failures
67: 
68: Exit code: 0

## Part2/verification/Change3_rails.txt (SHA-256 5d8e9bd4ae914cb75a71b9c5ce6e8c2d738f51036d89337e54e70c40e79ad0ae)
1: Checkpoint: Change3
2: Source: C:\Users\abhij\Desktop\A7\A7\Part2\checkpoints\Change3
3: Database: a7_part2_Change3_test
4: Executed at: 2026-10-11T00:30:03.2469624+05:30
5: Runtime: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/bin/ruby.exe
6: Bundle: checkpoint's own Gemfile/lockfile
7: Command: ruby bin/rails db:create
8: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
9: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
10: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
11: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
12: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
13: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
14: Created database 'a7_part2_Change3_test'
15: Exit code: 0
16: Command: ruby bin/rails db:migrate
17: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
18: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
19: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
20: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
21: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
22: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
23: == 20230518121724 DeviseCreateUsers: migrating ================================
24: -- create_table(:users)
25:    -> 0.0122s
26: -- add_index(:users, :email, {:unique=>true})
27:    -> 0.0034s
28: -- add_index(:users, :reset_password_token, {:unique=>true})
29:    -> 0.0033s
30: == 20230518121724 DeviseCreateUsers: migrated (0.0190s) =======================
31: 
32: == 20230521044444 CreateRooms: migrating ======================================
33: -- create_table(:rooms)
34:    -> 0.0155s
35: == 20230521044444 CreateRooms: migrated (0.0156s) =============================
36: 
37: == 20230521044712 CreateBooking: migrating ====================================
38: -- create_table(:bookings)
39:    -> 0.0135s
40: == 20230521044712 CreateBooking: migrated (0.0136s) ===========================
41: 
42: == 20230531042741 CreateActiveStorageTables: migrating ========================
43: -- create_table(:active_storage_blobs, {:id=>:primary_key})
44:    -> 0.0123s
45: -- create_table(:active_storage_attachments, {:id=>:primary_key})
46:    -> 0.0179s
47: -- create_table(:active_storage_variant_records, {:id=>:primary_key})
48:    -> 0.0118s
49: == 20230531042741 CreateActiveStorageTables: migrated (0.0422s) ===============
50: 
51: == 20230608045813 AddTotalPriceToBooking: migrating ===========================
52: -- add_column(:bookings, :total_ht, :decimal, {:default=>0.0})
53:    -> 0.0049s
54: -- add_column(:bookings, :total_ttc, :decimal, {:default=>0.0})
55:    -> 0.0008s
56: == 20230608045813 AddTotalPriceToBooking: migrated (0.0058s) ==================
57: 
58: == 20230609044940 AddCancelToBooking: migrating ===============================
59: -- add_column(:bookings, :canceled_at, :datetime, {:null=>true})
60:    -> 0.0006s
61: == 20230609044940 AddCancelToBooking: migrated (0.0007s) ======================
62: 
63: == 20230610114044 CreateSettingsTable: migrating ==============================
64: -- create_table(:settings)
65:    -> 0.0135s
66: == 20230610114044 CreateSettingsTable: migrated (0.0135s) =====================
67: 
68: == 20230618133900 CreatePayment: migrating ====================================
69: -- create_table(:payify_payments)
70:    -> 0.0099s
71: == 20230618133900 CreatePayment: migrated (0.0099s) ===========================
72: 
73: == 20230618133901 AddStripePaymentIntentId: migrating =========================
74: -- add_column(:payify_payments, :stripe_payment_inent_id, :string)
75:    -> 0.0007s
76: -- add_column(:payify_payments, :stripe_client_secret, :string)
77:    -> 0.0004s
78: == 20230618133901 AddStripePaymentIntentId: migrated (0.0012s) ================
79: 
80: == 20261004170000 CreateBookingServices: migrating ============================
81: -- create_table(:booking_services)
82:    -> 0.0130s
83: == 20261004170000 CreateBookingServices: migrated (0.0130s) ===================
84: 
85: == 20261004171000 AddRoomUpgradeFieldsToBookings: migrating ===================
86: -- add_reference(:bookings, :upgraded_from_room, {:foreign_key=>{:to_table=>:rooms}, :null=>true})
87:    -> 0.0053s
88: == 20261004171000 AddRoomUpgradeFieldsToBookings: migrated (0.0053s) ==========
89: 
90: == 20261010190000 AddCancellationRefundAmountToBookings: migrating ============
91: -- add_column(:bookings, :cancellation_refund_amount, :decimal, {:precision=>10, :scale=>2})
92:    -> 0.0007s
93: == 20261010190000 AddCancellationRefundAmountToBookings: migrated (0.0007s) ===
94: 
95: Exit code: 0
96: Command: ruby -rbundler/setup -e load Gem.bin_path("rspec-core", "rspec") -- spec --format documentation
97: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:66: warning: already initialized constant Net::ProtocRetryError
98: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:68: warning: previous definition of ProtocRetryError was here
99: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:206: warning: already initialized constant Net::BufferedIO::BUFSIZE
100: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:214: warning: previous definition of BUFSIZE was here
101: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/rubydevkit/lib/ruby/2.7.0/net/protocol.rb:503: warning: already initialized constant Net::NetPrivate::Socket
102: C:/Users/abhij/Desktop/Design Patterns Case Study/.tools/gems/gems/net-protocol-0.2.1/lib/net/protocol.rb:541: warning: previous definition of Socket was here
103: 
104: Evolved application boot
105:   eager loads the application and payment engine without unresolved constants
106: 
107: Booking
108:   When checking the booking price
109:     Book a room and check price
110:   When checking booking dates
111:     Should require start and end dates
112:     should be valid if there are no conflicting bookings
113:     should be invalid if there are conflicting bookings
114: 
115: Room
116:   Create a room
117: 
118: Rails booking cancellation
119:   uses the configured Strategy through the real POST route
120:   uses flexible cancellation by default
121:   does not let request parameters choose a more generous policy
122:   does not cancel another user's booking
123:   redirects guests to authentication without canceling
124:   reports repeated cancellation without changing the refund
125: 
126: AdditionalServicePricing
127:   includes captured breakfast and transfer charges in saved booking and payment totals
128:   recalculates prices after quantity updates and removal without changing dates
129:   keeps the captured unit price independent of later catalogue prices
130:   rejects zero and negative quantities without altering the booking total
131:   rejects negative unit prices and unrecognized service types
132:   keeps the original room-only total when no services are selected
133:   updates the existing pending payment rather than creating a replacement
134: 
135: CancellationService
136:   calculates and persists 360 with FlexibleCancellationPolicy
137:   calculates and persists 180 with PartialRefundCancellationPolicy
138:   calculates and persists 0 with NoRefundCancellationPolicy
139:   includes optional service charges in the refund basis
140:   supports a non-default partial refund rate
141:   leaves a denied booking uncanceled
142:   rejects repeated cancellation without replacing the original audit record
143:   rejects invalid partial refund rates
144:   preserves a paid payment record when canceling
145: 
146: RoomUpgrade
147:   rejects overlapping reservations without changing persisted room or totals
148:   persists an available room, its original room and the independently calculated difference
149:   allows adjacent checkout/check-in dates
150:   ignores canceled reservations in the target room
151:   retains service charges when the room price changes
152:   preserves the first original room across multiple upgrades
153:   restores the original persisted state when validation fails
154:   rejects upgrades of a canceled booking
155: 
156: Finished in 9.5 seconds (files took 13.15 seconds to load)
157: 36 examples, 0 failures
158: 
159: Exit code: 0
