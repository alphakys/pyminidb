from src.pager import Pager
from src.page import Page
from src.row import Row
import sys


class Table:
    """
    DB Engine Core.
    Pager와 Page를 조율하여 실제 SQL 로직을 수행합니다.
    (현재는 Page 0만 사용하는 Simplest Ver.)
    """

    def __init__(self, filename="mydb.db"):
        self.pager = Pager(filename)

    def execute_insert(self, id: int, username: str, email: str) -> bool:
        # [TODO 1] Insert Implement
        # 1. Read Page 0 from Pager
        # 2. If page is None, create new Page()
        # 3. Insert Row
        # 4. Write back to Pager (Persistence)
        curr_page: Page = self.pager.read_page(0)
        if not curr_page:
            curr_page = Page()

        is_success = curr_page.insert(Row(int(id), username, email))
        if is_success:
            self.pager.write_page(page_num=0, page=curr_page)
            return True
        else:
            return False

    def execute_select(self):
        # [TODO 2] Select Implement
        # 1. Read Page 0
        # 2. If None, print nothing
        # 3. Loop and Print all rows (How to know how many rows? page.num_rows)
        curr_page = self.pager.read_page(page_num=0)
        if curr_page:
            for i in range(curr_page.num_rows):
                print(curr_page.read_at(i))
        else:
            print("No data Found")

    def close(self):
        self.pager.close()


def main():
    table = Table()

    print("PyMiniDB version 0.1")
    print("Enter .exit to quit.")

    while True:
        try:
            user_input = input("db > ").strip()

            # 1. Handle Meta Commands
            if user_input.startswith("."):
                if user_input == ".exit":
                    table.close()
                    print("Bye!")
                    sys.exit(0)
                else:
                    print(f"Unrecognized command '{user_input}'")
                continue

            # 2. Handle SQL Commands
            # SQL 파싱 로직 (간단하게 구현)
            cmd_parts = user_input.split()
            cmd_type = cmd_parts[0].lower()

            if cmd_type == "insert":
                # db > insert 1 user1 user@1.com
                # [TODO 3] Parsing logic
                table.execute_insert(*cmd_parts[1:])

            elif cmd_type == "select":
                table.execute_select()

            else:
                print(f"Unrecognized keyword at start of '{user_input}'")

        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
