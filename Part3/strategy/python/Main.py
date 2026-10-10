from abc import ABC, abstractmethod
class CancellationPolicy(ABC):
    @abstractmethod
    def refund(self, amount): pass
class FlexiblePolicy(CancellationPolicy):
    def refund(self, amount): return amount
class PartialRefundPolicy(CancellationPolicy):
    def refund(self, amount): return amount*0.5
class NoRefundPolicy(CancellationPolicy):
    def refund(self, amount): return 0
class CancellationService:
    def __init__(self, policy): self.policy=policy
    def cancel(self, amount): return self.policy.refund(amount)
for p in [FlexiblePolicy(),PartialRefundPolicy(),NoRefundPolicy()]: print(f"{p.__class__.__name__}: {CancellationService(p).cancel(430):.2f}")
