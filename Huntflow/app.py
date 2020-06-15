from openpyxl import load_workbook
import os
import json
from pprint import pprint
from config import logger, status_dict, args, checker
from api_connector import ApiConnector as Api


class App:

    def __init__(self):
        logger.info('Init App Class')
        accounts_data = Api.get_accounts()
        self.account_data = accounts_data.json()['items'][0]
        self.account_id = self.account_data['id']
        self.checker = json.loads(checker.read())

    @staticmethod
    def conversion_db():
        """
        Парсерит xlsx файл для получения данных.

        :return: data: dict, словарь полученных данных,
                       где d.key - название столбика, d.value - данные в ячейке для каждой строки.
        """
        wb = load_workbook(args.folder+'/Тестовая база.xlsx', read_only=True)

        sheet = wb.get_sheet_by_name('Лист1')

        rows = sheet.rows

        cols = next(rows, None)

        data = []

        for row in rows:
            step = 0
            data_person = {}
            for s in row:
                data_person[cols[step].value] = s.value
                step += 1
            data.append(data_person)

        pprint(data)

        logger.info('Done')

        return data

    def send_resume_file(self, data_excel: dict):
        """
        Отправляет данные и файл резюме на сервер, а так же прикрепляет кандидаата к вакансии исходя из данных в базе.

        :param data_excel: словарь данных полученный с помощью функции conversion_db()
        """

        count_person = len(data_excel)

        statuses_list = Api.get_statuses_list(self.account_id)['items']
        vacancy_list = Api.get_vacancies_list(self.account_id)['items']

        for person in data_excel[self.checker['processed']:]:

            names = person['ФИО'].split(' ')
            len_names = len(names)

            if len_names != 0:
                last_name = names[0]
                if len_names > 1:
                    first_name = names[1]
                    if len_names > 2:
                        middle_name = names[2]
                    else:
                        middle_name = None
                else:
                    first_name = None
            else:
                last_name = None

            file_path = './Тестовое задание/'+person['Должность']+'/'

            logger.debug('Start to looking resume file')

            for element in os.scandir(file_path):
                if element.is_file():
                    if last_name in element.name:
                        logger.debug('File exist')

                        resume_data = Api.upload_resume_file(self.account_id,
                                                             filename=element.name,
                                                             file_path=element.path)

                        applicants_data = Api.add_applicants(
                            last_name=resume_data['fields']['name']['last'],
                            middle_name=resume_data['fields']['name']['middle'],
                            first_name=resume_data['fields']['name']['first'],
                            phone=resume_data['fields']['phones'][0],
                            email=resume_data['fields']['email'],
                            position=resume_data['fields']['position'],
                            money=resume_data['fields']['salary'],
                            birth_data=resume_data['fields']['birthdate'],
                            photo_id=resume_data['photo']['id'],
                            resume_file_id=resume_data['id'],
                            account_id=self.account_id,
                            resume_text=resume_data['text']
                        )

                        if person['Статус'].lower() in status_dict:
                            status_name = status_dict[person['Статус'].lower()]
                            for status in statuses_list:
                                if status['name'] == status_name:
                                    status_id = status['id']

                        for vacancy in vacancy_list:
                            if person['Должность'] == vacancy['position']:
                                vacancy_id = vacancy['id']

                        Api.add_applicants_to_vacancy(
                            account_id=self.account_id,
                            applicant_id=applicants_data['id'],
                            vacancy_id=vacancy_id,
                            status_id=status_id,
                            comment=person['Комментарий'],
                            resume_file_id=resume_data['id']
                        )

                        self.checker['processed'] += 1
                        logger.info(f"Processed {self.checker['processed']} of {count_person} resumes")
                        checker.seek(0)
                        json.dump(self.checker, checker, ensure_ascii=False)


if __name__ == '__main__':
    app = App()
    data_excel = app.conversion_db()

    app.send_resume_file(data_excel)
