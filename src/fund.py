from .utils import *


class Fund():
    def __init__(self, fund_data):
        self.save_info(fund_data)

    def save_info(self, fund_data):
        self.country = fund_data['country']
        self.name = fund_data['name']
        self.symbol = fund_data['symbol']
        self.issuer = fund_data['issuer']
        self.isin = fund_data['isin']
        self.asset_class = fund_data['asset_class']
        self.currency = fund_data['currency']
        fund_info = investpy.funds.get_fund_information(self.name, self.country, as_json=False)
        self.inception_date = fund_info['Inception Date'][0]
        self.market_cap = fund_info['Market Cap'][0]
        self.total_assets = fund_info['Total Assets'][0]
        self.expenses = float(fund_info['Expenses'][0].replace("%", ""))
        self.category = fund_info['Category'][0]
        self.ttm_yield = fund_info['TTM Yield'][0]
        self.roe = float(fund_info['ROE'][0].replace("%", ""))
        self.turnover = float(fund_info['Turnover'][0].replace("%", ""))
        self.roa = float(fund_info['ROA'][0].replace("%", ""))

    def get_historical_data(self, from_date="01/01/1990"):
        to_date = datetime.datetime.now().strftime("%d/%m/%Y")
        daily_df = investpy.get_fund_historical_data(fund=self.name, country=self.country, from_date=from_date, to_date=to_date).rename(columns={'Close': self.name})
        daily_df['return'] = daily_df[self.name].pct_change()
        daily_df = daily_df[abs(daily_df['return']) < 10*abs(daily_df['return']).median()]
        yearly_df = daily_df.resample('A').last()
        monthly_df = daily_df.resample('M').last()
        self.df = {'daily': daily_df, 'yearly': yearly_df, 'monthly': monthly_df}
        for period in self.df.keys():
            self.df[period]['return'] = self.df[period][self.name].pct_change()
        for window in [5, 10, 25, 50, 100, 150, 200, 300]:
            self.df['daily']['EMA-' + str(window)] = ta.trend.ema_indicator(self.df['daily'][self.name], window=window)

    def calculate_metrics(self):
        daily = self.df['daily'][self.name]
        self.inception_return = calculate_percent_return(daily)
        self.years = get_years_past(daily)
        self.cagr = calculate_cagr(daily)
        self.annualized_volatility = calculate_annualized_volatility(daily)
        self.sharpe_ratio = calculate_sharpe_ratio(daily)
        self.rolling_sharpe_ratio = calculate_rolling_sharpe_ratio(daily)
        self.annualized_downside_deviation = calculate_annualized_downside_deviation(daily)
        self.sortino_ratio = calculate_sortino_ratio(daily)
        self.pure_profit_score = calculate_pure_profit_score(daily)
        #self.jensens_alpha = calculate_jensens_alpha(daily)
        self.max_drawdown = calculate_max_drawdown(daily)
        self.calmar_ratio = calculate_calmar_ratio(daily)

    def to_dict(self):
        info_dict = dict(
            name=self.name,
            issuer=self.issuer,
            isin=self.isin,
            asset_class=self.asset_class,
            currency=self.currency,
            inception_date=self.inception_date,
            market_cap=self.market_cap,
            total_assets=self.total_assets,
            expenses=self.expenses,
            category=self.category,
            country=self.country,
            years=self.years,
            ttm_yield=self.ttm_yield,
            roe=self.roe,
            turnover=self.turnover,
            roa=self.roa,
            cagr=round(100*self.cagr, 2),
            annualized_volatility=self.annualized_volatility,
            sharpe_ratio=round(self.sharpe_ratio, 2) if self.sharpe_ratio > 1 else round(self.sharpe_ratio, 4),
            sortino_ratio=round(self.sortino_ratio, 2) if self.sortino_ratio > 1 else round(self.sortino_ratio, 4),
            pure_profit_score=round(self.pure_profit_score, 2) if self.pure_profit_score > 1 else round(self.pure_profit_score, 4),
            max_drawdown=round(100*self.max_drawdown, 2),
            calmar_ratio=round(self.calmar_ratio, 2) if self.calmar_ratio > 1 else round(self.calmar_ratio, 4),
        )
        for y in [1, 3, 5, 10, 15, 20]:
            info_dict['yearly_return_' + str(y)] = round(100*(self.df['yearly'][self.name].pct_change(y).iloc[-1] ** (1/y) -1), 2)
        for m in [1, 3, 6, 12, 18, 24]:
            info_dict['monthly_return_' + str(m)] = round(100*(self.df['monthly'][self.name].pct_change(m).iloc[-1] ** (1/m) -1), 2)
        return info_dict

    def display(self):
        fig, (ax, tb) = plt.subplots(1, 2, figsize=(30, 10),gridspec_kw=dict(width_ratios=[2,1]))
        ax.plot(self.df['daily'][self.name])
        ax.set_title(self.name)
        ax.grid(True)
        info_dict = self.to_dict()
        for info in info_dict:
          if isinstance(info_dict[info], float):
            if abs(info_dict[info]) > 1:
              info_dict[info] = round(info_dict[info], 2)
            else:
              info_dict[info] = round(info_dict[info], 4)
          if 'return' in info or info in ['max_drawdown', 'cagr', 'inception_return']:
              info_dict[info] = f'{info_dict[info]}%'
        txt = [[info, info_dict[info]] for info in info_dict.keys()]
        # Display all information in dictionary info_dict in a table in tb (round all floats to 4 significant figures)
        table = tb.table(cellText=txt, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        fig.tight_layout()
        plt.show()