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
                if len(cmd_parts) != 4:
                    print("Error: insert requires 3 arguments (id username email)")
                    continue

                try:
                    # 🔧 타입 변환: ID는 정수여야 함
                    id_val = int(cmd_parts[1])
                    username_val = cmd_parts[2]
                    email_val = cmd_parts[3]
                    table.execute_insert(id_val, username_val, email_val)
                except ValueError:
                    print(f"Error: ID must be an integer, got '{cmd_parts[1]}'")
                except Exception as e:
                    print(f"Insert failed: {e}")

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
