import streamlit as st

st.subheader("Short documentation on how to use the optimizer")

st.write("#")

st.markdown("1. Select any amount (min. 2) of ISIN's from the database at the top of the optimizer.   \n   If needed, you can also use the filters above the table to filter for your needs.")
st.markdown("2. You have the possibility to adjust the weighting of the ISIN's. Its important that the total weights add up to 100 otherwise you won't be able to continue.")
st.markdown("3. You can visually review your portfolio allocation by Sector, Continent and Currency.")
st.markdown("4. There are several optimization parameters to play around:   \n   - You can weight the importance of the yearly return, yearly risk and ESG score with 3 sliders   \n   - You can enter the amount of simulations. The higher the number the closer you will move to the global optimum but the longer it will take.   \n   - Allow if ISINs can be replaced by better performing ISINs that have the same sector, assetclass & currency.   \n   - Keep strategy: If yes it will keep the strategy as shown above with sector, continent and currency. Min. 10 ISIN's have to be selected and please also note that it may take much longer to optimize")
st.markdown("5. Review the optimization results with a two dimensional visualisation as well as a 3D Plot. The 3D plot is neccesarry to see the impact of the ESG score")
st.markdown("6. Download resuls of ISIN's and weights as a .csv file")

st.write("#")
st.write("#")

st.markdown("**The optimizer tries to:**   \n   - reduce the yearly risk as much as possible   \n   - reduce the ESG score as much as possible   \n   - increase the yearly return as much as possible")