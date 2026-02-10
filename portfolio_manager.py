import sqlite3

class PortfolioManager:
    def __init__(self, db_name="portfolio.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL UNIQUE,
                        quantity INTEGER NOT NULL,
                        purchase_price REAL NOT NULL
                    )
                """)
                # Check if current_price column exists, if not add it (migration for existing DBs)
                try:
                    cursor.execute("SELECT current_price FROM stocks LIMIT 1")
                except sqlite3.OperationalError:
                    cursor.execute("ALTER TABLE stocks ADD COLUMN current_price REAL")
                    cursor.execute("UPDATE stocks SET current_price = purchase_price")
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def add_stock(self, symbol, quantity, price):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO stocks (symbol, quantity, purchase_price, current_price) VALUES (?, ?, ?, ?)",
                               (symbol.upper(), quantity, price, price))
                conn.commit()
                msg = f"Successfully added {symbol.upper()}."
                print(msg)
                return True, msg
        except sqlite3.IntegrityError:
            msg = f"Error: Stock {symbol.upper()} already exists. Use update instead."
            print(msg)
            return False, msg
        except sqlite3.Error as e:
            msg = f"Database error: {e}"
            print(msg)
            return False, msg

    def fetch_portfolio_data(self):
        data = []
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT symbol, quantity, purchase_price, current_price FROM stocks")
                rows = cursor.fetchall()
                
                for row in rows:
                    symbol, qty, purchase_price, current_price = row
                    if current_price is None:
                        current_price = purchase_price
                    
                    cost_basis = qty * purchase_price
                    market_value = qty * current_price
                    profit = market_value - cost_basis
                    
                    data.append({
                        "Symbol": symbol,
                        "Quantity": qty,
                        "Purchase Price": purchase_price,
                        "Current Price": current_price,
                        "Total Cost": cost_basis,
                        "Total Value": market_value,
                        "Profit": profit
                    })
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        return data

    def view_portfolio(self):
        data = self.fetch_portfolio_data()
        if not data:
            print("Portfolio is empty.")
            return

        print(f"{'Symbol':<8} {'Qty':<8} {'Cost':<10} {'Mkt Price':<10} {'Tot Cost':<12} {'Cur Val':<12} {'Profit':<10}")
        print("-" * 75)
        total_portfolio_cost = 0
        total_portfolio_value = 0
        
        for item in data:
            print(f"{item['Symbol']:<8} {item['Quantity']:<8} {item['Purchase Price']:<10.2f} {item['Current Price']:<10.2f} {item['Total Cost']:<12.2f} {item['Total Value']:<12.2f} {item['Profit']:<10.2f}")
            total_portfolio_cost += item['Total Cost']
            total_portfolio_value += item['Total Value']
            
        print("-" * 75)
        print(f"Total Portfolio Cost:  TRY{total_portfolio_cost:.2f}")
        print(f"Total Portfolio Value: TRY{total_portfolio_value:.2f}")
        print(f"Total Profit/Loss:     TRY{total_portfolio_value - total_portfolio_cost:.2f}")

    def update_stock(self, symbol, quantity, price):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE stocks SET quantity = ?, purchase_price = ? WHERE symbol = ?",
                               (quantity, price, symbol.upper()))
                if cursor.rowcount > 0:
                    conn.commit()
                    msg = f"Successfully updated {symbol.upper()}."
                    print(msg)
                    return True, msg
                else:
                    msg = f"Error: Stock {symbol.upper()} not found."
                    print(msg)
                    return False, msg
        except sqlite3.Error as e:
            msg = f"Database error: {e}"
            print(msg)
            return False, msg

    def update_market_price(self, symbol, price):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE stocks SET current_price = ? WHERE symbol = ?",
                               (price, symbol.upper()))
                if cursor.rowcount > 0:
                    conn.commit()
                    msg = f"Successfully updated market price for {symbol.upper()}."
                    print(msg)
                    return True, msg
                else:
                    msg = f"Error: Stock {symbol.upper()} not found."
                    print(msg)
                    return False, msg
        except sqlite3.Error as e:
            msg = f"Database error: {e}"
            print(msg)
            return False, msg

    def delete_stock(self, symbol):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stocks WHERE symbol = ?", (symbol.upper(),))
                if cursor.rowcount > 0:
                    conn.commit()
                    msg = f"Successfully deleted {symbol.upper()}."
                    print(msg)
                    return True, msg
                else:
                    msg = f"Error: Stock {symbol.upper()} not found."
                    print(msg)
                    return False, msg
        except sqlite3.Error as e:
            msg = f"Database error: {e}"
            print(msg)
            return False, msg

def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")

def main():
    manager = PortfolioManager()

    while True:
        print("\n--- Stock Portfolio Manager ---")
        print("1. Add Stock")
        print("2. View Portfolio")
        print("3. Update Stock")
        print("4. Update Market Price")
        print("5. Delete Stock")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            symbol = input("Enter Stock Symbol: ")
            qty = get_int_input("Enter Quantity: ")
            price = get_float_input("Enter Purchase Price: ")
            manager.add_stock(symbol, qty, price)
        elif choice == '2':
            manager.view_portfolio()
        elif choice == '3':
            symbol = input("Enter Stock Symbol to Update: ")
            qty = get_int_input("Enter New Quantity: ")
            price = get_float_input("Enter New Purchase Price: ")
            manager.update_stock(symbol, qty, price)
        elif choice == '4':
            symbol = input("Enter Stock Symbol: ")
            price = get_float_input("Enter Current Market Price: ")
            manager.update_market_price(symbol, price)
        elif choice == '5':
            symbol = input("Enter Stock Symbol to Delete: ")
            manager.delete_stock(symbol)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
