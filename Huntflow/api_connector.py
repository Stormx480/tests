import requests
import json
from config import base_url, default_headers, logger


class ApiConnector:

    @staticmethod
    def get_me():
        """
        Получение информации о пользователе.
        :return: Response object
        """
        response = requests.get(base_url+'/me', headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response
        else:
            raise Exception('Error when try connect to API.')

    @staticmethod
    def get_accounts():
        """
        Получение доступных организаций.
        :return: Response object
        """
        response = requests.get(base_url+'/accounts', headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response
        else:
            raise Exception(response)

    @staticmethod
    def get_vacancies_list(account_id: int):
        """
        Получение списка вакансий.
        :param account_id: int, можно получить с помощью функции get_accounts()
        :return: json dict from Response object
        """
        response = requests.get(url=base_url+'/account/{account_id}/vacancies'.format(account_id=account_id),
                                headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)

    @staticmethod
    def get_statuses_list(account_id: int):

        response = requests.get(url=base_url+'/account/{account_id}/vacancy/statuses'.format(account_id=account_id),
                                headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)

    @staticmethod
    def get_applicants_list(account_id: int):
        """
        Получение списка кандидатов.
        :param account_id: int
        :return: json dict from Response object
        """
        response = requests.get(url=base_url+'/account/{account_id}/applicants'.format(account_id=account_id),
                                headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response
        else:
            raise Exception(response)

    @staticmethod
    def get_applicant_sources(account_id: int):

        response = requests.get(url=base_url+'/account/{account_id}/applicant/sources'.format(account_id=account_id),
                                headers=default_headers)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response
        else:
            raise Exception(response)

    @staticmethod
    def add_applicants(last_name: str = None, middle_name: str = None, first_name: str = None, phone: str = None,
                       email: str = None, position: str = None, money: str = None, birth_data: dict = None,
                       photo_id: int = None, resume_file_id: int = None, account_id: int = None,
                       resume_text: str = None):

        data = {
            "last_name": last_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "phone": phone,
            "email": email,
            "position": position,
            "money": money,
            "photo": photo_id,
            "externals": [
                {
                    "data": {
                        "body": resume_text,
                    },
                    "auth_type": "NATIVE",
                    "files": [
                        {
                            "id": resume_file_id
                        }
                    ]
                }
            ]
        }

        for argument in list(data):
            if data[argument] is None:
                data.pop(argument)

        if birth_data is not None:
            data["birthday_day"] = birth_data['day']
            data["birthday_month"] = birth_data['month']
            data["birthday_year"] = birth_data['year']

        if resume_text is None:
            data['externals'][0].pop('data')
        if resume_file_id is None:
            data['externals'][0].pop('files')
        if resume_text is None and resume_file_id is None:
            data.pop('externals')

        response = requests.post(url=base_url+'/account/{account_id}/applicants'.format(account_id=account_id),
                                 headers=default_headers,
                                 json=data)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)

    @staticmethod
    def add_applicants_to_vacancy(account_id: int, applicant_id: int, vacancy_id: int, status_id: int, comment: str,
                                  resume_file_id: int):

        data = {
            "vacancy": vacancy_id,
            "status": status_id,
            "comment": comment,
            "files": [
                {
                    "id": resume_file_id
                }
            ]
        }

        response = requests.post(url=base_url+'/account/{account_id}/applicants/{applicant_id}/vacancy'.format(
            account_id=account_id, applicant_id=applicant_id),
                                 headers=default_headers,
                                 json=data)

        logger.debug(json.loads(response.text))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)

    @staticmethod
    def upload_resume_file(account_id: int, filename: str, file_path: str):

        custom_headers = default_headers.copy()
        custom_headers['X-File-Parse'] = 'true'

        files = {'file': (filename, open(file_path, 'rb'), 'application/zip')}

        response = requests.post(url=base_url+'/account/{account_id}/upload'.format(account_id=account_id),
                                 headers=custom_headers,
                                 files=files)

        parsed = json.loads(response.text)
        logger.debug(parsed)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response)

