"""Reproduce current source-review observation counts, not historical review events.

The candidate decisions are documented judgements; this tool resolves their source
bounds and counts records. It does not discover patterns or recover past judgements.
"""
import csv
from collections import Counter
from pathlib import Path
from rebuild_part2 import PART, STAGES, VERSIONS, tree, write_csv

# earliest checkpoint, observation, current judgement, rationale, inspected files
CANDIDATES = [
    (0, 'Strategy via Pundit', 'rejected', 'Authorization policy classes do not establish a context delegating interchangeable business algorithms.', ['app/policies/booking_policy.rb', 'app/controllers/concerns/crud_concern.rb']),
    (0, 'Strategy via CRUD hooks', 'rejected', 'Hook variation belongs to the preserved Template Method skeleton.', ['app/controllers/concerns/crud_concern.rb', 'app/controllers/bookings_controller.rb']),
    (0, 'Policy inheritance', 'rejected', 'Policy inheritance alone does not prove a GoF collaboration.', ['app/policies/application_policy.rb', 'app/policies/booking_policy.rb']),
    (0, 'Observer via callbacks', 'rejected', 'Callbacks do not establish application-owned subject and observer objects.', ['app/models/booking.rb']),
    (0, 'Adapter via Payify', 'uncertain', 'Dependency internals are excluded; application calls do not prove the claimed dependency collaboration.', ['app/models/booking.rb', 'config/initializers/payify.rb']),
    (0, 'Facade via Payify', 'uncertain', 'Dependency internals are excluded; no application-owned facade collaboration is established.', ['app/models/booking.rb', 'config/initializers/payify.rb']),
    (0, 'Decorator via concerns', 'rejected', 'Mixin inclusion does not show runtime wrapping of component objects.', ['app/models/booking.rb', 'app/models/concerns/has_price_concern.rb']),
    (0, 'Composite via associations', 'rejected', 'Associations do not supply recursive uniform part-whole operations.', ['app/models/booking.rb', 'app/models/room.rb']),
    (0, 'Factory via constructors', 'rejected', 'Persistence helpers do not provide varying application-owned factory products.', ['app/controllers/concerns/crud_concern.rb', 'app/models/booking.rb']),
    (0, 'Command via controller actions', 'rejected', 'A controller action is not a separately encapsulated command collaboration.', ['app/controllers/concerns/crud_concern.rb']),
    (0, 'State via booking flags', 'rejected', 'No state-object family delegates state-dependent booking operations.', ['app/models/booking.rb']),
    (0, 'Memento via persistence', 'rejected', 'Persistence alone is not an object-state snapshot/restore collaboration.', ['app/models/booking.rb']),
    (0, 'Chain of Responsibility via request flow', 'rejected', 'Framework request processing is not an application-owned handler chain.', ['app/controllers/application_controller.rb', 'app/controllers/concerns/crud_concern.rb']),
    (0, 'Prototype via Active Record', 'rejected', 'No prototype-based object creation is established in inspected domain source.', ['app/models/booking.rb', 'app/models/room.rb']),
    (0, 'Singleton via configuration', 'rejected', 'A global configuration constant does not establish a Singleton implementation.', ['config/initializers/app_global.rb']),
    (1, 'Decorator via optional services', 'rejected', 'Captured service records are added arithmetically, not wrapped component objects.', ['app/models/booking_service.rb', 'app/models/booking.rb']),
    (1, 'Composite via optional services', 'rejected', 'The selection list is not a recursive uniform component hierarchy.', ['app/models/booking_service.rb', 'app/services/additional_service_pricing.rb']),
    (1, 'Strategy via AdditionalService', 'rejected', 'Pricing sums captured subtotals; no interchangeable pricing algorithm context is present.', ['app/models/additional_service.rb', 'app/services/additional_service_pricing.rb']),
    (1, 'Factory via service constructors', 'rejected', 'AdditionalService subclasses are direct value-object construction, not polymorphic factory hooks.', ['app/models/additional_service.rb', 'app/models/breakfast_package.rb', 'app/models/airport_transfer.rb']),
    (2, 'Command via RoomUpgrade', 'rejected', 'Domain operation extraction is not evidence of an invoker/command/receiver collaboration.', ['app/services/room_upgrade.rb']),
    (2, 'State via RoomUpgrade', 'rejected', 'The operation changes the associated room without a state-object family.', ['app/services/room_upgrade.rb', 'app/models/booking.rb']),
    (2, 'Strategy via RoomUpgrade', 'rejected', 'Upgrade workflow is not delegated to interchangeable upgrade algorithms.', ['app/services/room_upgrade.rb']),
    (3, 'Factory Method via policy selector', 'rejected', 'Configuration lookup plus direct construction is a composition root, without polymorphic creator hooks.', ['config/initializers/cancellation_policy.rb']),
]

TEMPLATE = ['CrudConcern', 'BookingsController', 'RoomsController', 'SettingsController']
POLICY = ['CancellationService', 'CancellationPolicy', 'FlexibleCancellationPolicy', 'PartialRefundCancellationPolicy', 'NoRefundCancellationPolicy']
CALLABLE = 'Rails.application.config.x.cancellation_policy'


def records():
    observations, summaries = [], []
    for i, stage in enumerate(STAGES):
        source = tree(PART / 'checkpoints' / stage)
        declarations = '\n'.join(b.decode('utf-8') for p,b in source.items() if p.endswith('.rb'))
        symbols = TEMPLATE + (POLICY + [CALLABLE] if i == 3 else [])
        for symbol in symbols:
            assert symbol in declarations, f'{stage}: participant {symbol} missing'
        for first, name, status, reason, paths in CANDIDATES:
            if first > i:
                continue
            refs = '; '.join(f'Part2/checkpoints/{stage}/{p}:1-{len(source[p].decode().splitlines())}' for p in paths)
            observations.append(dict(source_version=VERSIONS[i], observation_name=name, decision=status, reason=reason, source_locations=refs,
                                     review_basis='Current source review; not a recovered historical review event'))
        counts = Counter(r['decision'] for r in observations if r['source_version'] == VERSIONS[i])
        summaries.append(dict(source_version=VERSIONS[i], pattern_types=2 if i == 3 else 1, pattern_instances=2 if i == 3 else 1,
                              concrete_participant_classes=6 if i == 3 else 3, unique_participant_symbols=len(symbols),
                              rejected_observations=counts['rejected'], uncertain_observations=counts['uncertain'],
                              participant_symbols='; '.join(symbols), source_locations='Part2/checkpoints/'+stage+'/'))
    return observations, summaries


if __name__ == '__main__':
    dest = PART / 'evidence'; dest.mkdir(exist_ok=True)
    obs, summary = records()
    write_csv(dest / 'pattern_observations.csv', list(obs[0]), obs)
    write_csv(dest / 'snapshot_summary.csv', list(summary[0]), summary)
    for row in summary:
        print(row['source_version'], 'types/instances/concrete/symbols/rejected/uncertain:',
              *(row[k] for k in ['pattern_types','pattern_instances','concrete_participant_classes','unique_participant_symbols','rejected_observations','uncertain_observations']))
