#include <iostream>
#include <memory>
using namespace std;
class CancellationPolicy { public: virtual ~CancellationPolicy()=default; virtual double refund(double amount) const=0; };
class FlexiblePolicy: public CancellationPolicy { public: double refund(double amount)const override{return amount;} };
class PartialRefundPolicy: public CancellationPolicy { public: double refund(double amount)const override{return amount*0.5;} };
class NoRefundPolicy: public CancellationPolicy { public: double refund(double)const override{return 0;} };
class CancellationService { shared_ptr<CancellationPolicy> policy; public: CancellationService(shared_ptr<CancellationPolicy> p):policy(move(p)){} double cancel(double amount)const{return policy->refund(amount);} };
int main(){for(auto p:{shared_ptr<CancellationPolicy>(new FlexiblePolicy),shared_ptr<CancellationPolicy>(new PartialRefundPolicy),shared_ptr<CancellationPolicy>(new NoRefundPolicy)}) cout<<CancellationService(p).cancel(430)<<"\n";}
