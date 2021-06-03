from bs4 import BeautifulSoup
from requests import get
import pandas as pd
from bs4 import BeautifulSoup
from requests import get
import time
from random import choice
import numpy as np
from geopy.geocoders import Nominatim
import traceback


# get html text
def get_html(url):
    headers = ({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
           })

    response = get(url, headers=headers)
    if response.status_code==200 :
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else :
        return


def init_houe_data():
    house_data = {
        'property_name' : '',
        'property_address' : '',
        'latitude' : '',
        'longitude' : '',
        'OpenStreetMap_address' : '',
        'property_price' : '',
        'property_description' : '',
        'tipe_property':'',
        'certificate' : '',
        'dilengkapi_perabotan' : '',
        'kondisi_properti' : '',
        'jalur_telepon' : '',
        'jumlah_lantai' : '',
        'daya_listrik' : '',
        'tanggal_tayang' : '',
        'luas_bangunan' : '',
        'luas_tanah' : '',
        'kamar_tidur' : '',
        'kamar_mandi' : '',
        'garasi_mobil' : '',
    }
    return house_data


def get_house_detail(one_list_html, soup_html_HD, house_data, geolocator):    
    # name
    info_name = one_list_html.find('h2')
    if info_name is not None :
        house_data['property_name'] = info_name.text
    
    info_price = soup_html_HD.find('div', {'class':'property-price'})
    if info_price is not None :
        house_data['property_price'] = info_price.text
        
    info_desc = soup_html_HD.find('pre', {'class':'property-description'})
    if info_desc is not None :
        house_data['property_description'] = info_desc.text
        
    # address
    info_address = soup_html_HD.find('span', {'class':'property-address'})
    if info_address is not None :
        house_data['property_address'] = info_address.text
        
    # latitude, longitude & openstreetmap Address
    location = geolocator.geocode(info_address.text)
    if location is not None :
        house_data['latitude'] = location.latitude
        house_data['longitude'] = location.longitude
        house_data['OpenStreetMap_address'] = location.address
        
    # tipe property
    tipe_property = soup_html_HD.find('div', {'class':'property-attr-propertyType'})
    if tipe_property is not None :
        house_data['tipe_property'] = tipe_property.text.split(':')[1]
        
    # certificate
    certificate = soup_html_HD.find('div', {'class':'property-attr-certificate'})
    if certificate is not None :
        house_data['certificate'] = certificate.text.split(':')[1]
        
    # furnishing
    furnishing = soup_html_HD.find('div', {'class':'property-attr-furnishing'})
    if furnishing is not None :
        house_data['dilengkapi_perabotan'] = furnishing.text.split(':')[1]
        
    # property condition
    kondisi_property = soup_html_HD.find('div', {'class':'property-attr-propertyCondition'})
    if kondisi_property is not None :
        house_data['kondisi_properti'] = kondisi_property.text.split(':')[1]
        
    # jalur telepon
    jalur_telepon = soup_html_HD.find('div', {'class':'property-attr-phoneLine'})
    if jalur_telepon is not None :
        house_data['jalur_telepon'] = jalur_telepon.text.split(':')[1]
        
    # jumlah lantai
    jumlah_lantai = soup_html_HD.find('div', {'class':'property-attr-floors'})
    if jumlah_lantai is not None :
        house_data['jumlah_lantai'] = jumlah_lantai.text.split(':')[1]
        
    # daya listrik
    daya_listrik = soup_html_HD.find('div', {'class':'property-attr-electricity'})
    if daya_listrik is not None :
        house_data['daya_listrik'] = daya_listrik.text.split(':')[1]
        
    # tanggal tayang
    tanggal_tayang = soup_html_HD.find('div', {'class':'property-attr-updatedAt'})
    if tanggal_tayang is not None :
        house_data['tanggal_tayang'] = tanggal_tayang.text.split(':')[1]
        
    # property area info
    area_info = soup_html_HD.findAll('li', {'class':'PropertySummarystyle__AreaInfoItem-lmykjH kdRqkQ'})
    for area in area_info :
        if 'bangunan' in area.text.lower() :
            house_data['luas_bangunan'] = area.text.split(':')[1]
        elif 'tanah' in area.text.lower():
            house_data['luas_tanah'] = area.text.split(':')[1]
            
    # jumlah kamar
    kamar_tidur = soup_html_HD.find('i', {'class':'property-bed'})
    if kamar_tidur is not None :
        house_data['kamar_tidur'] = kamar_tidur.parent.text
        
    # jumlah kamar mandi
    kamar_mandi = soup_html_HD.find('i', {'class':'property-bath'})
    if kamar_mandi is not None :
        house_data['kamar_mandi'] = kamar_mandi.parent.text
        
    # garasi mobil
    garasi_mobil = soup_html_HD.find('i', {'class':'property-car'})
    if garasi_mobil is not None :
        house_data['garasi_mobil'] = garasi_mobil.parent.text
        
    return house_data


# looping terhadap semua item rumah di page itu
def get_all_list_house(listing, house_data_list, geolocator):
    for house in listing :
        try :
            # get url untuk detail rumah
            all_house_link = house.findAll('a')

            for link in all_house_link :
                link_data = link.get('href')
                if 'rumah123.com' not in link_data and '/' in link_data:
                    urlHouseDetail = F"{base_url}{link_data}"
                    house_data = init_houe_data()
                    html_soup_HD = get_html(urlHouseDetail)
                    house_data = get_house_detail(house, html_soup_HD, house_data, geolocator)
                    house_data_list.append(house_data)

                    # 
                    sleep_time = choice(np.arange(3, 6, 0.2))
                    time.sleep(sleep_time)
                    break
        except Exception as e :
            continue
    return house_data_list


if __name__ == '__main__' :
    geolocator = Nominatim(user_agent='house_scraping')
    base_url = 'https://www.rumah123.com'
    url = 'https://www.rumah123.com/jual/palembang/residensial/'
    house_data_list = []
    curr_page = 1
    continue_scrap = True
    try :
        while continue_scrap :
            html_soup = get_html(url)
            # get all listing
            listing = html_soup.find('ul', attrs={'class':'listing-list'}).findAll('li', {'class':'hrjLKa'}, recursive=False)
            house_data_list = get_all_list_house(listing, house_data_list, geolocator)
            
            # get next page
            continue_scrap = False
            all_pagination = html_soup.findAll('li', {'class':'pagination-item'})
            for page in all_pagination :
                if str(page.text) == str(curr_page + 1) :
                    continue_scrap = True
                    curr_page = page.text
                    url = f'https://www.rumah123.com/jual/palembang/residensial/?page={curr_page}'
                    break
    except Exception as e :
        print(traceback.format_exc())

    df = pd.DataFrame(house_data_list)
    print('Scraping is success')
    filename = input('what is the name of the file? ')
    df.to_csv(f'{filename}.csv', index=False)
    df.to_excel(f'{filename}.xlsx', index=False)