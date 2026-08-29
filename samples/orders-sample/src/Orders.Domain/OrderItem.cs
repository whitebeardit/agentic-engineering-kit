namespace Orders.Domain;

/// <summary>Item do pedido. Só o agregado <see cref="Order"/> muda seu estado.</summary>
public sealed class OrderItem
{
    internal OrderItem(Guid id, string sku, int quantity, Money unitPrice)
    {
        if (quantity <= 0)
        {
            throw new DomainRuleViolationException("RN-ORD-002", "Quantidade deve ser maior que zero.");
        }

        Id = id;
        Sku = sku;
        Quantity = quantity;
        UnitPrice = unitPrice;
    }

    public Guid Id { get; }
    public string Sku { get; }
    public int Quantity { get; }
    public Money UnitPrice { get; }
    public bool Cancelled { get; private set; }
    public Money Subtotal => UnitPrice * Quantity;

    internal void Cancel() => Cancelled = true;
}
