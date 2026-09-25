import logging
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = 'https://i-spa.su/'
GIRLS_URL = urljoin(BASE_URL, 'girls/')
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)
TODAY_MARKER = 'Ждёт вас сегодня'
REQUEST_TIMEOUT_SECONDS = 20


@dataclass(slots=True)
class Master:
    name: str
    profile_url: str
    photos: list[str]

    @property
    def html_link(self) -> str:
        return f'<a href="{self.profile_url}">{self.name}</a>'


class SpaParser:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def fetch_today_masters(self) -> list[Master]:
        soup = self._get_soup(GIRLS_URL)
        master_cards = soup.find_all('a', class_='master')
        masters: list[Master] = []

        for card in master_cards:
            if TODAY_MARKER not in card.get_text(' ', strip=True):
                continue

            master = self._parse_master_card(card)
            if master is None:
                continue

            masters.append(master)

        return masters

    def _parse_master_card(self, card: BeautifulSoup) -> Master | None:
        profile_href = card.get('href')
        image = card.find('img')

        if not profile_href or image is None:
            logger.warning('Skip card without profile link or image: %s', card)
            return None

        name = (image.get('alt') or '').strip()
        if not name:
            logger.warning('Skip card without master name: %s', card)
            return None

        profile_url = urljoin(BASE_URL, profile_href)
        preview_photo_url = urljoin(BASE_URL, image.get('src') or '')
        photos = self._fetch_master_photos(profile_url, preview_photo_url)

        return Master(name=name, profile_url=profile_url, photos=photos)

    def _fetch_master_photos(self, profile_url: str, preview_photo_url: str) -> list[str]:
        soup = self._get_soup(profile_url)
        photo_urls = [preview_photo_url] if preview_photo_url else []

        for photo_block in soup.find_all('a', class_='master-gallery__block'):
            href = photo_block.get('href')
            if not href:
                continue

            photo_url = urljoin(BASE_URL, href)
            if photo_url not in photo_urls:
                photo_urls.append(photo_url)

        return photo_urls

    def _get_soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
