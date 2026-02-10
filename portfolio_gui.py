import streamlit as st # type: ignore
import pandas as pd
from portfolio_manager import PortfolioManager

# Set page configuration
st.set_page_config(page_title="Portfolio Manager", layout="wide")

def main():
    st.title("Stock Portfolio Manager")

    # Initialize the manager
    if 'manager' not in st.session_state:
        st.session_state.manager = PortfolioManager()
    
    manager = st.session_state.manager

    # Sidebar navigation
    st.sidebar.title("Navigation")
    options = ["View Portfolio", "Add Stock", "Update Stock", "Update Market Price", "Delete Stock"]
    choice = st.sidebar.radio("Go to", options)

    if choice == "View Portfolio":
        st.header("Current Portfolio")
        data = manager.fetch_portfolio_data()
        
        if data:
            df = pd.DataFrame(data)
            
            # Display metrics
            total_cost = df["Total Cost"].sum()
            total_value = df["Total Value"].sum()
            total_profit = df["Profit"].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Cost", f"TRY {total_cost:,.2f}")
            col2.metric("Total Value", f"TRY {total_value:,.2f}")
            col3.metric("Total Profit/Loss", f"TRY {total_profit:,.2f}", delta=f"{total_profit:.2f}")
            
            st.divider()
            
            # Display dataframe
            st.dataframe(
                df.style.format({
                    "Purchase Price": "{:.2f}",
                    "Current Price": "{:.2f}",
                    "Total Cost": "{:.2f}",
                    "Total Value": "{:.2f}",
                    "Profit": "{:.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Your portfolio is currently empty. Add some stocks to get started!")

    elif choice == "Add Stock":
        st.header("Add New Stock")
        with st.form("add_stock_form"):
            symbol = st.text_input("Stock Symbol").upper()
            quantity = st.number_input("Quantity", min_value=1, step=1)
            price = st.number_input("Purchase Price", min_value=0.01, step=0.01, format="%.2f")
            submitted = st.form_submit_button("Add Stock")
            
            if submitted:
                if symbol and quantity > 0 and price > 0:
                    success, msg = manager.add_stock(symbol, quantity, price)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in all fields correctly.")

    elif choice == "Update Stock":
        st.header("Update Stock Details")
        with st.form("update_stock_form"):
            symbol = st.text_input("Stock Symbol to Update").upper()
            quantity = st.number_input("New Quantity", min_value=0, step=1)
            price = st.number_input("New Purchase Price", min_value=0.01, step=0.01, format="%.2f")
            submitted = st.form_submit_button("Update Stock")
            
            if submitted:
                if symbol:
                    success, msg = manager.update_stock(symbol, quantity, price)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a stock symbol.")

    elif choice == "Update Market Price":
        st.header("Update Market Price")
        with st.form("update_price_form"):
            symbol = st.text_input("Stock Symbol").upper()
            price = st.number_input("Current Market Price", min_value=0.01, step=0.01, format="%.2f")
            submitted = st.form_submit_button("Update Price")
            
            if submitted:
                if symbol and price > 0:
                    success, msg = manager.update_market_price(symbol, price)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a stock symbol and a valid price.")

    elif choice == "Delete Stock":
        st.header("Delete Stock")
        with st.form("delete_stock_form"):
            symbol = st.text_input("Stock Symbol to Delete").upper()
            submitted = st.form_submit_button("Delete Stock")
            
            if submitted:
                if symbol:
                    success, msg = manager.delete_stock(symbol)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter a stock symbol.")

if __name__ == "__main__":
    main()