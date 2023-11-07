import requests
import pandas as pd
from math import cos, pi, floor



### change url with race 1 url
start_url = 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx?RaceDate=2022/10/30&Racecourse=HV&RaceNo=1'
scrape_output_file = "scrape_output"

urls = list()
urls.append(start_url)
for i in range(2,13):
    url = start_url[:-1]+str(i)
    urls.append(url)


def parse_challenge(page):
    """
    Parse a challenge given by mmi and mavat's web servers, forcing us to solve
    some math stuff and send the result as a header to actually get the page.
    This logic is pretty much copied from https://github.com/R3dy/jigsaw-rails/blob/master/lib/breakbot.rb
    """
    top = page.split('<script>')[1].split('\n')
    challenge = top[1].split(';')[0].split('=')[1]
    challenge_id = top[2].split(';')[0].split('=')[1]
    return {'challenge': challenge, 'challenge_id': challenge_id, 'challenge_result': get_challenge_answer(challenge)}


def get_challenge_answer(challenge):
    """
    Solve the math part of the challenge and get the result
    """
    arr = list(challenge)
    last_digit = int(arr[-1])
    arr.sort()
    min_digit = int(arr[0])
    subvar1 = (2 * int(arr[2])) + int(arr[1])
    subvar2 = str(2 * int(arr[2])) + arr[1]
    power = ((int(arr[0]) * 1) + 2) ** int(arr[1])
    x = (int(challenge) * 3 + subvar1)
    y = cos(pi * subvar1)
    answer = x * y
    answer -= power
    answer += (min_digit - last_digit)
    answer = str(int(floor(answer))) + subvar2
    return answer


def scraper(url):
    s = requests.Session()
    r = s.get(url)

    if 'X-AA-Challenge' in r.text:
        challenge = parse_challenge(r.text)
        r = s.get(url, headers={
            'X-AA-Challenge': challenge['challenge'],
            'X-AA-Challenge-ID': challenge['challenge_id'],
            'X-AA-Challenge-Result': challenge['challenge_result']
        })

        yum = r.cookies
        r = s.get(url, cookies=yum)

    return  r.content


count = 1
for url in urls:
    print(url)
    try:
        scrape_data = pd.DataFrame()
        html = scraper(url)
        df_list = pd.read_html(html)
        x = df_list[4]
        x.columns = x.iloc[1]
        x = x.drop([0,1])
        scrape_data['Draw'] = x['Draw'].astype(int)
        scrape_data['Horse'] = x['Horse']
        scrape_data['Jockey'] = x['Jockey']
        scrape_data['No'] = x['Horse No.']
        scrape_data['Colour'] = ''
        scrape_data['DES'] = ''
        scrape_data.sort_values(by=['Draw'],ascending=False,inplace=True)
        print(scrape_data)
        if count == 1:
            with pd.ExcelWriter(scrape_output_file+".xlsx",engine='openpyxl',mode='w') as writer:
                scrape_data.to_excel(writer, sheet_name='Race'+str(count),index=False)
        else:
            with pd.ExcelWriter(scrape_output_file+".xlsx",engine='openpyxl',mode='a') as writer:
                scrape_data.to_excel(writer, sheet_name='Race'+str(count),index=False)
        count+=1
        print('Excel Converted')
    except:
        print('Skip url')
        pass





