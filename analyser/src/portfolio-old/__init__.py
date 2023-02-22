from .api import PortfolioAPI
def yield_portfolio():
    api: PortfolioAPI = PortfolioAPI.create()
    try:
        yield api
    finally:
        api.close()
