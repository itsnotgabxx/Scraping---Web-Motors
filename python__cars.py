import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
import random

chrome_service = ChromeService()

chrome_options = ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--start-minimized")

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

dados_carros = []

base_url = "https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2Festoque%3Flkid%3D1022&actualPage={}"

pular = 0
numero_de_paginas = 18
pagina = 1 + pular

def format_photo_path(photo_path):
    
    photo_path = photo_path.replace("\\", "/")
    
    parts = photo_path.split("https:")

    if len(parts) > 1:
        parts[1] = parts[1].replace("/", "\\\\")

    formatted_path = "".join(parts)

    base_url = "https://image.webmotors.com.br/_fotos/AnuncioUsados/gigante/"
    final_url = base_url + formatted_path

    return final_url

while pagina <= numero_de_paginas + pular:
    
    try:
        
        time.sleep(random.uniform(2, 5))

        url = base_url.format(pagina)
        driver.get(url)

        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        pre_element = soup.find('pre')

        if pre_element:
            
            json_data = pre_element.text
            
            data = json.loads(json_data)
            
            carros = data.get('SearchResults', [])

            for carro in carros:
                specification = carro.get('Specification', {})
                seller = carro.get('Seller', {})
                prices = carro.get('Prices', {})
                title = specification.get('Title', '')
                make = specification.get('Make', {}).get('Value', '')
                model = specification.get('Model', {}).get('Value', '')
                version = specification.get('Version', {}).get('Value', '')
                year_fabrication = specification.get('YearFabrication', '')
                year_model = specification.get('YearModel', 0)
                odometer = specification.get('Odometer', 0)
                transmission = specification.get('Transmission', '')
                number_ports = specification.get('NumberPorts', '')
                body_type = specification.get('BodyType', '')
                vehicle_attributes = [attr.get('Name', '') for attr in specification.get('VehicleAttributes', '')]
                armored = specification.get('Armored', '')
                color = specification.get('Color', {}).get('Primary', '')
                seller_id = seller.get('Id', '')
                seller_type = seller.get('SellerType', '')
                seller_city = seller.get('City', '')
                seller_state = seller.get('State', '')
                seller_ad_type = seller.get('AdType', {}).get('Value', '')
                seller_budget_investment = seller.get('BudgetInvestimento', 0)
                seller_dealer_score = seller.get('DealerScore', 0)
                seller_car_delivery = seller.get('CarDelivery', False)
                seller_troca_com_troco = seller.get('TrocaComTroco', False)
                seller_exceeded_plan = seller.get('ExceededPlan', False)
                seller_fantasy_name = seller.get('FantasyName', '')
                price = prices.get('Price', 0)
                search_price = prices.get('SearchPrice', 0)
                listing_type = carro.get('ListingType', '')
                product_code = carro.get('ProductCode', '')
                channels = [channel.get('Value', '') for channel in carro.get('Channels', [])]
                unique_id = carro.get('UniqueId', '')
                long_comment = carro.get('LongComment', '')
                fipe_percent = carro.get('FipePercent', 0)
                is_elegible_vehicle_inspection = carro.get('IsElegibleVehicleInspection', False)
                photos = carro.get('Media', {}).get('Photos', [])
                photo_urls = [format_photo_path(photo['PhotoPath']) for photo in photos]

                dados_carro = {
                    'Nome': title,
                    'Marca': make,
                    'Modelo': model,
                    'Versão': version,
                    'Ano_Fabricação': year_fabrication,
                    'Ano_Modelo': year_model,
                    'Odômetro': odometer,
                    'Transmissão': transmission,
                    'Número_Portas': number_ports,
                    'BodyType': body_type,
                    'Veículo_Atributos': vehicle_attributes,
                    'Blindado': armored,
                    'Cor': color,
                    'Id_Vendedor': seller_id,
                    'Tipo_De_Vendedor': seller_type,
                    'Cidade_Vendedor': seller_city,
                    'Estado_Vendedor': seller_state,
                    'Tipo_Ad_Vendedor': seller_ad_type,
                    'Orçamento_De_Investimento_Vendedor': seller_budget_investment,
                    'Pontuação_Vendedor': seller_dealer_score,
                    'Entrega_Carro_Vendedor': seller_car_delivery,
                    'Aceita_Troca': seller_troca_com_troco,
                    'Plano_Excedido_vendedor': seller_exceeded_plan,
                    'Nome_Fantasia_Vendedor': seller_fantasy_name,
                    'Preço': price,
                    'Preço_Busca': search_price,
                    'Novo_Ou_Usado': listing_type,
                    'Código_Produto': product_code,
                    'Canais': channels,
                    'Id_Único_Carro': unique_id,
                    'Comentário_Longo': long_comment,
                    'Percentual_Fipe': fipe_percent,
                    'Inspeção_De_Veículo_Elegível': is_elegible_vehicle_inspection,
                    'Imagens': photo_urls
                }
                dados_carros.append(dados_carro)
                
            print("Página coletada:", pagina)
            pagina += 1
        else:
            raise ValueError("Nada encontrado")

    except:
        driver.quit()

        tempo = random.uniform(20, 25)
        print("Aguardando para reiniciar chrome: ", tempo)
        time.sleep(random.uniform(10, 20))
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

data_atual = datetime.now().strftime("%d-%m-%Y")

nome_arquivo = f'dados_carros_{data_atual}_{pular + 1}_{pular + numero_de_paginas}.xlsx'

df = pd.DataFrame(dados_carros)
df.to_excel(nome_arquivo, index=False)

print(f"Dados exportados para {nome_arquivo}")