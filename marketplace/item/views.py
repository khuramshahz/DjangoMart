from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from django.contrib.auth.decorators import login_required
from .forms import NewItemForm,EditItemForm
from django.urls import reverse
from django.db.models import Q

def item(request):
    # Normalize legacy category filter to the current query parameter.
    if 'category' in request.GET and 'query' not in request.GET:
        category_value = request.GET.get('category', '')
        target_url = reverse('item:items')
        if category_value:
            return redirect(f"{target_url}?query={category_value}")
        return redirect(target_url)

    query=request.GET.get('query','')


    items=Item.objects.filter(is_sold=False)


    if query:
        items=items.filter(Q (name__icontains=query)| Q(description__icontains=query))

    return render(request,'item/items.html',{
        'items':items,
        'query':query

    })



def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items=Item.objects.filter(Category=item.Category,is_sold=False).exclude(pk=pk)[0:3]
    return render(request, 'item/detail.html', {
        'item': item,
        'related_item':related_items,
    })
@login_required
def new(request):
    if request.method=='POST':
        form=NewItemForm(request.POST,request.FILES)

        if form.is_valid():
            item=form.save(commit=False)
            item.created_by=request.user
            item.save()

            return redirect('item:detail', pk=item.id)


    else:
        form=NewItemForm()

    return render(request,'item/form.html',{
        'form':form,
        'title':'New item',
    })

@login_required
def edit(request,pk):
    item=get_object_or_404(Item,pk=pk,created_by=request.user)
    if request.method=='POST':
        form=EditItemForm(request.POST,request.FILES,instance=item)

        if form.is_valid():
            item.save()

            return redirect('item:detail', pk=item.id)


    else:
        form=EditItemForm(instance=item)

    return render(request,'item/form.html',{
        'form':form,
        'title':'Edit item',
    })

@login_required
def delete(request,pk):
    item=get_object_or_404(Item,pk=pk,created_by=request.user)
    item.delete()

    return render('dashboard:index')