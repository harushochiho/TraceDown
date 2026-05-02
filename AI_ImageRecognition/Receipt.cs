namespace AI_ImageRacognition;

public class Receipt
{
    public string CompanyName { get; set; } = string.Empty;
    public List<Item>? Items { get; set; } = [];
    public decimal Subtotal { get; set; }
    public decimal Tax { get; set; }
    public decimal TotalAfterTaxes { get; set; }
}

public class Item
{
    public string Name { get; set; } = string.Empty;
    public decimal Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal TotalPrice { get; set; }
    public string Category { get; set; } = string.Empty;
    public bool OnSale { get; set; }
    public bool Taxable { get; set; }
}