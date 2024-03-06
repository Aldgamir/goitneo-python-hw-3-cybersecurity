from collections import UserDict
import datetime

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
        if not self.validate_phone():
            raise ValueError("Invalid phone number format")

    def validate_phone(self):
        return len(str(self.value)) <= 10 and str(self.value).isdigit()     # Max number of digits - 10

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate_birthday():
            raise ValueError("Invalid birthday format")

    def validate_birthday(self):
        try:
            datetime.datetime.strptime(self.value, '%d.%m.%Y')
            return True
        except ValueError:
            return False

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.add_birthday(birthday)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phone_str = '; '.join(str(p) for p in self.phones)
        if self.birthday:
            return f"Contact name: {self.name.value}, phones: {phone_str}, birthday: {self.birthday}"
        else:
            return f"Contact name: {self.name.value}, phones: {phone_str}"

class AddressBook(UserDict):
    def add_record(self, name, *phones, birthday=None):
        record = Record(name, birthday)
        for phone in phones:
            record.add_phone(phone)
        self.data[name] = record

    def get_birthdays_per_week(self):
        today = datetime.date.today()
        next_week = today + datetime.timedelta(days=7)
        birthdays = []
        for record in self.data.values():
            if record.birthday:
                b_day, b_month = record.birthday.value.split('.')[:2]
                if int(b_day) >= today.day and int(b_month) == today.month:
                    birthdays.append(record)
                elif int(b_day) < today.day and int(b_month) == next_week.month:
                    birthdays.append(record)
        return birthdays

    def __str__(self):
        if self.data:
            return "\n".join(str(record) for record in self.data.values())
        else:
            return "No contacts found."

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format. Please check the input."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return inner

@input_error
def add_contact(args, address_book):
    name = args[0]
    phones = args[1:]
    address_book.add_record(name, *phones)
    return f"Contact '{name}' added."

@input_error
def remove_contact(args, address_book):
    name = args[0]
    del address_book[name]
    return f"Contact '{name}' removed."

@input_error
def change_contact(args, address_book):
    if len(args) != 3:
        raise ValueError("Invalid command format. Please use: change [name] [old phone number] [new phone number]")
    name, old_phone, new_phone = args
    address_book[name].edit_phone(old_phone, new_phone)
    return f"Phone '{old_phone}' edited to '{new_phone}' for contact '{name}'."

@input_error
def search_contact(args, address_book):
    name = args[0]
    return address_book.data.get(name)

@input_error
def show_phone(args, address_book):
    phone = args[0]
    record = address_book.find_record_by_phone(phone)
    if record:
        return str(record)
    else:
        return f"No contact found for phone '{phone}'."

@input_error
def show_all(address_book):
    return str(address_book)

@input_error
def add_birthday(args, address_book):
    name, birthday = args
    address_book.add_record(name, birthday=birthday)
    return f"Birthday '{birthday}' added to contact '{name}'."

@input_error
def show_birthday(args, address_book):
    name = args[0]
    record = address_book.data.get(name)
    if record and record.birthday:
        return f"Birthday of contact '{name}': {record.birthday}"
    else:
        return f"No birthday found for contact '{name}'."

@input_error
def birthdays(args, address_book):
    birthdays = address_book.get_birthdays_per_week()
    if birthdays:
        return "\n".join(str(record) for record in birthdays)
    else:
        return "No birthdays coming up in the next week."

def parse_input(user_input):
    cmd, *args = user_input.split(maxsplit=1)
    cmd = cmd.strip().lower()
    if args:
        if cmd in ["phone", "delete"]:
            if len(args[0].split()) != 1:
                raise ValueError(f"Invalid command format for '{cmd}'. Please check the input.")
            return cmd, [args[0]]
        elif cmd == "add-birthday":
            return cmd, args[0].split()
        elif cmd == "showbirthday":
            return cmd, args[0].split()
        elif len(args[0].split()) < 2:
            raise ValueError(f"Invalid command format for '{cmd}'. Please check the input.")
        return cmd, args[0].split()
    else:
        return cmd, []

def main():
    print("Welcome to the assistant bot!")
    address_book = AddressBook()
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "end", "finish", "bye"]:                     # eny of these commands are going to close our bot
            print("Good bye!")
            break

        elif command == "hello" or command == "hi":                                  # simply enter 'hello' or 'hi'
            print("How can I help you?")

        elif command == "add" or command == "new" or command == "create":            # cmd format: add [name] [phone number]
            print(add_contact(*args, address_book))

        elif command == "remove" or command == "delete":                             # cmd format: delete [name]
            print(remove_contact(*args, address_book))

        elif command == "change" or command == "update":                             # cmd format: [name] [old number] [new number]
            print(change_contact(*args, address_book))

        elif command == "phone" or command == "contact" or command == "search":      # cmd format: phone [name]
            print(search_contact(*args, address_book))

        elif command == "all":                         # cmd calls all info: name, number and dirthday date
            print(show_all(address_book))

        elif command == "add-birthday":                # Correct format: add-birthday [name] [DD.MM.YYYY]
            print(add_birthday(*args, address_book))

        elif command == "showbirthday":                # Correct format: showbirthday [name]
            print(show_birthday(*args, address_book))  

        elif command == "birthdays":                   # Just enter 'birthdays' to get birthdays for the next week. Return format: [name] [phonenumber] [DD.MM.YYYY]
            print(birthdays(*args, address_book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
