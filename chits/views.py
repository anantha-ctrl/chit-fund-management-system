from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import ChitGroup, ChitMember
from members.models import Member

class ChitGroupForm(forms.ModelForm):
    class Meta:
        model = ChitGroup
        fields = ['name', 'amount', 'duration_months', 'installment_amount', 'start_date', 'status', 'due_day', 'penalty_per_day']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

@login_required
def chit_list(request):
    chits = ChitGroup.objects.all()
    return render(request, 'chits/chit_list.html', {'chits': chits})

@login_required
def chit_create(request):
    if request.method == 'POST':
        form = ChitGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chit Group created successfully.')
            return redirect('chit_list')
    else:
        form = ChitGroupForm()
    return render(request, 'chits/chit_form.html', {'form': form, 'title': 'Create Chit Group'})

@login_required
def chit_edit(request, pk):
    chit = get_object_or_404(ChitGroup, pk=pk)
    if request.method == 'POST':
        form = ChitGroupForm(request.POST, instance=chit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chit Group updated successfully.')
            return redirect('chit_list')
    else:
        form = ChitGroupForm(instance=chit)
    return render(request, 'chits/chit_form.html', {'form': form, 'title': 'Edit Chit Group'})

@login_required
def chit_detail(request, pk):
    chit = get_object_or_404(ChitGroup, pk=pk)
    members = chit.chitmember_set.all()
    all_members = Member.objects.exclude(id__in=members.values_list('member_id', flat=True))
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        if member_id:
            member = get_object_or_404(Member, pk=member_id)
            ChitMember.objects.create(chit_group=chit, member=member)
            messages.success(request, f'Member {member.name} added to the group.')
            return redirect('chit_detail', pk=pk)
            
    return render(request, 'chits/chit_detail.html', {'chit': chit, 'members': members, 'all_members': all_members})

@login_required
def remove_member(request, pk, member_pk):
    if request.method == 'POST':
        cm = get_object_or_404(ChitMember, chit_group_id=pk, member_id=member_pk)
        cm.delete()
        messages.success(request, 'Member removed from group.')
    return redirect('chit_detail', pk=pk)
