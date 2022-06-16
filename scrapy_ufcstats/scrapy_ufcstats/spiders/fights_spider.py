from scrapy import Spider, Request
from datetime import datetime
from ..items import ScrapyEventItem, ScrapyFightItem
import pandas as pd
import re


class FightsSpider(Spider):        
    name = "fights"

    def extract_number_of(self, stat_string):
        pre_of = int(re.sub('[^0-9]', '', stat_string.split('of')[0]))
        post_of = int(re.sub('[^0-9]', '', stat_string.split('of')[1]))
        return(pre_of, post_of)

    def start_requests(self):
        event_urls = pd.read_csv("../data/events.csv")["event_url"][:10]

        for event_url in event_urls:
            yield Request(
                url=event_url,
                callback=self.parse_event_fights,
                meta={"event_url": event_url},
            )

    def parse_event_fights(self, response):
        scrape_datetime = datetime.utcnow()

        for fight_url in response.css("a.b-flag_style_green::attr(href)").getall():
            yield Request(
                fight_url,
                callback=self.parse_fight,
                meta={
                    "scrape_datetime": scrape_datetime,
                    "event_url": response.meta["event_url"],
                },
            )

    def parse_fight(self, response):
        # Initalizes fight_item to add the scraped data into.
        fight_item = ScrapyFightItem()

        # Parses url data from response.
        fight_item["fight_url"] = response.url

        # Extracts meta data from previous parsing layer.
        fight_item["datetime_scraped"] = response.meta["scrape_datetime"]
        fight_item["event_url"] = response.meta["event_url"]

        # Parses the weight division for the fight.
        fight_item["division"] = (
            response.xpath("//i[@class='b-fight-details__fight-title']")
            .extract()[0]
            .split("\n")[-2]
            .strip()
        )

        # Extracts fighter name.
        fighters = response.xpath(
            "//h3[@class='b-fight-details__person-name']//a/text()"
        ).extract()
        if len(fighters) == 0:
            fighters = response.xpath(
                "//h3[@class='b-fight-details__person-name']/span/text()"
            ).extract()

        # Extracts fighter nicknames.
        nicknames = response.xpath(
            "//p[@class='b-fight-details__person-title']/text()"
        ).extract()

        # Data wrangles names.
        fight_item["fighter1_name"] = fighters[0].strip()
        fight_item["fighter1_nickname"] = nicknames[0].strip()
        fight_item["fighter2_name"] = fighters[1].strip()
        fight_item["fighter2_nickname"] = nicknames[1].strip()

        # Extracts who won the fight.
        fighter_1_outcome = response.xpath(
            "//body[@class='b-page']/section[@class='b-statistics__section_details']"
            "/div[@class='l-page__container']/div[@class='b-fight-details']"
            "/div[@class='b-fight-details__persons clearfix']"
            "/div[1]/i/text()"
        ).extract()
        fighter_1_outcome = fighter_1_outcome[0].strip()
        if fighter_1_outcome == "W":
            fight_item["winner"] = fight_item["fighter1_name"]
        elif fighter_1_outcome == "L":
            fight_item["winner"] = fight_item["fighter2_name"]
        else:
            fight_item["winner"] = "Draw"

        # Extracts the winning method.
        fight_item["win_method"] = (
            response.xpath(
                "//body[@class='b-page']/section[@class='b-statistics__section_details']"
                "/div[@class='l-page__container']/div[@class='b-fight-details']"
                "/div[@class='b-fight-details__fight']/div[@class='b-fight-details__content']/p[1]/i[1]"
                "/i[2]/text()"
            )
            .extract()[0]
            .strip()
        )

        # Parses the winning method details.
        fight_item["win_method_details"] = response.xpath(
            "//body//div//div//div//p[2]"
        ).extract()[0]
        fight_item["win_method_details"] = re.sub(r"<.+?>", "", fight_item["win_method_details"])
        fight_item["win_method_details"] = (
            fight_item["win_method_details"]
            .replace("\n", "")
            .replace("Details:", "")
            .replace("  ", "")
        )

        # Parses the referee for the fight.
        fight_item["referee"] = (
            response.xpath("//body/section/div/div/div/div/p[1]")
            .extract()[0]
            .split("Referee:")[1]
            .split("\n")[-4]
            .strip()
        )

        # Extracts number of end_round fought.
        end_round = response.xpath(
            "/html[1]/body[1]/section[1]/div[1]/div[1]/div[2]/div[2]/p[1]/i[2]"
        ).get()
        # Data wrangles rounds by getting rid of all non numeric values and type converting string to int
        fight_item["end_round"] = int(
            re.sub("[^0-9]", "", end_round.split(" Round:\n        </i>\n ")[-1])
        )

        # Extracts the time the bout ended.
        fight_item["time"] = response.xpath("//p[1]//i[3]").extract()[0].split()[-2]
        date_time = datetime.strptime(fight_item["time"], "%M:%S").time()
        fight_item["end_second"] = date_time.minute * 60 + date_time.second

        # Obtains the all important stats table.
        fight_stats_table = response.xpath(
            "//p[@class='b-fight-details__table-text']"
        ).extract()

        # Extracts the totals and significant strikes tables
        for ind, stat in enumerate(fight_stats_table, start=0):
            # Set fighter number.
            if ind % 2 == 0:
                fighter_num = "f1"
            else:
                fighter_num = "f2"

            # Extracts the fighter detail urls.
            if ind == 0:
                fight_item["fighter1_detail_url"] = stat.split("href")[1].split('"')[1]
            elif ind == 1:
                fight_item["fighter2_detail_url"] = stat.split("href")[1].split('"')[1]

            if ind <= 20 * (fight_item["end_round"] + 1):
                # Sets a base index because there are 10 total columns with two rows of data for each fighter.
                base_ind = ind % 20

                # Set statistic type (total or round by round)
                time_type_ind = int(ind / 20)
                if time_type_ind == 0:
                    time_type = "total"
                else:
                    time_type = f"round{time_type_ind}"

                # Parses the totals table.
                if 2 <= base_ind <= 3:
                    fight_item[f"{fighter_num}_{time_type}_knockdown"] = int(
                        re.sub("[^0-9]", "", stat)
                    )
                elif 4 <= base_ind <= 5:
                    (
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_l"],
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_a"],
                    ) = self.extract_number_of(stat)
                elif 8 <= base_ind <= 9:
                    (
                        fight_item[f"{fighter_num}_{time_type}_strikes_l"],
                        fight_item[f"{fighter_num}_{time_type}_strikes_a"],
                    ) = self.extract_number_of(stat)
                elif 10 <= base_ind <= 11:
                    (
                        fight_item[f"{fighter_num}_{time_type}_takedown_l"],
                        fight_item[f"{fighter_num}_{time_type}_takedown_a"],
                    ) = self.extract_number_of(stat)
                elif 14 <= base_ind <= 15:
                    fight_item[f"{fighter_num}_{time_type}_submission_a"] = int(
                        re.sub("[^0-9]", "", stat)
                    )
                elif 16 <= base_ind <= 17:
                    fight_item[f"{fighter_num}_{time_type}_pass"] = int(
                        re.sub("[^0-9]", "", stat)
                    )
                elif 18 <= base_ind <= 19:
                    fight_item[f"{fighter_num}_{time_type}_reversal"] = int(
                        re.sub("[^0-9]", "", stat)
                    )

            else:
                # Sets a base index because there are 9 total columns with two rows of data for each fighter.
                base_ind = (ind - (20 * (fight_item["end_round"] + 1))) % 18

                # Set statistic type (total or round by round)
                time_type_ind = int((ind - (20 * (fight_item["end_round"] + 1))) / 18)
                if time_type_ind == 0:
                    time_type = "total"
                else:
                    time_type = f"round{time_type_ind}"

                # Parses the significant strikes table.
                if 6 <= base_ind <= 7:
                    (
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_head_l"],
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_head_a"],
                    ) = self.extract_number_of(stat)
                elif 8 <= base_ind <= 9:
                    (
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_body_l"],
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_body_a"],
                    ) = self.extract_number_of(stat)
                elif 10 <= base_ind <= 11:
                    (
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_leg_l"],
                        fight_item[f"{fighter_num}_{time_type}_sigstrikes_leg_a"],
                    ) = self.extract_number_of(stat)
                elif 12 <= base_ind <= 13:
                    (
                        fight_item[f"{fighter_num}_{time_type}_distance_l"],
                        fight_item[f"{fighter_num}_{time_type}_distance_a"],
                    ) = self.extract_number_of(stat)
                elif 14 <= base_ind <= 15:
                    (
                        fight_item[f"{fighter_num}_{time_type}_clinch_l"],
                        fight_item[f"{fighter_num}_{time_type}_clinch_a"],
                    ) = self.extract_number_of(stat)
                elif 16 <= base_ind <= 17:
                    (
                        fight_item[f"{fighter_num}_{time_type}_ground_l"],
                        fight_item[f"{fighter_num}_{time_type}_ground_a"],
                    ) = self.extract_number_of(stat)

        yield fight_item
