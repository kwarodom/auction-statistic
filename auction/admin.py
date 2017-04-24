from functools import reduce
from operator import or_

from django.contrib import admin
from django.db.models import Q
from solo.admin import SingletonModelAdmin

from .models import (AccountSetting, Action, Auction, Criteria, History,
                     Product, Result, Statistic, User)


class ProductAdmin(admin.ModelAdmin):
    def get_search_results(self, request, queryset, search_term):
        '''
        http://stackoverflow.com/questions/13638898/how-to-use-filter-map-and-reduce-in-python-3
        '''

        queryset, use_distinct = super(ProductAdmin, self).get_search_results(
                                               request, queryset, search_term)
        search_words = search_term.split()
        if search_words:
            q_objects = [Q(**{field + '__icontains': word})
                                for field in self.search_fields
                                for word in search_words]
            queryset |= self.model.objects.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def time_seconds(self, obj):
        if obj.item_terminated_on is not None:
            return obj.item_terminated_on.strftime("%a %d %b %y %H:%M:%S")
        else:
            return None

    def price_percentage(self, obj):
        if obj.item_price is not None and obj.item_c_price is not None:
            return ('%.2f%%' % (float(obj.item_c_price) / float(obj.item_price) * 100)).replace('.00', '')
        else:
            return None

    def discounted_percentage(self, obj):
        if obj.item_discounted is not None:
            return ('%.2f%%' % (obj.item_discounted)).replace('.00', '')
        else:
            return None

    def real_price_percentage(self, obj):
        if obj.item_bids is not None and obj.item_c_price is not None:
            if 'BidsPack' not in obj.item_name:
                net_price = (7 * obj.item_bids + obj.item_c_price)
                return ('%.2f (%.2f%%)' % (net_price, net_price / obj.item_price * 100)).replace('.00', '')
            else:
                net_price = (7 * obj.item_bids)
                return ('%.2f (%.2f%%)' % (net_price, net_price / obj.item_price * 100)).replace('.00', '')
        else:
            return None

    def item_c_price_percentage(self, obj):
        if obj.item_c_price is not None:
            return ('%.2f (%.2f%%)' % (obj.item_c_price, float(obj.item_c_price) / float(obj.item_price) * 100))
        else:
            return None

    time_seconds.admin_order_field = 'item_terminated_on'
    time_seconds.short_description = 'Item terminated on'
    # price_percentage.admin_order_field = 'price_percentage'
    price_percentage.short_description = 'CPrice percentage'
    discounted_percentage.admin_order_field = 'item_discounted'
    discounted_percentage.short_description = 'Discounted percentage'
    real_price_percentage.admin_order_field = 'real_price_percentage'
    real_price_percentage.short_description = 'Real price'
    item_c_price_percentage.admin_order_field = 'item_c_price_percentage'
    item_c_price_percentage.short_description = 'item close price'

    list_select_related = True

    list_display = ('item_id', 'item_name', 'item_price', 'item_c_price_percentage', 'real_price_percentage', 'discounted_percentage', 'item_winner', 'item_bids', 'time_seconds', 'enable_fetch_statistic', 'enable_smart_bid')
    list_editable = ('enable_fetch_statistic', 'enable_smart_bid')
    search_fields = ('item_id', 'item_name', 'item_price', 'item_c_price', 'item_discounted', 'item_bids', 'item_winner__name')

admin.site.register(Product, ProductAdmin)


class UserAdmin(admin.ModelAdmin):
    list_select_related = True

    list_display = ('name',)

admin.site.register(User, UserAdmin)


class StatisticAdmin(admin.ModelAdmin):
    '''
    http://stackoverflow.com/questions/7216764/in-the-django-admin-site-how-do-i-change-the-display-format-of-time-fields
    '''
    def time_seconds(self, obj):
        return obj.fetched_on.strftime("%a %d %b %H:%M:%S")

    time_seconds.admin_order_field = 'fetched_on'
    time_seconds.short_description = 'Fetched on'

    list_select_related = True

    list_display = ('item', 'price', 'user', 'time_seconds', 'bid_type')
    search_fields = ('item__item_id', 'price', 'user__name', 'bid_type')


admin.site.register(Statistic, StatisticAdmin)

class CriteriaAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.fetched_on.strftime("%a %d %b %H:%M:%S")

    time_seconds.admin_order_field = 'fetched_on'
    time_seconds.short_description = 'Fetched on'

    list_select_related = True

    list_display = ('item', 'json', 'time_seconds')
    search_fields = ('item__item_id', )


admin.site.register(Criteria, CriteriaAdmin)


class HistoryAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.fetched_on.strftime("%a %d %b %H:%M:%S")

    list_select_related = True

    time_seconds.admin_order_field = 'fetched_on'
    time_seconds.short_description = 'Fetched on'

    list_display = ('item', 'json', 'time_seconds')

admin.site.register(History, HistoryAdmin)


class ResultAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.fetched_on.strftime("%a %d %b %H:%M:%S")

    list_select_related = True

    time_seconds.admin_order_field = 'fetched_on'
    time_seconds.short_description = 'Fetched on'

    list_display = ('item', 'json', 'time_seconds')

admin.site.register(Result, ResultAdmin)


class AccountSettingAdmin(SingletonModelAdmin):
    list_select_related = True

    list_display = ('name', 'bids', 'php_session_id')

admin.site.register(AccountSetting, AccountSettingAdmin)


class AuctionAdmin(admin.ModelAdmin):
    list_select_related = True

    list_display = ('item', 'status', 'price_min', 'price_max', 'bid_limit', 'bid_used', 'enable_smart_bid')
    list_editable = ('price_min', 'price_max', 'bid_limit', 'enable_smart_bid')

admin.site.register(Auction, AuctionAdmin)


class ActionAdmin(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.created_on.strftime("%a %d %b %H:%M:%S")

    time_seconds.admin_order_field = 'created_on'
    time_seconds.short_description = 'Created on'

    def result_json_only(self, obj):
        return obj.result_json.json

    result_json_only.admin_order_field = 'result_json'
    result_json_only.short_description = 'Result Json'

    list_select_related = True

    list_display = ('auction', 'action', 'result_json_only', 'time_seconds')
    search_fields = ('auction__item__item_id', )

admin.site.register(Action, ActionAdmin)
