#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections

from django.db import models
from jsonfield import JSONField
from solo.models import SingletonModel

from .fields import PositiveTinyIntegerField


class Product(models.Model):
    class meta:
        managed = False

    def _id():
        pk = Product.objects.last().item_id
        return pk + 1 if pk else 1

    item_id             = models.PositiveSmallIntegerField(primary_key=True, default=_id)
    item_name           = models.CharField(max_length=1024, blank=True, null=True)
    item_image          = models.ImageField(upload_to='item/', blank=True, null=True)

    item_price          = models.FloatField(blank=True, null=True)
    item_c_price        = models.FloatField(blank=True, null=True)
    item_discounted     = models.FloatField(blank=True, null=True)

    item_winner         = models.ForeignKey('auction.User', null=True)
    item_bids           = models.PositiveIntegerField(blank=True, null=True)

    item_terminated_on  = models.DateTimeField(blank=True, null=True)

    enable_fetch_statistic = models.BooleanField(default=True)
    enable_smart_bid       = models.BooleanField(default=False)

    def __str__(self):
        return "%s. %s ราคา: %s" % (self.item_id, self.item_name, self.item_price)


class User(models.Model):
    '''
    http://stackoverflow.com/questions/35999186/change-type-of-django-model-field-from-charfield-to-foreignkey
    '''
    class meta:
        managed = False

    def _id():
        pk = User.objects.last().id
        return pk + 1 if pk else 1

    id   = models.PositiveSmallIntegerField(primary_key=True, default=_id)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s" % self.name


class Statistic(models.Model):
    class meta:
        managed = False

    SINGLE = 1
    AUTO   = 2
    SMS    = 3
    BID_TYPE_CHOICE = (
        (SINGLE, 'Single Bid'),
        (AUTO, 'Auto Bid'),
        (SMS, 'SMS Bid'),
    )

    item        = models.ForeignKey(Product, db_index=True)
    price       = models.FloatField()
    user        = models.ForeignKey(User, null=True)
    fetched_on  = models.DateTimeField(auto_now_add=True)
    bid_type    = PositiveTinyIntegerField(choices=BID_TYPE_CHOICE, blank=True, null=True)

    def __str__(self):
        return "%s %s (%s)" % (self.item, self.price, self.user)

    def update_bid_type(self, bt):
        if bt == 's':
            self.bid_type = self.SINGLE
        elif bt == 'b':
            self.bid_type = self.AUTO
        elif bt == 'm':
            self.bid_type = self.SMS

        self.save(update_fields=['bid_type'])


class Criteria(models.Model):
    class meta:
        managed = False

    item        = models.ForeignKey(Product)
    json        = JSONField()
    fetched_on  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.item, self.json)


class History(models.Model):
    class meta:
        managed = False

    item        = models.ForeignKey(Product)
    json        = JSONField()
    fetched_on  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.item, self.json)


class Result(models.Model):
    class meta:
        managed = False

    item        = models.ForeignKey(Product)
    json        = JSONField()
    fetched_on  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.item, self.json)


class AccountSetting(SingletonModel):
    class meta:
        managed = False

    singleton_instance_id = 1

    name           = models.CharField(max_length=255, blank=True, null=True)
    php_session_id = models.CharField(max_length=32, blank=True, null=True)
    username       = models.CharField(max_length=255, blank=True, null=True)
    password       = models.CharField(max_length=255, blank=True, null=True)
    bids           = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.bids)

    def use_bid(self):
        self.bids -= 1
        self.save(update_fields=['bids'])

    def update_bids_count(self, bids_count):
        self.bids = bids_count
        self.save(update_fields=['bids'])


class Auction(models.Model):
    class meta:
        managed = False

    DISABLED   = 0
    ACTIVE     = 1
    AUTO       = 2
    CANCELED   = 10
    TERMINATED = 20
    WIN        = 20
    LOST       = 20

    STATUS_CHOICE = (
        (DISABLED, 'DISABLED'),
        (ACTIVE, 'ACTIVE'),
        (AUTO, 'AUTO'),
        (CANCELED, 'CANCELED'),
        (TERMINATED, 'TERMINATED'),
        (WIN, 'WIN'),
        (LOST, 'LOST'),
    )

    item                = models.OneToOneField(Product, primary_key=True)
    status              = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, blank=True, null=True)
    price_min           = models.FloatField(blank=True, null=True)
    price_max           = models.FloatField(blank=True, null=True)
    bid_limit           = models.PositiveIntegerField(blank=True, null=True)
    bid_used            = models.PositiveIntegerField(blank=True, null=True, default=0)
    enable_smart_bid    = models.BooleanField(default=False)
    auto_bid_activated  = models.BooleanField(default=False)

    def __str__(self):
        return '%s (%s)' % (self.item, self.status)

    def use_bid(self, bid_used_count=0):
        if bid_used_count:
            self.bid_used += bid_used_count
        elif self.bid_used:
            self.bid_used += 1
        else:
            self.bid_used = 1
        self.save(update_fields=['bid_used'])


class Action(models.Model):
    class meta:
        managed = False

    SINGLE          = 1
    AUTO            = 2
    SMS             = 3
    SINGLE_RECOVERY = 5
    CANCEL_AUTO     = 10
    TERMINATE       = 20

    ACTION_CHOICE = (
        (SINGLE, 'Single Bid'),
        (AUTO, 'Auto Bid'),
        (SMS, 'SMS Bid'),
        (SINGLE_RECOVERY, 'Single Recovery'),
        (CANCEL_AUTO, 'Cancel Auto Bid'),
        (TERMINATE, 'Terminate Auction'),
    )

    auction       = models.ForeignKey(Auction, blank=True, null=True, on_delete=models.SET_NULL)
    action        = models.PositiveSmallIntegerField(choices=ACTION_CHOICE, blank=True, null=True)
    created_on    = models.DateTimeField(auto_now_add=True)
    criteria_json = models.ForeignKey(Criteria, blank=True, null=True, on_delete=models.SET_NULL)
    history_json  = models.ForeignKey(History, blank=True, null=True, on_delete=models.SET_NULL)
    result_json   = models.ForeignKey(Result, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s (%s)' % (self.auction.item, self.action)
