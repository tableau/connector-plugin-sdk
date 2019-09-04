DROP TABLE IF EXISTS "Staples";

\include ../DDL/Staples.sql

copy "Staples"(
        "Item Count"=text(0)csv,
        "Ship Priority"=text(0)csv,
        "Order Priority"=text(0)csv,
        "Order Status"=text(0)csv,
        "Order Quantity"=text(0)csv,
        "Sales Total"=text(0)csv,
        "Discount"=text(0)csv,
        "Tax Rate"=text(0)csv,
        "Ship Mode"=text(0)csv,
        "Fill Time"=text(0)csv,
        "Gross Profit"=text(0)csv,
        "Price"=text(0)csv,
        "Ship Handle Cost"=text(0)csv,
        "Employee Name"=text(0)csv,
        "Employee Dept"=text(0)csv,
        "Manager Name"=text(0)csv,
        "Employee Yrs Exp"=text(0)csv,
        "Employee Salary"=text(0)csv,
        "Customer Name"=text(0)csv,
        "Customer State"=text(0)csv,
        "Call Center Region"=text(0)csv,
        "Customer Balance"=text(0)csv,
        "Customer Segment"=text(0)csv,
        "Prod Type1"=text(0)csv,
        "Prod Type2"=text(0)csv,
        "Prod Type3"=text(0)csv,
        "Prod Type4"=text(0)csv,
        "Product Name"=text(0)csv,
        "Product Container"=text(0)csv,
        "Ship Promo"=text(0)csv,
        "Supplier Name"=text(0)csv,
        "Supplier Balance"=text(0)csv,
        "Supplier Region"=text(0)csv,
        "Supplier State"=text(0)csv,
        "Order ID"=text(0)csv,
        "Order Year"=text(0)csv,
        "Order Month"=text(0)csv,
        "Order Day"=text(0)csv,
        "Order Date"=text(0)csv,
        "Order Quarter"=text(0)csv,
        "Product Base Margin"=text(0)csv,
        "Product ID"=text(0)csv,
        "Receive Time"=text(0)csv,
        "Received Date"=text(0)csv,
        "Ship Date"=text(0)csv,
        "Ship Charge"=text(0)csv,
        "Total Cycle Time"=text(0)csv,
        "Product In Stock"=text(0)csv,
        "PID"=text(0)csv,
        "Market Segment"=text(0)csv
        )
from '../Staples_utf8.csv';
/*
from '../Staples_cp1252.csv';
*/
\p\g
