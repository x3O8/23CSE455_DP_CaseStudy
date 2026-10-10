interface CancellationPolicy { double refund(double amount); }
class FlexiblePolicy implements CancellationPolicy { public double refund(double amount){return amount;} }
class PartialRefundPolicy implements CancellationPolicy { public double refund(double amount){return amount*0.5;} }
class NoRefundPolicy implements CancellationPolicy { public double refund(double amount){return 0;} }
class CancellationService { private final CancellationPolicy policy; CancellationService(CancellationPolicy policy){this.policy=policy;} double cancel(double amount){return policy.refund(amount);} }
public class Main { public static void main(String[] args){double a=430; System.out.printf("Flexible refund: %.2f\n",new CancellationService(new FlexiblePolicy()).cancel(a)); System.out.printf("Partial refund: %.2f\n",new CancellationService(new PartialRefundPolicy()).cancel(a)); System.out.printf("No refund: %.2f\n",new CancellationService(new NoRefundPolicy()).cancel(a));}}
