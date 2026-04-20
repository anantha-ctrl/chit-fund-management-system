from django.db import models
from django.core.exceptions import ValidationError
from chits.models import ChitGroup
from members.models import Member

class Auction(models.Model):
    chit_group = models.ForeignKey(ChitGroup, on_delete=models.CASCADE)
    month_number = models.IntegerField()
    auction_date = models.DateField()
    winner = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='won_auctions')
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2) # The discount amount bid by the winner
    
    # Financial fields
    foreman_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    total_dividend = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    dividend_per_member = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False) # chit_amount - bid_amount
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chit_group', 'month_number')

    def save(self, *args, **kwargs):
        # Calculate foreman commission beforehand to validate against bid
        commission = (self.chit_group.commission_percentage / 100) * self.chit_group.amount
        
        # Validation: Bid must cover the foreman's commission
        if self.bid_amount < commission:
            raise ValidationError(f"The bid amount (₹{self.bid_amount}) must be greater than or equal to the Foreman Fee (₹{commission}). Please enter a higher bid.")

        # 1. Foreman Fee (Fixed usually)
        self.foreman_commission = commission
        
        # 2. Total Dividend = Full Bid Amount (Discount)
        # Members now get the full discount, they don't pay the commission
        self.total_dividend = max(0, self.bid_amount)
        
        # 3. Dividend Per Member (Distributed ONLY to non-winners)
        member_count = self.chit_group.members.count()
        # Dividend is split between all members EXCEPT the winner of this round
        eligible_members_count = max(1, member_count - 1) 
        self.dividend_per_member = self.total_dividend / eligible_members_count
        
        # 4. Net Payout for winner = (Total Chit Amount - Bid Amount - Foreman Fee)
        self.payout_amount = self.chit_group.amount - self.bid_amount - self.foreman_commission
        
        super().save(*args, **kwargs)
        
        # 5. Automated Dividend Distribution: 
        # Update or Create 'Payment' entries for the NEXT installment
        from payments.models import Payment
        from datetime import date
        import calendar
        
        next_month_num = self.month_number + 1
        if next_month_num <= self.chit_group.duration_months:
            # Determine due date for the next month
            year = self.auction_date.year
            month = self.auction_date.month + 1
            if month > 12:
                month = 1
                year += 1
            
            last_day = calendar.monthrange(year, month)[1]
            actual_due_day = min(self.chit_group.due_day, last_day)
            calculated_due_date = date(year, month, actual_due_day)

            for member in self.chit_group.members.all():
                # Apply dividend to the next monthly payment
                # IMPORTANT: Winner of this round gets ZERO dividend
                current_dividend = 0 if member == self.winner else self.dividend_per_member
                
                payment, created = Payment.objects.get_or_create(
                    chit_group=self.chit_group,
                    member=member,
                    installment_number=next_month_num,
                    defaults={
                        'amount': self.chit_group.installment_amount,
                        'due_date': calculated_due_date,
                        'status': 'PENDING'
                    }
                )
                
                # Update the dividend amount accurately
                payment.dividend_amount = current_dividend
                payment.save()

    def __str__(self):
        return f"Auction {self.month_number} for {self.chit_group.name} - Winner: {self.winner.name}"

class Guarantor(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='guarantors')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    relationship = models.CharField(max_length=100)
    id_proof_type = models.CharField(max_length=50, blank=True)
    id_proof_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Guarantor for Auction {self.auction.id})"
