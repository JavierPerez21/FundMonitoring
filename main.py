from src.fund import *


def get_funds(country = 'Spain', issuer_filter='Santander', limit_inception_date="01/01/2012"):
    available_funds = investpy.get_funds(country=country)
    time.sleep(1)
    funds = {}
    # Iterate over rows of available funds dataframe
    for index, row in available_funds.iterrows():
        # Condition
        if issuer_filter in  row['issuer']:
          try:
            fund = Fund(row)
            if pd.to_datetime(fund.inception_date) < pd.to_datetime(limit_inception_date):
              fund.get_historical_data()
              fund.calculate_metrics()
              funds[fund.name] = fund
              print(f'{round(100*index/len(available_funds), 2)}% extracted data for {row["name"]}')
              time.sleep(1)
          except Exception:
            pass

def compare_funds(fund1=None, fund2=None,from_date="01/01/1990"):
    available_funds = investpy.get_funds(country='Spain')
    if fund1 is None:
        fund1 = input("Enter first fund name: ")
    if fund2 is None:
        fund2 = input("Enter second fund name: ")
    fund1 = Fund(available_funds.loc[available_funds[available_funds['name'] == fund1].index[0]])
    fund2 = Fund(available_funds.loc[available_funds[available_funds['name'] == fund2].index[0]])

    fund1.get_historical_data(from_date=from_date)
    fund2.get_historical_data(from_date=from_date)

    fig, ax = plt.subplots(figsize=(15, 8))
    p1, = ax.plot(fund1.df['daily'][fund1.name], label=fund1.name, color='blue')
    twin = ax.twinx()
    p2, = twin.plot(fund2.df['daily'][fund2.name], label=fund2.name, color='red')
    ax.set_title(f'Comparison of {fund1.name} and {fund2.name}')
    ax.set_ylabel(fund1.name)
    twin.set_ylabel(fund2.name)
    ax.yaxis.label.set_color(p1.get_color())
    twin.yaxis.label.set_color(p2.get_color())
    plt.show()


if __name__ == '__main__':
    f1 = 'Santander Acciones Españolas A Fi'
    compare_funds(fund1=f1, fund2='Morgan Stanley Investment Funds - Us Growth Fund A', from_date="01/01/1990")
    compare_funds(fund1=f1, fund2='Blackrock Global Funds - Global Allocation Fund E2', from_date="01/01/1990")
    compare_funds(fund1=f1, fund2='Blackrock Global Funds - Next Generation Technology Fund E2', from_date="01/01/1990")