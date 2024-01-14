# Step Two - Project Proposal

1. **What goal will your website be designed to achieve?**

   - The goal will be to allow an easier comparison of market capitalization across various assets such as traditional stocks and cryptocurrencies.

2. **What kind of users will visit your site? In other words, what is the demographic of your users?**

   - Those that would like more insight into specific assets, their relative size, their performance, and a comparison of their market capitalizations.

3. **What data do you plan on using? You may have not picked your actual API yet, which is fine, just outline what kind of data you would like it to contain.**
   - Pricing data, specifically that of market capitalizations. This can/may also include current price, price history, outstanding shares, circulating supply, etc.
4. **In brief, outline your approach to creating your project (knowing that you may not know everything in advance and that these details might change later). Answer questions like the ones below, but feel free to add more information:**
   - **What does your database schema look like?**
     - Table 1: Asset Information
       - Columns:
         - Asset ID
         - Asset Name
         - Asset Ticker
         - Current Price
         - Market Capitalization
         - Shares Outstanding/Circulating supply
   - **What kinds of issues might you run into with your API?**
     - Integration with API
     - Inaccurate/inconsistent data
   - **Is there any sensitive information you need to secure?**
     - API key
     - Flask Passkey
     - username/password if applicable
   - **What functionality will your app include?**
     - Switching assets to compare
     - Showing the percent difference of each asset and how one is bigger/smaller than the other
   - **What will the user flow look like?**
     - Open app select asset A select asset B click compare look at output
   - **What features make your site more than CRUD? Do you have any stretch goals?**
     - Finding the percent difference and showing the comparison
     - Potentially add in feature of over time comparison, i.e. weekly/monthly
