import datetime
import random
import re
import time
from urllib.parse import urljoin

from dateutil import parser
from django.db import transaction
from rupture import Rupture

import winsound
from utils.devtools import dump_file, logger
from utils.parser import parse_float, parse_int

from .models import (AccountSetting, Action, Auction, Criteria, History,
                     Product, Result, Statistic, User)

import requests


class Bidpluz(Rupture):

    PARSER   = 'lxml'
    encoding = 'utf-8'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }
    COOKIES = {}
    AJAX_HEADERS = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': "application/x-www-form-urlencoded",
    }
    BASE_URL = 'http://www.bidpluz.com'
    UID      = '142125'
    URL = dict(
        update_login='updatelogin.php',
        update_history='updatehistory.php',
        index_page1='index.php',
        index_page4='index.php?pgno1=4',
        product_details='productdetails.php?aid=',
        info1='update_info.php?flp=1',
        info2='update_info.php?flp=2',

        getbid='getbid.php',
        addbidbutler='addbidbutler.php',
        deletebutler='deletebutler.php',
    )

    for k, v in URL.items():
        URL[k] = urljoin(BASE_URL, v)

    SESSION_INIT_COUNT  = 1

    def __init__(self, login=False):
        if login:
            self.COOKIES = {
                'PHPSESSID': AccountSetting.get_solo().php_session_id,
            }

        super().__init__(parser=self.PARSER, headers=self.HEADERS, cookies=self.COOKIES)

    def re_init(self, login=False):
        ''' Experiment with Re-Initialize Session '''
        self.__init__(login=login)
        self.SESSION_INIT_COUNT += 1
        logger('RE-INITIALIZE SESSION (%s)' % self.SESSION_INIT_COUNT)

    def login(self):
        pass

    def get_bids_count(self):
        TIMEOUT = 3
        response = self.http_get(self.URL['index_page1'], timeout=TIMEOUT, retries=1)
        bids_count = parse_int(response.soup.select_one('span#bids_count').text)
        logger('BIDS COUNT LEFT: %s' % bids_count)
        return bids_count

    def place_single_bid(self, url, auction, criteria=None, is_recovery=False):
        TIMEOUT = 0.5
        logger('Place [SINGLE BID]')
        response = self.xml_get(url, headers=self.AJAX_HEADERS, timeout=TIMEOUT, retries=1)
        response_json = response.json()[0]
        logger(response_json)
        result = Result.objects.create(
            item=auction.item,
            json=response_json
        )
        if is_recovery:
            action_type = Action.SINGLE_RECOVERY
        else:
            action_type = Action.SINGLE
        action = Action.objects.create(
            auction=auction,
            action=action_type,
            criteria_json=criteria,
            result_json=result,
        )
        return result.json['result']

    def place_auto_bid(self, auction, aid, bidsp, bidep, totb):
        TIMEOUT = 0.5
        logger('Place [AUTO BID] (aid: %s, bidsp: %s, bidep: %s, totb: %s)' % (aid, bidsp, bidep, totb))
        '''
        Place an auto bid
        Request URL: http://www.bidpluz.com/addbidbutler.php?aid=11051&bidsp=350&bidep=500&totb=2
        Request Method: GET
        Response: {"butlerslength":[{"bidbutler":{"startprice":"350.00","endprice":"500.00","bids":"2","id":"159545","usedbids":"0"}}]}
        '''
        params = dict(
            aid=aid,
            bidsp=bidsp,
            bidep=bidep,
            totb=totb,
        )
        response = self.xml_get(self.URL['addbidbutler'], headers=self.AJAX_HEADERS, params=params, timeout=TIMEOUT, retries=1)
        result = Result.objects.create(
            item=auction.item,
            json=response.json()
        )
        action = Action.objects.create(
            auction=auction,
            action=Action.AUTO,
            result_json=result,
        )
        # if result['result'] == 'unsuccessprice':
        #     result = self.place_auto_bid
        return result.json['butlerslength'][0]['bidbutler']['id']

    def cancel_auto_bid(self, auction, delid, history_json):
        TIMEOUT = 0.5
        logger('Cancel [AUTO BID] (delid: %s)' % (delid))
        '''
        Delete an auto bid
        Request URL: http://www.bidpluz.com/deletebutler.php?delid=159545
        Request Method: GET
        Response: {"butlerslength":[]}
        '''
        params = dict(
            delid=delid,
        )
        response = self.xml_get(self.URL['deletebutler'], headers=self.AJAX_HEADERS, params=params, timeout=TIMEOUT, retries=1)
        response_json = response.json()
        logger(response_json)
        result = Result.objects.create(
            item=auction.item,
            json=response_json
        )
        action = Action.objects.create(
            auction=auction,
            action=Action.CANCEL_AUTO,
            # history_json=history_json,
            result_json=result,
        )
        return result.json['butlerslength']

    def create_criteria(self, product, j):
        criteria, criteria_created = Criteria.objects.get_or_create(
            item=product,
            json=j,
        )
        if criteria_created:
            logger('Found Criteria: %s' % product.item_id)
        return criteria

    def smart_bid(self, product_id=None, ALLOW_AUTO_BID=True, time_bid_criteria=None, special_sleep_time=None, use_bid_counter=False):
        if product_id is None:
            return

        logger('Smart Bid [Product ID: %s]' % product_id)
        product, product_created = Product.objects.get_or_create(item_id=product_id)

        product_id       = str(product.item_id)
        response         = self.http_get(self.URL['product_details'] + product_id)
        img              = response.soup.select_one('img#image_main_%s' % product_id)
        if img:
            getbid_url = img.get('name', None)
            if getbid_url is None:
                logger('Single Bid Button is not found. (Need Login)')
                return
            '''
            Example: "getbid.php?prid=75&aid=10989&uid=142125"
            '''
            single_bid_url = urljoin(self.BASE_URL, img['name'])
        else:
            single_bid_url = None
            logger('Single Bid Button is not found.')

        bidbutstartprice   = 0
        bidbutendprice     = 0
        totalbids          = 0
        add_bid_butler_url = urljoin(self.BASE_URL, "addbidbutler.php?aid=" + product_id +
            "&bidsp=" + str(bidbutstartprice) +
            "&bidep=" + str(bidbutendprice) +
            "&totb="  + str(totalbids)
        )
        del_bid_butler_url = urljoin(self.BASE_URL, "deletebutler.php?delid=" + product_id)
        print(single_bid_url)
        print(add_bid_butler_url)
        print(del_bid_butler_url)

        def random_bid_counter():
            return random.randint(25,50)

        def random_auto_bid_offset():
            # offset = 0.5 + random.choice([0, 0.5, 1])
            offset = 0.75
            logger('Random Auto-Bid Offset: %.2f' % offset)
            return offset

        ''' Initailize Auction Process '''
        AccountSetting.get_solo().update_bids_count(self.get_bids_count())
        account = AccountSetting.get_solo()
        auction, auction_created = Auction.objects.get_or_create(item=product)

        FETCH_INTERVAL      = 1
        FETCH_INTERVAL_S    = 0.25
        TIME_SMART_ACTIVATE = 120
        TIME_BID_CRITERIA   = time_bid_criteria if time_bid_criteria is not None else 0
        TIME_AUCTION_ENDED  = -2
        AUTO_BID_ID         = None
        LAST_PRICE          = None
        AUTO_BID_COUNTER    = random_bid_counter()
        INITAIL_TOTAL_BIT   = 100
        DELAY_FOR_ZERO      = 0
        ENABLE_SPECIAL_WAIT = False
        STABLE_CONNECTION   = True
        LASTEST_COUNT_T     = 0
        LASTEST_COUNT_TIME  = datetime.datetime.now()
        SPECIAL_SLEEP_TIME  = special_sleep_time if special_sleep_time is not None else 0.5
        USE_BID_COUNTER     = use_bid_counter if use_bid_counter else False
        BID_COUNT_BEFORE    = account.bids
        t=0
        price=0
        username=''

        while True:
            print()
            try:
                t, price, username, j = self._fetch_auction(product_id)
            except Exception as e:

                STABLE_CONNECTION = False
                print(e)
                ''' Send Single Bid Recovery On Lost Connection '''
                LOST_CONNECTION_SECOND = (datetime.datetime.now() - LASTEST_COUNT_TIME).total_seconds()
                logger('LOST CONNECTION FOR: %s' % LOST_CONNECTION_SECOND)

                self.re_init(login=True)

                if not AUTO_BID_ID and LOST_CONNECTION_SECOND >= t:
                    logger('RECOVERY SINGLE BID')
                    try:
                        result_msg = self.place_single_bid(
                            url=single_bid_url,
                            auction=auction,
                            is_recovery=True,
                        )
                    except Exception as e:
                        print(e)
                    else:
                        if result_msg == 'success':
                            account.use_bid()
                            auction.use_bid()
                            winsound.Beep(4000, 200)
                continue
            else:
                LASTEST_COUNT_T     = t
                LASTEST_COUNT_TIME  = datetime.datetime.now()

                account = AccountSetting.get_solo()
                auction, auction_created = Auction.objects.get_or_create(item=product)
                logger('P: %s, T: %s, U: %s' % (price, t, username))

                # if t > TIME_SMART_ACTIVATE:
                #     time.sleep(TIME_SMART_ACTIVATE)

                if t >= (TIME_BID_CRITERIA + 1):
                    ''' Reset '''
                    DELAY_FOR_ZERO = 0

                if t <= TIME_BID_CRITERIA and username and username != account.name:
                    ''' Special wait for T0 single bid '''
                    if STABLE_CONNECTION and ENABLE_SPECIAL_WAIT and t == TIME_BID_CRITERIA and not DELAY_FOR_ZERO:
                        time.sleep(SPECIAL_SLEEP_TIME)
                        DELAY_FOR_ZERO += 1
                    else:
                        ''' Place a Single Bid '''
                        try:
                            result_msg = self.place_single_bid(
                                url=single_bid_url,
                                auction=auction,
                            )
                        except Exception as e:
                            print(e)
                        else:
                            if result_msg == 'success':
                                account.use_bid()
                                auction.use_bid()
                                winsound.Beep(2000, 200)
                            elif result_msg == 'unsuccess':
                                return

                        ''' Place an Auto Bid '''
                        if ALLOW_AUTO_BID and not AUTO_BID_ID:
                            time.sleep(random.uniform(0.5, 1))
                            bid_start_price = price + random_auto_bid_offset()
                            bid_end_price   = auction.price_max or (price + account.bids / 2)
                            # total_bids      = auction.bid_limit - auction.bid_used if auction.bid_limit else account.bids
                            total_bids = INITAIL_TOTAL_BIT
                            if total_bids > account.bids:
                                totabl_bids = account.bids
                            if account.bids <= 50:
                                logger('Low Bids Available (%s)' % account.bids)
                            try:
                                AUTO_BID_ID = self.place_auto_bid(
                                    auction=auction,
                                    aid=product_id,
                                    bidsp=bid_start_price,
                                    bidep=round(bid_end_price) - random.randint(0, 10),
                                    totb=total_bids - random.randint(0, 10),
                                )
                            except Exception as e:
                                print(e)
                            else:
                                BID_COUNT_BEFORE = account.bids
                                LAST_PRICE = price
                                AUTO_BID_COUNTER = random_bid_counter()

                        STABLE_CONNECTION = True

                    ''' END '''

                elif t <= TIME_AUCTION_ENDED and not username:
                    '''
                    Auction Terminated
                    '''
                    logger('AUCTION %s TERMINATED' % (product_id))
                    return

                if ALLOW_AUTO_BID and AUTO_BID_ID and LAST_PRICE != price:
                    def check_history_bid(result):
                        '''
                        Check for disable AutoBid
                        '''
                        h_username_1 = result['histories'][0]['history']['username']
                        h_username_2 = result['histories'][1]['history']['username']
                        h_bidtype_1  = result['histories'][0]['history']['bidtype']
                        h_bidtype_2  = result['histories'][1]['history']['bidtype']
                        if h_username_1 != account.name and h_username_2 != account.name:
                            return True
                        if h_username_1 != account.name and h_bidtype_1 != 'b':
                            return True
                        if h_username_2 != account.name and h_bidtype_2 != 'b':
                            return True
                        return False

                    result = self.fetch_history(product_id)
                    logger(result["butlerslength"])

                    if not result["butlerslength"]:
                        AUTO_BID_ID = None
                        account.update_bids_count(self.get_bids_count())
                        auction.use_bid(bid_used_count=BID_COUNT_BEFORE - account.bids)

                    elif len(result['histories']) > 1:
                        if check_history_bid(result) or (USE_BID_COUNTER and (AUTO_BID_COUNTER == 0)):
                            '''
                            More than 2 user participating in the auction now
                            - Cancel my Auto Bid
                            '''
                            time.sleep(random.uniform(0.5, 1))
                            try:
                                AUTO_BID_ID = self.cancel_auto_bid(
                                    auction=auction,
                                    delid=AUTO_BID_ID,
                                    history_json=result,
                                )
                            except Exception as e:
                                print(e)
                            else:
                                account.update_bids_count(self.get_bids_count())
                                auction.use_bid(bid_used_count=BID_COUNT_BEFORE - account.bids)
                                AUTO_BID_COUNTER = random_bid_counter()
                                # if AUTO_BID_COUNTER == 0:
                                #     AUTO_BID_COUNTER = AUTO_BID_COUNTER * random.randint(1, 3)

                            if not AUTO_BID_ID and AUTO_BID_COUNTER:  # ถ้าลบออกไม่โดยที่ไม่ใช่ Bid Counter ไม่เป็น 0
                                winsound.Beep(200, 200)
                            else:
                                winsound.Beep(220, 3000)

                        elif result['histories'][0]['history']['username'] == account.name:
                            AUTO_BID_COUNTER -= 1
                            logger('AUTO BID COUNTER (%s)' % AUTO_BID_COUNTER)

                LAST_PRICE = price

            if t > (TIME_BID_CRITERIA + 1):
                time.sleep(FETCH_INTERVAL)
            else:
                time.sleep(FETCH_INTERVAL_S)


    def _fetch_auction(self, product_id):
        TIMEOUT = 0.4
        data = {}
        data['auction_%s' % product_id] = product_id
        try:
            response = self.xml_post(self.URL['info1'], headers=self.AJAX_HEADERS, data=data, timeout=TIMEOUT)
            json_list = response.json()
            logger('Fetch Auctions: {} ({}) '.format(product_id, response.elapsed_all.total_seconds()))
        except Exception as e:
            # print(e)
            raise
        else:
            for j in sorted(json_list, key=lambda k: parse_float(k['a']['pr']), reverse=True):
                '''
                {a: {id: "11036", t: "3", pu: "0", pr: "1,366.75", u: "Jolyne", F: "M", ba: "no"}}
                '''
                j       = j['a']
                item_id = parse_int(j['id'])
                t       = parse_int(j['t'])
                price   = parse_float(j['pr'])
                user    = j['u']
                product, product_created = Product.objects.get_or_create(item_id=item_id)
                # if user:
                    # user, user_created = User.objects.get_or_create(name=user)
                    # statistic, statistic_created = Statistic.objects.get_or_create(
                    #     item=product,
                    #     price=price,
                    #     user=user
                    # )
                # else:
                #     user = None
                return [t, price, user, j]


    def _fetch_product(self, product_id):
        response = self.http_get(self.URL['product_details'] + str(product_id))
        logger('Product ID: {} ({}) '.format(product_id, response.elapsed_all.total_seconds()))

        try:
            item_name          = response.soup.select('div.myaccount_heading_middlebg')[1].strong.text
            item_name          = re.search(r'^\((?P<item_name>.+)\)$', item_name).group('item_name')
            item_image         = response.soup.select('span#mainimage1 > img')[0]['src']
        except Exception as e:
            logger('Product is now Disappeared')
            product, created   = Product.objects.get_or_create(item_id=product_id)
            product.enable_fetch_statistic = False
            product.save(update_fields=['enable_fetch_statistic'])
            return

        product, created   = Product.objects.get_or_create(item_id=product_id)
        product.item_name  = item_name
        product.item_image = item_image

        if len(response.soup.select('div#detailbodymargin')[2].find_all('div', recursive=False)) == 9:
            item_winner        = response.soup.select('div#detailbodymargin > div.detail-row')[1].select_one('div.right1').text.strip()
            item_price         = parse_float(response.soup.select('div#detailbodymargin')[2].select('div.detail-row')[3].select_one('div.right1').text.strip())
            item_c_price       = parse_float(response.soup.select_one('span#price_index_page_%s' % str(product_id)).text.strip())
            item_discounted    = response.soup.select('div#detailbodymargin')[2].select('div.detail-row')[1].select_one('div').text
            item_discounted    = parse_float(re.search(r'^ประหยัด : (?P<item_discounted>.+) %$', item_discounted).group('item_discounted'))
            item_bids          = response.soup.select('div#detailbodymargin')[2].select('div.detail-row')[4].select_one('div.left1').text.strip()
            item_bids          = parse_int(re.search(r'^มูลค่าบิทที่ใช้ไป \((?P<item_bids>.+)\):', item_bids).group('item_bids'))
            item_terminated_on = response.soup.select_one('div[style="width: 260px; font-weight:bold"]').text.split('\n')[1].strip().replace(',เวลา', '')
            item_terminated_on = parser.parse(item_terminated_on)

            item_winner, created       = User.objects.get_or_create(name=item_winner)
            product.item_winner        = item_winner
            product.item_price         = item_price
            product.item_c_price       = item_c_price
            product.item_discounted    = item_discounted
            product.item_bids          = item_bids
            product.item_terminated_on = item_terminated_on
        else:
            item_price         = parse_float(response.soup.select('div#detailbodymargin')[2].select('div.detail-row')[1].select_one('div.right1').text.strip())

            product.item_price = item_price

        product.save()

    def fetch_products(self, page=1, start_product_id=0, stop_product_id=0):
        start_time = datetime.datetime.now()
        if start_product_id == 0:
            start_product_id = Product.objects.filter(item_name__isnull=False, item_terminated_on__isnull=True, enable_fetch_statistic=True).first().item_id
        if stop_product_id == 0:
            if page:
                response        = self.http_get(self.URL['index_page%s' % page])
                product_list    = response.soup.select('div.auction-item')
                stop_product_id = max([int(p['title']) for p in product_list])

            last_product_id = Product.objects.filter(item_name__isnull=False, item_terminated_on__isnull=True).last().item_id
            stop_product_id = max(stop_product_id, last_product_id)

        for i in range(start_product_id, stop_product_id + 1):
            try:
                self._fetch_product(i)
            except Exception as e:
                print(e)

        elapsed = datetime.datetime.now() - start_time
        logger('Elapsed: %s' % elapsed)
        print()

    def fetch_auctions_history(self, page=1):
        while True:
            self.fetch_products()
            self._fetch_auctions_history(page)

    def test(self, page=1):
        FETCH_INTERVAL = 10

        aucid = {'11227': 0}
        for i in range(10000):
            start_time = datetime.datetime.now()
            for a, v in aucid.items():

                print(v)
                if v == 10:
                    return
                try:
                    histories = self.fetch_history(a)['histories']
                except ValueError as e:
                    pass
                except Exception as e:
                    print(e)
                    self.re_init()
                else:
                    '''
                        {"history": {"bprice":"60.25","username":"Daimond","bidtype":"b"}}
                    '''
                    for history in histories:
                        item_id = parse_int(a)
                        history = history['history']
                        price   = history['bprice']
                        user    = history['username']
                        bid     = history['bidtype']
                        product, product_created = Product.objects.get_or_create(item_id=item_id)
                        if user:
                            user, user_created = User.objects.get_or_create(name=user)
                            statistic, statistic_created = Statistic.objects.get_or_create(
                                item=product,
                                price=price,
                                user=user,
                            )
                            if statistic_created:
                                statistic.update_bid_type(bid)
                            else:
                                aucid[a] += 1
                                break
                finally:
                    time.sleep(0.25)

            print('ELAPSED: %s' % (datetime.datetime.now() - start_time))
            print()


    def _fetch_auctions_history(self, page=1):
        FETCH_INTERVAL = 10
        self.fetch_products()

        aucid = {}
        if not page :
            products = Product.objects.filter(item_id__gte=10000, item_name__isnull=False, item_terminated_on__isnull=True, enable_fetch_statistic=True)
            for p in products:
                data['auction_%s' % p.item_id] = p.item_id
        else:
            response = self.http_get(self.URL['index_page%s' % page])
            for d in response.soup.select('div.auction-item'):
                aucid[d['title']] = 0

        for index in range(1000):
            start_time = datetime.datetime.now()
            for a, v in aucid.items():
                # if v == 10:
                #     return
                try:
                    histories = self.fetch_history(a)['histories']
                except ValueError as e:
                    pass
                except Exception as e:
                    print(e)
                    self.re_init()
                else:
                    '''
                        {"history": {"bprice":"60.25","username":"Daimond","bidtype":"b"}}
                    '''
                    for history in histories:
                        item_id = parse_int(a)
                        history = history['history']
                        price   = history['bprice']
                        user    = history['username']
                        bid     = history['bidtype']
                        product, product_created = Product.objects.get_or_create(item_id=item_id)
                        if user:
                            user, user_created = User.objects.get_or_create(name=user)
                            statistic, statistic_created = Statistic.objects.get_or_create(
                                item=product,
                                price=price,
                                user=user,
                            )
                            if statistic_created:
                                statistic.update_bid_type(bid)
                            else:
                                break
                finally:
                    time.sleep(0.25)

            print('ELAPSED: %s' % (datetime.datetime.now() - start_time))
            print()

    def fetch_auctions(self, page=1):
        FETCH_INTERVAL = 1
        data = {}
        if not page :
            products = Product.objects.filter(item_id__gte=10000, item_name__isnull=False, item_terminated_on__isnull=True, enable_fetch_statistic=True)
            for p in products:
                data['auction_%s' % p.item_id] = p.item_id
        else:
            response = self.http_get(self.URL['index_page%s' % page])
            for d in response.soup.select('div.auction-item'):
                data['auction_%s' % d['title']] = d['title']

        while True:
            start_time = datetime.datetime.now()
            try:
                response = self.xml_post(self.URL['info2'], headers=self.AJAX_HEADERS, data=data, timeout=FETCH_INTERVAL)
                json_list = response.json()
                logger('Fetch Auctions ({}) '.format(response.elapsed_all.total_seconds()))
            except Exception as e:
                print(e)
                self.re_init()
            else:
                for j in sorted(json_list, key=lambda k: parse_float(k['a']['pr']), reverse=True):
                    logger(j)
                    j       = j['a']
                    item_id = parse_int(j['id'])
                    # t       = parse_int(j['t'])
                    price   = parse_float(j['pr'])
                    user    = j['u']
                    product, product_created = Product.objects.get_or_create(item_id=item_id)
                    if user:
                        user, user_created = User.objects.get_or_create(name=user)
                        statistic, statistic_created = Statistic.objects.get_or_create(
                            item=product,
                            price=price,
                            user=user
                        )
            finally:
                print('ELAPSED: %s' % (datetime.datetime.now() - start_time))
                print()
                time.sleep(FETCH_INTERVAL)

        # while True:
        #     start_time = datetime.datetime.now()
        #     try:
        #         response = self.xml_post(self.URL['info1'], headers=self.AJAX_HEADERS, data=data, timeout=FETCH_INTERVAL)
        #         json_list = response.json()
        #         logger('Fetch Auctions ({}) '.format(response.elapsed_all.total_seconds()))
        #     except Exception as e:
        #         print(e)
        #     else:
                # for j in sorted(json_list, key=lambda k: parse_float(k['a']['pr']), reverse=True):
                #     logger(j)
                #     j       = j['a']
                #     item_id = parse_int(j['id'])
                #     t       = parse_int(j['t'])
                #     price   = parse_float(j['pr'])
                #     user    = j['u']
                #     product, product_created = Product.objects.get_or_create(item_id=item_id)
                #     if user:
                #         user, user_created = User.objects.get_or_create(name=user)
                #         statistic, statistic_created = Statistic.objects.get_or_create(
                #             item=product,
                #             price=price,
                #             user=user
                #         )
                #         if statistic_created:
                #             try:
                #                 history_list = self.fetch_history(item_id)['histories']
                #             except Exception as e:
                #                 print(e)
                #             else:
                #                 for h in history_list:
                #                     h = h['history']
                #                     if parse_float(h['bprice']) == statistic.price and h['username'] == statistic.user.name:
                #                         statistic.update_bid_type(h['bidtype'])
                #                         break
                #     if t <= 1:
                #         criteria, criteria_created = Criteria.objects.get_or_create(
                #             item=product,
                #             json=j,
                #         )
                #         if criteria_created:
                #             logger('Found Criteria: %s' % product.item_id)
                #     if t <= -2:
                #         return
            # finally:
            #     print('ELAPSED: %s' % (datetime.datetime.now() - start_time))
            #     print()
            #     time.sleep(FETCH_INTERVAL)

    def fetch(self):
        while True:
            self.fetch_products()
            self.fetch_auctions()

    def fetch_history(self, product_id):
        TIMEOUT = 2
        '''
        {
            "histories": [
                {"history": {"bprice":"60.25","username":"Daimond","bidtype":"b"}},
                {"history": {"bprice":"60.00","username":"haha888","bidtype":"b"}},
                {"history": {"bprice":"59.75","username":"Daimond","bidtype":"b"}},
                {"history": {"bprice":"59.50","username":"haha888","bidtype":"b"}},
                {"history": {"bprice":"59.25","username":"Daimond","bidtype":"b"}}
            ],
            "myhistories": [
                {"myhistory": {"bprice":"5.00","time":" 10:15:01","bidtype":"s"}},
                {"myhistory": {"bprice":"4.50","time":" 10:14:59","bidtype":"s"}},
                {"myhistory": {"bprice":"4.00","time":" 09:50:14","bidtype":"s"}}
            ],
            "butlerslength": [

            ],
            "biddinglength": [
                {"placebids": {"bids":"3"}}
            ]
        }
        '''
        data = {
            'aucid_new': product_id,
        }
        response = self.xml_post(self.URL['update_history'], headers=self.AJAX_HEADERS, data=data, timeout=TIMEOUT)
        logger('Fetch History: %s' % product_id)
        # logger(response.json())
        return response.json()

    def get_product_id(self, page=1):
        response = self.http_get(self.URL['index_page%s' % page])
        product_id_1st = int(response.soup.select('div.auction-item')[0]['title'])
        product_id_2nd = int(response.soup.select('div.auction-item')[-1]['title'])
        return [product_id_1st, product_id_2nd]
