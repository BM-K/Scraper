from utils import Utils
from setting import Setting
from scraper import (JtbcScraper,
                     SbsScraper,
                     NewsisScraper,
                     NocutScraper,
)

def main(args):
    utils = Utils(args)
    config = utils.get_newest_config()

    if args.scraping_task == 'jtbc':
        scraper = JtbcScraper(args, config)
    elif args.scraping_task == 'sbs':
        scraper = SbsScraper(args, config)
    elif args.scraping_task == 'newsis':
        scraper = NewsisScraper(args, config)
    elif args.scraping_task == 'nocut':
        scraper = NocutScraper(args, config)
    else:
        pass

    information = scraper.run()
    utils.upload_data(information)

if __name__ == '__main__':
    args = Setting().run()
    main(args)