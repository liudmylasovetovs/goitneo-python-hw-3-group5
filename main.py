from datetime import datetime, timedelta
from collections import defaultdict

class InvalidParameterCount(Exception):
    pass

class ContactAlreadyExists(Exception):
    pass

class ContactDoesNotExist(Exception):
    pass

class NoBirthdaySet(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format")

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format for birthday. Please use DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

        if phone:
            self.add_phone(phone)
        if birthday:
            self.add_birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones.remove(Phone(phone))

    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Contact can have only one birthday.")

    def __str__(self, only_phones=False):
        if only_phones:
            phones_str = '; '.join(p.value for p in self.phones)
            return phones_str
        else:
            phones_str = '; '.join(p.value for p in self.phones)
            birthday_str = f', birthday: {self.birthday.value}' if self.birthday and self.birthday.value else ''
            return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook:
    def __init__(self):
        self.contacts = {}

    def add_contact(self, record):
        if record.name.value not in self.contacts:
            self.contacts[record.name.value] = record
            return "Contact added."
        else:
            raise ContactAlreadyExists

    def change_contact(self, record):
        if record.name.value in self.contacts:
            self.contacts[record.name.value] = record
            return "Contact updated."
        else:
            raise ContactDoesNotExist

    def show_phone(self, name):
        if name in self.contacts:
            return self.contacts[name].__str__(only_phones=True)
        else:
            raise ContactDoesNotExist

    def show_birthday(self, name):
        if name in self.contacts:
            contact = self.contacts[name]
            if contact.birthday:
                return contact.birthday.value
            else:
                raise NoBirthdaySet("No birthday set for this contact.")
        else:
            raise ContactDoesNotExist

    def show_all(self):
        for record in self.contacts.values():
            print(record)

    def get_birthdays_per_week(self):
        today = datetime.now()
        this_week_birthdays = defaultdict(list)

        for record in self.contacts.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, '%d.%m.%Y')
                user_delta = (birthday_date.replace(year=today.year) - today).days
                if 7 > user_delta >= 0:
                    if get_day_of_week_from_date(birthday_date) == 'Saturday':
                        user_delta += 2
                    elif get_day_of_week_from_date(birthday_date) == 'Sunday':
                        user_delta += 1
                    next_birthday = get_day_of_week_from_date(today + timedelta(days=user_delta))
                    this_week_birthdays[next_birthday].append(record.name.value)

        return this_week_birthdays

def get_day_of_week_from_date(input_date):
    return input_date.strftime("%A")

def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        raise InvalidParameterCount
    cmd, *args = parts
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            try:
                name, phone, *birthday = args
                if birthday:
                    record = Record(name=name, phone=phone, birthday=birthday[0])
                else:
                    record = Record(name=name, phone=phone)
                print(book.add_contact(record))
            except (InvalidParameterCount, ContactAlreadyExists, ValueError) as e:
                print(str(e))
        elif command == "change":
            try:
                name, phone, *birthday = args
                if birthday:
                    record = Record(name=name, phone=phone, birthday=birthday[0])
                else:
                    record = Record(name=name, phone=phone)
                print(book.change_contact(record))
            except (InvalidParameterCount, ContactDoesNotExist, ValueError) as e:
                print(str(e))
        elif command == "phone":
            try:
                name = args[0]
                print(book.show_phone(name))
            except (InvalidParameterCount, ContactDoesNotExist) as e:
                print(str(e))
        elif command == "all":
            book.show_all()
        elif command == "add-birthday":
            try:
                name, birthday = args
                if name in book.contacts:
                    book.contacts[name].add_birthday(birthday)
                    print(f"Birthday added for {name}.")
                else:
                    raise ContactDoesNotExist
            except (InvalidParameterCount, ContactDoesNotExist, ValueError) as e:
                print(str(e))
        elif command == "show-birthday":
            try:
                name = args[0]
                print(book.show_birthday(name))
            except (InvalidParameterCount, ContactDoesNotExist, NoBirthdaySet) as e:
                print(str(e))
        elif command == "birthdays":
            upcoming_birthdays = book.get_birthdays_per_week()
            if upcoming_birthdays:
                for day, names in upcoming_birthdays.items():
                    print(f"{day}: {', '.join(names)}")
            else:
                print("No upcoming birthdays in the next week.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
