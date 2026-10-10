class CancellationPolicy { refund(amount){ throw new Error("abstract"); } }
class FlexiblePolicy extends CancellationPolicy { refund(amount){return amount;} }
class PartialRefundPolicy extends CancellationPolicy { refund(amount){return amount*0.5;} }
class NoRefundPolicy extends CancellationPolicy { refund(amount){return 0;} }
class CancellationService { constructor(policy){this.policy=policy;} cancel(amount){return this.policy.refund(amount);} }
for (const p of [new FlexiblePolicy(),new PartialRefundPolicy(),new NoRefundPolicy()]) console.log(`${p.constructor.name}: ${new CancellationService(p).cancel(430).toFixed(2)}`);
