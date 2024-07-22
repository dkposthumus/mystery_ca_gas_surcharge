# California Mystery Gas Surcharge Project 

This project is an attempt to replicate the methodology of Severin Borenstein's 
calculations for California's Mystery Gasoline Surcharge, a description of which 
can be found [here](https://faculty.haas.berkeley.edu/borenste/MysterySurchargeCalculation2019May.pdf).
The Mystery Gas Surcharge is the unexplained difference between the retail price
of gasoline in California and the rest of the United State. This unexplained 
difference is the difference in retail price, *beyond* the difference in taxes 
and fees between California and the rest of the country. 

## Resources on the Mystery Gas Surcharge

Severin Borenstein's work on MGS:
- [Methodology](https://faculty.haas.berkeley.edu/borenste/MysterySurchargeCalculation2019May.pdf)
- The most recent [blog post](https://faculty.haas.berkeley.edu/borenste/MysterySurchargeCalculation2019May.pdf) 
summarizing the state of the MGS in January 2023
- The Petroleum Market Advisory Committee's (PMAC) 
[final report](https://efiling.energy.ca.gov/getdocument.aspx?tn=221306) 
(Borenstein was the chair of PMAC)

## Requirements 

For the packages required to run this project, see the "requirements.txt" file in the repository.

## Summary of Borenstein's Methodology
This section reflects only the information provided by Borenstein in the methodology document found above.

The MGS is calculated using the following equation:
\
MGS = (Price<sub>CA</sub> - Taxes<sub>CA</sub> - Enviro_Programs<sub>CA</sub> - CARB_Cost_Premium<sub>CA</sub>) - (Price<sub>USA</sub> - Taxes<sub>USA</sub>), where:

- **Price<sub>CA</sub>** = average retail price of gasoline in California
    - "California All Grades All Formlations Retail Gasoline Prices" from the [EIA](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=emm_epm0_pte_sca_dpg&f=m)
- **Taxes<sub>CA</sub>** = sum of total state and local gasoline taxes per gallon in California
    - State gasoline sale and excise taxes (two separate taxes) are taken from [CDTFA](https://www.cdtfa.ca.gov/taxes-and-fees/sales-tax-rates-for-fuels.htm)
    - Borenstein adds a 1% local sales tax, approximating average local sales tax by city/county jurisdictions (no source)
- **Enviro_Programs<sub>CA</sub>** = per-gallon cost of compliance for the following programs for California:
    - *Borenstein assumes that gasoline sold is E-10, the most common blend of gasoline sold in the US.*
        - *Borenstein assumes that E-10 gasoline is 0.007902 tonnes.*
    - Cap-and-trade (CAX)
        - The price of CAX is determined from the most recent [auction](https://ww2.arb.ca.gov/our-work/programs/cap-and-trade-program/auction-information) held by CA Air Resources Board (CARB)
    - Low Carbon Fuel Standard (LCFS)
        - LCFS credit prices are found [here](https://ww2.arb.ca.gov/resources/documents/lcfs-data-dashboard) under Figure 4
            - This price is transformed into the LCFS cost per gallon through the credit value calculator found [here](https://ww2.arb.ca.gov/resources/documents/lcfs-data-dashboard) under Figure 7
    - UST maintenance fee
        - The UST rate per gallon is found at the [CDTFA](https://www.cdtfa.ca.gov/taxes-and-fees/tax-rates-stfd.htm) under the "Underground Storage Tank Maintenance Fee" table
- **CARB Cost Premium<sub>CA</sub>** = estimate of cost per gallon to produce gas complying with CA's emission standard
    - Borenstein assumes that the nominal cost of CARB standards is 10 cents per gallon, *nominally*
        - Assumed cost is likely higher than true cost, which would result in an under-estimate of MGS
- **Price<sub>USA</sub>** = average retail price of gasoline in the US, excluding CA
    - "U.S. All Grades All Formulations Retail Gasoline Prices" from [EIA](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=emm_epm0_pte_nus_dpg&f=m), adjusted to exclude CA
        - Borenstein assumes that CA has 10% weight in national average
- **Taxes<sub>USA</sub>** = average of state gasoline excise taxes, excluding CA
    - Sum of federal and state taxes applied to gasoline sales in US, excluding CA
        - Borenstein assumes that CA has 10% weight in national average
    - Borenstein does *not* adjust for local fuel taxes outside of CA, this would tend to bias downwards MGS estimate

Note: All data is expressed in March 2023 constant dollars, using [BLS's All-Urban CPI](https://data.bls.gov/timeseries/CUUR0000SA0).

## My Methodology
I tried to replicate Borenstein's approach as closely as possible. However, there were areas where, due to either a lack of clarity or data access, I had to construct my own methods. In his methodology document, Borenstein wrote that he included federal taxes; however in the spreadsheet containing his actual calculations, he did *not* include federal taxes. Therefore, I did not include any federal gas tax data.

Those differences are summarized below:
- **Price<sub>CA</sub>** 
    - Here I was able to exactly replicate Borenstein's approach/data
- **Taxes<sub>CA</sub>** = sum of total state and local gasoline taxes per gallon in California
    - Here I was able to exactly replicate Borenstein's approach/data
- **Enviro_Programs<sub>CA</sub>**
    - Here I replicated Borenstein's approach/data, although I had to make the following clarifying assumptions:
    - Cap-and-trade (CAX)
        - From the CARB's summary of CAX auctions [table](https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf), I pulled the "Current Auction Settlement Price", which is the price per tonne of CO2e. Thus, to find the cost of gallon I multiplied the price by 0.007902. I then filled in the intervening months with the most recent auction price.
            - For example, there were auctions in August 2022 and November 2022. Thus, the auction price observations for September and October 2022 match that for August 2022, and December 2022's observation matches November 2022's.
    - Low Carbon Fuel Standard (LCFS)
        - I pulled the LCFS credit prices from this [spreadsheet](https://ww2.arb.ca.gov/resources/documents/lcfs-data-dashboard#:~:text=to%20ease%20compliance.-,Figure%204,-orted%20by%20Argus).
            - Then, that credit price is plugged into this [credit value spreadsheet](https://ww2.arb.ca.gov/resources/documents/lcfs-data-dashboard#:~:text=from%20fish%20processing.-,Figure%207,-Figure%208). 
                - Borenstein did not leave clear instructions here.
                - So as to not to upwards bias estimates, I assumed the maximum pass-through cost for gasoline, associated with a carbon intensity (CI) score of 100.82 gCO2e/MJ. 
                    - Then, the quantity of the LCFS premium is calculated by the following formula:
$$
\text{lcfs\_cost} = -\frac{\left( (\text{gas\_ci\_standard} - 99.78) \times 107.577 + (\text{gas\_ci\_standard} - 79.9) \times 8.151 \right) \times \text{lcfs\_credit\_price}}{1000000}
$$
which is adopted from the credit value spreadsheet. gas_ci_standard varies year-by-year and its data can also be found on the credit value spreadsheet.

For the UST, I was able to exactly replicate Borenstein's approach/data.
- **CARB Cost Premium<sub>CA</sub>**
    - I copied Borenstein's assumption that the CARB cost premium was precisely 10 cents nominally over time.
- **Price<sub>USA</sub>**
    - I use the same EIA series as Borenstein does. 
    - I have data on monthly motor fuel sales reported by states from [here](https://catalog.data.gov/dataset/monthly-motor-fuel-sales-reported-by-states-selected-data-from-fhwa-monthly-motor-fuel-rep).
        - From this data, I derived California's share of monthly motor fuel sales across the whole country and then used this instead of Borenstein's constant assumption of 10%.
- **Taxes<sub>USA</sub>**
    - I pulled state-by-state excise tax data from [here](https://catalog.data.gov/dataset/tax-rates-by-motor-fuel-and-state). I then used the monthly motor fuel sales to create a weighted average excise tax, weighted by motor fuel sales--*excluding California*. Borenstein only pulled a top-line number and used assumption that California was responsible for 10% of gas sales to find an average excluding California.
    - Like Borenstein, I also exclude local sales taxes outside of CA.