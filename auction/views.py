import datetime
import operator
from collections import Counter, OrderedDict, namedtuple

import numpy
from django import template
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.datastructures import SortedDict
from django.views.generic import DetailView, ListView

from utils.decorators import json_response
from utils.devtools import logger

from .crawler import Bidpluz
from .models import Product, Statistic

register = template.Library()

Bidder = namedtuple('Bidder', 'index bids is_professional statistic_count')


class ProductGraphView(DetailView):
    model = Product

    def get(self, request, *args, **kwargs):
        start_time = datetime.datetime.now()
        sort_by = request.GET.get('sort_by', default='last')
        minimum_bids = int(request.GET.get('min', default=0))
        self.object = self.get_object()

        '''
        Up to 10 times faster!!!
        https://docs.djangoproject.com/en/1.10/ref/models/querysets/#prefetch-objects
        '''
        statistics           = Statistic.objects.prefetch_related(Prefetch('user')).filter(item=self.object)
        users                = []
        fighting             = []
        single, auto, unknow = [], [], []
        bidders              = {}

        for s in statistics:
            users.append(s.user.name)
            if len(users) > 5 and users[-1] == users[-3] and users[-2] == users[-4]:
                fighting.append(s)
            if s.bid_type == Statistic.SINGLE:
                single.append(s)
            elif s.bid_type == Statistic.AUTO:
                auto.append(s)
            else:
                unknow.append(s)

        users = dict(Counter(users))
        if minimum_bids:
            users_filtered = {k: v for k, v in users.items() if v >= minimum_bids}
            users = users_filtered

        PROFESSIONAL_BID_MINIMUM = 1000
        users = OrderedDict(sorted(users.items(), key=lambda d:d[1], reverse=True))
        for i, u in enumerate(users.items(), start=1):
            s = Statistic.objects.filter(user__name=u[0]).count()
            is_professional = True if s >= PROFESSIONAL_BID_MINIMUM else False
            bidders[u[0]] = Bidder(index=i, bids=u[1], is_professional=is_professional, statistic_count=s)

        if sort_by == 'last':
            '''
            http://stackoverflow.com/questions/4915920/how-to-delete-an-item-in-a-list-if-it-exists
            '''
            filtered_statistics = list(statistics)
            index = 0
            while filtered_statistics:
                user = filtered_statistics[-1].user
                if user.name in bidders.keys():
                    index += 1
                    bidders[user.name] = bidders[user.name]._replace(index=index)
                filtered_statistics = [x for x in filtered_statistics if x.user is not user]

        def serialize_bid_sequence(bid_sequence, user_id=None):
            '''
            string: "[161.2, 5], [167.5, 2],"

            '''
            string = ''
            if user_id is None:
                for b in bid_sequence:
                    if b.user.name in bidders.keys():
                        string += '[%s, %s], ' % (b.price, bidders[b.user.name].index)
            else:
                for b in bid_sequence:
                    string += '[%s, %s], ' % (b.price, user_id)
            return string

        fighting_bids_count = len(fighting)
        fighting_bids       = serialize_bid_sequence(fighting, user_id = 0)
        single_bids         = serialize_bid_sequence(single)
        auto_bids           = serialize_bid_sequence(auto)
        unknow_bids         = serialize_bid_sequence(unknow)

        height = (len(bidders) * 50) + 120

        winner = bidders[statistics.last().user.name] if statistics.last() else None

        context = self.get_context_data(
            object=self.object,
            sum_bid=sum(users.values()),
            fighting_bids=fighting_bids,
            fighting_bids_count=fighting_bids_count,
            single_bids=single_bids,
            auto_bids=auto_bids,
            unknow_bids=unknow_bids,
            bidders=bidders,
            height=height,
            y_max=len(bidders),
            winner=winner,
        )
        print('ELAPSED: %s' % (datetime.datetime.now() - start_time))
        return self.render_to_response(context)


class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        bidpluz = Bidpluz()
        product_id_first, product_id_last = bidpluz.get_product_id()
        return queryset.filter(item_id__gte=int(product_id_first), item_id__lte=int(product_id_last), item_name__isnull=False, item_terminated_on__isnull=False).order_by('item_id')

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.
        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )

def script(request):
    from auction.models import Product
    import numpy

    item_bids__gte = int(request.GET.get('item_bids__gte', '0'))


    products = Product.objects.filter(item_price__gte=30000, item_bids__gte=item_bids__gte, item_id__gte=10000).order_by('item_bids')
    count = products.count()

    context = dict(
        products=products,
        count=count
    )
    return render(request, 'auction/script.html', context)

def user(request):
    from auction.models import User, Statistic

    username = request.GET.get('username', 'Homerun')
    statistics = Statistic.objects.prefetch_related(Prefetch('user'), Prefetch('item')).filter(user__name=username)
    products = set()
    for s in statistics:
        products.add(s.item)
    count = len(products)

    context = dict(
        username=username,
        products=products,
        count=count
    )
    product_id_list = username
    for p in products:
        product_id_list += ' %s' % p.item_id

    return redirect('/admin/auction/product/?q=%s' % product_id_list)

def product_bid_count(request):
    from auction.models import Product
    import datetime

    item_price__gte = int(request.GET.get('item_price__gte', 0))
    item_price__lte = int(request.GET.get('item_price__lte', 100000))
    item_id__gte    = int(request.GET.get('item_id__gte', 10000))
    item_id__lte    = int(request.GET.get('item_id__lte', 100000))

    products = Product.objects.filter(item_terminated_on__isnull=False, item_id__gte=item_id__gte, item_id__lte=item_id__lte, item_price__gte=item_price__gte, item_price__lte=item_price__lte).exclude(item_name__icontains='BidsPack')

    string = ''
    item_bids = []
    for p in products:
        b = p.item_bids
        item_bids.append(p.item_bids)
        # print(p.item_bids)
        d = datetime.datetime.strftime(p.item_terminated_on, '%x')
        string += '[%s, %s], ' % (p.item_id, b)

    context = dict(
        products=products,
        product_sequence=string,
        item_bids_mean=int(numpy.mean(item_bids)) if item_bids else 0,
        item_bids_count=len(item_bids)
    )
    return render(request, 'auction/product_bid_count.html', context)
