from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from ...crawler import Bidpluz

class Command(BaseCommand):

    help = '''Usage: python manage.py bidpluz
        --fetch_products
        --fetch_auctions
        --fetch_history
        --fetch
        --init
        --smart_bid
        --smart_bid_single
    '''

    option_list = BaseCommand.option_list + (

        make_option(
            '--script',
            action='store_true',
            dest='script',
            default=False,
            help=''
        ),

        make_option(
            '--fetch_products',
            action='store_true',
            dest='fetch_products',
            default=False,
            help=''
        ),

        make_option(
            '--fetch_auctions',
            action='store_true',
            dest='fetch_auctions',
            default=False,
            help=''
        ),

        make_option(
            '--fetch_history',
            action='store_true',
            dest='fetch_history',
            default=False,
            help=''
        ),

        make_option(
            '--fetch_auctions_history',
            action='store_true',
            dest='fetch_auctions_history',
            default=False,
            help=''
        ),

        make_option(
            '--test',
            action='store_true',
            dest='test',
            default=False,
            help=''
        ),

        make_option(
            '--fetch',
            action='store_true',
            dest='fetch',
            default=False,
            help=''
        ),

        make_option(
            '--init',
            action='store_true',
            dest='init',
            default=False,
            help=''
        ),

        make_option(
            '--smart_bid',
            action='store_true',
            dest='smart_bid',
            default=False,
            help=''
        ),

        make_option(
            '--smart_bid_single',
            action='store_true',
            dest='smart_bid_single',
            default=False,
            help=''
        ),

    )

    def handle(self, *args, **options):

        if options['script']:
            import script

        bidpluz = Bidpluz()
        if options['fetch_products']:
            bidpluz.fetch_products()

        if options['fetch_auctions']:
            bidpluz.fetch_auctions()

        if options['fetch_history']:
            bidpluz.fetch_history()

        if options['fetch_auctions_history']:
            bidpluz.fetch_auctions_history()

        if options['test']:
            bidpluz.test()

        if options['fetch']:
            bidpluz.fetch()

        if options['init']:
            bidpluz.fetch_products(start_product_id=1)

        bidpluz = Bidpluz(login=True)
        if options['smart_bid']:
            product_id = args[0]
            bidpluz.smart_bid(product_id)
            import winsound
            winsound.Beep(2000, 3000)

        if options['smart_bid_single']:
            product_id = args[0]
            if len(args) > 1:
                time_bid_criteria = int(args[1].replace('m', '-'))
            else:
                time_bid_criteria = 0
            bidpluz.smart_bid(product_id, ALLOW_AUTO_BID=False, time_bid_criteria=time_bid_criteria, special_sleep_time=0.75)
