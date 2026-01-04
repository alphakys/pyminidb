from src.table import Table
import sys

# Table Class was moved to src/table.py for better architecture.


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
