from abc import ABC, abstractmethod


class BaseBrowser(ABC):

    @abstractmethod
    def load_sites(self):
        pass

    @abstractmethod
    def scrape_sites_by_xpath(self):
        pass

    @abstractmethod
    def refresh_sites(self):
        pass

    @abstractmethod
    def close(self):
        pass
