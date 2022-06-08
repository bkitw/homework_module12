from collections import UserDict
from datetime import datetime
from datetime import date
from itertools import islice
import pickle
import os
import re


class Record:
	def __init__(self, name, phone=None, birthday=None):
		self.name = name
		self.phones = []
		self.birthday = birthday

		if phone:
			self.add_phone(phone)

	def check_phone(self, phone) -> bool:
		if str(phone) in self.phones:
			return True
		return False

	def add_phone(self, phone) -> bool:
		if not self.check_phone(phone):
			self.phones.append(str(phone))
			return True
		return False

	def update_phone(self, phone, new_phone) -> bool:
		if self.check_phone(phone):
			self.delete_phone(phone)
			self.add_phone(new_phone.value)
			return True
		raise ValueError

	def delete_phone(self, phone) -> bool:
		if self.check_phone(phone):
			self.phones.remove(str(phone))
			return True
		return False

	def days_to_birthday(self):
		if self.birthday.value is None:
			return "невозможно посчитать"
		today = date.today()
		splitted_data = self.birthday.value.split('.')
		needed_data = datetime(year=int(today.year), month=int(splitted_data[1]),
		                       day=int(splitted_data[0]))
		needed_data = needed_data.date()
		if needed_data < today:
			needed_data = datetime(year=int(today.year) + 1, month=int(splitted_data[1]),
			                       day=int(splitted_data[0]))
			needed_data = needed_data.date()
		difference = needed_data - today
		result = difference.days
		return f'{result}'

	def __repr__(self):
		return f'{self.phones if self.phones else "Number not recorded"}; ' \
		       f'BD: {self.birthday.value if self.birthday else "Birth date not recorded"}; ' \
		       f"{self.days_to_birthday() if self.birthday else 'Cant calculate'}."


class Field:
	def __init__(self, value) -> None:
		self.__value = None
		self.value = value


class Name(Field):

	def __repr__(self):
		return self.value

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, value):
		if value and type(value) is str and not [x for x in value if x.isdigit()]:
			self.__value = value
		else:
			raise NameIncorrect


class Phone(Field):

	def __repr__(self):
		return f'{self.__value}'

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, n_value):
		n_value = n_value.strip()
		for ch in n_value:
			if ch not in "0123456789()-+":
				raise ValueError
		self.__value = n_value


class Birthday(Field):
	def __repr__(self):
		return self.value

	@property
	def value(self):
		return self.__value

	@value.setter
	def value(self, b_value):
		if b_value:
			try:
				datetime.strptime(b_value, "%d.%m.%Y")
			except ValueError:
				raise BirthdayIncorrect
		else:
			self.__value = None
		self.__value = b_value


class AddressBook(UserDict):

	def add_record(self, record: Record):
		self.data[record.name.value] = record

	def __next__(self):
		return next(self.iterator())

	def iterator(self, n=2):
		start, page = 0, n
		while True:
			yield dict(islice(self.data.items(), start, n))
			start, n = n, n + page
			if start >= len(self.data):
				break


address_book = AddressBook()

f_name = 'contacts_data.bin'


class NameAlreadyExists(Exception):
	pass


class PhoneAlreadyExists(Exception):
	pass


class ChooseOverweld(Exception):
	pass


class NameIncorrect(Exception):
	pass


class BirthdayIncorrect(Exception):
	pass


def input_exception(func):
	def wrapper(*args, **kwargs):
		while True:
			try:
				return func(*args, **kwargs)
			except NameIncorrect:
				print('Некорректное имя.')
				continue
			except ValueError:
				print("Номер введён неверно. Попробуйте ещё раз.")
				continue
			except BirthdayIncorrect:
				print("Дата рождения введена неверно. Попробуйте ещё раз.")
				continue
			except NameAlreadyExists:
				print("Такое имя уже существует. Попробуйте ещё раз.")
				continue
			except KeyError:
				print("Такого контакта в телефонной книге нет!")
				continue
			except PhoneAlreadyExists:
				print("Такой номер уже существует. Попробуйте ещё раз.")
				continue
			except ChooseOverweld:
				print("Выберите один из пунктов меню!")
				continue

	return wrapper


...


@input_exception
def add_name() -> Name:
	name = Name(input('Введите имя: ').strip().title())
	if name.value in address_book:
		raise NameAlreadyExists

	return name


@input_exception
def add_phone() -> Phone:
	phone = Phone(input('Введите номер телефона: ').strip())

	return phone


@input_exception
def add_birthday() -> Birthday:
	birthday = Birthday(input('Введите дату рождения "дд.мм.гггг.": ').strip())
	if birthday.value == '':
		birthday.value = None
	elif birthday.value.split('.')[2] < '1900' or birthday.value.split('.')[2] > '2022':
		raise BirthdayIncorrect
	return birthday


@input_exception
def add_command() -> None:
	print('--- Добавление записи ---')
	name = add_name()
	phone = add_phone()
	birthday = add_birthday()
	record = Record(name, phone, birthday)
	address_book.add_record(record)
	print(f'Запись "{record.name.value}" добавлена\n---***---')


def view_command() -> None:
	print('--- Просмотр записей ---')
	for key, value in address_book.items():
		print(f'{key} - {", ".join(address_book[key].phones)}; '
		      f'{address_book[key].birthday.value if address_book[key].birthday.value else "Не указано"}\n----')


@input_exception
def update_command() -> None:
	print('--- Обновление записи ---')
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	for index, name in enumerate(address_book):
		print(f'{str(index + 1) + ".":<3} -- {name + ";":<15}')
	name_choose = int(input('Выберите номер записи для обновления: '))
	if name_choose > len(address_book):
		raise ChooseOverweld
	name = address_book[list(address_book.keys())[name_choose - 1]]
	print(f'Запись "{name.name.value}" выбрана')
	for index, number in enumerate(name.phones):
		print(f'{str(index + 1) + ".":<1} -- {number};')
	number_choose = int(input('Выберите номер для обновления: '))
	if number_choose > len(name.phones):
		raise ChooseOverweld
	phone = name.phones[number_choose - 1]
	print(f'Номер "{phone}" выбран')
	new_phone = add_phone()
	if new_phone in name.phones:
		raise PhoneAlreadyExists
	name.phones[number_choose - 1] = str(new_phone)
	print(f'Номер "{phone}" обновлён на "{new_phone}"\n---***---')


@input_exception
def append_command() -> None:
	print('--- Добавление номера телефона ---')
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	for index, name in enumerate(address_book):
		print(f'{str(index + 1) + ".":<3} -- {name + ";":<15}')
	name_choose = int(input('Выберите запись, в которую нужно добавить телефон: '))

	if name_choose > len(address_book):
		raise ChooseOverweld
	name = address_book[list(address_book.keys())[name_choose - 1]]
	print(f'Запись "{name.name.value}" выбрана')
	phone = add_phone()
	if phone.value in name.phones:
		raise PhoneAlreadyExists
	name.phones.append(phone.value)
	print(f'Номер "{phone}" добавлен к записи "{name.name.value}"\n---***---')


@input_exception
def delete_phone_command() -> None:
	print('--- Удаление номера телефона ---')
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	for index, name in enumerate(address_book):
		print(f'{str(index + 1) + ".":<3} -- {name + ";":<15}')
	name_choose = int(input('Выберите запись из которой нужно удалить телефон: '))
	if name_choose > len(address_book):
		raise ChooseOverweld
	name = address_book[list(address_book.keys())[name_choose - 1]]
	print(f'Запись "{name.name.value}" выбрана:')
	for index, number in enumerate(name.phones):
		print(f'{str(index + 1) + ".":<1} -- {number};')
	number_choose = int(input('Выберите номер телефона для удаления: '))
	if number_choose > len(name.phones):
		raise ChooseOverweld
	phone = name.phones[number_choose - 1]
	name.phones.pop(number_choose - 1)
	print(f'Номер "{phone}" удалён из записи "{name.name.value}".\n---***---')


@input_exception
def delete_contact_command() -> None:
	print('--- Удаление контакта ---')
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	for index, name in enumerate(address_book.keys()):
		print(f'{str(index + 1) + ".":<3} -- {name + ";":<15}')
	contact = int(input('Введите порядковый номер контакта, который вы хотели бы удалить: '))
	for inx, name in enumerate(address_book.keys()):
		if contact == inx + 1:
			del address_book[name]
			print(f'Запись "{name}" удалена.\n---***---')
			break
		elif contact > inx + 1:
			continue
		else:
			raise ChooseOverweld


@input_exception
def search_command() -> None:
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	choose = input('Выберите поиск (введите соответствующую цифру):\n'
	               '1) По имени;\n2) По номеру телефона;\n>>>> ').strip().lower()
	if choose == '1':
		print('--- Поиск по имени ---')
		name = input('Введите имя или фрагмент имени контакта: ').strip()
		for contact in address_book.keys():
			if re.search(name, contact):
				print(f'Найдено: {contact}')
				print(f'Телефон(ы) контакта: {", ".join(address_book[contact].phones)}')
				print(
					f'Дата рождения контакта: {address_book[contact].birthday.value if address_book[contact].birthday.value else "Не указано."}')
				print('-----')
	elif choose == '2':
		print('--- Поиск по номеру телефона ---')
		phone = input('Введите номер или фрагмент номера телефона: ').strip()
		for contact in address_book.values():
			for number in contact.phones:
				if re.search(phone, number):
					print(f'Найдено: {contact.name.value}')
					print(f'Телефон(ы) контакта: {", ".join(contact.phones)}')
					print(
						f'Дата рождения контакта: {contact.birthday.value if contact.birthday.value else "Не указано."}')
					print('-----')
	print("--- Поиск завершен ---")


@input_exception
def days_to_birthday() -> None:
	if len(address_book) == 0:
		print('Телефонная книга пуста!')
		return
	print('--- Сколько дней до дня рождения? ---')
	for index, name in enumerate(address_book.keys()):
		print(f'{str(index + 1) + ".":<3} -- {name + ";":<15}')
	name_choose = int(input('Выберите запись, для которой вы хотите получить информацию: '))
	for inx, name in enumerate(address_book.keys()):
		if name_choose == inx + 1:
			if address_book[name].birthday.value:
				print(f'До дня рождения осталось {address_book[name].days_to_birthday()} дней.\n---***---')
			else:
				print('Дата рождения не указана.')
			break
		elif name_choose > inx + 1:
			continue
		else:
			raise ChooseOverweld


...


def goodbye() -> None:
	print('До свидания!')
	exit()


def help_command() -> None:
	print(
		'---\n'
		'Доступные команды:\n'
		'add - добавить запись\n'
		'show all - просмотреть все записи\n'
		'show dtb - просмотреть количество дней до дня рождения контакта\n'
		'change - обновить номер телефона\n'
		'append - добавить номер телефона\n'
		'delete phone - удалить запись\n'
		'здравствуйте, привет, hello, hi - приветствие\n'
		'delete contact - удалить контакт\n'
		'find - поиск записи\n'
		'clear, cls - очистить экран\n'
		'help - помощь\n'
		'exit, выход, quit, q  - выход\n---')


def greetings() -> None:
	clear_screen()
	print('---\nДобро пожаловать в контактную книгу!\nЧем я могу помочь?')


def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

...


def command_parser(command: str) -> None:
	for func, comm in main_commands.items():
		if command in comm:
			return func()
	else:
		print('---\nНеизвестная команда!\n---')


main_commands = {
	add_command: 'add',
	update_command: 'change',
	append_command: 'append',
	delete_phone_command: 'delete phone',
	delete_contact_command: 'delete contact',
	view_command: 'show all',
	days_to_birthday: 'show dtb',
	search_command: 'find',
	help_command: ('help', 'помощь'),
	goodbye: ('exit', 'выход', 'quit', 'q'),
	greetings: ('здравствуйте', 'привет', 'hello', 'hi'),
	clear_screen: ('clear', 'cls')
}


def main():
	greetings()
	try:
		with open(f_name, 'rb') as f:
			address_book.data = pickle.load(f)
	except FileNotFoundError:
		print(f'Файл {f_name} не найден! Cоздаю новый...')
	finally:
		with open(f_name, 'wb') as f:
			pickle.dump(address_book.data, f)
	while True:
		command = input('Введите "hello" или "help":\n>>>> ')
		command_parser(command.strip().lower())
		with open(f_name, 'wb') as f:
			pickle.dump(address_book.data, f)


if __name__ == '__main__':
	main()
